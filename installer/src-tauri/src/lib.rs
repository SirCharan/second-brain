use serde::Serialize;
use std::io::{BufRead, BufReader};
use std::path::{Path, PathBuf};
use std::process::{Command, Stdio};
use std::sync::Mutex;
use tauri::{AppHandle, Emitter, State};

const REPO_URL: &str = "https://github.com/SirCharan/second-brain.git";
const CLAUDE_INSTALL_URL: &str = "https://claude.com/claude-code";
const OBSIDIAN_DOWNLOAD_URL: &str = "https://obsidian.md/download";

struct InstallLock(Mutex<()>);

fn home_dir() -> PathBuf {
    std::env::var_os("HOME")
        .map(PathBuf::from)
        .unwrap_or_else(|| PathBuf::from("/"))
}

fn default_vault() -> PathBuf {
    home_dir().join(".claude").join("second-brain-vault")
}

fn repo_dir() -> PathBuf {
    home_dir().join("second-brain")
}

/// GUI apps on macOS don't inherit the login-shell PATH.
fn augmented_path() -> String {
    let home = home_dir();
    let extras = [
        "/opt/homebrew/bin",
        "/opt/homebrew/sbin",
        "/usr/local/bin",
        "/usr/bin",
        "/bin",
        "/usr/sbin",
        "/sbin",
    ];
    let mut parts: Vec<String> = extras.iter().map(|s| s.to_string()).collect();
    parts.push(home.join(".local/bin").display().to_string());
    parts.push(home.join(".cargo/bin").display().to_string());
    if let Ok(existing) = std::env::var("PATH") {
        for p in existing.split(':') {
            if !p.is_empty() && !parts.iter().any(|x| x == p) {
                parts.push(p.to_string());
            }
        }
    }
    parts.join(":")
}

fn which_cmd(name: &str) -> Option<String> {
    let output = Command::new("/usr/bin/env")
        .env("PATH", augmented_path())
        .args(["which", name])
        .output()
        .ok()?;
    if !output.status.success() {
        return None;
    }
    let path = String::from_utf8_lossy(&output.stdout).trim().to_string();
    if path.is_empty() {
        None
    } else {
        Some(path)
    }
}

fn emit_log(app: &AppHandle, line: impl AsRef<str>) {
    let _ = app.emit("install-log", line.as_ref().to_string());
}

#[derive(Serialize, Clone)]
#[serde(rename_all = "camelCase")]
pub struct ToolStatus {
    pub name: String,
    pub ok: bool,
    pub path: Option<String>,
    pub hint: Option<String>,
}

#[derive(Serialize, Clone)]
#[serde(rename_all = "camelCase")]
pub struct PrereqReport {
    pub tools: Vec<ToolStatus>,
    pub vault_path: String,
    pub repo_path: String,
    pub repo_present: bool,
    pub obsidian_installed: bool,
    pub all_required_ok: bool,
}

#[tauri::command]
fn default_vault_path() -> String {
    default_vault().display().to_string()
}

#[tauri::command]
fn check_prereqs() -> PrereqReport {
    let claude = which_cmd("claude");
    let git = which_cmd("git");
    let node = which_cmd("node");
    let brew = which_cmd("brew");

    let tools = vec![
        ToolStatus {
            name: "Claude Code".into(),
            ok: claude.is_some(),
            path: claude.clone(),
            hint: if claude.is_none() {
                Some(format!("Install from {CLAUDE_INSTALL_URL}"))
            } else {
                None
            },
        },
        ToolStatus {
            name: "git".into(),
            ok: git.is_some(),
            path: git.clone(),
            hint: if git.is_none() {
                Some("Install Xcode Command Line Tools or Homebrew git".into())
            } else {
                None
            },
        },
        ToolStatus {
            name: "node".into(),
            ok: node.is_some(),
            path: node.clone(),
            hint: if node.is_none() {
                Some("Install Node from https://nodejs.org or `brew install node`".into())
            } else {
                None
            },
        },
        ToolStatus {
            name: "brew".into(),
            ok: brew.is_some(),
            path: brew.clone(),
            hint: if brew.is_none() {
                Some("Optional — used to install Obsidian. Get it at https://brew.sh".into())
            } else {
                None
            },
        },
    ];

    // node is nice-to-have for the ecosystem; required = Claude Code + git
    let required_ok = claude.is_some() && git.is_some();
    let repo = repo_dir();
    let obsidian = Path::new("/Applications/Obsidian.app").exists();

    PrereqReport {
        tools,
        vault_path: default_vault().display().to_string(),
        repo_path: repo.display().to_string(),
        repo_present: repo.join("install.sh").is_file(),
        obsidian_installed: obsidian,
        all_required_ok: required_ok,
    }
}

fn ensure_repo(app: &AppHandle) -> Result<PathBuf, String> {
    let repo = repo_dir();
    let install_sh = repo.join("install.sh");
    let path = augmented_path();

    if install_sh.is_file() {
        emit_log(app, format!("→ repo present at {}", repo.display()));
        emit_log(app, "→ git pull --ff-only origin main");
        let status = Command::new("git")
            .env("PATH", &path)
            .args(["-C", &repo.display().to_string(), "pull", "--ff-only", "origin", "main"])
            .stdout(Stdio::piped())
            .stderr(Stdio::piped())
            .spawn()
            .and_then(|mut child| {
                if let Some(out) = child.stdout.take() {
                    for line in BufReader::new(out).lines().flatten() {
                        emit_log(app, line);
                    }
                }
                if let Some(err) = child.stderr.take() {
                    for line in BufReader::new(err).lines().flatten() {
                        emit_log(app, line);
                    }
                }
                child.wait()
            })
            .map_err(|e| format!("git pull failed: {e}"))?;

        if !status.success() {
            emit_log(
                app,
                "• git pull did not fast-forward (continuing with local tree)",
            );
        }
        return Ok(repo);
    }

    emit_log(app, format!("→ cloning {REPO_URL} → {}", repo.display()));
    if let Some(parent) = repo.parent() {
        std::fs::create_dir_all(parent).map_err(|e| e.to_string())?;
    }
    // If a partial dir exists without install.sh, remove empty-ish clone attempts carefully.
    if repo.exists() && !install_sh.is_file() {
        // only remove if it looks like a failed clone (no .git or empty)
        let is_empty = std::fs::read_dir(&repo)
            .map(|mut d| d.next().is_none())
            .unwrap_or(false);
        if is_empty {
            let _ = std::fs::remove_dir(&repo);
        } else if !repo.join(".git").exists() {
            return Err(format!(
                "{} exists but is not a second-brain clone. Move it aside and retry.",
                repo.display()
            ));
        }
    }

    let mut child = Command::new("git")
        .env("PATH", &path)
        .args(["clone", "--depth", "1", REPO_URL, &repo.display().to_string()])
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .spawn()
        .map_err(|e| format!("git clone failed to start: {e}"))?;

    if let Some(out) = child.stdout.take() {
        for line in BufReader::new(out).lines().flatten() {
            emit_log(app, line);
        }
    }
    if let Some(err) = child.stderr.take() {
        for line in BufReader::new(err).lines().flatten() {
            emit_log(app, line);
        }
    }

    let status = child.wait().map_err(|e| e.to_string())?;
    if !status.success() {
        return Err("git clone failed".into());
    }
    if !repo.join("install.sh").is_file() {
        return Err("clone succeeded but install.sh is missing".into());
    }
    Ok(repo)
}

#[tauri::command]
fn install_plugin(
    app: AppHandle,
    lock: State<'_, InstallLock>,
    vault_path: String,
) -> Result<String, String> {
    let _guard = lock
        .0
        .lock()
        .map_err(|_| "install already in progress".to_string())?;

    let vault = vault_path.trim();
    if vault.is_empty() {
        return Err("vault path is empty".into());
    }
    let vault_pb = PathBuf::from(vault);
    if let Some(parent) = vault_pb.parent() {
        std::fs::create_dir_all(parent).map_err(|e| format!("cannot create vault parent: {e}"))?;
    }

    emit_log(&app, "second-brain installer");
    emit_log(&app, format!("vault → {vault}"));

    let repo = ensure_repo(&app)?;
    let script = repo.join("install.sh");
    emit_log(&app, format!("→ running {}", script.display()));

    let mut child = Command::new("bash")
        .env("PATH", augmented_path())
        .env("CLAUDE_MEMORY_DIR", vault)
        .env("HOME", home_dir())
        .arg(&script)
        .current_dir(&repo)
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .spawn()
        .map_err(|e| format!("failed to start install.sh: {e}"))?;

    let stdout = child.stdout.take();
    let stderr = child.stderr.take();

    // Drain stdout then stderr (install.sh is mostly sequential).
    if let Some(out) = stdout {
        for line in BufReader::new(out).lines().flatten() {
            emit_log(&app, line);
        }
    }
    if let Some(err) = stderr {
        for line in BufReader::new(err).lines().flatten() {
            emit_log(&app, line);
        }
    }

    let status = child.wait().map_err(|e| e.to_string())?;
    if status.success() {
        emit_log(&app, "✓ plugin install finished");
        Ok(format!("Installed. Vault: {vault}"))
    } else {
        let code = status.code().unwrap_or(-1);
        Err(format!("install.sh exited with code {code}"))
    }
}

// Optional: wire the second-brain MCP server into Claude Desktop + Cursor by running
// `python3 mcp/mcp-setup.py --write` (idempotent; backs up each client config first).
#[tauri::command]
fn setup_mcp(app: AppHandle, vault_path: String) -> Result<String, String> {
    let vault = vault_path.trim();
    let repo = ensure_repo(&app)?;
    let script = repo.join("mcp").join("mcp-setup.py");
    emit_log(&app, format!("→ python3 {} --write", script.display()));

    let mut child = Command::new("python3")
        .env("PATH", augmented_path())
        .env("CLAUDE_MEMORY_DIR", vault)
        .env("HOME", home_dir())
        .arg(&script)
        .arg("--write")
        .current_dir(&repo)
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .spawn()
        .map_err(|e| format!("failed to start mcp-setup.py: {e}"))?;

    if let Some(out) = child.stdout.take() {
        for line in BufReader::new(out).lines().flatten() {
            emit_log(&app, line);
        }
    }
    if let Some(err) = child.stderr.take() {
        for line in BufReader::new(err).lines().flatten() {
            emit_log(&app, line);
        }
    }

    let status = child.wait().map_err(|e| e.to_string())?;
    if status.success() {
        emit_log(&app, "✓ MCP server wired into Claude Desktop + Cursor");
        Ok("MCP configured. Restart Claude Desktop / Cursor to load the tools.".into())
    } else {
        Err(format!(
            "mcp-setup.py exited with code {}",
            status.code().unwrap_or(-1)
        ))
    }
}

#[derive(Serialize, Clone)]
#[serde(rename_all = "camelCase")]
pub struct ObsidianResult {
    pub installed: bool,
    pub message: String,
    pub used_brew: bool,
    pub opened_download: bool,
}

#[tauri::command]
fn install_obsidian(app: AppHandle) -> Result<ObsidianResult, String> {
    if Path::new("/Applications/Obsidian.app").exists() {
        return Ok(ObsidianResult {
            installed: true,
            message: "Obsidian is already installed.".into(),
            used_brew: false,
            opened_download: false,
        });
    }

    let path = augmented_path();
    if which_cmd("brew").is_some() {
        emit_log(&app, "→ brew install --cask obsidian");
        let mut child = Command::new("brew")
            .env("PATH", &path)
            .env("HOME", home_dir())
            .args(["install", "--cask", "obsidian"])
            .stdout(Stdio::piped())
            .stderr(Stdio::piped())
            .spawn()
            .map_err(|e| format!("brew failed to start: {e}"))?;

        if let Some(out) = child.stdout.take() {
            for line in BufReader::new(out).lines().flatten() {
                emit_log(&app, line);
            }
        }
        if let Some(err) = child.stderr.take() {
            for line in BufReader::new(err).lines().flatten() {
                emit_log(&app, line);
            }
        }

        let status = child.wait().map_err(|e| e.to_string())?;
        if status.success() && Path::new("/Applications/Obsidian.app").exists() {
            return Ok(ObsidianResult {
                installed: true,
                message: "Obsidian installed via Homebrew.".into(),
                used_brew: true,
                opened_download: false,
            });
        }
        emit_log(&app, "• brew install did not place Obsidian; opening download page");
    } else {
        emit_log(&app, "• brew not found; opening download page");
    }

    let _ = open::that(OBSIDIAN_DOWNLOAD_URL);
    Ok(ObsidianResult {
        installed: Path::new("/Applications/Obsidian.app").exists(),
        message: format!("Opened {OBSIDIAN_DOWNLOAD_URL} — install Obsidian, then continue."),
        used_brew: false,
        opened_download: true,
    })
}

#[derive(Serialize, Clone)]
#[serde(rename_all = "camelCase")]
pub struct OpenVaultResult {
    pub method: String,
    pub message: String,
}

#[tauri::command]
fn open_vault(vault_path: String) -> Result<OpenVaultResult, String> {
    let vault = vault_path.trim();
    if vault.is_empty() {
        return Err("vault path is empty".into());
    }
    let pb = PathBuf::from(vault);
    if !pb.exists() {
        std::fs::create_dir_all(&pb).map_err(|e| format!("cannot create vault: {e}"))?;
    }

    // Prefer Obsidian deep link when the app is present.
    if Path::new("/Applications/Obsidian.app").exists() {
        let encoded = urlencoding::encode(vault);
        let url = format!("obsidian://open?path={encoded}");
        // `open` on macOS handles custom URL schemes.
        let status = Command::new("open")
            .arg(&url)
            .status()
            .map_err(|e| format!("failed to open Obsidian URL: {e}"))?;
        if status.success() {
            return Ok(OpenVaultResult {
                method: "obsidian".into(),
                message: format!("Opened vault in Obsidian: {vault}"),
            });
        }
    }

    // Fallback: reveal in Finder
    let status = Command::new("open")
        .arg(vault)
        .status()
        .map_err(|e| format!("failed to reveal in Finder: {e}"))?;
    if status.success() {
        Ok(OpenVaultResult {
            method: "finder".into(),
            message: format!("Revealed vault in Finder: {vault}"),
        })
    } else {
        Err("could not open vault in Obsidian or Finder".into())
    }
}

#[tauri::command]
fn open_url(url: String) -> Result<(), String> {
    open::that(&url).map_err(|e| e.to_string())
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_opener::init())
        .plugin(tauri_plugin_dialog::init())
        .manage(InstallLock(Mutex::new(())))
        .invoke_handler(tauri::generate_handler![
            check_prereqs,
            default_vault_path,
            install_plugin,
            install_obsidian,
            setup_mcp,
            open_vault,
            open_url,
        ])
        .setup(|app| {
            // Warm default path into env for any child that reads it.
            let _ = app;
            Ok(())
        })
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}

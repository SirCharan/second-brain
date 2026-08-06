import { invoke } from "@tauri-apps/api/core";
import { listen } from "@tauri-apps/api/event";
import { open as openDialog } from "@tauri-apps/plugin-dialog";

type ToolStatus = {
  name: string;
  ok: boolean;
  path: string | null;
  hint: string | null;
};

type PrereqReport = {
  tools: ToolStatus[];
  vaultPath: string;
  repoPath: string;
  repoPresent: boolean;
  obsidianInstalled: boolean;
  allRequiredOk: boolean;
  pluginModeDetected: boolean;
  pluginInstallPath: string | null;
};

type ObsidianResult = {
  installed: boolean;
  message: string;
  usedBrew: boolean;
  openedDownload: boolean;
};

type OpenVaultResult = {
  method: string;
  message: string;
};

type LogLine = {
  channel: string;
  line: string;
};

const CLAUDE_URL = "https://claude.com/claude-code";

const $ = <T extends HTMLElement>(id: string) =>
  document.getElementById(id) as T | null;

function setBusy(btn: HTMLButtonElement | null, busy: boolean, label?: string) {
  if (!btn) return;
  btn.classList.toggle("busy", busy);
  btn.disabled = busy || btn.dataset.locked === "1";
  if (label) btn.textContent = label;
}

function unlock(btn: HTMLButtonElement | null) {
  if (!btn) return;
  btn.disabled = false;
  btn.dataset.locked = "0";
}

function markStep(id: string, state: "active" | "done" | "idle") {
  const el = $(id);
  if (!el) return;
  el.classList.remove("is-active", "is-done");
  if (state === "active") el.classList.add("is-active");
  if (state === "done") el.classList.add("is-done");
}

function showNote(id: string, text: string) {
  const el = $(id);
  if (!el) return;
  el.hidden = false;
  el.textContent = text;
}

function appendLog(channel: string, line: string) {
  const log = $<HTMLPreElement>(`log-${channel}`);
  if (!log) return;
  log.hidden = false;
  log.textContent = (log.textContent ? log.textContent + "\n" : "") + line;
  log.scrollTop = log.scrollHeight;
}

function clearLog(channel: string) {
  const log = $<HTMLPreElement>(`log-${channel}`);
  if (!log) return;
  log.hidden = false;
  log.textContent = "";
}

function linkifyHint(hint: string): string {
  const urlRe = /(https?:\/\/[^\s]+)/g;
  return hint.replace(
    urlRe,
    (url) => `<a href="${url}" data-external="${url}">${url}</a>`,
  );
}

async function openExternal(url: string) {
  try {
    await invoke("open_url", { url });
  } catch {
    window.open(url, "_blank");
  }
}

async function copyText(text: string): Promise<boolean> {
  try {
    await navigator.clipboard.writeText(text);
    return true;
  } catch {
    // fall through to the legacy path (WKWebView can deny the async API)
  }
  try {
    const ta = document.createElement("textarea");
    ta.value = text;
    ta.style.position = "fixed";
    ta.style.opacity = "0";
    document.body.appendChild(ta);
    ta.select();
    const ok = document.execCommand("copy");
    ta.remove();
    return ok;
  } catch {
    return false;
  }
}

async function init() {
  const vaultInput = $<HTMLInputElement>("vault-path");
  const btnBrowse = $<HTMLButtonElement>("btn-browse");
  const btnCheck = $<HTMLButtonElement>("btn-check");
  const btnInstall = $<HTMLButtonElement>("btn-install");
  const btnSetup = $<HTMLButtonElement>("btn-setup");
  const btnTerminal = $<HTMLButtonElement>("btn-terminal");
  const btnMcp = $<HTMLButtonElement>("btn-mcp");
  const btnObsidian = $<HTMLButtonElement>("btn-obsidian");
  const btnOpen = $<HTMLButtonElement>("btn-open");
  const prereqList = $<HTMLUListElement>("prereq-list");
  const done = $("done");

  const vault = () => vaultInput?.value.trim() || "";

  try {
    const path = await invoke<string>("default_vault_path");
    if (vaultInput) vaultInput.value = path;
  } catch {
    if (vaultInput) vaultInput.value = "~/.claude/second-brain-vault";
  }

  await listen<LogLine>("install-log", (event) => {
    appendLog(event.payload.channel, event.payload.line);
  });

  document.body.addEventListener("click", (e) => {
    const t = e.target as HTMLElement | null;
    const a = t?.closest("a[data-external]") as HTMLAnchorElement | null;
    if (a) {
      e.preventDefault();
      void openExternal(a.dataset.external || a.href);
      return;
    }
    const copyBtn = t?.closest(
      "button[data-copy]",
    ) as HTMLButtonElement | null;
    if (copyBtn) {
      const text = copyBtn.dataset.copy || "";
      void copyText(text).then((ok) => {
        const prev = copyBtn.textContent;
        copyBtn.textContent = ok ? "Copied" : "Select + ⌘C";
        window.setTimeout(() => {
          copyBtn.textContent = prev || "Copy";
        }, 1600);
      });
    }
  });

  btnBrowse?.addEventListener("click", async () => {
    const selected = await openDialog({
      directory: true,
      multiple: false,
      title: "Choose vault folder",
      defaultPath: vaultInput?.value || undefined,
    });
    if (typeof selected === "string" && vaultInput) {
      vaultInput.value = selected;
    }
  });

  async function runCheck() {
    setBusy(btnCheck, true, "Checking…");
    markStep("step-1", "active");
    try {
      const report = await invoke<PrereqReport>("check_prereqs");
      if (prereqList) {
        prereqList.hidden = false;
        prereqList.innerHTML = report.tools
          .map((t) => {
            const mark = t.ok
              ? `<span class="mark ok">✓</span>`
              : `<span class="mark bad">×</span>`;
            const path = t.path
              ? `<span class="tool-path">${escapeHtml(t.path)}</span>`
              : "";
            let hint = "";
            if (!t.ok && t.hint) {
              // Claude Code missing: force known URL
              if (t.name === "Claude Code") {
                hint = `<span class="tool-hint"><a href="${CLAUDE_URL}" data-external="${CLAUDE_URL}">Install Claude Code</a></span>`;
              } else {
                hint = `<span class="tool-hint">${linkifyHint(escapeHtml(t.hint))}</span>`;
              }
            }
            return `<li>${mark}<div><span class="tool-name">${escapeHtml(t.name)}</span>${path}${hint}</div></li>`;
          })
          .join("");
      }

      // Double-install guard: a plugin-mode install + install.sh = every hook fires twice.
      if (report.pluginModeDetected) {
        showNote(
          "plugin-warning",
          `You already run second-brain as a Claude Code plugin` +
            (report.pluginInstallPath
              ? ` (${report.pluginInstallPath})`
              : "") +
            `. Running both the plugin and this installer double-fires every hook, ` +
            `so step 2 is blocked. To switch to this installer, first run ` +
            `“/plugin uninstall second-brain” inside Claude Code, then Check again.`,
        );
      } else {
        const w = $("plugin-warning");
        if (w) w.hidden = true;
      }

      if (report.allRequiredOk && !report.pluginModeDetected) {
        markStep("step-1", "done");
        showNote(
          "prereq-note",
          report.repoPresent
            ? `Ready. Repo at ${report.repoPath}`
            : `Ready. Will clone into ${report.repoPath} on install.`,
        );
        unlock(btnInstall);
        markStep("step-2", "active");
      } else if (!report.allRequiredOk) {
        markStep("step-1", "idle");
        showNote(
          "prereq-note",
          "Install the missing required tools, then Check again.",
        );
      } else {
        // tools fine, but plugin mode blocks the install step
        markStep("step-1", "idle");
        const n = $("prereq-note");
        if (n) n.hidden = true;
      }

      if (report.obsidianInstalled && btnObsidian) {
        btnObsidian.textContent = "Installed";
      }
    } catch (err) {
      showNote("prereq-note", String(err));
    } finally {
      setBusy(btnCheck, false, "Check");
    }
  }

  btnCheck?.addEventListener("click", () => {
    void runCheck();
  });

  // auto-check after listeners are wired
  void runCheck();

  btnInstall?.addEventListener("click", async () => {
    if (!vault()) {
      showNote("prereq-note", "Pick a vault folder first.");
      return;
    }
    clearLog("install");
    setBusy(btnInstall, true, "Running…");
    markStep("step-2", "active");
    try {
      const msg = await invoke<string>("install_plugin", {
        vaultPath: vault(),
      });
      appendLog("install", msg);
      markStep("step-2", "done");
      unlock(btnSetup);
      unlock(btnTerminal);
      unlock(btnMcp);
      unlock(btnObsidian);
      unlock(btnOpen);
      markStep("step-3", "active");
    } catch (err) {
      appendLog("install", `error: ${String(err)}`);
    } finally {
      setBusy(btnInstall, false, "Run");
    }
  });

  btnSetup?.addEventListener("click", async () => {
    clearLog("setup");
    setBusy(btnSetup, true, "Running…");
    markStep("step-3", "active");
    try {
      const msg = await invoke<string>("run_setup", { vaultPath: vault() });
      showNote("setup-note", msg);
      markStep("step-3", "done");
      markStep("step-4", "active");
    } catch (err) {
      showNote("setup-note", String(err));
    } finally {
      setBusy(btnSetup, false, "Run");
    }
  });

  btnTerminal?.addEventListener("click", async () => {
    setBusy(btnTerminal, true, "Opening…");
    try {
      const msg = await invoke<string>("open_terminal_setup", {
        vaultPath: vault(),
      });
      showNote("setup-note", msg);
      markStep("step-3", "done");
      markStep("step-4", "active");
    } catch (err) {
      showNote("setup-note", String(err));
    } finally {
      setBusy(btnTerminal, false, "Finish in Terminal");
    }
  });

  btnMcp?.addEventListener("click", async () => {
    setBusy(btnMcp, true, "Working…");
    markStep("step-4", "active");
    try {
      const msg = await invoke<string>("setup_mcp", { vaultPath: vault() });
      showNote("mcp-note", msg);
      markStep("step-4", "done");
      if (btnMcp) btnMcp.textContent = "Done";
    } catch (err) {
      showNote("mcp-note", String(err));
      if (btnMcp) btnMcp.textContent = "Retry";
    } finally {
      setBusy(btnMcp, false);
      if (btnMcp && btnMcp.textContent === "Working…") {
        btnMcp.textContent = "Set up";
      }
    }
  });

  btnObsidian?.addEventListener("click", async () => {
    setBusy(btnObsidian, true, "Working…");
    markStep("step-6", "active");
    try {
      const res = await invoke<ObsidianResult>("install_obsidian");
      showNote("obsidian-note", res.message);
      if (res.installed) {
        if (btnObsidian) btnObsidian.textContent = "Installed";
      } else {
        if (btnObsidian) btnObsidian.textContent = "Retry";
      }
    } catch (err) {
      showNote("obsidian-note", String(err));
      if (btnObsidian) btnObsidian.textContent = "Retry";
    } finally {
      setBusy(btnObsidian, false);
      if (btnObsidian && btnObsidian.textContent === "Working…") {
        btnObsidian.textContent = "Install";
      }
    }
  });

  btnOpen?.addEventListener("click", async () => {
    setBusy(btnOpen, true, "Opening…");
    markStep("step-6", "active");
    try {
      const res = await invoke<OpenVaultResult>("open_vault", {
        vaultPath: vault(),
      });
      showNote("obsidian-note", res.message);
      markStep("step-6", "done");
      markStep("step-7", "done");
      if (done) done.hidden = false;
    } catch (err) {
      showNote("obsidian-note", String(err));
    } finally {
      setBusy(btnOpen, false, "Open vault");
    }
  });
}

function escapeHtml(s: string): string {
  return s
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

window.addEventListener("DOMContentLoaded", () => {
  void init();
});

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

const CLAUDE_URL = "https://claude.com/claude-code";

const $ = <T extends HTMLElement>(id: string) =>
  document.getElementById(id) as T | null;

function setBusy(btn: HTMLButtonElement | null, busy: boolean, label?: string) {
  if (!btn) return;
  btn.classList.toggle("busy", busy);
  btn.disabled = busy || btn.dataset.locked === "1";
  if (label) btn.textContent = label;
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

function appendLog(line: string) {
  const log = $<HTMLPreElement>("install-log");
  if (!log) return;
  log.hidden = false;
  log.textContent = (log.textContent ? log.textContent + "\n" : "") + line;
  log.scrollTop = log.scrollHeight;
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

async function init() {
  const vaultInput = $<HTMLInputElement>("vault-path");
  const btnBrowse = $<HTMLButtonElement>("btn-browse");
  const btnCheck = $<HTMLButtonElement>("btn-check");
  const btnInstall = $<HTMLButtonElement>("btn-install");
  const btnObsidian = $<HTMLButtonElement>("btn-obsidian");
  const btnOpen = $<HTMLButtonElement>("btn-open");
  const prereqList = $<HTMLUListElement>("prereq-list");
  const done = $("done");

  try {
    const path = await invoke<string>("default_vault_path");
    if (vaultInput) vaultInput.value = path;
  } catch {
    if (vaultInput) vaultInput.value = "~/.claude/second-brain-vault";
  }

  await listen<string>("install-log", (event) => {
    appendLog(event.payload);
  });

  document.body.addEventListener("click", (e) => {
    const t = e.target as HTMLElement | null;
    const a = t?.closest("a[data-external]") as HTMLAnchorElement | null;
    if (a) {
      e.preventDefault();
      void openExternal(a.dataset.external || a.href);
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

  btnCheck?.addEventListener("click", async () => {
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
              const linked = linkifyHint(escapeHtml(t.hint));
              // Claude Code missing: force known URL
              if (t.name === "Claude Code") {
                hint = `<span class="tool-hint"><a href="${CLAUDE_URL}" data-external="${CLAUDE_URL}">Install Claude Code</a></span>`;
              } else {
                hint = `<span class="tool-hint">${linked}</span>`;
              }
            }
            return `<li>${mark}<div><span class="tool-name">${escapeHtml(t.name)}</span>${path}${hint}</div></li>`;
          })
          .join("");
      }

      if (report.allRequiredOk) {
        markStep("step-1", "done");
        showNote(
          "prereq-note",
          report.repoPresent
            ? `Ready. Repo at ${report.repoPath}`
            : `Ready. Will clone into ${report.repoPath} on install.`,
        );
        if (btnInstall) {
          btnInstall.disabled = false;
          btnInstall.dataset.locked = "0";
        }
        markStep("step-2", "active");
      } else {
        markStep("step-1", "idle");
        showNote(
          "prereq-note",
          "Install the missing required tools, then Check again.",
        );
      }

      if (report.obsidianInstalled && btnObsidian) {
        btnObsidian.textContent = "Installed";
      }
    } catch (err) {
      showNote("prereq-note", String(err));
    } finally {
      setBusy(btnCheck, false, "Check");
    }
  });

  btnInstall?.addEventListener("click", async () => {
    const vault = vaultInput?.value.trim() || "";
    if (!vault) {
      showNote("prereq-note", "Pick a vault folder first.");
      return;
    }
    const log = $<HTMLPreElement>("install-log");
    if (log) {
      log.hidden = false;
      log.textContent = "";
    }
    setBusy(btnInstall, true, "Running…");
    markStep("step-2", "active");
    try {
      const msg = await invoke<string>("install_plugin", { vaultPath: vault });
      appendLog(msg);
      markStep("step-2", "done");
      if (btnObsidian) {
        btnObsidian.disabled = false;
        btnObsidian.dataset.locked = "0";
      }
      if (btnOpen) {
        btnOpen.disabled = false;
        btnOpen.dataset.locked = "0";
      }
      markStep("step-3", "active");
    } catch (err) {
      appendLog(`error: ${String(err)}`);
    } finally {
      setBusy(btnInstall, false, "Run");
    }
  });

  btnObsidian?.addEventListener("click", async () => {
    setBusy(btnObsidian, true, "Working…");
    markStep("step-3", "active");
    try {
      const res = await invoke<ObsidianResult>("install_obsidian");
      showNote("obsidian-note", res.message);
      if (res.installed) {
        markStep("step-3", "done");
        if (btnObsidian) btnObsidian.textContent = "Installed";
        markStep("step-4", "active");
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
    const vault = vaultInput?.value.trim() || "";
    setBusy(btnOpen, true, "Opening…");
    markStep("step-4", "active");
    try {
      const res = await invoke<OpenVaultResult>("open_vault", {
        vaultPath: vault,
      });
      showNote("open-note", res.message);
      markStep("step-4", "done");
      markStep("step-3", "done");
      if (done) done.hidden = false;
    } catch (err) {
      showNote("open-note", String(err));
    } finally {
      setBusy(btnOpen, false, "Open");
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

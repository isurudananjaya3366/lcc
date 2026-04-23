#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════╗
║   LankaCommerce Cloud — Docker Setup Tool                ║
║   Windows 11 / Docker Desktop Edition                    ║
║                                                          ║
║   This tool:                                             ║
║     • Checks all prerequisites                           ║
║     • Creates required configuration files               ║
║     • Pulls and starts all Docker services               ║
║     • Verifies the system is working correctly           ║
║     • Opens the app in your browser                      ║
╚══════════════════════════════════════════════════════════╝

Requirements: Python 3.8+, Docker Desktop (Windows 11)
"""

import importlib
import subprocess
# ── Bootstrap: auto-install missing packages ──────────────────
import sys


def _bootstrap_install(package: str, import_name: str | None = None) -> bool:
    """Install a package if not available. Returns True on success."""
    mod = import_name or package
    try:
        importlib.import_module(mod)
        return True
    except ImportError:
        pass
    try:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", package, "--quiet", "--user"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        importlib.import_module(mod)
        return True
    except Exception:
        return False

# Show a basic tkinter splash while packages install
import tkinter as _tk
import tkinter.ttk as _ttk

_splash = _tk.Tk()
_splash.title("LankaCommerce Setup")
_splash.geometry("420x130")
_splash.resizable(False, False)
_splash.configure(bg="#1a1a2e")
_splash.attributes("-topmost", True)
_tk.Label(_splash, text="LankaCommerce Cloud Setup", font=("Segoe UI", 14, "bold"),
          bg="#1a1a2e", fg="#eaeaea").pack(pady=(24, 4))
_splash_lbl = _tk.Label(_splash, text="Initialising…", font=("Segoe UI", 10),
                          bg="#1a1a2e", fg="#90caf9")
_splash_lbl.pack()
_splash_pb = _ttk.Progressbar(_splash, mode="indeterminate", length=360)
_splash_pb.pack(pady=12)
_splash_pb.start(12)
_splash.update()

_PACKAGES = [
    ("customtkinter", "customtkinter"),
    ("Pillow", "PIL"),
    ("requests", "requests"),
]
for _pkg, _mod in _PACKAGES:
    _splash_lbl.config(text=f"Installing {_pkg}…")
    _splash.update()
    _bootstrap_install(_pkg, _mod)

_splash.destroy()
del _splash, _splash_lbl, _splash_pb, _splash_pb

import json
# ── Real imports ───────────────────────────────────────────────
import os
import platform
import re
import shutil
import socket
import threading
import time
import webbrowser
from datetime import datetime
from pathlib import Path
from typing import Optional

import customtkinter as ctk
import requests

# ── Theme & constants ──────────────────────────────────────────

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

APP_NAME    = "LankaCommerce Cloud — Setup Tool"
APP_VERSION = "1.0.0"

COLORS = {
    "bg":       "#0d1117",
    "surface":  "#161b22",
    "card":     "#21262d",
    "border":   "#30363d",
    "primary":  "#2d7dd2",
    "success":  "#3fb950",
    "warning":  "#d29922",
    "error":    "#f85149",
    "info":     "#58a6ff",
    "text":     "#c9d1d9",
    "muted":    "#8b949e",
    "white":    "#f0f6fc",
}

# Ports used by the application
REQUIRED_PORTS = {
    3000: "Frontend (Next.js)",
    8000: "Backend (Django)",
    8001: "Backend proxy (nginx override)",
    5432: "PostgreSQL",
    6379: "Redis",
    6432: "PgBouncer",
    5555: "Flower (Celery monitor)",
}

# Services and their container names
SERVICES = [
    ("lcc-postgres",       "PostgreSQL"),
    ("lcc-pgbouncer",      "PgBouncer"),
    ("lcc-redis",          "Redis"),
    ("lcc-backend",        "Django API"),
    ("lcc-celery-worker",  "Celery Worker"),
    ("lcc-celery-beat",    "Celery Beat"),
    ("lcc-flower",         "Flower"),
    ("lcc-frontend",       "Next.js"),
]

HEALTH_TIMEOUT  = 300   # seconds to wait for services
HEALTH_INTERVAL = 5     # polling interval

# ── Path resolution ────────────────────────────────────────────

def _find_project_root() -> Optional[Path]:
    """Walk up from this script's location until we find docker-compose.yml."""
    here = Path(__file__).resolve().parent
    for candidate in [here, here.parent, here.parent.parent]:
        if (candidate / "docker-compose.yml").exists():
            return candidate
    return None

PROJECT_ROOT = _find_project_root()


# ── Docker command builder ─────────────────────────────────────

def _docker_cmd(args: list[str]) -> list[str]:
    """
    Build the correct docker / docker compose command for this OS.
    - Windows 11 + Docker Desktop  → `docker compose …`  (no WSL prefix)
    - Windows 10 + Docker in WSL   → `wsl bash -c "cd … && docker compose …"`
    """
    return ["docker"] + args


def _compose_cmd(args: list[str], cwd: Path) -> list[str]:
    """Build `docker compose <args>` command."""
    return ["docker", "compose"] + args


def _run(cmd: list[str], cwd: Optional[Path] = None, timeout: int = 120) -> tuple[int, str, str]:
    """Run a command, return (returncode, stdout, stderr)."""
    try:
        proc = subprocess.run(
            cmd,
            cwd=str(cwd) if cwd else None,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return proc.returncode, proc.stdout.strip(), proc.stderr.strip()
    except subprocess.TimeoutExpired:
        return -1, "", "Command timed out"
    except FileNotFoundError as e:
        return -1, "", str(e)
    except Exception as e:
        return -1, "", str(e)


# ══════════════════════════════════════════════════════════════
#  Setup Steps
# ══════════════════════════════════════════════════════════════

class SetupStep:
    """Represents a single setup step."""
    def __init__(self, name: str, description: str, weight: int = 1):
        self.name        = name
        self.description = description
        self.weight      = weight   # relative time weight for progress
        self.status      = "pending"   # pending | running | done | error | skipped
        self.detail      = ""


STEPS: list[SetupStep] = [
    SetupStep("prerequisites",  "Check prerequisites",           weight=1),
    SetupStep("wsl_docker",     "Docker Desktop / WSL setup",   weight=1),
    SetupStep("project",        "Locate project files",          weight=1),
    SetupStep("env_files",      "Configure environment files",   weight=1),
    SetupStep("docker_running", "Verify Docker is running",      weight=1),
    SetupStep("pull_images",    "Pull Docker images",            weight=8),
    SetupStep("start_services", "Start services",                weight=2),
    SetupStep("wait_healthy",   "Wait for services (auto-fix)",  weight=6),
    SetupStep("verify_app",     "Verify application endpoints",  weight=2),
    SetupStep("complete",       "Setup complete",                weight=1),
]


# ══════════════════════════════════════════════════════════════
#  Main Application GUI
# ══════════════════════════════════════════════════════════════

class SetupApp(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title(APP_NAME)
        self.geometry("900x680")
        self.minsize(760, 580)
        self.configure(fg_color=COLORS["bg"])

        # State
        self._running   = False
        self._cancelled = False
        self._thread: Optional[threading.Thread] = None
        self._project_root: Optional[Path] = PROJECT_ROOT

        # Build UI
        self._build_ui()
        self.protocol("WM_DELETE_WINDOW", self._on_close)

        # Welcome
        self.after(200, self._show_welcome)

    # ── UI Construction ────────────────────────────────────────

    def _build_ui(self):
        # ── Header ──────────────────────────────────────────
        header = ctk.CTkFrame(self, fg_color=COLORS["surface"], corner_radius=0, height=72)
        header.pack(fill="x", side="top")
        header.pack_propagate(False)

        ctk.CTkLabel(
            header,
            text="🚀  LankaCommerce Cloud",
            font=ctk.CTkFont("Segoe UI", 22, "bold"),
            text_color=COLORS["white"],
        ).pack(side="left", padx=24, pady=16)

        ctk.CTkLabel(
            header,
            text=f"Docker Setup Tool  v{APP_VERSION}",
            font=ctk.CTkFont("Segoe UI", 11),
            text_color=COLORS["muted"],
        ).pack(side="right", padx=24)

        # ── Body: step list (left) + log (right) ────────────
        body = ctk.CTkFrame(self, fg_color=COLORS["bg"], corner_radius=0)
        body.pack(fill="both", expand=True, padx=0, pady=0)

        # Left panel — step list
        left = ctk.CTkFrame(body, fg_color=COLORS["surface"], corner_radius=0, width=240)
        left.pack(side="left", fill="y")
        left.pack_propagate(False)

        ctk.CTkLabel(
            left,
            text="SETUP STEPS",
            font=ctk.CTkFont("Segoe UI", 10, "bold"),
            text_color=COLORS["muted"],
        ).pack(pady=(20, 8), padx=16, anchor="w")

        self._step_labels: dict[str, ctk.CTkLabel] = {}
        self._step_icons:  dict[str, ctk.CTkLabel] = {}

        for step in STEPS[:-1]:   # exclude "complete" dummy step
            row = ctk.CTkFrame(left, fg_color="transparent", height=36)
            row.pack(fill="x", padx=12, pady=2)
            row.pack_propagate(False)

            icon_lbl = ctk.CTkLabel(row, text="○", width=20,
                                    font=ctk.CTkFont("Segoe UI", 13),
                                    text_color=COLORS["muted"])
            icon_lbl.pack(side="left", padx=(4, 6))

            txt_lbl = ctk.CTkLabel(row, text=step.description,
                                   font=ctk.CTkFont("Segoe UI", 11),
                                   text_color=COLORS["muted"],
                                   anchor="w")
            txt_lbl.pack(side="left", fill="x", expand=True)

            self._step_icons[step.name]  = icon_lbl
            self._step_labels[step.name] = txt_lbl

        # Right panel — log + progress
        right = ctk.CTkFrame(body, fg_color=COLORS["bg"], corner_radius=0)
        right.pack(side="left", fill="both", expand=True)

        # Current step banner
        self._status_var = ctk.StringVar(value="Ready to start setup")
        self._status_lbl = ctk.CTkLabel(
            right,
            textvariable=self._status_var,
            font=ctk.CTkFont("Segoe UI", 13, "bold"),
            text_color=COLORS["info"],
            anchor="w",
        )
        self._status_lbl.pack(fill="x", padx=20, pady=(18, 4))

        # Detail sub-label
        self._detail_var = ctk.StringVar(value="")
        ctk.CTkLabel(
            right,
            textvariable=self._detail_var,
            font=ctk.CTkFont("Segoe UI", 10),
            text_color=COLORS["muted"],
            anchor="w",
        ).pack(fill="x", padx=20, pady=(0, 8))

        # Overall progress
        prog_frame = ctk.CTkFrame(right, fg_color="transparent")
        prog_frame.pack(fill="x", padx=20, pady=(0, 4))

        ctk.CTkLabel(prog_frame, text="Overall progress",
                     font=ctk.CTkFont("Segoe UI", 10),
                     text_color=COLORS["muted"]).pack(anchor="w")

        self._progress_bar = ctk.CTkProgressBar(
            prog_frame,
            mode="determinate",
            height=14,
            progress_color=COLORS["primary"],
            fg_color=COLORS["card"],
            corner_radius=6,
        )
        self._progress_bar.pack(fill="x", pady=(4, 0))
        self._progress_bar.set(0)

        self._pct_var = ctk.StringVar(value="0%")
        ctk.CTkLabel(prog_frame, textvariable=self._pct_var,
                     font=ctk.CTkFont("Segoe UI", 10),
                     text_color=COLORS["muted"]).pack(anchor="e")

        # Log panel
        log_frame = ctk.CTkFrame(right, fg_color=COLORS["card"],
                                  corner_radius=8, border_width=1,
                                  border_color=COLORS["border"])
        log_frame.pack(fill="both", expand=True, padx=20, pady=(8, 4))

        ctk.CTkLabel(log_frame, text="  Setup Log",
                     font=ctk.CTkFont("Consolas", 10, "bold"),
                     text_color=COLORS["muted"],
                     anchor="w").pack(fill="x", padx=4, pady=(6, 0))

        self._log_text = ctk.CTkTextbox(
            log_frame,
            font=ctk.CTkFont("Consolas", 11),
            fg_color=COLORS["card"],
            text_color=COLORS["text"],
            corner_radius=0,
            border_width=0,
            wrap="word",
            state="disabled",
        )
        self._log_text.pack(fill="both", expand=True, padx=4, pady=(2, 4))

        # Tag colours (using underlying tk widget)
        self._log_text._textbox.tag_config("success", foreground=COLORS["success"])
        self._log_text._textbox.tag_config("error",   foreground=COLORS["error"])
        self._log_text._textbox.tag_config("warning", foreground=COLORS["warning"])
        self._log_text._textbox.tag_config("info",    foreground=COLORS["info"])
        self._log_text._textbox.tag_config("dim",     foreground=COLORS["muted"])
        self._log_text._textbox.tag_config("bold",    font=("Consolas", 11, "bold"))

        # ── Footer: action buttons ───────────────────────────
        footer = ctk.CTkFrame(self, fg_color=COLORS["surface"],
                               corner_radius=0, height=60)
        footer.pack(fill="x", side="bottom")
        footer.pack_propagate(False)

        btn_frame = ctk.CTkFrame(footer, fg_color="transparent")
        btn_frame.pack(side="right", padx=20, pady=10)

        self._cancel_btn = ctk.CTkButton(
            btn_frame, text="Cancel", width=100,
            fg_color=COLORS["card"], hover_color=COLORS["border"],
            text_color=COLORS["muted"],
            command=self._on_close,
        )
        self._cancel_btn.pack(side="left", padx=4)

        self._start_btn = ctk.CTkButton(
            btn_frame, text="▶  Start Setup", width=160,
            fg_color=COLORS["primary"], hover_color="#1a5a9e",
            font=ctk.CTkFont("Segoe UI", 13, "bold"),
            command=self._start_setup,
        )
        self._start_btn.pack(side="left", padx=4)

        self._open_btn = ctk.CTkButton(
            btn_frame, text="🌐  Open App", width=140,
            fg_color=COLORS["success"], hover_color="#2a8a3e",
            font=ctk.CTkFont("Segoe UI", 12, "bold"),
            command=self._open_app,
            state="disabled",
        )
        self._open_btn.pack(side="left", padx=4)

        # Left side of footer: project path
        self._path_var = ctk.StringVar(
            value=f"Project: {PROJECT_ROOT}" if PROJECT_ROOT else "Project: Not found"
        )
        ctk.CTkLabel(footer, textvariable=self._path_var,
                     font=ctk.CTkFont("Segoe UI", 9),
                     text_color=COLORS["muted"]).pack(side="left", padx=16)

    # ── Logging helpers ────────────────────────────────────────

    def _log(self, msg: str, level: str = "info"):
        """Append a log line (thread-safe)."""
        self.after(0, self._log_ui, msg, level)

    def _log_ui(self, msg: str, level: str):
        ts    = datetime.now().strftime("%H:%M:%S")
        icons = {"success": "✓", "error": "✗", "warning": "⚠",
                 "info": "›", "dim": " "}
        icon  = icons.get(level, "›")

        self._log_text.configure(state="normal")
        self._log_text._textbox.insert("end", f"[{ts}] {icon} ", "dim")
        self._log_text._textbox.insert("end", msg + "\n", level)
        self._log_text._textbox.see("end")
        self._log_text.configure(state="disabled")

    def _log_section(self, title: str):
        self._log(f"{'─' * 55}", "dim")
        self._log(f"  {title}", "bold")
        self._log(f"{'─' * 55}", "dim")

    # ── Progress helpers ───────────────────────────────────────

    def _set_progress(self, fraction: float):
        self.after(0, self._progress_bar.set, min(fraction, 1.0))
        self.after(0, self._pct_var.set, f"{int(fraction * 100)}%")

    def _set_status(self, msg: str, detail: str = ""):
        self.after(0, self._status_var.set, msg)
        self.after(0, self._detail_var.set, detail)

    def _mark_step(self, name: str, status: str):
        icons    = {"running": "◉", "done": "✓", "error": "✗",
                    "skipped": "–", "pending": "○"}
        colours  = {
            "running": COLORS["primary"], "done": COLORS["success"],
            "error":   COLORS["error"],   "skipped": COLORS["muted"],
            "pending": COLORS["muted"],
        }
        icon  = icons.get(status, "○")
        color = colours.get(status, COLORS["muted"])

        def _upd():
            if name in self._step_icons:
                self._step_icons[name].configure(text=icon, text_color=color)
            if name in self._step_labels:
                self._step_labels[name].configure(text_color=color)
        self.after(0, _upd)

    # ── Welcome message ────────────────────────────────────────

    def _show_welcome(self):
        self._log_section("Welcome to LankaCommerce Cloud Setup")
        self._log("This tool will set up your development environment.", "info")
        self._log("It will check prerequisites, configure files,", "info")
        self._log("pull Docker images, and start all services.", "info")
        self._log("", "dim")
        self._log("Prerequisites required on your PC:", "info")
        self._log("  • Docker Desktop (running)", "dim")
        self._log("  • Python 3.8 or later", "dim")
        self._log("  • Git (optional, for updates)", "dim")
        self._log("", "dim")
        self._log("Press  ▶ Start Setup  to begin.", "warning")

    # ── Setup orchestration ────────────────────────────────────

    def _start_setup(self):
        if self._running:
            return
        self._running   = True
        self._cancelled = False
        self._start_btn.configure(state="disabled", text="Running…")
        self._cancel_btn.configure(text="Stop")
        self._thread = threading.Thread(target=self._run_setup, daemon=True)
        self._thread.start()

    def _run_setup(self):
        """Main setup sequence (runs in background thread)."""
        total_weight = sum(s.weight for s in STEPS)
        done_weight  = 0
        success      = True

        def advance(step: SetupStep):
            nonlocal done_weight
            done_weight += step.weight
            self._set_progress(done_weight / total_weight)

        try:
            # ── Step 1: Prerequisites ──────────────────────
            step = STEPS[0]
            self._mark_step(step.name, "running")
            self._set_status("Checking prerequisites…")
            self._log_section("Step 1 — Prerequisites")

            ok, errors = self._check_prerequisites()
            if not ok:
                for e in errors:
                    self._log(e, "error")
                self._mark_step(step.name, "error")
                self._fail("Prerequisites check failed. Please fix the issues above and try again.")
                return
            advance(step)
            self._mark_step(step.name, "done")

            # ── Step 2: WSL + Docker Desktop check ─────────
            step = STEPS[1]
            self._mark_step(step.name, "running")
            self._set_status("Checking Docker Desktop / WSL integration…")
            self._log_section("Step 2 — Docker Desktop & WSL Setup")
            self._setup_wsl_docker()
            advance(step)
            self._mark_step(step.name, "done")

            # ── Step 3: Locate project ─────────────────────
            step = STEPS[2]
            self._mark_step(step.name, "running")
            self._set_status("Locating project files…")
            self._log_section("Step 2 — Project Location")

            if not self._project_root:
                self._mark_step(step.name, "error")
                self._fail("Could not find docker-compose.yml.\nPlease run this script from inside the project folder.")
                return

            self._log(f"Project root: {self._project_root}", "success")
            advance(step)
            self._mark_step(step.name, "done")

            # ── Step 4: Environment files ──────────────────
            step = STEPS[3]
            self._mark_step(step.name, "running")
            self._set_status("Configuring environment files…")
            self._log_section("Step 3 — Environment Files")

            self._setup_env_files()
            advance(step)
            self._mark_step(step.name, "done")

            # ── Step 5: Docker running ─────────────────────
            step = STEPS[4]
            self._mark_step(step.name, "running")
            self._set_status("Verifying Docker Desktop…")
            self._log_section("Step 4 — Docker Status")

            ok = self._check_docker_running()
            if not ok:
                self._mark_step(step.name, "error")
                self._fail("Docker Desktop is not running.\nPlease start Docker Desktop and try again.")
                return
            advance(step)
            self._mark_step(step.name, "done")

            # ── Step 6: Pull images ────────────────────────
            step = STEPS[5]
            self._mark_step(step.name, "running")
            self._set_status("Pulling Docker images…", "This may take several minutes on first run")
            self._log_section("Step 5 — Pull Docker Images")
            self._log("Downloading images. This may take 5–15 minutes on first run.", "warning")

            ok = self._docker_pull()
            if not ok:
                self._mark_step(step.name, "error")
                self._fail("Failed to pull Docker images. Check your internet connection.")
                return
            advance(step)
            self._mark_step(step.name, "done")

            # ── Step 7: Start services ─────────────────────
            step = STEPS[6]
            self._mark_step(step.name, "running")
            self._set_status("Starting all services…")
            self._log_section("Step 6 — Start Services")

            ok = self._docker_up()
            if not ok:
                self._mark_step(step.name, "error")
                self._fail("Failed to start Docker services. Check the log for details.")
                return
            advance(step)
            self._mark_step(step.name, "done")

            # ── Step 8: Wait for health ────────────────────
            step = STEPS[7]
            self._mark_step(step.name, "running")
            self._set_status("Waiting for services to become ready…",
                             "Backend compiles on first start — this may take 60–90 seconds")
            self._log_section("Step 7 — Service Health Check")

            ok = self._wait_for_healthy()
            advance(step)
            if ok:
                self._mark_step(step.name, "done")
            else:
                self._mark_step(step.name, "warning")
                self._log("Some services took longer than expected. Proceeding anyway.", "warning")

            # ── Step 9: Verify app ─────────────────────────
            step = STEPS[8]
            self._mark_step(step.name, "running")
            self._set_status("Verifying application endpoints…")
            self._log_section("Step 8 — Application Verification")

            ok = self._verify_endpoints()
            advance(step)
            if ok:
                self._mark_step(step.name, "done")
            else:
                self._mark_step(step.name, "warning")

            # ── Complete ───────────────────────────────────
            self._set_progress(1.0)
            self._log_section("Setup Complete!")
            self._success()

        except Exception as exc:
            self._log(f"Unexpected error: {exc}", "error")
            self._fail(str(exc))

    # ── Individual step implementations ───────────────────────

    def _setup_wsl_docker(self):
        """Check WSL 2 and Docker Desktop integration on Windows."""
        import platform
        if platform.system() != "Windows":
            self._log("Non-Windows OS — skipping WSL check", "success")
            return

        # Check WSL installed
        rc, out, _ = _run(["wsl", "--status"], timeout=10)
        if rc == 0:
            self._log("WSL is installed", "success")
            for line in out.splitlines():
                line = line.strip()
                if line and ("Default" in line or "Version" in line or "Kernel" in line):
                    self._log(f"  {line}", "dim")
        else:
            # Try listing distros
            rc2, out2, _ = _run(["wsl", "-l", "-v"], timeout=10)
            if rc2 == 0:
                self._log("WSL available (distros listed below)", "success")
                for line in out2.splitlines()[:5]:
                    if line.strip():
                        self._log(f"  {line.strip()}", "dim")
            else:
                self._log("WSL not found — Docker Desktop may still work without it (Windows 11)", "warning")
                self._log("  If Docker fails, enable WSL via: wsl --install", "dim")

        # Check WSL2 is the default version
        rc, out, _ = _run(["wsl", "--list", "--verbose"], timeout=10)
        if rc == 0:
            for line in out.splitlines():
                if "VERSION" not in line and line.strip():
                    parts = line.split()
                    if len(parts) >= 3:
                        name    = parts[-3].lstrip("*").strip()
                        version = parts[-1].strip()
                        state   = parts[-2].strip()
                        if version == "2":
                            self._log(f"  WSL2 distro: {name} ({state}) ✓", "success")
                        elif version == "1":
                            self._log(f"  WSL1 distro: {name} — consider upgrading to WSL2", "warning")
                            self._log(f"    Run: wsl --set-version {name} 2", "dim")

        # Check Docker context
        rc, out, _ = _run(["docker", "context", "ls"], timeout=10)
        if rc == 0:
            for line in out.splitlines():
                if "*" in line:
                    self._log(f"Active Docker context: {line.strip()}", "success")
                    break

        # Check Docker Desktop integration hint
        self._log("Docker Desktop WSL2 integration: enabled by default in Docker Desktop 4.x+", "info")
        self._log("  If issues arise, open Docker Desktop → Settings → Resources → WSL Integration", "dim")

    def _check_prerequisites(self) -> tuple[bool, list[str]]:
        errors = []

        # Python version
        pver = sys.version_info
        self._log(f"Python {pver.major}.{pver.minor}.{pver.micro}", "success")
        if pver < (3, 8):
            errors.append(f"Python 3.8+ required (found {pver.major}.{pver.minor})")

        # OS
        os_info = f"{platform.system()} {platform.release()}"
        self._log(f"OS: {os_info}", "success")

        # Docker CLI
        rc, out, err = _run(["docker", "--version"])
        if rc == 0:
            self._log(f"Docker: {out}", "success")
        else:
            errors.append("Docker CLI not found. Is Docker Desktop installed and in PATH?")

        # Docker Compose
        rc, out, err = _run(["docker", "compose", "version"])
        if rc == 0:
            self._log(f"Docker Compose: {out}", "success")
        else:
            rc, out, err = _run(["docker-compose", "--version"])
            if rc == 0:
                self._log(f"Docker Compose (legacy): {out}", "success")
            else:
                errors.append("Docker Compose not found.")

        # Git (optional)
        rc, out, _ = _run(["git", "--version"])
        if rc == 0:
            self._log(f"Git: {out}", "success")
        else:
            self._log("Git not found (optional — not required for running)", "warning")

        # Port availability
        self._log("", "dim")
        self._log("Checking required ports:", "info")
        busy_ports = []
        for port, name in REQUIRED_PORTS.items():
            in_use = self._is_port_in_use(port)
            if in_use:
                self._log(f"  Port {port} ({name}) is IN USE", "warning")
                busy_ports.append(port)
            else:
                self._log(f"  Port {port} ({name}) — available", "success")

        if busy_ports:
            self._log("Some ports are in use. If they are from a previous run, this is OK.", "warning")

        return len(errors) == 0, errors

    def _is_port_in_use(self, port: int) -> bool:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(0.5)
                return s.connect_ex(("127.0.0.1", port)) == 0
        except Exception:
            return False

    def _setup_env_files(self):
        root = self._project_root

        # docker-compose.override.yml
        override_src = root / "docker-compose.override.example.yml"
        override_dst = root / "docker-compose.override.yml"
        if override_dst.exists():
            self._log("docker-compose.override.yml already exists — keeping", "success")
        elif override_src.exists():
            shutil.copy(override_src, override_dst)
            self._log("Created docker-compose.override.yml from example", "success")
        else:
            self._log("No docker-compose.override.example.yml found — skipping", "warning")

        # .env.docker
        env_dst = root / ".env.docker"
        env_src = root / ".env.docker.example"
        if env_dst.exists():
            self._log(".env.docker already exists — keeping", "success")
        elif env_src.exists():
            shutil.copy(env_src, env_dst)
            self._log("Created .env.docker from example", "success")
        else:
            # Create a minimal .env.docker
            self._log(".env.docker not found — creating minimal config", "warning")
            minimal = self._minimal_env_docker()
            env_dst.write_text(minimal, encoding="utf-8")
            self._log("Created minimal .env.docker", "success")

        # Verify .env.docker is sane
        env_content = env_dst.read_text(encoding="utf-8") if env_dst.exists() else ""
        required_keys = ["CORS_ALLOWED_ORIGINS", "CORS_ALLOW_CREDENTIALS"]
        for key in required_keys:
            if key in env_content:
                self._log(f"  {key} ✓", "dim")
            else:
                self._log(f"  {key} — not set, using default", "warning")

    def _minimal_env_docker(self) -> str:
        return """# LankaCommerce Cloud — Docker Environment
# Auto-generated by setup.py — customise as needed

# Django
DEBUG=True
DJANGO_SETTINGS_MODULE=config.settings.local
DJANGO_SECRET_KEY=docker-dev-secret-change-me-in-production
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,backend,0.0.0.0

# Database
DATABASE_URL=postgres://lcc_user:dev_password_change_me@pgbouncer:6432/lankacommerce

# Redis
REDIS_URL=redis://redis:6379/0
CELERY_BROKER_URL=redis://redis:6379/0

# CORS — must match the frontend URL
CORS_ALLOWED_ORIGINS=http://localhost:3000
CORS_ALLOW_CREDENTIALS=True

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8001/api/v1
NEXT_PUBLIC_APP_URL=http://localhost:3000
NEXT_PUBLIC_SITE_NAME=LankaCommerce Cloud
NEXT_PUBLIC_SITE_DESCRIPTION=Multi-tenant SaaS ERP for Sri Lankan SMEs

# Storage (local filesystem)
STORAGE_BACKEND=local
"""

    def _check_docker_running(self) -> bool:
        rc, out, err = _run(["docker", "info"])
        if rc == 0:
            self._log("Docker Desktop is running", "success")
            # Extract version info
            for line in out.splitlines():
                if "Server Version" in line or "Engine Version" in line:
                    self._log(f"  {line.strip()}", "dim")
            return True
        else:
            self._log("Docker is not running or not accessible", "error")
            self._log(f"Error: {err[:200]}", "dim")
            return False

    def _docker_pull(self) -> bool:
        root = self._project_root
        self._log("Running: docker compose pull", "info")

        proc = subprocess.Popen(
            ["docker", "compose", "pull"],
            cwd=str(root),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )

        for line in proc.stdout:
            line = line.rstrip()
            if line:
                if "Pull complete" in line or "Pulled" in line:
                    self._log(f"  {line}", "success")
                elif "Error" in line or "error" in line:
                    self._log(f"  {line}", "error")
                else:
                    self._log(f"  {line}", "dim")

        rc = proc.wait(timeout=600)
        if rc == 0:
            self._log("All images pulled successfully", "success")
            return True
        else:
            self._log(f"docker compose pull exited with code {rc}", "error")
            return False

    def _docker_up(self) -> bool:
        root = self._project_root
        self._log("Running: docker compose up -d", "info")

        rc, out, err = _run(
            ["docker", "compose", "up", "-d", "--remove-orphans"],
            cwd=root,
            timeout=120,
        )

        for line in (out + "\n" + err).splitlines():
            if line.strip():
                if "Started" in line or "Running" in line:
                    self._log(f"  {line.strip()}", "success")
                elif "Error" in line or "error" in line:
                    self._log(f"  {line.strip()}", "error")
                else:
                    self._log(f"  {line.strip()}", "dim")

        if rc == 0:
            self._log("Services started", "success")
            return True
        else:
            self._log(f"docker compose up exited with code {rc}", "error")
            return False

    def _wait_for_healthy(self) -> bool:
        root                      = self._project_root
        deadline                  = time.time() + HEALTH_TIMEOUT
        all_ok                    = False
        service_unhealthy_count: dict[str, int] = {}
        service_fix_attempts:    dict[str, int] = {}
        FIX_AFTER_POLLS = 3   # try fix after this many consecutive unhealthy polls
        MAX_FIX_ATTEMPTS = 3  # maximum fix attempts per service

        while time.time() < deadline:
            if self._cancelled:
                return False

            rc, out, _ = _run(
                ["docker", "compose", "ps", "--format", "json"],
                cwd=root,
                timeout=15,
            )

            statuses: dict[str, str] = {}

            # Docker compose ps --format json returns one JSON object per line
            if rc == 0:
                for line in out.splitlines():
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        obj    = json.loads(line)
                        name   = obj.get("Name", obj.get("Service", ""))
                        health = obj.get("Health", "")
                        state  = obj.get("State", "")
                        status = health if health else state
                        statuses[name] = status
                    except json.JSONDecodeError:
                        pass

            # Fallback: parse table output
            if not statuses:
                rc2, out2, _ = _run(["docker", "compose", "ps"], cwd=root, timeout=15)
                for line in out2.splitlines():
                    parts = line.split()
                    if len(parts) >= 2 and parts[0].startswith("lcc-"):
                        statuses[parts[0]] = " ".join(parts[1:])

            healthy_count = 0
            total         = len(SERVICES)
            self._set_detail_status(statuses)

            for cname, sname in SERVICES:
                status    = statuses.get(cname, "not started")
                is_ok     = any(k in status.lower() for k in ["healthy", "running"])
                is_exited = any(k in status.lower() for k in ["exited", "dead", "error"])

                if is_ok:
                    healthy_count += 1
                    service_unhealthy_count[cname] = 0  # reset
                else:
                    count = service_unhealthy_count.get(cname, 0) + 1
                    service_unhealthy_count[cname] = count

                    # Trigger a fix attempt after FIX_AFTER_POLLS consecutive failures
                    fix_done = service_fix_attempts.get(cname, 0)
                    if count >= FIX_AFTER_POLLS and fix_done < MAX_FIX_ATTEMPTS:
                        self._log(
                            f"{sname} still not ready (attempt {fix_done+1}/{MAX_FIX_ATTEMPTS}) — applying fix…",
                            "warning",
                        )
                        self._fix_unhealthy_service(cname, sname, fix_done)
                        service_fix_attempts[cname] = fix_done + 1
                        service_unhealthy_count[cname] = 0  # reset counter

                    elif fix_done >= MAX_FIX_ATTEMPTS and is_exited:
                        self._log(f"{sname} exited after {MAX_FIX_ATTEMPTS} fix attempts — giving up on this service", "error")

            elapsed   = int(time.time() - deadline + HEALTH_TIMEOUT)
            remaining = max(0, HEALTH_TIMEOUT - elapsed)
            self._set_status(
                f"Waiting for services… ({healthy_count}/{total} ready)",
                f"Auto-fix active | Timeout in {remaining}s",
            )

            if healthy_count >= total:
                all_ok = True
                self._log(f"All {total} services are healthy!", "success")
                break

            time.sleep(HEALTH_INTERVAL)

        if not all_ok:
            rc, out, _ = _run(["docker", "compose", "ps"], cwd=root, timeout=15)
            self._log("Final service status:", "warning")
            for line in out.splitlines():
                self._log(f"  {line}", "dim")

        return all_ok

    def _get_service_logs(self, cname: str, tail: int = 30) -> str:
        root = self._project_root
        rc, out, _ = _run(
            ["docker", "compose", "logs", f"--tail={tail}", cname],
            cwd=root, timeout=15,
        )
        return out if rc == 0 else ""

    def _fix_unhealthy_service(self, cname: str, sname: str, attempt: int):
        """Diagnose and apply a fix for an unhealthy service."""
        root = self._project_root
        logs = self._get_service_logs(cname, tail=40)
        logs_lower = logs.lower()

        # Show relevant log lines
        self._log(f"  Logs ({cname}, last 10 lines):", "dim")
        for line in logs.splitlines()[-10:]:
            if line.strip():
                if any(k in line.lower() for k in ["error", "fatal", "exception", "traceback", "critical"]):
                    self._log(f"    {line.strip()}", "error")
                elif any(k in line.lower() for k in ["warn"]):
                    self._log(f"    {line.strip()}", "warning")
                else:
                    self._log(f"    {line.strip()}", "dim")

        # ── Service-specific diagnosis & fixes ────────────
        fixed = False

        if cname == "lcc-backend":
            if "no such table" in logs_lower or "relation\"" in logs_lower or "does not exist" in logs_lower:
                self._log("  Detected: missing DB table — running migrations…", "warning")
                rc, out, err = _run(
                    ["docker", "compose", "exec", "-T", cname,
                     "python", "manage.py", "migrate", "--run-syncdb"],
                    cwd=root, timeout=120,
                )
                if rc == 0:
                    self._log("  Migrations applied successfully", "success")
                    fixed = True
                else:
                    self._log(f"  Migration failed: {err[:120]}", "error")

            elif "staticfiles" in logs_lower and "not found" in logs_lower:
                self._log("  Detected: missing static files — collecting static…", "warning")
                rc, out, err = _run(
                    ["docker", "compose", "exec", "-T", cname,
                     "python", "manage.py", "collectstatic", "--noinput"],
                    cwd=root, timeout=60,
                )
                if rc == 0:
                    self._log("  Static files collected", "success")
                    fixed = True

            elif "connection refused" in logs_lower or "could not connect to server" in logs_lower:
                self._log("  Detected: backend cannot reach database — waiting 15s then restarting…", "warning")
                time.sleep(15)

            elif "secret_key" in logs_lower or "improperly configured" in logs_lower:
                self._log("  Detected: missing Django SECRET_KEY in .env.docker", "error")
                self._log("  Fix: add DJANGO_SECRET_KEY=<random-string> to .env.docker", "dim")

        elif cname == "lcc-postgres":
            if "permission denied" in logs_lower or "could not open file" in logs_lower:
                self._log("  Detected: PostgreSQL data directory permission error", "error")
                self._log("  Fix: docker compose down -v && docker compose up -d", "dim")
                self._log("  WARNING: This will delete all data in the database!", "warning")

            elif "address already in use" in logs_lower or "port is already allocated" in logs_lower:
                self._log("  Detected: Port 5432 already in use — another PostgreSQL may be running", "error")
                self._log("  Fix: stop the conflicting process or change POSTGRES_PORT in .env.docker", "dim")

            elif "password authentication failed" in logs_lower:
                self._log("  Detected: wrong password in DB config — check POSTGRES_PASSWORD in .env.docker", "error")

        elif cname == "lcc-pgbouncer":
            if "cannot connect to server" in logs_lower or "server login failed" in logs_lower:
                self._log("  PgBouncer cannot reach Postgres yet — will retry after Postgres is up", "warning")
                fixed = True  # No action needed; just wait

            elif "config file" in logs_lower and "not found" in logs_lower:
                self._log("  PgBouncer config file missing — check docker/pgbouncer/ folder", "error")

        elif cname == "lcc-redis":
            if "address already in use" in logs_lower:
                self._log("  Detected: Port 6379 already in use", "error")
                self._log("  Fix: stop the conflicting Redis or change REDIS_PORT in .env.docker", "dim")

        elif cname in ("lcc-celery-worker", "lcc-celery-beat"):
            if "connection refused" in logs_lower or "nodename nor servname provided" in logs_lower:
                self._log("  Celery cannot reach Redis — waiting for Redis to become healthy", "warning")
                fixed = True

            elif "module" in logs_lower and "not found" in logs_lower:
                self._log("  Detected: Celery task module import error — check INSTALLED_APPS in settings", "error")

        elif cname == "lcc-frontend":
            if "enoent" in logs_lower or "cannot find module" in logs_lower:
                self._log("  Detected: Frontend missing node_modules — rebuilding…", "warning")
                rc, _, _ = _run(
                    ["docker", "compose", "exec", "-T", cname, "pnpm", "install"],
                    cwd=root, timeout=120,
                )
                if rc == 0:
                    fixed = True

        # ── Universal fix: restart or recreate ────────────
        if attempt < 2:
            self._log(f"  Restarting {sname}…", "warning")
            rc, _, err = _run(["docker", "compose", "restart", cname], cwd=root, timeout=60)
            if rc == 0:
                self._log(f"  {sname} restarted — waiting for it to come up…", "success")
            else:
                self._log(f"  Restart failed: {err[:100]}", "error")
        else:
            self._log(f"  Recreating {sname} container (force)…", "warning")
            rc, _, err = _run(
                ["docker", "compose", "up", "-d", "--force-recreate", "--no-deps", cname],
                cwd=root, timeout=90,
            )
            if rc == 0:
                self._log(f"  {sname} recreated successfully", "success")
            else:
                self._log(f"  Recreate failed: {err[:120]}", "error")
                self._log(f"  Remaining fix: run  docker compose logs {cname}  for full details", "dim")

    def _set_detail_status(self, statuses: dict[str, str]):
        lines = []
        for cname, sname in SERVICES:
            st = statuses.get(cname, "…")
            lines.append(f"{sname}: {st}")
        self.after(0, self._detail_var.set, "  |  ".join(lines[:4]))

    def _verify_endpoints(self) -> bool:
        endpoints = [
            ("http://localhost:8001/health/",      "Backend health"),
            ("http://localhost:8001/api/v1/",      "Backend API root"),
            ("http://localhost:3000/",             "Frontend"),
        ]

        # Also try port 8000 (direct Django without nginx override)
        all_ok = True
        for url, name in endpoints:
            ok = self._http_check(url, name)
            if not ok:
                all_ok = False

        return all_ok

    def _http_check(self, url: str, name: str, timeout: int = 15) -> bool:
        self._log(f"Checking {name}: {url}", "info")
        # Retry a few times
        for attempt in range(3):
            try:
                resp = requests.get(url, timeout=timeout, allow_redirects=True)
                if resp.status_code < 500:
                    self._log(f"  ✓ {name} → HTTP {resp.status_code}", "success")
                    return True
                else:
                    self._log(f"  HTTP {resp.status_code} — retrying…", "warning")
            except requests.ConnectionError:
                if attempt < 2:
                    self._log(f"  Connection refused — waiting 10s…", "warning")
                    time.sleep(10)
                else:
                    self._log(f"  ✗ Cannot reach {url}", "error")
            except Exception as e:
                self._log(f"  ✗ {e}", "error")
                break
        return False

    # ── Success / Failure states ───────────────────────────────

    def _success(self):
        def _ui():
            self._running = False
            self._status_lbl.configure(text_color=COLORS["success"])
            self._status_var.set("✓  Setup complete — LankaCommerce Cloud is ready!")
            self._detail_var.set("Click 'Open App' to access the application in your browser.")
            self._start_btn.configure(state="disabled", text="✓ Done",
                                       fg_color=COLORS["success"])
            self._open_btn.configure(state="normal")
            self._cancel_btn.configure(text="Close")
        self.after(0, _ui)

        self._log("", "dim")
        self._log("Application URLs:", "success")
        self._log("  🌐  http://localhost:3000/login    — Login", "info")
        self._log("  📊  http://localhost:3000/dashboard — Dashboard", "info")
        self._log("  🔌  http://localhost:8001/api/v1/  — Backend API", "info")
        self._log("  🌸  http://localhost:5555/          — Celery Flower", "info")
        self._log("", "dim")
        self._log("Admin credentials:", "success")
        self._log("  Email:    admin@lcc.lk", "info")
        self._log("  Password: Admin1234x", "info")
        self._log("", "dim")
        self._log("─── Suggested Test Run ─────────────────────────────────────", "dim")
        self._log("Verify all services are running:", "info")
        self._log("  docker compose ps", "dim")
        self._log("", "dim")
        self._log("Run the full backend test suite:", "info")
        self._log("  docker compose exec -T backend bash -c \\", "dim")
        self._log("    'DJANGO_SETTINGS_MODULE=config.settings.test_pg pytest tests/ -q --no-header'", "dim")
        self._log("", "dim")
        self._log("Run accounting tests only (faster — ~95s):", "info")
        self._log("  docker compose exec -T backend bash -c \\", "dim")
        self._log("    'DJANGO_SETTINGS_MODULE=config.settings.test_pg pytest tests/accounting/ -q'", "dim")
        self._log("", "dim")
        self._log("Check backend health endpoint:", "info")
        self._log("  curl http://localhost:8001/health/", "dim")
        self._log("", "dim")
        self._log("─────────────────────────────────────────────────────────────", "dim")
        self._log("", "dim")
        self._log("To stop all services later:", "info")
        self._log("  docker compose down", "dim")

    def _fail(self, message: str):
        def _ui():
            self._running = False
            self._status_lbl.configure(text_color=COLORS["error"])
            self._status_var.set("✗  Setup failed")
            self._detail_var.set(message)
            self._start_btn.configure(state="normal", text="↺  Retry",
                                       fg_color=COLORS["warning"])
            self._cancel_btn.configure(text="Close")
        self.after(0, _ui)
        self._log(f"FAILED: {message}", "error")

    # ── Action buttons ─────────────────────────────────────────

    def _open_app(self):
        webbrowser.open("http://localhost:3000/login")

    def _on_close(self):
        if self._running:
            self._cancelled = True
            self._running   = False
        self.destroy()


# ══════════════════════════════════════════════════════════════
#  Entry point
# ══════════════════════════════════════════════════════════════

def main():
    app = SetupApp()
    app.mainloop()


if __name__ == "__main__":
    main()

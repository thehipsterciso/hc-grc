#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# Phoenix observability server — launchd service manager for the compute node.
#
# Phoenix needs a long-lived server process (unlike MLflow's serverless SQLite
# backend). Per ADR-0014 the compute node runs always-on, so Phoenix is managed
# as a launchd LaunchAgent: RunAtLoad + KeepAlive, surviving logout and reboot.
#
# Usage: scripts/infra/phoenix-service.sh {install|uninstall|status|restart|logs}
#
# The plist is generated into ~/Library/LaunchAgents with absolute paths derived
# from this repo's location, so nothing user-specific is committed to the repo.
# ─────────────────────────────────────────────────────────────────────────────
set -euo pipefail

LABEL="com.hcgrc.phoenix"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
VENV_PHOENIX="$REPO_ROOT/.venv/bin/phoenix"
STORAGE_DIR="$REPO_ROOT/phoenix_storage"
LOG_FILE="$STORAGE_DIR/phoenix_server.log"
PLIST="$HOME/Library/LaunchAgents/$LABEL.plist"

# Host/port are read from configs/platform.yaml so the service tracks config.
read_cfg() {
  "$REPO_ROOT/.venv/bin/python" - "$1" <<'PY'
import sys
from src.infrastructure.config import load_platform_config
load_platform_config.cache_clear()
print(load_platform_config()["observability"]["phoenix"][sys.argv[1]])
PY
}

write_plist() {
  local host port
  host="$(cd "$REPO_ROOT" && read_cfg host)"
  port="$(cd "$REPO_ROOT" && read_cfg port)"
  mkdir -p "$STORAGE_DIR" "$(dirname "$PLIST")"
  cat > "$PLIST" <<PLISTEOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key><string>$LABEL</string>
  <key>ProgramArguments</key>
  <array>
    <string>$VENV_PHOENIX</string>
    <string>serve</string>
    <string>--host</string><string>$host</string>
    <string>--port</string><string>$port</string>
  </array>
  <key>EnvironmentVariables</key>
  <dict>
    <key>PHOENIX_WORKING_DIR</key><string>$STORAGE_DIR</string>
  </dict>
  <key>WorkingDirectory</key><string>$REPO_ROOT</string>
  <key>RunAtLoad</key><true/>
  <key>KeepAlive</key><true/>
  <key>StandardOutPath</key><string>$LOG_FILE</string>
  <key>StandardErrorPath</key><string>$LOG_FILE</string>
</dict>
</plist>
PLISTEOF
  echo "Wrote $PLIST (host=$host port=$port)"
}

case "${1:-}" in
  install)
    [ -x "$VENV_PHOENIX" ] || { echo "ERROR: $VENV_PHOENIX not found. Run 'make install' first."; exit 1; }
    write_plist
    launchctl unload "$PLIST" 2>/dev/null || true
    launchctl load "$PLIST"
    echo "Phoenix service loaded. Tail logs: $0 logs"
    ;;
  uninstall)
    launchctl unload "$PLIST" 2>/dev/null || true
    rm -f "$PLIST"
    echo "Phoenix service unloaded and plist removed."
    ;;
  restart)
    launchctl kickstart -k "gui/$(id -u)/$LABEL"
    echo "Phoenix service restarted."
    ;;
  status)
    launchctl list | grep "$LABEL" || echo "$LABEL not loaded."
    ;;
  logs)
    tail -n 40 -f "$LOG_FILE"
    ;;
  *)
    echo "Usage: $0 {install|uninstall|status|restart|logs}"; exit 1
    ;;
esac

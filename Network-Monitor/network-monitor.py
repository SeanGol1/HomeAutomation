#!/usr/bin/env python3

import subprocess
import time
import platform
import socket
import os
from pathlib import Path
from datetime import datetime

# === CONFIG ===
CHECK_INTERVAL = 15        # seconds between checks
PING_TARGET = "8.8.8.8"   # reliable external host

# Log file placed in the repository's `logs/` folder so it works cross-platform
LOG_DIR = Path(__file__).resolve().parent / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = str(LOG_DIR / "network_monitor.log")

# =================

def timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def is_internet_up():
    """
    Returns True if the internet is reachable.

    First tries a TCP connect to DNS port 53 (fast & cross-platform).
    Falls back to calling the system `ping` command with platform-appropriate flags.
    """
    # Fast, cross-platform socket check
    try:
        with socket.create_connection((PING_TARGET, 53), timeout=2):
            return True
    except Exception:
        pass

    # Fallback to ping command (platform-specific flags)
    try:
        if platform.system().lower() == "windows":
            args = ["ping", "-n", "1", "-w", "2000", PING_TARGET]
        else:
            args = ["ping", "-c", "1", "-W", "2", PING_TARGET]

        result = subprocess.run(
            args,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        return result.returncode == 0
    except Exception:
        return False


def get_interface_status():
    """
    Returns the output of `ip addr` (Unix) or `ipconfig /all` (Windows) for logging.
    """
    try:
        if platform.system().lower() == "windows":
            cmd = ["ipconfig", "/all"]
        else:
            cmd = ["ip", "addr"]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True
        )
        return result.stdout.strip()
    except Exception as e:
        return f"Error getting interface status: {e}"


def log_event(event_type):
    """
    Writes a log entry with timestamp and interface state.
    """
    with open(LOG_FILE, "a") as log:
        log.write("\n")
        log.write("=" * 60 + "\n")
        log.write(f"{timestamp()} - INTERNET {event_type}\n")
        log.write("-" * 60 + "\n")
        log.write(get_interface_status())
        log.write("\n")


def main():
    print("Starting network monitor...")
    print(f"Logging to: {LOG_FILE}")

    last_state = None

    while True:
        current_state = is_internet_up()

        if last_state is None:
            # First run
            last_state = current_state
            log_event("INITIAL UP" if current_state else "INITIAL DOWN")
            print(f"{timestamp()} - Initial state: {'UP' if current_state else 'DOWN'}")

        elif current_state != last_state:
            if not current_state:
                log_event("DOWN")
                print(f"{timestamp()} - Internet DOWN")
            else:
                log_event("UP")
                print(f"{timestamp()} - Internet UP")

            last_state = current_state

        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    main()
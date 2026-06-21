"""
alert_logger.py

Handles two responsibilities:
  1. Writing a permanent, timestamped event log to disk (for later
     security review -- this satisfies the "maintain an event log"
     objective from the project proposal).
  2. Printing human-readable alerts to the terminal in real time.

Keeping logging/alerting separate from scanning and comparing means
each piece of the tool can be tested and explained independently.

Author: Michael
Course: CYB 333
"""

from datetime import datetime, timezone


LOG_FILE = "port_monitor.log"


def _timestamp() -> str:
    """Consistent timestamp format used for every log line."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")


def log_event(message: str, log_file: str = LOG_FILE) -> None:
    """
    Append a single timestamped line to the persistent log file.

    Using append mode ("a") rather than overwrite mode ("w") is
    deliberate -- the whole point of an event log is that it builds
    up a permanent history over time rather than only showing the
    most recent scan.
    """
    with open(log_file, "a") as f:
        f.write(f"[{_timestamp()}] {message}\n")


def report_results(target_ip: str, comparison: dict, log_file: str = LOG_FILE) -> None:
    """
    Print results to the terminal AND write them to the log file.

    This is the main function main.py calls after every scan -- it
    decides what the human-readable alert text should say based on
    what changed, then sends that same text to both the terminal and
    the log so the two are always consistent with each other.
    """
    if comparison["is_first_run"]:
        msg = (
            f"Baseline established for {target_ip}. "
            f"Open ports recorded: {comparison['unchanged']}"
        )
        print(f"[INFO] {msg}")
        log_event(f"BASELINE | {msg}")
        return

    newly_opened = comparison["newly_opened"]
    newly_closed = comparison["newly_closed"]

    if not newly_opened and not newly_closed:
        msg = f"No change detected on {target_ip}. All monitored ports stable."
        print(f"[OK] {msg}")
        log_event(f"NO_CHANGE | {msg}")
        return

    # Something changed -- this is the core "alert" scenario the whole
    # project is built around.
    if newly_opened:
        msg = f"ALERT: Port(s) {newly_opened} OPENED on {target_ip}."
        print(f"[ALERT] {msg}")
        log_event(f"PORT_OPENED | {msg}")

    if newly_closed:
        msg = f"ALERT: Port(s) {newly_closed} CLOSED on {target_ip}."
        print(f"[ALERT] {msg}")
        log_event(f"PORT_CLOSED | {msg}")

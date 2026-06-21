"""
comparator.py

Compares the current scan result against the previous scan result and
reports what changed. This is the "detection" half of the project --
scanner.py answers "what's open right now?" and this file answers
"what's different from last time?"

Author: Michael
Course: CYB 333
"""

import json
import os


# Where we persist the last scan's results so we have something to
# compare against the next time the tool runs. Using a simple JSON
# file (rather than a database) keeps this dependency-free and easy
# to inspect/explain in a write-up.
STATE_FILE = "last_scan_state.json"


def load_previous_state(state_file: str = STATE_FILE) -> dict | None:
    """
    Load the previous scan's results from disk, if they exist.

    Returns None if this is the very first time the tool has been run
    (no baseline to compare against yet).
    """
    if not os.path.exists(state_file):
        return None

    with open(state_file, "r") as f:
        return json.load(f)


def save_current_state(scan_result: dict, state_file: str = STATE_FILE) -> None:
    """
    Persist the current scan's results to disk so the *next* run of
    the tool has something to compare against.
    """
    with open(state_file, "w") as f:
        json.dump(scan_result, f, indent=2)


def compare_scans(previous: dict | None, current: dict) -> dict:
    """
    Compare the previous scan to the current scan and identify changes.

    Returns a dictionary shaped like:
        {
            "newly_opened": [80, 443],
            "newly_closed": [8080],
            "unchanged": [22, 3306],
            "is_first_run": False
        }

    Using sets here makes the "what changed" logic a one-liner instead
    of writing nested loops to manually compare two lists -- set
    difference and intersection do exactly what we need.
    """
    if previous is None:
        # No baseline exists yet -- this run simply establishes one.
        return {
            "newly_opened": [],
            "newly_closed": [],
            "unchanged": current["open_ports"],
            "is_first_run": True,
        }

    previous_ports = set(previous["open_ports"])
    current_ports = set(current["open_ports"])

    newly_opened = sorted(current_ports - previous_ports)
    newly_closed = sorted(previous_ports - current_ports)
    unchanged = sorted(current_ports & previous_ports)

    return {
        "newly_opened": newly_opened,
        "newly_closed": newly_closed,
        "unchanged": unchanged,
        "is_first_run": False,
    }


def has_changes(comparison: dict) -> bool:
    """
    Convenience helper: did anything actually change between scans?
    Used by main.py to decide whether to fire an alert.
    """
    return bool(comparison["newly_opened"] or comparison["newly_closed"])

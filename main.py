"""
main.py

Entry point for the Automated Linux Port Status Monitoring and
Alerting System.

Each time this script is run, it performs ONE scan of the target IP
(set in config.py), compares the result against the last saved scan,
prints/logs any changes, and saves the new result as the baseline for
next time.

This is the "manual run" mode -- you run it whenever you want to
check for changes (e.g. after opening/closing a port on the VM to
simulate a security event). A continuous/scheduled mode could be
added later by wrapping this same logic in a loop with a sleep
interval, but manual runs are clearer for demonstrating cause and
effect during testing.

Usage:
    python3 main.py

Author: Michael
Course: CYB 333
"""

import sys

import config
from scanner import scan_ports
from comparator import load_previous_state, save_current_state, compare_scans
from alert_logger import report_results, log_event


def main():
    target_ip = config.TARGET_IP

    print(f"Starting port scan on {target_ip} "
          f"(ports {config.START_PORT}-{config.END_PORT})...")
    log_event(f"SCAN_STARTED | target={target_ip}")

    # Step 1: Scan the target right now.
    current_scan = scan_ports(target_ip, config.START_PORT, config.END_PORT)

    # Step 2: Load whatever we saved from the last run (None if this
    # is the very first scan ever).
    previous_scan = load_previous_state()

    # Step 3: Figure out what, if anything, changed.
    comparison = compare_scans(previous_scan, current_scan)

    # Step 4: Tell the user (terminal) and the permanent record (log file).
    report_results(target_ip, comparison)

    # Step 5: Save this scan so the *next* run has something to compare against.
    save_current_state(current_scan)

    log_event(f"SCAN_COMPLETED | target={target_ip} | "
              f"open_ports={current_scan['open_ports']}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nScan interrupted by user.")
        sys.exit(0)
    except Exception as e:
        # Catch-all so a single unexpected error produces a clear
        # message instead of a raw Python traceback -- and so it's
        # still recorded in the log for review.
        print(f"[ERROR] Something went wrong: {e}")
        log_event(f"ERROR | {e}")
        sys.exit(1)

# Automated Linux Port Status Monitoring and Alerting System

A Python tool that scans a Linux host for open ports, compares the result
against the last scan, and alerts when a port changes from closed to open
or open to closed. Built for CYB 333 (Security Automation).

## Project Objectives

- Automate port status monitoring instead of checking ports manually.
- Detect unauthorized service changes -- an unexpected open port can mean
  misconfiguration or an unauthorized service; an unexpected closed port
  can mean a service failure.
- Maintain a timestamped event log for later security review.

## Features

- Scans the full 1-1024 port range on a configurable target IP.
- Threaded scanning (up to 100 ports checked at once) so a full scan
  finishes in seconds instead of minutes.
- Compares each scan against the previous one to detect changes.
- Prints alerts to the terminal in real time.
- Logs every scan (baseline, no-change, and alerts) to `port_monitor.log`
  with a timestamp.

## Files

| File | What it does |
|---|---|
| `config.py` | Sets the target IP and port range to scan. Edit this to point at a different host. |
| `scanner.py` | Scans the target and returns which ports are open, using Python's built-in `socket` library. |
| `comparator.py` | Compares the current scan to the previous one and reports what changed. |
| `alert_logger.py` | Prints alerts to the terminal and writes timestamped entries to the log file. |
| `main.py` | Runs the whole process: scan, compare, alert/log, save new baseline. |

## Prerequisites

- Python 3.8 or later
- No external libraries required -- everything used (`socket`,
  `concurrent.futures`, `datetime`, `json`, `os`) is built into Python.
- Network access from the scanning machine to the target IP.

## Setup and Usage

1. Clone the repository:
   ```bash
   git clone https://github.com/mknauer514/CYB333-Port-Monitor.git
   cd CYB333-Port-Monitor
   ```

2. Open `config.py` and set the target IP:
   ```python
   TARGET_IP = "192.168.56.101"   # replace with your target's IP
   ```

3. Run a scan:
   ```bash
   python3 main.py
   ```

4. Results:
   - **First run**: no previous scan exists yet, so the tool saves the
     current open ports as the baseline.
   - **Every run after that**: compares to the saved baseline and prints
     one of:
     - `[OK] No change detected`
     - `[ALERT] Port(s) [...] OPENED`
     - `[ALERT] Port(s) [...] CLOSED`
   - Every result is also appended to `port_monitor.log`.

5. To test the alerting, open a port within 1-1024 on the target (e.g.
   `sudo python3 -m http.server 888`), then run `python3 main.py` again --
   it should report that port as newly opened. Stop the server and run
   the scan once more to see the closed-port alert.

## Additional Notes

- The target used during development was an isolated Ubuntu Server VM
  in VirtualBox, connected via a Host-Only network adapter so it could be
  scanned safely from the host without exposing it to the wider network.
- `last_scan_state.json` (the saved baseline) and `port_monitor.log` are
  generated automatically when the tool runs and are excluded from this
  repository via `.gitignore`, since they're scan output, not project code.

## Author

Michael -- CYB 333, Security Automation

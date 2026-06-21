"""
scanner.py

Core port-scanning logic for the Automated Linux Port Status Monitoring
and Alerting System.

This module is responsible ONLY for scanning ports on a target IP and
returning the results. It does not handle comparison, logging, or
alerting -- that separation of concerns keeps each file easy to test
and explain on its own.

Author: Michael
Course: CYB 333
"""

import socket
import concurrent.futures
from datetime import datetime, timezone


# How long (in seconds) to wait for a response from each port before
# deciding it's closed/filtered. Lower = faster scan, but more risk of
# false negatives on a slow or congested network.
CONNECT_TIMEOUT = 0.5

# How many ports to check at the same time. Scanning 1-1024 one at a time
# with a blocking socket call would take far too long (1024 x timeout
# seconds in the worst case). Threading lets us check many ports in
# parallel, which is what makes a full 1-1024 scan practical here.
MAX_WORKERS = 100


def scan_single_port(target_ip: str, port: int) -> bool:
    """
    Attempt to open a TCP connection to a single port on the target IP.

    Returns True if the port is OPEN (connection succeeded), False if
    the port is CLOSED or unreachable (connection refused or timed out).

    Using a raw socket here (rather than an external tool like nmap)
    means this script has no dependencies beyond the Python standard
    library -- it will run on any machine with Python 3 installed.
    """
    # AF_INET = use IPv4. SOCK_STREAM = use TCP (not UDP).
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(CONNECT_TIMEOUT)
        try:
            # connect_ex() returns an error code instead of raising an
            # exception, which is faster and cleaner for scanning a lot
            # of ports back-to-back than wrapping connect() in try/except.
            result = sock.connect_ex((target_ip, port))
            return result == 0  # 0 means the connection succeeded
        except socket.error:
            # Covers cases like "network unreachable" -- treat as closed
            # rather than crashing the whole scan over one bad port.
            return False


def scan_ports(target_ip: str, start_port: int = 1, end_port: int = 1024) -> dict:
    """
    Scan a range of ports on target_ip and return which ones are open.

    Returns a dictionary shaped like:
        {
            "target": "192.168.56.101",
            "timestamp": "2026-06-21T19:42:10Z",
            "open_ports": [22, 80, 3306, 33060]
        }

    The timestamp is recorded here -- at scan time -- rather than later,
    so the log always reflects exactly when the scan was actually taken,
    not when it happened to get written to disk.
    """
    open_ports = []

    # ThreadPoolExecutor lets us fire off many scan_single_port() calls
    # concurrently instead of waiting for each one to finish before
    # starting the next. This is what makes scanning 1024 ports take
    # a few seconds instead of several minutes.
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        # Map each port number to a running scan task.
        future_to_port = {
            executor.submit(scan_single_port, target_ip, port): port
            for port in range(start_port, end_port + 1)
        }

        # As each task finishes (in whatever order completes first),
        # check its result and record the port if it came back open.
        for future in concurrent.futures.as_completed(future_to_port):
            port = future_to_port[future]
            try:
                is_open = future.result()
                if is_open:
                    open_ports.append(port)
            except Exception:
                # If a single port's scan throws an unexpected error,
                # skip it rather than letting one failure kill the
                # entire scan.
                continue

    open_ports.sort()

    return {
        "target": target_ip,
        "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "open_ports": open_ports,
    }


if __name__ == "__main__":
    # Allows this file to be run standalone for a quick manual test,
    # separate from the full monitoring tool in main.py.
    test_ip = input("Enter target IP to scan: ").strip()
    print(f"Scanning {test_ip} (ports 1-1024)... this may take a few seconds.")
    result = scan_ports(test_ip)
    print(f"\nScan complete at {result['timestamp']}")
    print(f"Open ports on {result['target']}: {result['open_ports']}")

# Network Monitoring Script

A lightweight, dependency free network reachability monitor built in Python. 
Continuously pings a list of network devices, detects status changes in real time, 
and logs all activity with timestamps,built as part of a CCNA aligned networking 
portfolio project.

## Features (Phase 1 — Complete)
- Cross-platform ICMP ping (Windows & Linux/Mac)
- Monitors multiple devices simultaneously
- Retry logic to avoid false-positive "DOWN" alerts from transient packet loss
- Continuous monitoring loop with configurable check interval
- Change-detection logging — only logs/flags real status transitions (UP → DOWN, DOWN → UP)
- Persistent log file (`network_monitor.log`) with timestamps
- Graceful shutdown via Ctrl+C

## How It Works
The script pings each device in a list using the OS's native `ping` command via 
Python's `subprocess` module (no external dependencies required). Each device is 
retried up to 2 times before being marked DOWN, reducing false alarms from single 
dropped packets. The script tracks each device's previous status between check 
cycles, so only genuine state changes are logged prominently — repeated "still UP" 
checks are logged quietly without cluttering output.

## Usage
'''bash
python network_monitor.py
'''

Edit the devices list in the __main__ block to monitor your own IP addresses.

Adjust check_interval (seconds) to change how often devices are checked.

## Sample Output
'''
Starting network monitor. Checking every 30 seconds. Press Ctrl+C to stop.
8.8.8.8: UP  <-- CHANGED
1.1.1.1: UP  <-- CHANGED
192.168.1.1: DOWN  <-- CHANGED
8.8.8.8: UP
1.1.1.1: UP
192.168.1.1: DOWN
'''

## Roadmap
- [x] Phase 1: Reachability monitoring with retry logic and change-detection logging
- [ ] Phase 2: Netmiko integration for live device config/status polling (Cisco IOS)
- [ ] Phase 3: Scapy-based traffic analysis and anomaly detection
- [ ] Phase 4: Threshold-based alerting and structured reporting (CSV export)
- [ ] Phase 5: Full documentation and deployment guide

## Tech Stack
Python 3, subprocess, logging — zero external dependencies for Phase 1.

## Author
Chibuike — Computer Science student, Rivers State University, pursuing CCNA 200-301
and a career in network engineering.
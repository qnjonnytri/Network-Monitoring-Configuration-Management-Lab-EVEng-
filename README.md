# Network-Monitoring-Configuration-Management-Lab-EVEng-
# Network Backup Project

## Introduction
This project provides Python scripts to **backup** and **restore** network device configurations (Cisco IOS) using the libraries **Netmiko** and **Napalm**.  
It supports both **single device** and **multiple devices** through YAML configuration files.

---

## Backup – What it does
- Connects to devices via SSH (Netmiko/Napalm).
- Retrieves the current running configuration.
- Saves backup files with timestamps to maintain history.
- Compares today’s configuration with yesterday’s using `difflib.HtmlDiff` → generates `.html` difference reports.
- Logs backup results into `backup.log`.

**Supported modes:**
- **Netmiko**: backup for one device or multiple devices (via YAML).
- **Napalm**: backup for one device or multiple devices (via YAML).

---

## Restore – How it works
- Finds the latest backup file in the backup directory.
- Reads configuration data from the backup file.
- Connects to the device via SSH.
- Applies configuration from the backup file:
  - **Netmiko**: uses `send_config_set` and `save_config`.
  - **Napalm**: uses `load_replace_candidate`, `compare_config`, and `commit_config`.
- Logs restore results into `restore.log`.

**Supported modes:**
- Restore for **single device** or **multiple devices** (via YAML).

---

## Demo – Tested
- Successfully tested with Cisco IOS devices in a lab environment.
- Backup generates files:
  - `hostname_YYYY-MM-DD_HH-MM-SS.txt` (historical backup)
  - `hostname_YYYY-MM-DD.txt` (daily overwrite backup)
  - `difference_hostname.html` (configuration comparison)
- Restore applies configuration from the latest backup file.
- Log files (`backup.log`, `restore.log`) record success or failure for each operation.

---

## Directory Structure

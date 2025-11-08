# Cool Llama - LinuxOptimizer (ubopt) CLI Reference

## Overview

`ubopt` is a command-line tool for managing Linux system updates, security hardening, health checks, backups, and more across Ubuntu, Debian, Fedora, RHEL, and Arch Linux.

## Installation

### From Release

```bash
# Download latest release
wget https://github.com/120git/tinyllama-x/releases/latest/download/ubopt-x.x.x.tar.gz

# Verify checksum
sha256sum -c ubopt-x.x.x.tar.gz.sha256

# Extract and install
tar -xzf ubopt-x.x.x.tar.gz
cd ubopt-x.x.x
sudo make install
```

### From Source

```bash
git clone https://github.com/120git/tinyllama-x.git
cd tinyllama-x
sudo make install
```

## Global Options

These flags can be used with any command:

### `--json`
Output results in JSON format for parsing by other tools.

```bash
ubopt health --json
```

### `--dry-run`
Simulate actions without making changes. Useful for testing.

```bash
ubopt update --dry-run
```

### `--config FILE`
Use an alternate configuration file.

```bash
ubopt update --config /path/to/config.json
```

### `--verbose` or `-v`
Enable verbose output for debugging.

```bash
ubopt update --verbose
```

### `--help` or `-h`
Show help message.

```bash
ubopt --help
```

### `--version`
Show version information.

```bash
ubopt --version
```

## Commands

### `update`

Update system packages.

**Usage:**
```bash
ubopt update [options]
```

**Examples:**
```bash
# Update system packages
sudo ubopt update

# Dry-run to see what would be updated
sudo ubopt update --dry-run

# Update and get JSON output
sudo ubopt update --json
```

**Requirements:** Root privileges

**What it does:**
1. Updates package cache
2. Lists available updates
3. Installs updates (unless `--dry-run`)
4. Cleans package cache

### `harden`

Run security hardening checks.

**Usage:**
```bash
ubopt harden [options]
```

**Examples:**
```bash
# Check security configuration
sudo ubopt harden

# Check and show results as JSON
sudo ubopt harden --json
```

**Requirements:** Root privileges (for most checks)

**What it checks:**
- SSH configuration (PermitRootLogin, PasswordAuthentication)
- Firewall status (ufw/firewalld)
- Automatic updates configuration
- Other security best practices

### `health`

Run system health checks.

**Usage:**
```bash
ubopt health [options]
```

**Examples:**
```bash
# Check system health
ubopt health

# Get detailed health report
ubopt health --verbose

# Get health status as JSON
ubopt health --json
```

**Requirements:** None (some checks more detailed with root)

**What it checks:**
- Disk space usage
- Memory usage
- CPU load
- Failed systemd services
- System uptime

### `backup`

Create system backup.

**Usage:**
```bash
ubopt backup [DIRECTORY] [options]
```

**Examples:**
```bash
# Backup to default location
sudo ubopt backup

# Backup to specific directory
sudo ubopt backup /mnt/backups

# Dry-run to see what would be backed up
sudo ubopt backup --dry-run
```

**Requirements:** Root privileges

**What it backs up:**
- `/etc` directory
- SSH keys from `/root/.ssh`
- User SSH keys from `/home/*/.ssh`

**Retention:** Keeps last 5 backups automatically

### `benchmark`

Run performance benchmarks.

**Usage:**
```bash
ubopt benchmark [options]
```

**Examples:**
```bash
# Run benchmarks
ubopt benchmark

# Get benchmark results as JSON
ubopt benchmark --json
```

**Requirements:** None

**What it benchmarks:**
- CPU calculation speed
- Disk I/O (read/write)
- Network connectivity
- Memory information

### `log`

View ubopt logs.

**Usage:**
```bash
ubopt log [LINES] [options]
```

**Examples:**
```bash
# View last 50 lines (default)
ubopt log

# View last 100 lines
ubopt log 100

# Get logs as JSON
ubopt log --json
```

**Requirements:** Read access to log file (`/var/log/ubopt.log`)

### `version`

Show version information.

**Usage:**
```bash
ubopt version
```

**Examples:**
```bash
# Show version
ubopt version

# Show version as JSON
ubopt version --json
```

## Configuration

Configuration file location: `/etc/ubopt/config.json`

### Example Configuration

```json
{
  "update": {
    "enabled": true,
    "auto_clean": true,
    "auto_remove": true
  },
  "hardening": {
    "enabled": true,
    "ssh_check": true,
    "firewall_check": true
  },
  "backup": {
    "enabled": true,
    "directory": "/var/backups/ubopt",
    "retention_count": 5
  },
  "logging": {
    "enabled": true,
    "log_file": "/var/log/ubopt.log",
    "log_level": "info"
  },
  "notifications": {
    "enabled": false,
    "email": ""
  }
}
```

## Systemd Integration

### Enable Automatic Updates

```bash
# Enable daily automatic updates at 3 AM
sudo systemctl enable --now ubopt.timer

# Check timer status
sudo systemctl status ubopt.timer

# View next scheduled run
sudo systemctl list-timers ubopt.timer
```

### Manual Service Execution

```bash
# Run update service manually
sudo systemctl start ubopt.service

# View service logs
sudo journalctl -u ubopt.service

# View recent service runs
sudo journalctl -u ubopt.service --since today
```

### Disable Automatic Updates

```bash
sudo systemctl disable --now ubopt.timer
```

## Environment Variables

### `UBOPT_LOGFILE`
Override default log file location.

```bash
export UBOPT_LOGFILE=/var/log/my-ubopt.log
ubopt update
```

## Exit Codes

- `0`: Success
- `1`: General error
- `2`: Invalid usage/arguments

## Examples by Use Case

### Daily System Maintenance

```bash
#!/bin/bash
# Daily maintenance script

# Update system
sudo ubopt update

# Check health
ubopt health --verbose

# Check security
sudo ubopt harden

# Create backup
sudo ubopt backup /mnt/backups
```

### Monitoring Integration

```bash
#!/bin/bash
# Send health status to monitoring system

HEALTH=$(ubopt health --json)
curl -X POST https://monitor.example.com/api/health \
  -H "Content-Type: application/json" \
  -d "$HEALTH"
```

### Pre-Production Validation

```bash
#!/bin/bash
# Validate changes before production

# Test updates without applying
sudo ubopt update --dry-run

# Check system health
ubopt health

# Run benchmarks
ubopt benchmark
```

## Troubleshooting

### Command fails silently

Check logs:
```bash
ubopt log 100
# or
journalctl -u ubopt.service
```

### Permission denied errors

Most management commands require root:
```bash
sudo ubopt update
```

### Module not found errors

Verify installation:
```bash
sudo make install
```

### Check installation paths

```bash
which ubopt
ls -la /usr/local/lib/ubopt/
```

## Getting Help

- View command help: `ubopt COMMAND --help`
- Check logs: `ubopt log`
- View systemd logs: `journalctl -u ubopt.service`
- Report issues: https://github.com/120git/tinyllama-x/issues

## See Also

- [ARCHITECTURE.md](ARCHITECTURE.md) - System architecture details
- [README.md](../README.md) - Project overview
- Makefile - Build and installation targets

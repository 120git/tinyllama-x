# UbuntOptimizer CLI Reference

## Synopsis

```bash
ubopt [GLOBAL_OPTIONS] COMMAND [COMMAND_OPTIONS] [ARGS...]
```

## Global Options

### `--config PATH`
Specify custom configuration file path.

**Default:** `/etc/ubopt/ubopt.yaml` (root) or `~/.config/ubopt/ubopt.yaml` (user)

```bash
ubopt --config /path/to/config.yaml health
```

### `--dry-run`
Show planned actions without making changes. Available for all commands.

```bash
ubopt --dry-run update
ubopt --dry-run hardening
```

### `--json`
Output structured JSON logs to stdout instead of human-readable format.

```bash
ubopt --json health
ubopt --json update --dry-run
```

### `--headless`
Non-interactive mode. Suppresses prompts and confirmations. Use with caution.

```bash
ubopt --headless update
```

### `--verbose, -v`
Increase verbosity. Can be repeated for more detail.

```bash
ubopt -v update
ubopt -vv update  # Very verbose
```

### `--version`
Show version information and exit.

```bash
ubopt --version
```

### `--help, -h`
Show help message and exit.

```bash
ubopt --help
ubopt update --help
```

## Commands

### `update`
Perform system updates including security patches.

**Options:**
- `--security-only` - Only apply security updates
- `--reboot-if-required` - Automatically reboot if kernel/init updated
- `--no-reboot` - Never reboot even if required

**Examples:**
```bash
# Check and apply all updates (interactive)
ubopt update

# Dry-run to see what would be updated
ubopt --dry-run update

# Apply only security updates
ubopt update --security-only

# Headless update with automatic reboot
ubopt --headless update --reboot-if-required

# JSON output for automation
ubopt --json update --dry-run
```

**Exit codes:**
- `0` - Success, no reboot required
- `1` - General error
- `2` - No updates available
- `10` - Reboot required

---

### `hardening`
Apply security hardening baseline to the system.

**Options:**
- `--ssh-only` - Only apply SSH hardening
- `--firewall-only` - Only configure firewall
- `--skip-ssh` - Skip SSH configuration
- `--skip-firewall` - Skip firewall configuration

**Examples:**
```bash
# Apply all hardening (interactive)
ubopt hardening

# Dry-run to see planned changes
ubopt --dry-run hardening

# Apply only SSH hardening
ubopt hardening --ssh-only

# Headless hardening
ubopt --headless hardening
```

**Exit codes:**
- `0` - Success
- `1` - General error
- `3` - Partial failure (some hardening failed)

---

### `health`
Gather and report system health metrics.

**Options:**
- `--format FORMAT` - Output format: json, text, prometheus (default: text)
- `--output FILE` - Write output to file instead of stdout

**Examples:**
```bash
# Display health report
ubopt health

# JSON output
ubopt health --format json
ubopt --json health

# Prometheus textfile exporter format
ubopt health --format prometheus --output /var/lib/node_exporter/textfile/ubopt.prom
```

**Exit codes:**
- `0` - System healthy
- `1` - General error
- `4` - Critical issues detected

---

### `backup`
Manage system backups (stub in MVP).

**Options:**
- `--target PATH` - Backup target directory or remote
- `--type TYPE` - Backup type: full, incremental (default: full)

**Examples:**
```bash
# Dry-run backup
ubopt --dry-run backup --target /mnt/backup

# Create backup
ubopt backup --target /mnt/backup
```

**Exit codes:**
- `0` - Success
- `1` - General error
- `5` - Backup failed

---

### `benchmark`
Run system performance benchmarks (stub in MVP).

**Options:**
- `--disk` - Run disk I/O benchmarks
- `--cpu` - Run CPU benchmarks
- `--memory` - Run memory benchmarks

**Examples:**
```bash
# Run all benchmarks
ubopt benchmark

# Run specific benchmarks
ubopt benchmark --disk --cpu
```

**Exit codes:**
- `0` - Success
- `1` - General error
- `6` - Benchmark tools not available

---

### `version`
Display version information.

```bash
ubopt version
```

**Exit codes:**
- `0` - Always success

---

### `help`
Display help information.

```bash
ubopt help
ubopt help update
```

**Exit codes:**
- `0` - Always success

---

## Exit Codes Summary

| Code | Meaning |
|------|---------|
| 0    | Success |
| 1    | General error |
| 2    | No updates available |
| 3    | Partial failure |
| 4    | Critical issues detected |
| 5    | Backup failed |
| 6    | Benchmark tools not available |
| 10   | Reboot required |
| 125  | Invalid arguments |
| 126  | Command cannot execute |
| 127  | Command not found |
| 130  | Terminated by Ctrl+C |

## Configuration File

The configuration file uses YAML format:

```yaml
# /etc/ubopt/ubopt.yaml

updates:
  schedule: "daily"        # daily, weekly, manual
  auto_reboot: false       # Auto-reboot after kernel updates
  security_only: false     # Only apply security updates

reboot:
  strategy: "prompt"       # prompt, auto, never
  delay_minutes: 5         # Delay before reboot

hardening:
  ssh:
    disable_root_login: true
    disable_password_auth: true
    port: 22
  firewall:
    enabled: true
    policy: "deny-by-default"
    allow_ports: [22, 80, 443]

backup:
  enabled: false
  target: "/mnt/backup"
  schedule: "weekly"
  retention_days: 30

report:
  targets:
    - type: "file"
      path: "/var/log/ubopt/report.json"
    - type: "prometheus"
      path: "/var/lib/node_exporter/textfile/ubopt.prom"

logging:
  level: "info"           # debug, info, warn, error
  json: true              # JSON structured logs
  file: "/var/log/ubopt/ubopt.log"
```

## Environment Variables

- `UBOPT_CONFIG` - Override default config path
- `UBOPT_DRY_RUN` - Enable dry-run mode (any non-empty value)
- `UBOPT_LOG_LEVEL` - Set log level (debug, info, warn, error)
- `UBOPT_NO_COLOR` - Disable colored output

## Examples

### Automated Daily Updates
```bash
# Via systemd timer
systemctl enable --now ubopt-agent.timer

# Manual headless update
ubopt --headless --json update
```

### Initial System Hardening
```bash
# Review what will be changed
ubopt --dry-run hardening

# Apply hardening
sudo ubopt hardening

# Verify SSH config
sudo ubopt health --format json | jq '.ssh'
```

### Health Monitoring Integration
```bash
# Export metrics for Prometheus
ubopt health --format prometheus --output /var/lib/node_exporter/textfile/ubopt.prom

# Check critical services
ubopt health --format json | jq '.services[] | select(.status != "active")'
```

### Scripting with JSON Output
```bash
#!/bin/bash
# Check if updates are available

if ubopt --json update --dry-run | jq -e '.fields.updates_available > 0' > /dev/null; then
    echo "Updates available!"
    ubopt --headless update
else
    echo "System up to date"
fi
```

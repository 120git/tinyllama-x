# UbuntOptimizer Architecture

## Overview

UbuntOptimizer (ubopt) is a modular security and system maintenance suite designed for Linux systems. It provides automated updates, security hardening, health monitoring, and system optimization capabilities.

## Module Graph

```
cmd/ubopt (entrypoint)
    ↓
lib/common.sh (shared utilities)
    ↓
┌───────────────┴──────────────┐
│                              │
providers/                   modules/
├── apt.sh                  ├── update.sh
├── dnf.sh                  ├── hardening.sh
├── pacman.sh               ├── health.sh
                            ├── backup.sh
                            ├── benchmark.sh
                            └── logging.sh
```

## Provider Abstraction

The provider layer abstracts package manager operations across different Linux distributions:

### Interface
Each provider (apt, dnf, pacman) implements:
- `pkg_update()` - Refresh package metadata
- `pkg_upgrade()` - Upgrade installed packages
- `pkg_install()` - Install specific packages
- `pkg_available()` - Check if package is available
- `security_updates_available()` - Check for security updates

### Selection
Provider is auto-detected via `/etc/os-release` and `common.sh::detect_os()`.

## Logging Strategy

### JSON Structured Logging
All logs are emitted as JSON for easy parsing and integration with log aggregation systems.

**Format:**
```json
{
  "timestamp": "2025-11-08T19:43:49Z",
  "level": "INFO|WARN|ERROR",
  "module": "update|hardening|health|...",
  "message": "Human-readable message",
  "fields": {
    "key": "value",
    "dry_run": true|false
  }
}
```

### Functions
- `json_log(level, module, message, [fields])` - Primary logging function
- `log_info()`, `log_warn()`, `log_error()` - Convenience wrappers

### Outputs
- **stdout**: JSON logs (when --json flag is used)
- **stderr**: Human-readable messages (default)
- **/var/log/ubopt/**: Persistent logs (when running as daemon)

### Rotation
Logrotate configuration in `packaging/logrotate/ubopt`:
- Daily rotation
- 30-day retention
- Compress old logs
- Create with mode 0640

## Module Design

### Common Patterns
1. **Dry-run support**: All modules respect `--dry-run` flag
2. **State files**: Write to `/var/lib/ubopt/` or `~/.local/share/ubopt/`
3. **Config-driven**: Read from `/etc/ubopt/ubopt.yaml` or `~/.config/ubopt/ubopt.yaml`
4. **Non-destructive**: Require explicit confirmation unless `--headless` mode

### Module Responsibilities

#### update.sh
- Check for security updates
- Stage package updates
- Apply updates with selected provider
- Coordinate optional reboot
- Write state to `state.json`

#### hardening.sh
- SSH configuration baseline (disable root login, password auth)
- Enable unattended-upgrades (apt-based systems)
- Apply minimal sysctl hardening
- Configure ufw firewall (deny-by-default)

#### health.sh
- Gather system metrics (hostname, kernel, uptime)
- Check disk space and SMART status
- Monitor critical services
- Emit JSON report to stdout

#### backup.sh
- Rsync/tar backup strategies
- Dry-run only in MVP
- Configurable backup targets

#### benchmark.sh
- Invoke fio/sysbench if available
- System performance baseline
- Informative no-op if tools not installed

#### logging.sh
- JSON log formatter
- Logrotate configuration
- Log aggregation helpers

## Security Considerations

1. **Root privileges**: Most operations require root; validated via `require_root()`
2. **Confirmation**: Interactive confirmation for destructive actions
3. **Audit trail**: All actions logged to JSON
4. **State tracking**: Changes recorded in state.json
5. **Signal handling**: Proper cleanup on SIGINT/SIGTERM

## Configuration

YAML-based configuration at `/etc/ubopt/ubopt.yaml`:

```yaml
updates:
  schedule: "daily"
  auto_reboot: false
  
reboot:
  strategy: "prompt|auto|never"
  delay_minutes: 5
  
hardening:
  ssh:
    disable_root_login: true
    disable_password_auth: true
  firewall:
    enabled: true
    policy: "deny-by-default"
    
report:
  targets:
    - type: "file"
      path: "/var/log/ubopt/report.json"
```

## Execution Modes

### Interactive
Default mode with user prompts and confirmations.

### Headless
Automated execution via systemd timer:
```bash
ubopt update --headless --json --config /etc/ubopt/ubopt.yaml
```

### Dry-run
Shows planned actions without making changes:
```bash
ubopt update --dry-run
ubopt hardening --dry-run
```

## Integration Points

### Systemd
- **ubopt-agent.service**: One-shot service unit
- **ubopt-agent.timer**: Scheduled execution timer

### Monitoring
- **Prometheus**: Textfile exporter at `/var/lib/node_exporter/textfile/ubopt.prom`
- **Health checks**: Exit codes and JSON status

### Package Management
- **Debian/Ubuntu**: APT provider with unattended-upgrades
- **RHEL/Fedora**: DNF provider with dnf-automatic
- **Arch**: Pacman provider with system updates

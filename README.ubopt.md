# UbuntOptimizer (ubopt)

A modular security and system maintenance suite for Linux systems.

## Features

- **System Updates**: Automated package updates with security-only options
- **Security Hardening**: SSH configuration, firewall setup, sysctl tuning
- **Health Monitoring**: System metrics with JSON/Prometheus output
- **Provider Abstraction**: Support for APT, DNF, and Pacman
- **Non-Destructive**: Dry-run mode for all operations
- **Automation Ready**: Systemd timer for scheduled execution

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/120git/tinyllama-x.git
cd tinyllama-x

# Install ubopt system-wide
sudo make install

# Enable automatic updates (optional)
sudo systemctl enable --now ubopt-agent.timer
```

### Basic Usage

```bash
# Show help
ubopt --help

# Check system health
ubopt health

# Get health report as JSON
ubopt --json health

# Dry-run system update (shows what would be done)
ubopt --dry-run update

# Apply system updates (requires root)
sudo ubopt update

# Apply security hardening (requires root)
sudo ubopt --dry-run hardening  # Preview changes
sudo ubopt hardening            # Apply changes
```

## Commands

### `ubopt update`
Perform system updates including security patches.

```bash
# Interactive update
sudo ubopt update

# Security updates only
sudo ubopt update --security-only

# Headless mode with auto-reboot
sudo ubopt --headless update --reboot-if-required

# Dry-run to preview
ubopt --dry-run update
```

### `ubopt hardening`
Apply security hardening baseline.

```bash
# Preview all hardening
ubopt --dry-run hardening

# Apply SSH hardening only
sudo ubopt hardening --ssh-only

# Apply all hardening measures
sudo ubopt hardening
```

### `ubopt health`
Check and report system health metrics.

```bash
# Text format (default)
ubopt health

# JSON format
ubopt --json health

# Prometheus metrics
ubopt health --format prometheus

# Save to file
ubopt health --format json --output /var/log/health.json
```

### `ubopt backup` (MVP stub)
Backup system (currently dry-run only).

```bash
ubopt --dry-run backup --target /mnt/backup
```

### `ubopt benchmark` (MVP stub)
Run system benchmarks.

```bash
ubopt benchmark
ubopt benchmark --disk --cpu
```

## Global Options

- `--config PATH` - Use custom config file
- `--dry-run` - Show planned actions without executing
- `--json` - Output JSON logs
- `--headless` - Non-interactive mode
- `-v, --verbose` - Increase verbosity
- `--version` - Show version
- `-h, --help` - Show help

## Configuration

Configuration file: `/etc/ubopt/ubopt.yaml`

```yaml
updates:
  schedule: "daily"
  auto_reboot: false
  security_only: false

reboot:
  strategy: "prompt"  # prompt, auto, never
  delay_minutes: 5

hardening:
  ssh:
    disable_root_login: true
    disable_password_auth: true
  firewall:
    enabled: true
    policy: "deny-by-default"

logging:
  level: "info"
  json: true
  file: "/var/log/ubopt/ubopt.log"
```

## Systemd Integration

### Service
```bash
# Check status
systemctl status ubopt-agent.service

# Run manually
sudo systemctl start ubopt-agent.service

# View logs
journalctl -u ubopt-agent.service
```

### Timer
```bash
# Enable automatic updates (daily at 3 AM)
sudo systemctl enable --now ubopt-agent.timer

# Check timer status
systemctl status ubopt-agent.timer

# List next run times
systemctl list-timers ubopt-agent.timer
```

## Development

### Prerequisites

```bash
# Install development dependencies
make dev
```

This installs:
- shellcheck (bash linting)
- bats (bash testing)
- jq (JSON processing)

### Testing

```bash
# Run all tests
make test

# Run shellcheck only
make shellcheck

# Run bats tests only
make bats
```

### Project Structure

```
ubopt/
├── cmd/
│   └── ubopt              # Main entrypoint
├── lib/
│   └── common.sh          # Shared utilities
├── providers/
│   ├── apt.sh             # APT package manager
│   ├── dnf.sh             # DNF package manager
│   └── pacman.sh          # Pacman package manager
├── modules/
│   ├── update.sh          # Update module
│   ├── hardening.sh       # Security hardening
│   ├── health.sh          # Health monitoring
│   ├── backup.sh          # Backup (stub)
│   ├── benchmark.sh       # Benchmarks (stub)
│   └── logging.sh         # Logging utilities
├── etc/
│   └── ubopt/
│       └── ubopt.example.yaml
├── systemd/
│   ├── ubopt-agent.service
│   └── ubopt-agent.timer
├── docs/
│   ├── ARCHITECTURE.md    # Architecture overview
│   └── CLI.md             # CLI reference
└── tests/
    └── bats/              # BATS test suite
```

## Architecture

UbuntOptimizer uses a modular architecture with:

1. **Provider Layer**: Abstracts package manager operations (apt/dnf/pacman)
2. **Module Layer**: Implements specific functionality (update, hardening, health)
3. **Common Library**: Shared utilities and logging
4. **CLI**: Command-line interface with global options

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for details.

## Exit Codes

- `0` - Success
- `1` - General error
- `2` - No updates available
- `3` - Partial failure
- `4` - Critical issues detected
- `5` - Backup failed
- `6` - Benchmark tools not available
- `10` - Reboot required
- `125` - Invalid arguments
- `127` - Command not found
- `130` - Terminated by Ctrl+C

## Examples

### Automated Security Updates

```bash
# Enable automatic security updates
sudo ubopt hardening
sudo systemctl enable --now ubopt-agent.timer

# Configure to only apply security updates
sudo vi /etc/ubopt/ubopt.yaml
# Set: updates.security_only: true
```

### Health Monitoring with Prometheus

```bash
# Export metrics for node_exporter
ubopt health --format prometheus \
  --output /var/lib/node_exporter/textfile/ubopt.prom

# Add to crontab for periodic updates
echo "*/5 * * * * ubopt health --format prometheus --output /var/lib/node_exporter/textfile/ubopt.prom" | crontab -
```

### Scripting with JSON Output

```bash
#!/bin/bash
# Check if updates are available

if ubopt --json update --dry-run | jq -e '.fields.updates_available > 0' > /dev/null; then
    echo "Updates available, applying..."
    sudo ubopt --headless update
else
    echo "System up to date"
fi
```

## Security Considerations

1. **Root Privileges**: Most operations require root access
2. **SSH Hardening**: Disables root login and password auth - ensure SSH keys are configured
3. **Firewall**: Default deny policy - ensure required ports are allowed
4. **Dry-Run First**: Always test with `--dry-run` before applying changes
5. **Backups**: Not yet implemented - backup manually before system changes

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes and add tests
4. Run `make test` to verify
5. Submit a pull request

## License

MIT License - See LICENSE file for details.

## Support

- Documentation: [docs/](docs/)
- Issues: [GitHub Issues](https://github.com/120git/tinyllama-x/issues)
- Architecture: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- CLI Reference: [docs/CLI.md](docs/CLI.md)

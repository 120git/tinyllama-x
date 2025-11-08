# 🦙 Cool Llama - LinuxOptimizer (ubopt)

Enterprise-grade, cross-distro Linux security + updater suite with automated scheduling, comprehensive testing, and signed releases.

[![CI](https://github.com/120git/tinyllama-x/workflows/CI/badge.svg)](https://github.com/120git/tinyllama-x/actions)
[![Shellcheck](https://github.com/120git/tinyllama-x/workflows/Shellcheck/badge.svg)](https://github.com/120git/tinyllama-x/actions)
[![Test](https://github.com/120git/tinyllama-x/workflows/Test/badge.svg)](https://github.com/120git/tinyllama-x/actions)

## Features

- ✅ **Cross-Distribution Support**: Ubuntu, Debian, Fedora, RHEL, Arch Linux
- ✅ **Modular Architecture**: Clean separation of CLI, providers, and modules
- ✅ **Multiple Output Formats**: Text and JSON output for automation
- ✅ **Dry-Run Mode**: Test changes before applying them
- ✅ **Automated Updates**: Systemd timer for daily headless updates
- ✅ **Security Hardening**: Built-in security checks and recommendations
- ✅ **Health Monitoring**: System health checks (disk, memory, CPU, services)
- ✅ **Backup Utilities**: Automated configuration backups
- ✅ **Performance Benchmarking**: CPU, disk, and network benchmarks
- ✅ **Comprehensive Testing**: 17+ bats tests, shellcheck validation
- ✅ **Signed Releases**: Cosign signatures and SLSA provenance
- ✅ **SBOM Generation**: Software Bill of Materials included

## Quick Start

### Installation

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

### Basic Usage

```bash
# Update system packages
sudo ubopt update

# Check system health
ubopt health

# Run security checks
sudo ubopt harden

# Create system backup
sudo ubopt backup

# View logs
ubopt log
```

### Enable Automatic Updates

```bash
# Enable daily updates at 3 AM
sudo systemctl enable --now ubopt.timer

# Check timer status
sudo systemctl status ubopt.timer
```

## Commands

| Command | Description | Root Required |
|---------|-------------|---------------|
| `update` | Update system packages | ✓ |
| `harden` | Run security hardening checks | ✓ |
| `health` | Run system health checks | - |
| `backup` | Create system backup | ✓ |
| `benchmark` | Run performance benchmarks | - |
| `log` | View ubopt logs | - |
| `version` | Show version information | - |

## Global Options

- `--json`: Output in JSON format
- `--dry-run`: Simulate actions without changes
- `--config FILE`: Use alternate config file
- `--verbose, -v`: Enable verbose output
- `--help, -h`: Show help message
- `--version`: Show version

## Examples

### Update with dry-run

```bash
sudo ubopt update --dry-run
```

### Get health status as JSON

```bash
ubopt health --json
```

Output:
```json
{
  "errors": 0,
  "warnings": 1,
  "disk_usage": 45
}
```

### Verbose security check

```bash
sudo ubopt harden --verbose
```

### Custom backup location

```bash
sudo ubopt backup /mnt/external-backup
```

## Architecture

```
ubopt/
├── cmd/ubopt           # Main CLI entry point
├── lib/                # Core libraries
│   └── common.sh       # Shared utilities
├── providers/          # Package managers
│   ├── apt.sh          # Ubuntu/Debian
│   ├── dnf.sh          # Fedora/RHEL
│   └── pacman.sh       # Arch Linux
├── modules/            # Features
│   ├── update.sh
│   ├── hardening.sh
│   ├── health.sh
│   ├── backup.sh
│   ├── benchmark.sh
│   └── logging.sh
├── systemd/            # Automation
│   ├── ubopt.service
│   └── ubopt.timer
└── etc/ubopt/          # Configuration
    └── config.json
```

## Configuration

Edit `/etc/ubopt/config.json`:

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
  }
}
```

## Systemd Integration

### Timer Configuration

The timer runs daily at 3 AM with a randomized delay of up to 1 hour to prevent server load spikes.

```bash
# View timer configuration
systemctl cat ubopt.timer

# Check next run time
systemctl list-timers ubopt.timer

# View service logs
journalctl -u ubopt.service --since today
```

### Service Configuration

The service runs with security hardening:
- `NoNewPrivileges=true`
- `PrivateTmp=true`
- `ProtectSystem=strict`
- `ProtectHome=true`

## Development

### Prerequisites

- Bash 4.0+
- Make
- bats (for testing)
- shellcheck (for linting)

### Running Tests

```bash
# Run all tests
make test

# Run shellcheck only
make shellcheck

# Run bats only
make bats
```

### Adding a New Module

1. Create `modules/mymodule.sh`
2. Implement `run_mymodule()` function
3. Add command case in `cmd/ubopt`
4. Add tests in `tests/bats/`
5. Update documentation

### Project Structure

See [ARCHITECTURE.md](docs/ARCHITECTURE.md) for detailed architecture information.

## CI/CD

The project includes comprehensive CI/CD workflows:

- **Shellcheck**: Validates all bash scripts
- **Tests**: Runs bats test suite
- **Release**: Creates signed releases with SBOM and SLSA provenance

### Release Process

1. Tag a new version: `git tag v1.0.0`
2. Push the tag: `git push origin v1.0.0`
3. GitHub Actions automatically:
   - Creates release archive
   - Generates SHA256 checksums
   - Creates SBOM (Syft)
   - Signs artifacts (Cosign)
   - Generates SLSA provenance
   - Publishes GitHub release

## Security

### Signed Releases

All releases are signed with Cosign:

```bash
# Verify signature
cosign verify-blob ubopt-x.x.x.tar.gz \
  --signature ubopt-x.x.x.tar.gz.sig \
  --certificate ubopt-x.x.x.tar.gz.pem \
  --certificate-identity-regexp=".*" \
  --certificate-oidc-issuer="https://token.actions.githubusercontent.com"
```

### SLSA Provenance

Each release includes SLSA Level 3 provenance for supply chain security.

### SBOM

Software Bill of Materials (SBOM) in SPDX and JSON formats included with each release.

## Troubleshooting

### Common Issues

**Permission denied**
```bash
# Most commands require root
sudo ubopt update
```

**Module not found**
```bash
# Reinstall
sudo make install
```

**Timer not running**
```bash
# Check timer status
sudo systemctl status ubopt.timer

# Enable if disabled
sudo systemctl enable --now ubopt.timer
```

### Debug Mode

```bash
# Run with verbose output
ubopt health --verbose

# Check logs
ubopt log 100

# View systemd logs
sudo journalctl -u ubopt.service -n 50
```

## Documentation

- [CLI Reference](docs/CLI.md) - Detailed command documentation
- [Architecture](docs/ARCHITECTURE.md) - System design and architecture
- [Contributing](CONTRIBUTING.md) - How to contribute
- [Changelog](CHANGELOG.md) - Version history

## Supported Distributions

| Distribution | Package Manager | Status |
|--------------|----------------|--------|
| Ubuntu 20.04+ | apt | ✅ Tested |
| Debian 11+ | apt | ✅ Tested |
| Fedora 38+ | dnf | ✅ Supported |
| RHEL 8+ | dnf | ✅ Supported |
| Arch Linux | pacman | ✅ Supported |

## Roadmap

- [ ] Web dashboard for monitoring
- [ ] Email notifications
- [ ] Advanced reporting
- [ ] Plugin system
- [ ] Multi-system management
- [ ] Integration with Ansible/Puppet/Chef

## License

MIT License - see [LICENSE](LICENSE) for details

## Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) first.

## Credits

Built with ❤️ by the Cool Llama team

## Support

- Issues: https://github.com/120git/tinyllama-x/issues
- Discussions: https://github.com/120git/tinyllama-x/discussions
- Documentation: https://github.com/120git/tinyllama-x/tree/main/docs

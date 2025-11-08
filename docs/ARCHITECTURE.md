# Cool Llama - LinuxOptimizer (ubopt) Architecture

## Overview

ubopt is an enterprise-grade, cross-distro Linux security and updater suite designed with modularity, testability, and security in mind.

## Directory Structure

```
ubopt/
├── cmd/                    # CLI entry points
│   └── ubopt              # Main CLI executable
├── lib/                    # Core library functions
│   └── common.sh          # Shared utility functions
├── providers/              # Package manager providers
│   ├── apt.sh             # Ubuntu/Debian support
│   ├── dnf.sh             # Fedora/RHEL support
│   └── pacman.sh          # Arch Linux support
├── modules/                # Feature modules
│   ├── update.sh          # System updates
│   ├── hardening.sh       # Security hardening
│   ├── health.sh          # Health checks
│   ├── backup.sh          # Backup utilities
│   ├── benchmark.sh       # Performance benchmarking
│   └── logging.sh         # Log management
├── etc/ubopt/              # Configuration files
│   └── config.json        # Main configuration
├── systemd/                # Systemd units
│   ├── ubopt.service      # Service unit
│   └── ubopt.timer        # Timer for scheduled runs
├── tests/                  # Test suites
│   └── bats/              # Bats test files
├── docs/                   # Documentation
└── Makefile               # Build and install targets
```

## Architecture Principles

### 1. Modularity

The system is divided into clear, independent modules:

- **CLI Layer** (`cmd/`): User interface and command routing
- **Library Layer** (`lib/`): Common utilities and helpers
- **Provider Layer** (`providers/`): Distribution-specific package management
- **Module Layer** (`modules/`): Feature implementations

### 2. Cross-Distribution Support

The provider system abstracts package manager differences:

```bash
# Provider interface (common functions)
provider_update_cache()
provider_upgrade()
provider_install()
provider_remove()
provider_is_installed()
provider_list_upgradable()
provider_clean()
```

Each provider implements these functions for their package manager (apt, dnf, pacman).

### 3. Idempotency and Dry-Run

All operations are:
- **Idempotent**: Can be run multiple times safely
- **Dry-run aware**: Support `--dry-run` flag for simulation

### 4. Security

Security considerations:
- All scripts pass shellcheck with strict warnings
- Systemd units run with restricted permissions
- No hardcoded credentials
- Input validation on all user inputs
- Privilege escalation only when necessary

### 5. Observability

Multiple output formats and logging:
- Standard text output for interactive use
- JSON output with `--json` flag for automation
- Persistent logging to `/var/log/ubopt.log`
- Verbose mode with `--verbose` flag

## Component Details

### CLI (cmd/ubopt)

The main entry point that:
1. Parses global flags (`--json`, `--dry-run`, `--config`, `--verbose`)
2. Routes to appropriate subcommand
3. Loads configuration
4. Executes command with proper error handling

### Providers (providers/)

Distribution-specific implementations:
- Auto-detection based on `/etc/os-release`
- Consistent interface across all distributions
- Dry-run support built-in

### Modules (modules/)

Feature implementations:
- **Update**: Package cache updates and system upgrades
- **Hardening**: Security configuration checks and enforcement
- **Health**: System health monitoring (disk, memory, CPU, services)
- **Backup**: Configuration and system backup
- **Benchmark**: Performance testing
- **Logging**: Log viewing and management

### Systemd Integration (systemd/)

Automated scheduling:
- **ubopt.service**: Runs update command
- **ubopt.timer**: Schedules daily execution (3 AM with 1-hour random delay)

Enable with:
```bash
sudo systemctl enable --now ubopt.timer
```

## Data Flow

```
User Command
    ↓
cmd/ubopt (parse flags, route command)
    ↓
Load Configuration (etc/ubopt/config.json)
    ↓
Detect Distribution
    ↓
Load Provider (providers/{apt,dnf,pacman}.sh)
    ↓
Load Module (modules/{update,harden,health,...}.sh)
    ↓
Execute with error handling
    ↓
Log results
    ↓
Return status
```

## Error Handling

- All scripts use `set -euo pipefail` for strict error handling
- Functions return appropriate exit codes
- Errors logged to stderr and log file
- JSON error format when `--json` is used

## Testing Strategy

### Unit Tests (bats)
- CLI argument parsing
- Provider interface compliance
- Module functionality
- Error handling

### Integration Tests
- End-to-end command execution
- Cross-distribution compatibility
- Systemd timer functionality

### Static Analysis
- shellcheck for all bash scripts
- SBOM generation for dependencies
- Security scanning in CI/CD

## Configuration

Configuration file (`/etc/ubopt/config.json`):
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

## Extensibility

### Adding a New Module

1. Create `modules/mymodule.sh`
2. Implement `run_mymodule()` function
3. Add command case in `cmd/ubopt`
4. Add tests in `tests/bats/`

### Adding a New Provider

1. Create `providers/myprovider.sh`
2. Implement provider interface functions
3. Add detection logic in `load_provider()`
4. Add tests in `tests/bats/providers.bats`

## Performance Considerations

- Lazy loading of modules and providers
- Minimal external dependencies
- Efficient package cache management
- Parallel operations where safe

## Future Enhancements

- [ ] Web dashboard for monitoring
- [ ] Plugin system for third-party modules
- [ ] Advanced reporting and analytics
- [ ] Multi-system management
- [ ] Integration with configuration management tools

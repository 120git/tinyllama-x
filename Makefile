.PHONY: help dev test install uninstall clean shellcheck bats

# Default target
help:
	@echo "UbuntOptimizer - Makefile"
	@echo ""
	@echo "Targets:"
	@echo "  make dev        - Install development dependencies (shellcheck, bats)"
	@echo "  make test       - Run tests (shellcheck + bats)"
	@echo "  make shellcheck - Run shellcheck on all bash scripts"
	@echo "  make bats       - Run bats tests"
	@echo "  make install    - Install ubopt system-wide"
	@echo "  make uninstall  - Uninstall ubopt"
	@echo "  make clean      - Clean temporary files"

# Install development dependencies
dev:
	@echo "Installing development dependencies..."
	@which shellcheck > /dev/null || (echo "Installing shellcheck..." && sudo apt-get install -y shellcheck || sudo dnf install -y ShellCheck || sudo pacman -S --noconfirm shellcheck)
	@which bats > /dev/null || (echo "Installing bats..." && \
		if [ -d /tmp/bats-core ]; then rm -rf /tmp/bats-core; fi && \
		git clone https://github.com/bats-core/bats-core.git /tmp/bats-core && \
		cd /tmp/bats-core && sudo ./install.sh /usr/local)
	@which jq > /dev/null || (echo "Installing jq..." && sudo apt-get install -y jq || sudo dnf install -y jq || sudo pacman -S --noconfirm jq)
	@echo "Development dependencies installed!"

# Run shellcheck on all bash scripts
shellcheck:
	@echo "Running shellcheck..."
	@find . -name "*.sh" -type f -exec shellcheck -x {} +
	@shellcheck cmd/ubopt
	@echo "Shellcheck passed!"

# Run bats tests
bats:
	@echo "Running bats tests..."
	@bats tests/bats/*.bats
	@echo "Bats tests passed!"

# Run all tests
test: shellcheck bats
	@echo "All tests passed!"

# Install ubopt system-wide
install:
	@echo "Installing ubopt..."
	@sudo install -m 755 cmd/ubopt /usr/local/bin/ubopt
	@sudo mkdir -p /etc/ubopt
	@sudo install -m 644 etc/ubopt/ubopt.example.yaml /etc/ubopt/ubopt.example.yaml
	@if [ ! -f /etc/ubopt/ubopt.yaml ]; then \
		sudo cp etc/ubopt/ubopt.example.yaml /etc/ubopt/ubopt.yaml; \
		echo "Created /etc/ubopt/ubopt.yaml"; \
	fi
	@sudo mkdir -p /usr/local/share/ubopt/lib
	@sudo mkdir -p /usr/local/share/ubopt/providers
	@sudo mkdir -p /usr/local/share/ubopt/modules
	@sudo cp -r lib/*.sh /usr/local/share/ubopt/lib/
	@sudo cp -r providers/*.sh /usr/local/share/ubopt/providers/
	@sudo cp -r modules/*.sh /usr/local/share/ubopt/modules/
	@sudo mkdir -p /etc/systemd/system
	@sudo install -m 644 systemd/ubopt-agent.service /etc/systemd/system/
	@sudo install -m 644 systemd/ubopt-agent.timer /etc/systemd/system/
	@sudo mkdir -p /etc/logrotate.d
	@sudo install -m 644 packaging/logrotate/ubopt /etc/logrotate.d/ubopt
	@sudo mkdir -p /var/lib/ubopt
	@sudo mkdir -p /var/log/ubopt
	@sudo systemctl daemon-reload
	@echo "ubopt installed to /usr/local/bin/ubopt"
	@echo "Enable with: sudo systemctl enable --now ubopt-agent.timer"

# Uninstall ubopt
uninstall:
	@echo "Uninstalling ubopt..."
	@sudo systemctl stop ubopt-agent.timer 2>/dev/null || true
	@sudo systemctl disable ubopt-agent.timer 2>/dev/null || true
	@sudo rm -f /usr/local/bin/ubopt
	@sudo rm -rf /usr/local/share/ubopt
	@sudo rm -f /etc/systemd/system/ubopt-agent.service
	@sudo rm -f /etc/systemd/system/ubopt-agent.timer
	@sudo rm -f /etc/logrotate.d/ubopt
	@sudo systemctl daemon-reload
	@echo "ubopt uninstalled"
	@echo "Config and logs remain in /etc/ubopt and /var/log/ubopt"

# Clean temporary files
clean:
	@echo "Cleaning..."
	@find . -name "*.bak" -type f -delete
	@find . -name "*~" -type f -delete
	@rm -rf /tmp/bats-core
	@echo "Cleaned!"

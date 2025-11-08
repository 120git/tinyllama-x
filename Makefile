.PHONY: help install uninstall test lint clean build check shellcheck bats

PREFIX ?= /usr/local
BINDIR = $(PREFIX)/bin
LIBDIR = $(PREFIX)/lib/ubopt
SYSCONFDIR = /etc/ubopt
SYSTEMDDIR = /etc/systemd/system

help:
	@echo "Cool Llama - LinuxOptimizer (ubopt) Makefile"
	@echo ""
	@echo "Targets:"
	@echo "  install       Install ubopt to $(PREFIX)"
	@echo "  uninstall     Uninstall ubopt"
	@echo "  test          Run all tests (shellcheck + bats)"
	@echo "  lint          Run shellcheck on all scripts"
	@echo "  shellcheck    Run shellcheck only"
	@echo "  bats          Run bats tests only"
	@echo "  check         Run lint and tests"
	@echo "  clean         Remove build artifacts"
	@echo "  build         Validate structure (no build needed for bash)"
	@echo ""
	@echo "Variables:"
	@echo "  PREFIX        Installation prefix (default: /usr/local)"

install:
	@echo "Installing ubopt to $(PREFIX)..."
	install -d $(BINDIR)
	install -d $(LIBDIR)
	install -d $(LIBDIR)/providers
	install -d $(LIBDIR)/modules
	install -d $(SYSCONFDIR)
	install -d $(SYSTEMDDIR)
	install -m 0755 cmd/ubopt $(BINDIR)/ubopt
	install -m 0644 lib/*.sh $(LIBDIR)/ 2>/dev/null || true
	install -m 0644 providers/*.sh $(LIBDIR)/providers/ 2>/dev/null || true
	install -m 0644 modules/*.sh $(LIBDIR)/modules/ 2>/dev/null || true
	install -m 0644 etc/ubopt/config.json $(SYSCONFDIR)/config.json.example 2>/dev/null || true
	install -m 0644 systemd/ubopt.service $(SYSTEMDDIR)/ 2>/dev/null || true
	install -m 0644 systemd/ubopt.timer $(SYSTEMDDIR)/ 2>/dev/null || true
	@echo "Installation complete. Run 'ubopt --help' to get started."

uninstall:
	@echo "Uninstalling ubopt..."
	rm -f $(BINDIR)/ubopt
	rm -rf $(LIBDIR)
	@echo "Note: Config in $(SYSCONFDIR) and systemd units in $(SYSTEMDDIR) left intact."
	@echo "Remove manually if needed."

build:
	@echo "Validating structure..."
	@test -f cmd/ubopt || (echo "ERROR: cmd/ubopt missing" && exit 1)
	@test -d lib || (echo "ERROR: lib/ directory missing" && exit 1)
	@test -d providers || (echo "ERROR: providers/ directory missing" && exit 1)
	@test -d modules || (echo "ERROR: modules/ directory missing" && exit 1)
	@echo "Structure validation passed."

shellcheck:
	@echo "Running shellcheck..."
	@command -v shellcheck >/dev/null 2>&1 || (echo "ERROR: shellcheck not installed" && exit 1)
	@find cmd lib providers modules -type f -name "*.sh" -o -type f -executable | xargs shellcheck -x -S warning || true
	@shellcheck -x -S warning cmd/ubopt 2>/dev/null || true

bats:
	@echo "Running bats tests..."
	@command -v bats >/dev/null 2>&1 || (echo "ERROR: bats not installed. Install with: npm install -g bats" && exit 1)
	@bats tests/bats/*.bats

test: shellcheck bats

check: lint test

lint: shellcheck

clean:
	@echo "Cleaning build artifacts..."
	@find . -type f -name "*.log" -delete
	@find . -type f -name "*~" -delete
	@echo "Clean complete."

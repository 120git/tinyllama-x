#!/usr/bin/env bats

# Test provider system

setup() {
    export PATH="$BATS_TEST_DIRNAME/../../cmd:$PATH"
    LIB_DIR="$BATS_TEST_DIRNAME/../../lib"
}

@test "apt provider exists" {
    [ -f "$BATS_TEST_DIRNAME/../../providers/apt.sh" ]
}

@test "dnf provider exists" {
    [ -f "$BATS_TEST_DIRNAME/../../providers/dnf.sh" ]
}

@test "pacman provider exists" {
    [ -f "$BATS_TEST_DIRNAME/../../providers/pacman.sh" ]
}

@test "apt provider can be sourced" {
    source "$LIB_DIR/common.sh"
    export DRY_RUN=true
    source "$BATS_TEST_DIRNAME/../../providers/apt.sh"
    # Check that functions are defined
    declare -f provider_update_cache >/dev/null
}

@test "dnf provider can be sourced" {
    source "$LIB_DIR/common.sh"
    export DRY_RUN=true
    source "$BATS_TEST_DIRNAME/../../providers/dnf.sh"
    declare -f provider_update_cache >/dev/null
}

@test "pacman provider can be sourced" {
    source "$LIB_DIR/common.sh"
    export DRY_RUN=true
    source "$BATS_TEST_DIRNAME/../../providers/pacman.sh"
    declare -f provider_update_cache >/dev/null
}

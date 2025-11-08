#!/usr/bin/env bats
# cli.bats - CLI basic functionality tests

setup() {
    # Get the path to ubopt
    UBOPT_CMD="${BATS_TEST_DIRNAME}/../../cmd/ubopt"
    export PATH="${BATS_TEST_DIRNAME}/../../cmd:$PATH"
}

@test "ubopt command exists and is executable" {
    [ -x "$UBOPT_CMD" ]
}

@test "ubopt --help shows usage" {
    run "$UBOPT_CMD" --help
    [ "$status" -eq 0 ]
    [[ "$output" =~ "Usage:" ]]
    [[ "$output" =~ "Commands:" ]]
}

@test "ubopt without arguments shows usage" {
    run "$UBOPT_CMD"
    [ "$status" -eq 0 ]
    [[ "$output" =~ "Usage:" ]]
}

@test "ubopt --version shows version" {
    run "$UBOPT_CMD" --version
    [ "$status" -eq 0 ]
    [[ "$output" =~ "ubopt version" ]]
}

@test "ubopt help command works" {
    run "$UBOPT_CMD" help
    [ "$status" -eq 0 ]
    [[ "$output" =~ "Usage:" ]]
}

@test "ubopt help update shows update help" {
    run "$UBOPT_CMD" help update
    [ "$status" -eq 0 ]
    [[ "$output" =~ "Usage: ubopt update" ]]
}

@test "ubopt help hardening shows hardening help" {
    run "$UBOPT_CMD" help hardening
    [ "$status" -eq 0 ]
    [[ "$output" =~ "Usage: ubopt hardening" ]]
}

@test "ubopt help health shows health help" {
    run "$UBOPT_CMD" help health
    [ "$status" -eq 0 ]
    [[ "$output" =~ "Usage: ubopt health" ]]
}

@test "ubopt version command works" {
    run "$UBOPT_CMD" version
    [ "$status" -eq 0 ]
    [[ "$output" =~ "ubopt version" ]]
}

@test "ubopt with invalid command shows error" {
    run "$UBOPT_CMD" invalid-command
    [ "$status" -eq 127 ]
    [[ "$output" =~ "Unknown command" ]]
}

@test "ubopt with invalid option shows error" {
    run "$UBOPT_CMD" --invalid-option
    [ "$status" -eq 125 ]
    [[ "$output" =~ "Unknown option" ]]
}

@test "ubopt update --help shows update help" {
    run "$UBOPT_CMD" update --help
    [ "$status" -eq 0 ]
    [[ "$output" =~ "Usage: ubopt update" ]]
}

@test "ubopt hardening --help shows hardening help" {
    run "$UBOPT_CMD" hardening --help
    [ "$status" -eq 0 ]
    [[ "$output" =~ "Usage: ubopt hardening" ]]
}

@test "ubopt health --help shows health help" {
    run "$UBOPT_CMD" health --help
    [ "$status" -eq 0 ]
    [[ "$output" =~ "Usage: ubopt health" ]]
}

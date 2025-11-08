"""Tests for GUI presenter and services."""
from __future__ import annotations

import time

import pytest

from tinyllamax.core.intents import InstallPackage
from tinyllamax.gui.presenter import TinyLlamaPresenter
from tinyllamax.gui.services import (
    BackgroundTask,
    CancellationError,
    CancellationToken,
    run_background,
)
from tinyllamax.model_backends.fake import FakeBackend


def test_cancellation_token():
    """Test cancellation token functionality."""
    token = CancellationToken()
    assert not token.is_cancelled()
    
    token.cancel()
    assert token.is_cancelled()
    
    with pytest.raises(CancellationError):
        token.check_cancelled()


def test_background_task_success():
    """Test successful background task execution."""
    result_value = None
    
    def task() -> str:
        return "success"
    
    def on_done(result: str) -> None:
        nonlocal result_value
        result_value = result
    
    bg_task = BackgroundTask(task, on_done=on_done)
    bg_task.start()
    
    # Wait for completion
    timeout = 2.0
    start = time.time()
    while bg_task.is_alive() and (time.time() - start) < timeout:
        time.sleep(0.1)
    
    assert result_value == "success"


def test_background_task_error():
    """Test background task error handling."""
    error_caught = None
    
    def task() -> None:
        raise ValueError("test error")
    
    def on_error(error: Exception) -> None:
        nonlocal error_caught
        error_caught = error
    
    bg_task = BackgroundTask(task, on_error=on_error)
    bg_task.start()
    
    # Wait for completion
    timeout = 2.0
    start = time.time()
    while bg_task.is_alive() and (time.time() - start) < timeout:
        time.sleep(0.1)
    
    assert isinstance(error_caught, ValueError)
    assert str(error_caught) == "test error"


def test_background_task_cancellation():
    """Test background task cancellation."""
    cancelled = False
    
    def task(cancel_token: CancellationToken) -> None:
        nonlocal cancelled
        for _ in range(10):
            if cancel_token.is_cancelled():
                cancelled = True
                raise CancellationError()
            time.sleep(0.1)
    
    bg_task = BackgroundTask(task)
    bg_task.start(cancel_token=bg_task.token)
    
    # Cancel after short delay
    time.sleep(0.2)
    bg_task.cancel()
    
    # Wait for cancellation
    timeout = 2.0
    start = time.time()
    while bg_task.is_alive() and (time.time() - start) < timeout:
        time.sleep(0.1)
    
    assert cancelled


def test_run_background():
    """Test run_background convenience function."""
    result_value = None
    
    def task(x: int, y: int) -> int:
        return x + y
    
    def on_done(result: int) -> None:
        nonlocal result_value
        result_value = result
    
    bg_task = run_background(task, on_done, None, None, 5, 3)
    
    # Wait for completion
    timeout = 2.0
    start = time.time()
    while bg_task.is_alive() and (time.time() - start) < timeout:
        time.sleep(0.1)
    
    assert result_value == 8


def test_presenter_initialization():
    """Test presenter initialization."""
    backend = FakeBackend()
    presenter = TinyLlamaPresenter(backend)
    
    assert presenter.backend == backend
    assert presenter.decider is not None
    assert presenter.distro_id != "unknown"
    assert presenter.pkg_manager != "unknown"


def test_presenter_callbacks():
    """Test presenter callback mechanisms."""
    backend = FakeBackend()
    presenter = TinyLlamaPresenter(backend)
    
    status_updates = []
    output_updates = []
    plan_updates = []
    errors = []
    
    presenter.on_status_update = lambda s: status_updates.append(s)
    presenter.on_output_update = lambda s: output_updates.append(s)
    presenter.on_plan_update = lambda s: plan_updates.append(s)
    presenter.on_error = lambda s: errors.append(s)
    
    # Trigger detection (should update status)
    presenter._detect_system()
    assert len(status_updates) > 0


def test_presenter_plan_intent():
    """Test presenter planning an intent."""
    backend = FakeBackend()
    presenter = TinyLlamaPresenter(backend)
    
    presenter.on_plan_update = lambda _: None  # Suppress output
    
    intent = InstallPackage(package="htop")
    plan = presenter.plan_intent(intent)
    
    assert plan is not None
    assert plan.description is not None
    assert presenter.current_plan == plan


def test_presenter_simulate_plan():
    """Test presenter simulating a plan."""
    backend = FakeBackend()
    presenter = TinyLlamaPresenter(backend)
    
    outputs = []
    presenter.on_output_update = lambda s: outputs.append(s)
    
    intent = InstallPackage(package="htop")
    plan = presenter.plan_intent(intent)
    result = presenter.simulate_plan(plan)
    
    assert result is not None
    assert len(outputs) > 0


def test_presenter_explain():
    """Test presenter explain functionality."""
    backend = FakeBackend()
    presenter = TinyLlamaPresenter(backend)
    
    outputs = []
    presenter.on_output_update = lambda s: outputs.append(s)
    
    explanation = presenter.explain("ls")
    
    assert explanation is not None
    assert len(outputs) > 0


def test_presenter_get_history():
    """Test presenter history retrieval."""
    backend = FakeBackend()
    presenter = TinyLlamaPresenter(backend)
    
    # Should not raise even if no history
    records = presenter.get_history(limit=5)
    assert isinstance(records, list)

"""GTK 4 desktop application for TinyLlama-X.

Provides a graphical user interface with:
- Command input and intent classification
- Propose/simulate and execute workflows
- Command explanation
- Operation history viewing
"""
from __future__ import annotations

import sys

try:
    import gi
    gi.require_version('Gtk', '4.0')
    from gi.repository import GLib, Gtk
    GTK_AVAILABLE = True
except (ImportError, ValueError):
    GTK_AVAILABLE = False
    Gtk = None  # type: ignore
    GLib = None  # type: ignore

from tinyllamax.gui.presenter import TinyLlamaPresenter
from tinyllamax.gui.services import BackgroundTask, run_background
from tinyllamax.model_backends.fake import FakeBackend
from tinyllamax.model_backends.ollama import OllamaBackend

try:
    from tinyllamax.model_backends.llamacpp import LlamaCppBackend
except ImportError:
    LlamaCppBackend = None  # type: ignore


class TinyLlamaWindow(Gtk.ApplicationWindow):
    """Main application window for TinyLlama-X GUI."""
    
    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)
        self.set_title("TinyLlama-X Desktop")
        self.set_default_size(900, 700)
        
        # Initialize presenter with default backend
        backend = FakeBackend()  # Will be replaced based on user selection
        self.presenter = TinyLlamaPresenter(backend)
        self.current_task: BackgroundTask | None = None
        
        # Set up callbacks
        self.presenter.on_status_update = self._on_status_update
        self.presenter.on_output_update = self._on_output_append
        self.presenter.on_plan_update = self._on_plan_update
        self.presenter.on_error = self._on_error
        
        # Build UI
        self._build_ui()
    
    def _build_ui(self) -> None:
        """Build the user interface."""
        # Main container
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        main_box.set_margin_start(10)
        main_box.set_margin_end(10)
        main_box.set_margin_top(10)
        main_box.set_margin_bottom(10)
        
        # Top section: Input and buttons
        input_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        
        # Command input
        input_label = Gtk.Label(label="What do you want to do?")
        input_label.set_halign(Gtk.Align.START)
        input_box.append(input_label)
        
        self.command_entry = Gtk.Entry()
        self.command_entry.set_placeholder_text("e.g., install htop, update system, explain ls")
        self.command_entry.connect("activate", self._on_propose_clicked)
        input_box.append(self.command_entry)
        
        main_box.append(input_box)
        
        # Options section
        options_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        
        # Backend selector
        backend_label = Gtk.Label(label="Backend:")
        options_box.append(backend_label)
        
        self.backend_combo = Gtk.ComboBoxText()
        self.backend_combo.append("fake", "Fake (Testing)")
        self.backend_combo.append("ollama", "Ollama")
        if LlamaCppBackend:
            self.backend_combo.append("llamacpp", "Llama.cpp")
        self.backend_combo.set_active_id("ollama")
        self.backend_combo.connect("changed", self._on_backend_changed)
        options_box.append(self.backend_combo)
        
        # Model input
        model_label = Gtk.Label(label="Model:")
        options_box.append(model_label)
        
        self.model_entry = Gtk.Entry()
        self.model_entry.set_text("tinyllama:latest")
        self.model_entry.set_width_chars(20)
        options_box.append(self.model_entry)
        
        # Simulate only checkbox
        self.simulate_only_check = Gtk.CheckButton(label="Simulate Only")
        self.simulate_only_check.set_active(True)
        options_box.append(self.simulate_only_check)
        
        main_box.append(options_box)
        
        # Button bar
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        
        self.propose_button = Gtk.Button(label="Propose/Simulate")
        self.propose_button.connect("clicked", self._on_propose_clicked)
        button_box.append(self.propose_button)
        
        self.run_button = Gtk.Button(label="Run")
        self.run_button.set_sensitive(False)
        self.run_button.connect("clicked", self._on_run_clicked)
        button_box.append(self.run_button)
        
        self.cancel_button = Gtk.Button(label="Cancel")
        self.cancel_button.set_sensitive(False)
        self.cancel_button.connect("clicked", self._on_cancel_clicked)
        button_box.append(self.cancel_button)
        
        self.explain_button = Gtk.Button(label="Explain")
        self.explain_button.connect("clicked", self._on_explain_clicked)
        button_box.append(self.explain_button)
        
        self.history_button = Gtk.Button(label="History")
        self.history_button.connect("clicked", self._on_history_clicked)
        button_box.append(self.history_button)
        
        main_box.append(button_box)
        
        # Planned command panel
        plan_frame = Gtk.Frame(label="Planned Command")
        plan_scroll = Gtk.ScrolledWindow()
        plan_scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        plan_scroll.set_min_content_height(80)
        
        self.plan_view = Gtk.TextView()
        self.plan_view.set_editable(False)
        self.plan_view.set_wrap_mode(Gtk.WrapMode.WORD)
        self.plan_view.set_monospace(True)
        plan_scroll.set_child(self.plan_view)
        plan_frame.set_child(plan_scroll)
        
        main_box.append(plan_frame)
        
        # Output console
        output_frame = Gtk.Frame(label="Output Console")
        output_scroll = Gtk.ScrolledWindow()
        output_scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        output_scroll.set_vexpand(True)
        
        self.output_view = Gtk.TextView()
        self.output_view.set_editable(False)
        self.output_view.set_wrap_mode(Gtk.WrapMode.WORD)
        self.output_view.set_monospace(True)
        output_scroll.set_child(self.output_view)
        output_frame.set_child(output_scroll)
        
        main_box.append(output_frame)
        
        # Status bar
        self.status_label = Gtk.Label(label="Ready")
        self.status_label.set_halign(Gtk.Align.START)
        main_box.append(self.status_label)
        
        self.set_child(main_box)
        
        # Initialize backend
        self._on_backend_changed(self.backend_combo)
    
    def _on_backend_changed(self, combo: Gtk.ComboBoxText) -> None:
        """Handle backend selection change."""
        backend_id = combo.get_active_id()
        model_name = self.model_entry.get_text()
        
        try:
            if backend_id == "fake":
                backend = FakeBackend()
            elif backend_id == "ollama":
                backend = OllamaBackend(model=model_name)
            elif backend_id == "llamacpp" and LlamaCppBackend:
                backend = LlamaCppBackend(model_path=model_name)
            else:
                backend = FakeBackend()
            
            self.presenter.backend = backend
            self.presenter.decider.backend = backend
            self._append_output(f"Backend switched to: {backend_id}\n")
        except Exception as e:
            self._show_error(f"Failed to initialize backend: {e}")
    
    def _on_propose_clicked(self, _widget: object) -> None:
        """Handle Propose/Simulate button click."""
        user_text = self.command_entry.get_text().strip()
        if not user_text:
            self._show_error("Please enter a command")
            return
        
        self._clear_output()
        self._set_buttons_enabled(False)
        self.cancel_button.set_sensitive(True)
        
        def task() -> None:
            self.presenter.propose_and_simulate(user_text)
        
        def on_done(_result: object) -> None:
            GLib.idle_add(self._on_propose_complete)
        
        def on_error(error: Exception) -> None:
            GLib.idle_add(self._show_error, str(error))
            GLib.idle_add(self._set_buttons_enabled, True)
        
        self.current_task = run_background(task, on_done, on_error)
    
    def _on_propose_complete(self) -> None:
        """Handle completion of propose/simulate workflow."""
        self._set_buttons_enabled(True)
        self.cancel_button.set_sensitive(False)
        
        # Enable Run button if not simulate-only
        if not self.simulate_only_check.get_active():
            self.run_button.set_sensitive(True)
    
    def _on_run_clicked(self, _widget: object) -> None:
        """Handle Run button click."""
        if not self.presenter.current_plan:
            self._show_error("No plan to execute")
            return
        
        # Show confirmation dialog
        dialog = Gtk.AlertDialog()
        dialog.set_message("Execute Command?")
        dialog.set_detail("This will execute the real command on your system.")
        dialog.set_buttons(["Cancel", "Execute"])
        dialog.set_cancel_button(0)
        dialog.set_default_button(1)
        
        def on_response(_source: object, result: object) -> None:
            try:
                response = dialog.choose_finish(result)  # type: ignore
                if response == 1:  # Execute button
                    self._execute_real_command()
            except Exception:
                pass  # User cancelled
        
        dialog.choose(self, None, on_response)
    
    def _execute_real_command(self) -> None:
        """Execute the real command in background."""
        if not self.presenter.current_plan:
            return
        
        self._set_buttons_enabled(False)
        self.cancel_button.set_sensitive(True)
        
        plan = self.presenter.current_plan
        
        def task() -> None:
            self.presenter.execute_plan(plan)
        
        def on_done(_result: object) -> None:
            GLib.idle_add(self._set_buttons_enabled, True)
            GLib.idle_add(self.cancel_button.set_sensitive, False)
        
        def on_error(error: Exception) -> None:
            GLib.idle_add(self._show_error, str(error))
            GLib.idle_add(self._set_buttons_enabled, True)
        
        self.current_task = run_background(task, on_done, on_error)
    
    def _on_cancel_clicked(self, _widget: object) -> None:
        """Handle Cancel button click."""
        if self.current_task:
            self.current_task.cancel()
            self._append_output("\n=== Operation Cancelled ===\n")
            self._set_buttons_enabled(True)
            self.cancel_button.set_sensitive(False)
    
    def _on_explain_clicked(self, _widget: object) -> None:
        """Handle Explain button click."""
        command = self.command_entry.get_text().strip()
        if not command:
            self._show_error("Please enter a command to explain")
            return
        
        self._clear_output()
        self._set_buttons_enabled(False)
        
        def task() -> None:
            self.presenter.explain(command)
        
        def on_done(_result: object) -> None:
            GLib.idle_add(self._set_buttons_enabled, True)
        
        def on_error(error: Exception) -> None:
            GLib.idle_add(self._show_error, str(error))
            GLib.idle_add(self._set_buttons_enabled, True)
        
        self.current_task = run_background(task, on_done, on_error)
    
    def _on_history_clicked(self, _widget: object) -> None:
        """Handle History button click."""
        self._clear_output()
        
        try:
            records = self.presenter.get_history(limit=20)
            if not records:
                self._append_output("No history records found.\n")
                return
            
            self._append_output("=== Recent Operations (last 20) ===\n\n")
            for rec in records:
                timestamp = rec.timestamp.strftime("%Y-%m-%d %H:%M:%S")
                self._append_output(f"[{timestamp}] {rec.intent_type}\n")
                self._append_output(f"  Command: {rec.command}\n")
                self._append_output(f"  Status: {rec.status}\n")
                if rec.output_summary:
                    self._append_output(f"  Output: {rec.output_summary[:100]}...\n")
                self._append_output("\n")
        except Exception as e:
            self._show_error(f"Failed to load history: {e}")
    
    def _set_buttons_enabled(self, enabled: bool) -> None:
        """Enable or disable action buttons."""
        self.propose_button.set_sensitive(enabled)
        self.explain_button.set_sensitive(enabled)
        self.history_button.set_sensitive(enabled)
        if enabled:
            self.run_button.set_sensitive(False)
    
    def _on_status_update(self, status: str) -> None:
        """Handle status update from presenter."""
        GLib.idle_add(self.status_label.set_text, status)
    
    def _on_plan_update(self, plan_text: str) -> None:
        """Handle plan update from presenter."""
        def update() -> bool:
            buffer = self.plan_view.get_buffer()
            buffer.set_text(plan_text)
            return False
        
        GLib.idle_add(update)
    
    def _on_output_append(self, text: str) -> None:
        """Handle output append from presenter."""
        GLib.idle_add(self._append_output, text)
    
    def _append_output(self, text: str) -> bool:
        """Append text to output console."""
        buffer = self.output_view.get_buffer()
        end_iter = buffer.get_end_iter()
        buffer.insert(end_iter, text)
        
        # Auto-scroll to bottom
        mark = buffer.get_insert()
        self.output_view.scroll_to_mark(mark, 0.0, False, 0.0, 0.0)
        
        return False
    
    def _clear_output(self) -> None:
        """Clear the output console."""
        buffer = self.output_view.get_buffer()
        buffer.set_text("")
    
    def _on_error(self, error: str) -> None:
        """Handle error from presenter."""
        GLib.idle_add(self._show_error, error)
    
    def _show_error(self, message: str) -> None:
        """Show error dialog."""
        self._append_output(f"\n[ERROR] {message}\n")
        self.status_label.set_text(f"Error: {message}")


class TinyLlamaApp(Gtk.Application):
    """GTK Application for TinyLlama-X."""
    
    def __init__(self) -> None:
        super().__init__(application_id="com.tinyllama.desktop")
    
    def do_activate(self) -> None:
        """Activate the application."""
        window = TinyLlamaWindow(application=self)
        window.present()


def run_gui() -> None:
    """Launch the GTK GUI application."""
    if not GTK_AVAILABLE:
        print("Error: GTK 4 is not available. Please install PyGObject:")
        print("  pip install PyGObject")
        print("  # Or on Ubuntu: sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-4.0")
        sys.exit(1)
    
    app = TinyLlamaApp()
    app.run(sys.argv)


__all__ = ["TinyLlamaApp", "TinyLlamaWindow", "run_gui"]

#!/usr/bin/env python3
"""
Enhanced TinyLlama-X chat interface with intelligent assistance.
Integrates intent detection, distro adapters, command help, and safe execution.
"""

import os
import sys
import datetime
from pathlib import Path

# Add lib directory to path
lib_path = Path(__file__).parent / 'lib'
sys.path.insert(0, str(lib_path))

from colorama import Fore, Style, init
from llama_cpp import Llama

# Import TinyLlama-X intelligence modules
from lib import (
    classify_intent, IntentType,
    detect_distro, get_install_command, get_update_command,
    get_adapter,
    explain_command,
    SafeExecutor, RiskLevel,
    log_operation, get_recent_operations
)

init(autoreset=True)

# Configuration
MODEL_PATH = os.getenv('TINYLLAMA_X_MODEL', os.path.expanduser('~/tinyllama-x/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf'))
LOG_FILE = os.path.expanduser('~/tinyllama-x/conversation.log')
CONTEXT_SIZE = 2048
THREADS = int(os.getenv('TINYLLAMA_X_THREADS', os.cpu_count() or 4))


class IntelligentAssistant:
    """TinyLlama-X intelligent terminal assistant."""
    
    def __init__(self, model_path: str):
        """Initialize assistant with TinyLlama model and system detection."""
        print(f"{Fore.YELLOW}\n🔹 Initializing TinyLlama-X Intelligence Layer...{Style.RESET_ALL}")
        
        # Detect system
        self.distro = detect_distro()
        print(f"{Fore.CYAN}📍 Detected: {self.distro}{Style.RESET_ALL}")
        
        # Initialize executor
        self.executor = SafeExecutor(interactive=True, auto_confirm_low_risk=False)
        
        # Load LLM
        print(f"{Fore.YELLOW}🔹 Loading TinyLlama model...{Style.RESET_ALL}")
        self.llm = Llama(
            model_path=model_path,
            n_ctx=CONTEXT_SIZE,
            n_threads=THREADS
        )
        
        print(f"{Fore.GREEN}\n🤖 TinyLlama-X Intelligence Ready!{Style.RESET_ALL}")
        print(f"{Fore.CYAN}💡 Try asking me to:{Style.RESET_ALL}")
        print(f"   • Install a package: 'install git'")
        print(f"   • Explain a command: 'what does rsync do?'")
        print(f"   • Update system: 'update my system'")
        print(f"   • General chat: 'tell me about Linux'")
        print(f"{Fore.YELLOW}   Type 'exit' to quit.\n{Style.RESET_ALL}")
    
    def process_query(self, query: str) -> str:
        """
        Process user query with intent detection and intelligent routing.
        
        Returns response string.
        """
        # Classify intent
        intent = classify_intent(query)
        
        print(f"{Fore.MAGENTA}[Intent: {intent.type.value}, confidence: {intent.confidence:.0%}]{Style.RESET_ALL}")
        
        # Route based on intent
        if intent.type == IntentType.PACKAGE_INSTALL:
            return self._handle_package_install(intent)
        
        elif intent.type == IntentType.PACKAGE_REMOVE:
            return self._handle_package_remove(intent)
        
        elif intent.type == IntentType.SYSTEM_UPDATE:
            return self._handle_system_update(intent)
        
        elif intent.type == IntentType.COMMAND_EXPLAIN:
            return self._handle_command_explain(intent)
        
        elif intent.type == IntentType.SYSTEM_INFO:
            return self._handle_system_info(intent)
        
        else:
            # General chat - use LLM
            return self._handle_general_chat(intent)
    
    def _handle_package_install(self, intent) -> str:
        """Handle package installation intent."""
        package = intent.entities.get('package')
        
        if not package:
            return "Which package would you like to install?"
        
        # Get install command for this distro
        command = get_install_command(package, self.distro)
        
        if not command:
            return f"Sorry, I don't know how to install packages on {self.distro.name}."
        
        # Create execution plan
        plan = self.executor.plan(
            command=command,
            description=f"Install '{package}' using {self.distro.package_manager}"
        )
        
        # Execute with confirmation
        result = self.executor.execute(plan)
        
        # Log to history
        status = 'success' if result.success else ('cancelled' if result.returncode == -2 else 'failed')
        log_operation(
            intent_type='package_install',
            command=command,
            status=status,
            output_summary=result.stdout[:200] if result.stdout else '',
            error_message=result.stderr if not result.success else None
        )
        
        if result.success:
            return f"✓ Successfully installed {package}!"
        elif result.returncode == -2:
            return "Installation cancelled."
        else:
            return f"Failed to install {package}. Check errors above."
    
    def _handle_package_remove(self, intent) -> str:
        """Handle package removal intent."""
        package = intent.entities.get('package')
        
        if not package:
            return "Which package would you like to remove?"
        
        adapter = get_adapter(self.distro.package_manager, dry_run=False)
        if not adapter:
            return f"Sorry, package management not supported for {self.distro.name}."
        
        # Show what will be removed (dry run first)
        print(f"\n{Fore.YELLOW}Checking what will be removed...{Style.RESET_ALL}")
        dry_adapter = get_adapter(self.distro.package_manager, dry_run=True)
        dry_result = dry_adapter.remove([package])
        
        if dry_result.stdout:
            print(dry_result.stdout)
        
        # Confirm
        response = input(f"\n{Fore.RED}Remove {package}? [y/N]: {Style.RESET_ALL}").lower()
        if response != 'y':
            return "Removal cancelled."
        
        # Execute
        result = adapter.remove([package])
        
        status = 'success' if result.success else 'failed'
        log_operation(
            intent_type='package_remove',
            command=result.command,
            status=status,
            output_summary=result.stdout[:200] if result.stdout else '',
            error_message=result.stderr if not result.success else None
        )
        
        if result.success:
            return f"✓ Successfully removed {package}."
        else:
            return f"Failed to remove {package}."
    
    def _handle_system_update(self, intent) -> str:
        """Handle system update intent."""
        command = get_update_command(self.distro)
        
        if not command:
            return f"Sorry, I don't know how to update {self.distro.name}."
        
        plan = self.executor.plan(
            command=command,
            description=f"Update {self.distro.name} system packages"
        )
        
        result = self.executor.execute(plan)
        
        status = 'success' if result.success else ('cancelled' if result.returncode == -2 else 'failed')
        log_operation(
            intent_type='system_update',
            command=command,
            status=status,
            output_summary=result.stdout[:200] if result.stdout else '',
            error_message=result.stderr if not result.success else None
        )
        
        if result.success:
            return "✓ System update completed!"
        elif result.returncode == -2:
            return "Update cancelled."
        else:
            return "System update failed. Check errors above."
    
    def _handle_command_explain(self, intent) -> str:
        """Handle command explanation intent using RAG-lite."""
        command = intent.entities.get('command')
        
        if not command:
            return "Which command would you like me to explain?"
        
        # Get help from tldr/man
        help_info = explain_command(command)
        
        if not help_info:
            return f"Sorry, I don't have information about '{command}'. Try: man {command}"
        
        # Format response
        response = f"{Fore.CYAN}━━━ {command.upper()} ━━━{Style.RESET_ALL}\n\n"
        response += f"{help_info.description}\n\n"
        
        if help_info.safety_warning:
            response += f"{help_info.safety_warning}\n\n"
        
        if help_info.examples:
            response += f"{Fore.GREEN}Examples:{Style.RESET_ALL}\n"
            for i, example in enumerate(help_info.examples[:3], 1):
                response += f"\n{i}. {example}\n"
        
        response += f"\n{Fore.BLUE}Source: {help_info.source}{Style.RESET_ALL}"
        
        return response
    
    def _handle_system_info(self, intent) -> str:
        """Handle system information request."""
        info = f"{Fore.CYAN}━━━ SYSTEM INFORMATION ━━━{Style.RESET_ALL}\n\n"
        info += f"Distribution:     {self.distro.name}\n"
        info += f"Version:          {self.distro.version}\n"
        info += f"ID:               {self.distro.id}\n"
        info += f"Package Manager:  {self.distro.package_manager}\n"
        
        if self.distro.id_like:
            info += f"Based on:         {', '.join(self.distro.id_like)}\n"
        
        return info
    
    def _handle_general_chat(self, intent) -> str:
        """Handle general conversation using LLM."""
        try:
            # System prompt with date context
            today = datetime.datetime.now().strftime("%B %d, %Y")
            
            response = self.llm.create_chat_completion(
                messages=[
                    {
                        "role": "system",
                        "content": f"You are TinyLlama-X, a helpful Linux terminal assistant. Today is {today}. Keep responses concise (2-3 sentences) and actionable."
                    },
                    {
                        "role": "user",
                        "content": intent.original_query
                    }
                ],
                max_tokens=200,
                temperature=0.7
            )
            
            reply = response["choices"][0]["message"]["content"].strip()
            return reply
        
        except Exception as e:
            return f"Error generating response: {e}"


def main():
    """Main chat loop."""
    if not os.path.exists(MODEL_PATH):
        print(f"{Fore.RED}Error: Model not found at {MODEL_PATH}{Style.RESET_ALL}")
        print(f"Set TINYLLAMA_X_MODEL environment variable to your model path.")
        return 1
    
    # Initialize assistant
    try:
        assistant = IntelligentAssistant(MODEL_PATH)
    except Exception as e:
        print(f"{Fore.RED}Failed to initialize: {e}{Style.RESET_ALL}")
        return 1
    
    # Chat loop
    while True:
        try:
            sys.stdout.write(f"\n{Fore.CYAN}🧑 You: {Style.RESET_ALL}")
            sys.stdout.flush()
            
            user_input = sys.stdin.readline().strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ['exit', 'quit', 'bye']:
                print(f"{Fore.MAGENTA}\n👋 Goodbye! Stay curious.{Style.RESET_ALL}")
                break
            
            # Process query
            response = assistant.process_query(user_input)
            
            # Display response
            print(f"\n{Fore.GREEN}🤖 TinyLlama-X:{Style.RESET_ALL} {response}\n")
            
            # Log to file
            with open(LOG_FILE, 'a') as f:
                f.write(f"\n[{datetime.datetime.now()}]\n")
                f.write(f"You: {user_input}\n")
                f.write(f"Assistant: {response}\n")
        
        except KeyboardInterrupt:
            print(f"\n{Fore.RED}\n🛑 Interrupted.{Style.RESET_ALL}")
            break
        
        except EOFError:
            print(f"\n{Fore.RED}\n⚠️ EOF detected.{Style.RESET_ALL}")
            break
        
        except Exception as e:
            print(f"\n{Fore.RED}Error: {e}{Style.RESET_ALL}")
            continue
    
    return 0


if __name__ == '__main__':
    sys.exit(main())

#!/usr/bin/env python3
"""
Model Router Setup Wizard

Interactive setup for configuring AI model routing across multiple providers.
Safely collects API keys and helps users configure task-to-model mappings.

Run: python3 setup-wizard.py
"""

import os
import sys
import json
import getpass
from pathlib import Path
from typing import Dict, Optional


# Configuration paths
CONFIG_DIR = Path.home() / ".model-router"
CONFIG_FILE = CONFIG_DIR / "config.json"
API_KEYS_FILE = CONFIG_DIR / ".api-keys"


# Color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_header(text: str):
    """Print a formatted header."""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text.center(60)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}\n")


def print_success(text: str):
    """Print success message."""
    print(f"{Colors.OKGREEN}✓ {text}{Colors.ENDC}")


def print_warning(text: str):
    """Print warning message."""
    print(f"{Colors.WARNING}⚠ {text}{Colors.ENDC}")


def print_error(text: str):
    """Print error message."""
    print(f"{Colors.FAIL}✗ {text}{Colors.ENDC}")


def print_info(text: str):
    """Print info message."""
    print(f"{Colors.OKCYAN}ℹ {text}{Colors.ENDC}")


def ensure_config_dir():
    """Create config directory if it doesn't exist."""
    CONFIG_DIR.mkdir(mode=0o700, exist_ok=True)
    # Set restrictive permissions on existing directory
    if CONFIG_DIR.exists():
        os.chmod(CONFIG_DIR, 0o700)


def load_config() -> Dict:
    """Load existing configuration."""
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE) as f:
            return json.load(f)
    return {
        "version": "1.1",
        "providers": {},
        "task_mappings": {},
        "preferences": {
            "cost_optimization": "balanced",
            "default_provider": None
        }
    }


def save_config(config: Dict):
    """Save configuration to file."""
    ensure_config_dir()
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)
    os.chmod(CONFIG_FILE, 0o600)


def save_api_key(provider: str, key: str, base_url: str = None):
    """Safely store API key."""
    ensure_config_dir()

    # Load existing keys
    keys = {}
    if API_KEYS_FILE.exists():
        with open(API_KEYS_FILE) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    keys[k.strip()] = v.strip()

    # Add new key
    env_key = f"{provider.upper()}_API_KEY"
    keys[env_key] = key
    if base_url:
        url_key = f"{provider.upper()}_BASE_URL"
        keys[url_key] = base_url

    # Save with restrictive permissions
    with open(API_KEYS_FILE, 'w') as f:
        f.write("# Model Router API Keys\n")
        f.write("# DO NOT commit to version control\n")
        f.write("# Permissions: 600 (owner read/write only)\n\n")
        for k, v in keys.items():
            f.write(f"{k}={v}\n")

    os.chmod(API_KEYS_FILE, 0o600)


def prompt_provider_setup() -> Dict:
    """Guide user through provider setup."""
    print_header("AI Provider Configuration")

    config = load_config()

    # Available providers with descriptions
    providers = {
        "anthropic": {
            "name": "Anthropic (Claude)",
            "description": "Excellent for coding, reasoning, and creative writing",
            "models": ["claude-opus-4-5", "claude-sonnet-4-5", "claude-haiku-4-5"],
            "key_format": "sk-ant-...",
            "help_url": "https://console.anthropic.com/settings/keys"
        },
        "openai": {
            "name": "OpenAI (GPT)",
            "description": "Great for tools, function calling, and o1 reasoning",
            "models": ["gpt-4o", "gpt-4o-mini", "o1-mini", "o1-preview"],
            "key_format": "sk-proj-...",
            "help_url": "https://platform.openai.com/api-keys"
        },
        "gemini": {
            "name": "Google Gemini",
            "description": "Fast multimodal with huge context (up to 2M tokens)",
            "models": ["gemini-2.0-flash", "gemini-1.5-pro", "gemini-1.5-flash"],
            "key_format": "AIza...",
            "help_url": "https://aistudio.google.com/app/apikey"
        },
        "moonshot": {
            "name": "Moonshot (Chinese LLM)",
            "description": "Optimized for Chinese language tasks",
            "models": ["moonshot-v1-8k", "moonshot-v1-32k", "moonshot-v1-128k"],
            "key_format": "sk-...",
            "help_url": "https://platform.moonshot.cn/console/api-keys"
        },
        "zai": {
            "name": "Z.ai (GLM Proxy)",
            "description": "Cost-effective proxy for GLM models",
            "models": ["glm-4.5-air", "glm-4.7"],
            "key_format": "Various formats",
            "help_url": "https://api.z.ai"
        },
        "glm": {
            "name": "GLM (Zhipu AI Direct)",
            "description": "Direct access to Zhipu AI's GLM models",
            "models": ["glm-4-flash", "glm-4-plus", "glm-4-0520"],
            "key_format": "ID.secret",
            "help_url": "https://open.bigmodel.cn/usercenter/apikeys"
        }
    }

    print("Available providers:\n")
    for i, (key, info) in enumerate(providers.items(), 1):
        status = f"{Colors.OKGREEN}✓ Configured{Colors.ENDC}" if key in config.get("providers", {}) else "○ Not configured"
        print(f"  {i}. {Colors.BOLD}{info['name']}{Colors.ENDC} - {info['description']}")
        print(f"     Models: {', '.join(info['models'])}")
        print(f"     Status: {status}\n")

    print(f"  {Colors.BOLD}0. Skip provider setup{Colors.ENDC}")
    print()

    choice = input(f"{Colors.OKCYAN}Select a provider to configure (0-6): {Colors.ENDC}").strip()

    if choice == "0":
        return config

    try:
        provider_idx = int(choice) - 1
        provider_keys = list(providers.keys())

        if 0 <= provider_idx < len(provider_keys):
            provider = provider_keys[provider_idx]
            info = providers[provider]

            print_header(f"Configure {info['name']}")

            print(f"\n{Colors.BOLD}Get your API key:{Colors.ENDC}")
            print(f"  Visit: {Colors.UNDERLINE}{info['help_url']}{Colors.ENDC}")
            print(f"  Key format: {info['key_format']}")
            print()

            # Prompt for API key with hidden input
            api_key = getpass.getpass(f"{Colors.OKCYAN}Enter API key (input hidden): {Colors.ENDC}").strip()

            if not api_key:
                print_warning("No API key entered. Skipping.")
                return config

            # Optional base URL for some providers
            base_url = None
            if provider in ["openai", "moonshot", "glm"]:
                default_url = {
                    "openai": "https://api.openai.com/v1",
                    "moonshot": "https://api.moonshot.cn/v1",
                    "glm": "https://open.bigmodel.cn/api/paas/v4"
                }.get(provider)

                custom_url = input(f"{Colors.OKCYAN}Base URL [default: {default_url}]: {Colors.ENDC}").strip()
                base_url = custom_url if custom_url else default_url

            # Save API key securely
            save_api_key(provider, api_key, base_url)

            # Update config
            if "providers" not in config:
                config["providers"] = {}
            config["providers"][provider] = {
                "configured": True,
                "models": info["models"],
                "base_url": base_url
            }

            save_config(config)
            print_success(f"{info['name']} configured successfully!")

            # Ask to configure another provider
            another = input(f"\n{Colors.OKCYAN}Configure another provider? (y/N): {Colors.ENDC}").strip().lower()
            if another == 'y':
                return prompt_provider_setup()

    except (ValueError, IndexError):
        print_error("Invalid selection.")

    return config


def prompt_task_mappings(config: Dict) -> Dict:
    """Configure task-to-model mappings."""
    print_header("Task-to-Model Mapping")

    print("Customize which models are used for different task types.\n")
    print("Press Enter to use the recommended default, or type a custom model.\n")

    # Default mappings
    defaults = {
        "simple": {
            "description": "Quick queries, facts, weather (1-2 prompts)",
            "recommended": "glm-4.5-air",
            "alternatives": ["claude-haiku-4-5", "gpt-4o-mini", "gemini-1.5-flash"]
        },
        "coding": {
            "description": "Debug, refactor, build features",
            "recommended": "claude-sonnet-4-5",
            "alternatives": ["gpt-4o", "glm-4.7", "gemini-1.5-pro"]
        },
        "research": {
            "description": "Deep analysis, synthesis, comparisons",
            "recommended": "claude-sonnet-4-5",
            "alternatives": ["gpt-4o", "gemini-1.5-pro", "claude-opus-4-5"]
        },
        "creative": {
            "description": "Writing, brainstorming, ideation",
            "recommended": "claude-opus-4-5",
            "alternatives": ["gpt-4o", "gemini-1.5-pro"]
        },
        "math": {
            "description": "Calculations, equations, logic",
            "recommended": "o1-mini",
            "alternatives": ["claude-sonnet-4-5", "gemini-1.5-pro"]
        },
        "vision": {
            "description": "Image analysis, multimodal",
            "recommended": "gemini-1.5-flash",
            "alternatives": ["gpt-4o", "claude-opus-4-5"]
        },
        "chinese": {
            "description": "Chinese language tasks",
            "recommended": "glm-4.7",
            "alternatives": ["moonshot-v1-32k", "gemini-1.5-pro"]
        },
        "long_context": {
            "description": "Very long documents (100k+ tokens)",
            "recommended": "gemini-1.5-pro",
            "alternatives": ["moonshot-v1-128k", "claude-sonnet-4-5"]
        }
    }

    mappings = {}

    for task_type, info in defaults.items():
        print(f"\n{Colors.BOLD}Task: {task_type.upper()}{Colors.ENDC}")
        print(f"  Description: {info['description']}")
        print(f"  Recommended: {Colors.OKGREEN}{info['recommended']}{Colors.ENDC}")
        print(f"  Alternatives: {', '.join(info['alternatives'])}")

        choice = input(f"\n  Model for {task_type} [{info['recommended']}]: ").strip()
        mappings[task_type] = choice if choice else info['recommended']

    config["task_mappings"] = mappings
    save_config(config)

    print_success("Task mappings configured!")
    return config


def prompt_preferences(config: Dict) -> Dict:
    """Configure user preferences."""
    print_header("Preferences")

    print("\nCost Optimization Level:")
    print("  1. Aggressive - Always use cheapest model")
    print("  2. Balanced - Consider cost vs quality (recommended)")
    print("  3. Quality - Use best model regardless of cost")

    cost_choice = input(f"\n{Colors.OKCYAN}Select cost optimization (1-3) [2]: {Colors.ENDC}").strip()
    cost_levels = {"1": "aggressive", "2": "balanced", "3": "quality"}
    config["preferences"]["cost_optimization"] = cost_levels.get(cost_choice, "balanced")

    # Set default provider
    providers = list(config.get("providers", {}).keys())
    if providers:
        print(f"\n{Colors.BOLD}Available providers:{Colors.ENDC}")
        for i, p in enumerate(providers, 1):
            print(f"  {i}. {p}")

        default_choice = input(f"\n{Colors.OKCYAN}Default provider [1]: {Colors.ENDC}").strip()
        try:
            idx = int(default_choice) - 1 if default_choice else 0
            if 0 <= idx < len(providers):
                config["preferences"]["default_provider"] = providers[idx]
        except ValueError:
            pass

    save_config(config)
    print_success("Preferences saved!")
    return config


def show_summary(config: Dict):
    """Display configuration summary."""
    print_header("Configuration Summary")

    print(f"\n{Colors.BOLD}Configured Providers:{Colors.ENDC}")
    providers = config.get("providers", {})
    if providers:
        for provider, info in providers.items():
            print(f"  {Colors.OKGREEN}✓{Colors.ENDC} {provider}")
    else:
        print(f"  {Colors.WARNING}No providers configured{Colors.ENDC}")

    print(f"\n{Colors.BOLD}Task Mappings:{Colors.ENDC}")
    mappings = config.get("task_mappings", {})
    if mappings:
        for task, model in mappings.items():
            print(f"  {task:15} → {Colors.OKCYAN}{model}{Colors.ENDC}")
    else:
        print(f"  {Colors.WARNING}Using default mappings{Colors.ENDC}")

    print(f"\n{Colors.BOLD}Preferences:{Colors.ENDC}")
    prefs = config.get("preferences", {})
    print(f"  Cost optimization: {prefs.get('cost_optimization', 'balanced')}")
    print(f"  Default provider: {prefs.get('default_provider', 'None')}")

    print(f"\n{Colors.BOLD}Configuration Files:{Colors.ENDC}")
    print(f"  Config: {CONFIG_FILE}")
    print(f"  API Keys: {API_KEYS_FILE}")
    print(f"  Permissions: 600 (owner read/write only)")


def main():
    """Main setup wizard flow."""
    print_header("Model Router Setup Wizard v1.1")

    print("This wizard will help you:")
    print("  • Configure AI provider API keys securely")
    print("  • Set up task-to-model mappings")
    print("  • Customize your routing preferences")
    print()
    print(f"{Colors.WARNING}Your API keys will be stored locally with restrictive permissions (600).{Colors.ENDC}")
    print(f"{Colors.WARNING}Never commit your API keys to version control.{Colors.ENDC}")

    input(f"\n{Colors.OKCYAN}Press Enter to continue...{Colors.ENDC}")

    config = load_config()

    # Step 1: Provider setup
    config = prompt_provider_setup(config)

    # Step 2: Task mappings
    another = input(f"\n{Colors.OKCYAN}Configure task-to-model mappings? (Y/n): {Colors.ENDC}").strip().lower()
    if another != 'n':
        config = prompt_task_mappings(config)

    # Step 3: Preferences
    another = input(f"\n{Colors.OKCYAN}Configure preferences? (Y/n): {Colors.ENDC}").strip().lower()
    if another != 'n':
        config = prompt_preferences(config)

    # Show summary
    show_summary(config)

    print_header("Setup Complete!")
    print_success("Your Model Router is now configured.")
    print()
    print("Next steps:")
    print("  1. Test your configuration: python3 classify_task.py \"your task\"")
    print("  2. Run the router for recommendations")
    print("  3. Customize mappings anytime by editing: " + str(CONFIG_FILE))
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.WARNING}Setup cancelled.{Colors.ENDC}")
        sys.exit(0)
    except Exception as e:
        print_error(f"An error occurred: {e}")
        sys.exit(1)

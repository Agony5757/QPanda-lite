"""Example: Using QPanda-lite configuration management system.

This example demonstrates how to use the new config module to manage
quantum cloud platform configurations.
"""

from qpandalite.config import (
    load_config,
    save_config,
    get_platform_config,
    validate_config,
    update_platform_config,
    create_default_config,
    get_originq_config,
    get_quafu_config,
    get_ibm_config,
    DEFAULT_CONFIG,
)


def example_1_create_default_config():
    """Example 1: Create default configuration file."""
    print("=" * 60)
    print("Example 1: Create default configuration")
    print("=" * 60)
    
    # Create default config at ~/.qpandalite/qpandalite.yml
    create_default_config()
    print("✓ Default configuration created at ~/.qpandalite/qpandalite.yml")
    print()


def example_2_load_and_modify():
    """Example 2: Load, modify and save configuration."""
    print("=" * 60)
    print("Example 2: Load, modify and save configuration")
    print("=" * 60)
    
    # Load current configuration
    config = load_config()
    print("Current config:")
    print(f"  Profiles: {list(config.keys())}")
    
    # Modify configuration
    config["default"]["originq"]["token"] = "your_originq_token_here"
    config["default"]["originq"]["submit_url"] = "https://api.originq.com/submit"
    config["default"]["originq"]["query_url"] = "https://api.originq.com/query"
    
    config["default"]["quafu"]["token"] = "your_quafu_token_here"
    
    config["default"]["ibm"]["token"] = "your_ibm_token_here"
    config["default"]["ibm"]["proxy"] = {
        "http": "http://proxy.example.com:8080",
        "https": "https://proxy.example.com:8080",
    }
    
    # Save configuration
    save_config(config)
    print("✓ Configuration updated and saved")
    print()


def example_3_get_platform_config():
    """Example 3: Get platform-specific configuration."""
    print("=" * 60)
    print("Example 3: Get platform configuration")
    print("=" * 60)
    
    # Get OriginQ configuration
    originq = get_platform_config("originq")
    print(f"OriginQ token: {originq.get('token', 'Not set')}")
    
    # Get Quafu configuration
    quafu = get_platform_config("quafu")
    print(f"Quafu token: {quafu.get('token', 'Not set')}")
    
    # Get IBM configuration
    ibm = get_platform_config("ibm")
    print(f"IBM token: {ibm.get('token', 'Not set')}")
    if ibm.get("proxy", {}).get("http"):
        print(f"IBM proxy: {ibm['proxy']['http']}")
    print()


def example_4_convenience_functions():
    """Example 4: Use convenience functions."""
    print("=" * 60)
    print("Example 4: Convenience functions")
    print("=" * 60)
    
    # These are shorthand for get_platform_config()
    originq = get_originq_config()
    quafu = get_quafu_config()
    ibm = get_ibm_config()
    
    print(f"OriginQ: {originq.get('token', 'Not set')}")
    print(f"Quafu: {quafu.get('token', 'Not set')}")
    print(f"IBM: {ibm.get('token', 'Not set')}")
    print()


def example_5_multiple_profiles():
    """Example 5: Work with multiple profiles."""
    print("=" * 60)
    print("Example 5: Multiple profiles")
    print("=" * 60)
    
    # Add a 'prod' profile
    update_platform_config("originq", {
        "token": "prod_originq_token",
        "submit_url": "https://prod.originq.com/submit",
        "query_url": "https://prod.originq.com/query",
    }, profile="prod")
    
    update_platform_config("quafu", {
        "token": "prod_quafu_token",
    }, profile="prod")
    
    # Get configuration from different profiles
    default_originq = get_platform_config("originq", profile="default")
    prod_originq = get_platform_config("originq", profile="prod")
    
    print(f"Default OriginQ token: {default_originq['token']}")
    print(f"Prod OriginQ token: {prod_originq['token']}")
    print()


def example_6_validate_config():
    """Example 6: Validate configuration."""
    print("=" * 60)
    print("Example 6: Validate configuration")
    print("=" * 60)
    
    # Validate current configuration
    errors = validate_config()
    
    if errors:
        print("Configuration errors found:")
        for error in errors:
            print(f"  - {error}")
    else:
        print("✓ Configuration is valid")
    print()


def example_7_environment_variable():
    """Example 7: Use environment variable for active profile."""
    print("=" * 60)
    print("Example 7: Environment variable QPANDALITE_PROFILE")
    print("=" * 60)
    
    print("Set QPANDALITE_PROFILE environment variable to switch profiles:")
    print("  export QPANDALITE_PROFILE=prod")
    print("  python your_script.py")
    print()
    print("Or in Python:")
    print("  import os")
    print("  os.environ['QPANDALITE_PROFILE'] = 'prod'")
    print()


def main():
    """Run all examples."""
    print("\n" + "=" * 60)
    print("QPanda-lite Configuration Management Examples")
    print("=" * 60 + "\n")
    
    # Note: These examples create/modify ~/.qpandalite/qpandalite.yml
    # Uncomment the ones you want to run
    
    # example_1_create_default_config()
    # example_2_load_and_modify()
    # example_3_get_platform_config()
    # example_4_convenience_functions()
    # example_5_multiple_profiles()
    # example_6_validate_config()
    example_7_environment_variable()
    
    print("=" * 60)
    print("Examples completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()

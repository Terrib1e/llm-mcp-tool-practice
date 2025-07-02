"""
Setup and Installation Guide for MCP & Function Calling Learning Project

This script helps you set up your Python environment and install all necessary
dependencies to start learning about MCP servers and function calling with LLMs.
"""

import subprocess
import sys
import os
from pathlib import Path


def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"Error: {e.stderr}")
        return False


def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    print(f"🐍 Python version: {version.major}.{version.minor}.{version.micro}")

    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8 or higher is required")
        return False

    print("✅ Python version is compatible")
    return True


def create_virtual_environment():
    """Create a Python virtual environment"""
    venv_path = "venv"

    if os.path.exists(venv_path):
        print("📦 Virtual environment already exists")
        return True

    return run_command(f"{sys.executable} -m venv {venv_path}", "Creating virtual environment")


def get_activation_command():
    """Get the command to activate the virtual environment"""
    if os.name == 'nt':  # Windows
        return "venv\\Scripts\\activate"
    else:  # Unix/Linux/macOS
        return "source venv/bin/activate"


def install_requirements():
    """Install Python packages from requirements.txt"""
    pip_command = "venv\\Scripts\\pip" if os.name == 'nt' else "venv/bin/pip"

    if not os.path.exists("requirements.txt"):
        print("❌ requirements.txt not found")
        return False

    return run_command(f"{pip_command} install -r requirements.txt", "Installing Python packages")


def create_env_template():
    """Create a .env template file"""
    env_content = """# Environment Variables for MCP & Function Calling Learning
# Copy this to .env and fill in your actual API keys

# OpenAI API Key (for OpenAI function calling examples)
OPENAI_API_KEY=your_openai_api_key_here

# Anthropic API Key (for Claude function calling examples)
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Optional: Other API keys for advanced examples
# WEATHER_API_KEY=your_weather_api_key_here
# DATABASE_URL=your_database_connection_string_here
"""

    try:
        with open(".env.template", "w") as f:
            f.write(env_content)
        print("✅ Created .env.template file")
        return True
    except Exception as e:
        print(f"❌ Failed to create .env.template: {e}")
        return False


def display_next_steps():
    """Display next steps for the user"""
    activation_cmd = get_activation_command()

    print("\n" + "="*60)
    print("🎉 Setup completed successfully!")
    print("="*60)
    print("\n📋 Next steps:")
    print(f"1. Activate the virtual environment:")
    print(f"   {activation_cmd}")
    print("\n2. Set up your API keys (optional for basic examples):")
    print("   - Copy .env.template to .env")
    print("   - Add your OpenAI and/or Anthropic API keys")
    print("\n3. Start with basic function calling:")
    print("   python 01_function_calls/basic_function_calling.py")
    print("\n4. Try the simple MCP server:")
    print("   python 02_mcp_basics/simple_mcp_server.py")
    print("\n5. Explore the examples in order:")
    print("   📁 01_function_calls/     - Basic function calling")
    print("   📁 02_mcp_basics/         - MCP fundamentals")
    print("   📁 03_mcp_servers/        - Advanced MCP servers")
    print("\n💡 Tips:")
    print("   - Read the README.md files in each directory")
    print("   - Start with the basic examples and work your way up")
    print("   - Experiment with modifying the code")
    print("   - Check the requirements.txt for all available packages")


def main():
    """Main setup function"""
    print("🚀 MCP & Function Calling Learning Project Setup")
    print("="*50)

    # Check Python version
    if not check_python_version():
        return

    # Create virtual environment
    if not create_virtual_environment():
        return

    # Install requirements
    if not install_requirements():
        print("⚠️  Package installation failed. You may need to install manually:")
        print(f"   {get_activation_command()}")
        print("   pip install -r requirements.txt")

    # Create environment template
    create_env_template()

    # Show next steps
    display_next_steps()


if __name__ == "__main__":
    main()

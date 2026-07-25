#!/bin/bash
# Installation script for Meanwhile - Toronto Edition

set -e

echo "=== Meanwhile - Toronto Edition Installation ==="
echo

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
REQUIRED_VERSION="3.11"

echo "Checking Python version..."
echo "Found: Python $PYTHON_VERSION"
echo "Required: Python $REQUIRED_VERSION or higher"
echo

# Make the script executable
echo "Making meanwhile.py executable..."
chmod +x meanwhile.py

# Ask if user wants to create symlink
echo
read -p "Create symlink in ~/.local/bin/meanwhile? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]
then
    mkdir -p ~/.local/bin
    ln -sf "$PWD/meanwhile.py" ~/.local/bin/meanwhile
    echo "✓ Symlink created: ~/.local/bin/meanwhile"
    echo
    echo "Make sure ~/.local/bin is in your PATH:"
    echo "  export PATH=\"\$HOME/.local/bin:\$PATH\""
fi

# Ask about Tavily API key
echo
read -p "Do you have a Tavily API key? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]
then
    echo
    read -p "Enter your Tavily API key: " API_KEY

    # Ask where to save it
    echo
    echo "Where would you like to save the API key?"
    echo "1) ~/.env (recommended)"
    echo "2) ~/dev/.env"
    echo "3) Show export command (manual setup)"
    read -p "Choice (1-3): " -n 1 -r
    echo

    case $REPLY in
        1)
            echo "TAVILY_API_KEY=$API_KEY" >> ~/.env
            echo "✓ API key saved to ~/.env"
            ;;
        2)
            mkdir -p ~/dev
            echo "TAVILY_API_KEY=$API_KEY" >> ~/dev/.env
            echo "✓ API key saved to ~/dev/.env"
            ;;
        3)
            echo
            echo "Add this to your shell profile (.bashrc, .zshrc, etc.):"
            echo "  export TAVILY_API_KEY=\"$API_KEY\""
            ;;
    esac
else
    echo
    echo "No problem! Meanwhile will use RSS feeds (Fox News + Science feeds)"
    echo "You can add a Tavily API key later to enable AI-powered search."
fi

echo
echo "=== Installation Complete! ==="
echo
echo "Run meanwhile with:"
if [[ -f ~/.local/bin/meanwhile ]]; then
    echo "  meanwhile"
else
    echo "  ./meanwhile.py"
fi
echo
echo "Keyboard shortcuts:"
echo "  Click/Enter - Decode story"
echo "  t - Edit topics"
echo "  g - Edit places"
echo "  f - Focus mode"
echo "  Space - Pause"
echo "  q - Quit"
echo
echo "Configuration will be saved to: ~/.config/meanwhile/config.json"
echo

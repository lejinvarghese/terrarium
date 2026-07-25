#!/bin/bash
# Setup meanwhile as screensaver

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCREENSAVER_SCRIPT="$SCRIPT_DIR/meanwhile-screensaver.sh"

echo "=== Meanwhile Screensaver Setup ==="
echo

# Make scripts executable
chmod +x "$SCREENSAVER_SCRIPT"

echo "Choose your setup method:"
echo "1) xautolock (recommended - works with most desktop environments)"
echo "2) Manual command (run yourself when needed)"
echo
read -p "Choice (1-2): " choice

case $choice in
    1)
        # Check if xautolock is installed
        if ! command -v xautolock &> /dev/null; then
            echo
            echo "Installing xautolock..."
            sudo apt-get update && sudo apt-get install -y xautolock
        fi

        # Create autostart entry
        AUTOSTART_DIR="$HOME/.config/autostart"
        AUTOSTART_FILE="$AUTOSTART_DIR/meanwhile-screensaver.desktop"

        mkdir -p "$AUTOSTART_DIR"

        cat > "$AUTOSTART_FILE" << EOF
[Desktop Entry]
Type=Application
Name=Meanwhile Screensaver
Comment=Launch meanwhile as screensaver after 5 minutes idle
Exec=xautolock -time 5 -locker "$SCREENSAVER_SCRIPT" -detectsleep
Terminal=false
Hidden=false
X-GNOME-Autostart-enabled=true
EOF

        echo
        echo "✓ Autostart entry created: $AUTOSTART_FILE"
        echo
        echo "To activate now (will start on next login automatically):"
        echo "  xautolock -time 5 -locker \"$SCREENSAVER_SCRIPT\" -detectsleep &"
        echo
        echo "To disable later:"
        echo "  rm $AUTOSTART_FILE"
        echo "  killall xautolock"
        ;;

    2)
        echo
        echo "Manual setup:"
        echo "  Run: $SCREENSAVER_SCRIPT"
        echo
        echo "Or add to your startup applications:"
        echo "  xautolock -time 5 -locker \"$SCREENSAVER_SCRIPT\" -detectsleep &"
        ;;
esac

echo
echo "=== Disable Default Screensaver ==="
echo
echo "To prevent conflicts, disable your desktop's built-in screensaver:"
echo
echo "GNOME:"
echo "  gsettings set org.gnome.desktop.screensaver idle-activation-enabled false"
echo "  gsettings set org.gnome.desktop.session idle-delay 0"
echo
echo "KDE:"
echo "  System Settings > Screen Locking > uncheck 'Lock screen automatically'"
echo
echo "=== Interaction Notes ==="
echo
echo "Meanwhile allows clicking headlines to view summaries"
echo "Press 'q' to exit the screensaver"
echo "Keyboard input will also exit (except within meanwhile's controls)"
echo

# Ask if they want to disable GNOME screensaver now
if [ "$XDG_CURRENT_DESKTOP" = "GNOME" ] || [ "$XDG_CURRENT_DESKTOP" = "ubuntu:GNOME" ]; then
    read -p "Disable GNOME screensaver now? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        gsettings set org.gnome.desktop.screensaver idle-activation-enabled false
        gsettings set org.gnome.desktop.session idle-delay 0
        echo "✓ GNOME screensaver disabled"
    fi
fi

echo
echo "Setup complete! Log out and back in for autostart to take effect."
echo "Or run the xautolock command above to start now."

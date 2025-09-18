#!/bin/bash

# dler command completion installation script for zsh
# Compatible with Warp terminal and other modern terminals

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COMPLETION_FILE="$SCRIPT_DIR/dler.zsh"
ZSH_COMPLETION_DIR="$HOME/.zsh/completions"
ZSHRC="$HOME/.zshrc"
WARP_DIR="$HOME/.warp"

echo "Installing dler command completion for zsh..."
echo "Detecting terminal and zsh configuration..."

# Detect if running in Warp terminal
if [[ "$TERM_PROGRAM" == "WarpTerminal" ]] || [[ -d "$WARP_DIR" ]]; then
    echo "Warp terminal detected!"
    IS_WARP=true
else
    echo "Standard terminal detected"
    IS_WARP=false
fi

# Detect zsh configuration system
if [[ -L "$ZSHRC" ]]; then
    REAL_ZSHRC=$(readlink "$ZSHRC")
    echo "Detected linked zshrc: $ZSHRC -> $REAL_ZSHRC"
    ZSHRC="$REAL_ZSHRC"
fi

# Create completion directory if it doesn't exist
if [ ! -d "$ZSH_COMPLETION_DIR" ]; then
    echo "Creating completion directory: $ZSH_COMPLETION_DIR"
    mkdir -p "$ZSH_COMPLETION_DIR"
fi

# Copy completion script
echo "Copying completion script to $ZSH_COMPLETION_DIR"
cp "$COMPLETION_FILE" "$ZSH_COMPLETION_DIR/_dler"

# Configure fpath and compinit
if ! grep -q "fpath=.*completions" "$ZSHRC" 2>/dev/null; then
    echo "Adding completion configuration to $ZSHRC"
    echo "" >> "$ZSHRC"
    echo "# dler command completion" >> "$ZSHRC"
    echo "fpath=(\$HOME/.zsh/completions \$fpath)" >> "$ZSHRC"
    
    # Add autoload and compinit
    if [[ "$IS_WARP" == true ]]; then
        # Warp terminal specific configuration
        echo "# Enhanced for Warp terminal" >> "$ZSHRC"
        echo "autoload -Uz compinit" >> "$ZSHRC"
        echo "compinit -u" >> "$ZSHRC"
        echo "# Force reload completions in new Warp windows" >> "$ZSHRC"
        echo "if [[ \$TERM_PROGRAM == \"WarpTerminal\" ]]; then" >> "$ZSHRC"
        echo "    rehash" >> "$ZSHRC"
        echo "    compinit -u" >> "$ZSHRC"
        echo "    # Ensure dler completion is registered" >> "$ZSHRC"
        echo "    if type _dler &>/dev/null; then" >> "$ZSHRC"
        echo "        compdef _dler dler" >> "$ZSHRC"
        echo "    fi" >> "$ZSHRC"
        echo "fi" >> "$ZSHRC"
    else
        # Standard terminal configuration  
        echo "autoload -U compinit && compinit" >> "$ZSHRC"
    fi
else
    echo "Completion configuration already exists in $ZSHRC"
    
    # Check if Warp-specific config exists for existing installations
    if [[ "$IS_WARP" == true ]] && ! grep -q "rehash" "$ZSHRC" 2>/dev/null; then
        echo "Adding enhanced Warp compatibility to existing configuration"
        echo "" >> "$ZSHRC"
        echo "# Enhanced Warp terminal compatibility for completions" >> "$ZSHRC"
        echo "if [[ \$TERM_PROGRAM == \"WarpTerminal\" ]]; then" >> "$ZSHRC"
        echo "    rehash" >> "$ZSHRC"
        echo "    compinit -u" >> "$ZSHRC"
        echo "    # Ensure dler completion is registered" >> "$ZSHRC"
        echo "    if type _dler &>/dev/null; then" >> "$ZSHRC"
        echo "        compdef _dler dler" >> "$ZSHRC"
        echo "    fi" >> "$ZSHRC"
        echo "fi" >> "$ZSHRC"
    fi
fi

echo ""
echo "Installation completed!"
echo ""

if [[ "$IS_WARP" == true ]]; then
    echo "=== Warp Terminal Setup ==="
    echo "Configuration applied for automatic completion loading."
    echo "To enable completion:"
    echo "1. ✅ Restart Warp terminal (strongly recommended)"
    echo "2. ✅ Or open a new tab/session"
    echo "3. ❌ Manual 'zsh' command should no longer be needed!"
    echo ""
    echo "Enhanced Warp features enabled:"
    echo "- Automatic completion loading on new windows"
    echo "- Force rehash for immediate availability"
    echo "- Optimized compinit for Warp"
else
    echo "=== Standard Terminal Setup ==="
    echo "To enable completion, run one of the following:"
    echo "1. Restart your terminal"
    echo "2. Or run: source ~/.zshrc"
    echo "3. Or run: exec zsh"
fi

echo ""
echo "After setup, you can use tab completion with the 'dler' command:"
echo "  dler -d <TAB>              # 补全目录"
echo "  dler -o <TAB>              # 补全文件路径"
echo "  dler --segment-size <TAB>  # 补全分片大小选项"
echo "  dler <TAB>                 # 补全所有可用选项"
echo ""

if [[ "$IS_WARP" == true ]]; then
    echo "Warp-specific tips:"
    echo "- Warp supports advanced completion with descriptions"
    echo "- Use Ctrl+Space for completion menu if Tab doesn't work"
    echo "- Check Warp Settings > Features > Completions if issues persist"
else
    echo "If completion doesn't work immediately, try running: compinit"
fi

echo ""
echo "Happy coding! 🎉"
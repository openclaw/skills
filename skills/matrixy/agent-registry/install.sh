#!/bin/bash
# Agent Registry Skill Installer
# Installs the agent-registry skill to your Claude Code skills directory

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${CYAN}"
echo "╔══════════════════════════════════════════════════════════╗"
echo "║       Agent Registry Skill Installer                     ║"
echo "║  Reduce agent token overhead by ~95%                     ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Determine installation location
if [ "$1" == "--project" ] || [ "$1" == "-p" ]; then
    INSTALL_DIR=".claude/skills/agent-registry"
    echo -e "${YELLOW}Installing to project-level: ${INSTALL_DIR}${NC}"
else
    INSTALL_DIR="$HOME/.claude/skills/agent-registry"
    echo -e "${GREEN}Installing to user-level: ${INSTALL_DIR}${NC}"
fi

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Create target directory
echo -e "\n${CYAN}Creating skill directory...${NC}"
mkdir -p "$INSTALL_DIR"
mkdir -p "$INSTALL_DIR/scripts"
mkdir -p "$INSTALL_DIR/references"
mkdir -p "$INSTALL_DIR/agents"

# Copy files
echo -e "${CYAN}Copying skill files...${NC}"

cp "$SCRIPT_DIR/SKILL.md" "$INSTALL_DIR/"
cp "$SCRIPT_DIR/scripts/"*.py "$INSTALL_DIR/scripts/"
chmod +x "$INSTALL_DIR/scripts/"*.py

# Create empty registry if it doesn't exist
if [ ! -f "$INSTALL_DIR/references/registry.json" ]; then
    echo '{"version": 1, "agents": [], "stats": {"total_agents": 0, "total_tokens": 0}}' > "$INSTALL_DIR/references/registry.json"
fi

# Install Python dependencies
echo -e "\n${CYAN}Installing Python dependencies...${NC}"
if command -v pip3 &> /dev/null; then
    pip3 install questionary --quiet
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ questionary installed${NC}"
    else
        echo -e "${YELLOW}Warning: Failed to install questionary. Interactive selection will use fallback mode.${NC}"
        echo -e "${YELLOW}  You can install it manually with: pip3 install questionary${NC}"
    fi
else
    echo -e "${YELLOW}Warning: pip3 not found. Interactive selection will use fallback mode.${NC}"
    echo -e "${YELLOW}  Please install questionary manually: pip3 install questionary${NC}"
fi

echo -e "\n${GREEN}✓ Skill installed successfully!${NC}"
echo ""
echo -e "${CYAN}Next steps:${NC}"
echo ""
echo "1. Run the migration script to move your agents to the registry:"
echo -e "   ${YELLOW}cd $INSTALL_DIR && python scripts/init_registry.py${NC}"
echo ""
echo "2. After migration, Claude Code will use lazy loading for agents"
echo ""
echo "3. Verify with:"
echo -e "   ${YELLOW}cd $INSTALL_DIR && python scripts/list_agents.py${NC}"
echo ""
echo -e "${GREEN}Installation complete!${NC}"

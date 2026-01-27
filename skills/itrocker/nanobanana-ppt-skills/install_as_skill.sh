#!/bin/bash

##############################################################################
# PPT Generator Pro - Claude Code Skill 安装脚本
#
# 功能：
# 1. 自动创建 Skill 目录
# 2. 复制所有必要文件
# 3. 安装 Python 依赖
# 4. 引导配置 API 密钥
#
# 使用方法：
#   bash install_as_skill.sh
##############################################################################

set -e  # 遇到错误立即退出

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印函数
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_header() {
    echo ""
    echo "========================================"
    echo "$1"
    echo "========================================"
    echo ""
}

# 检查命令是否存在
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# 主函数
main() {
    print_header "PPT Generator Pro - Claude Code Skill 安装"

    # 1. 确定 Skill 目录
    SKILL_DIR="$HOME/.claude/skills/ppt-generator"
    print_info "目标目录: $SKILL_DIR"

    # 2. 检查是否已存在
    if [ -d "$SKILL_DIR" ]; then
        print_warning "Skill 目录已存在: $SKILL_DIR"
        read -p "是否覆盖安装？(y/N) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            print_info "安装已取消"
            exit 0
        fi
        print_info "删除旧版本..."
        rm -rf "$SKILL_DIR"
    fi

    # 3. 创建目录
    print_info "创建 Skill 目录..."
    mkdir -p "$SKILL_DIR"
    print_success "目录已创建"

    # 4. 复制文件
    print_info "复制项目文件..."

    # 获取当前脚本所在目录（即项目根目录）
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

    # 复制所有必要文件
    cp -r "$SCRIPT_DIR"/* "$SKILL_DIR/"

    # 排除不需要的文件
    if [ -d "$SKILL_DIR/.git" ]; then
        rm -rf "$SKILL_DIR/.git"
    fi
    if [ -d "$SKILL_DIR/venv" ]; then
        rm -rf "$SKILL_DIR/venv"
    fi
    if [ -d "$SKILL_DIR/outputs" ]; then
        rm -rf "$SKILL_DIR/outputs"
    fi
    if [ -f "$SKILL_DIR/.env" ]; then
        rm "$SKILL_DIR/.env"
    fi

    print_success "文件复制完成"

    # 5. 检查 Python
    print_info "检查 Python 环境..."
    if ! command_exists python3; then
        print_error "未找到 Python 3，请先安装 Python 3.8+"
        exit 1
    fi

    PYTHON_VERSION=$(python3 --version)
    print_success "Python 已安装: $PYTHON_VERSION"

    # 6. 检查 pip
    if ! command_exists pip3 && ! command_exists pip; then
        print_error "未找到 pip，请先安装 pip"
        exit 1
    fi
    print_success "pip 已安装"

    # 7. 安装 Python 依赖
    print_info "安装 Python 依赖..."
    cd "$SKILL_DIR"

    # 尝试使用 pip3，如果不存在则使用 pip
    if command_exists pip3; then
        pip3 install -q google-genai pillow python-dotenv
    else
        pip install -q google-genai pillow python-dotenv
    fi

    print_success "Python 依赖安装完成"

    # 8. 检查 FFmpeg（可选）
    print_info "检查 FFmpeg（视频功能需要）..."
    if command_exists ffmpeg; then
        FFMPEG_VERSION=$(ffmpeg -version | head -n 1)
        print_success "FFmpeg 已安装: $FFMPEG_VERSION"
    else
        print_warning "FFmpeg 未安装，视频功能将不可用"
        print_info "安装方法:"
        print_info "  macOS:  brew install ffmpeg"
        print_info "  Ubuntu: sudo apt-get install ffmpeg"
    fi

    # 9. 配置 API 密钥
    print_header "配置 API 密钥"

    print_info "PPT Generator Pro 需要以下 API 密钥："
    print_info "  1. GEMINI_API_KEY (必需) - Google AI API"
    print_info "  2. KLING_ACCESS_KEY (可选) - 可灵 AI Access Key"
    print_info "  3. KLING_SECRET_KEY (可选) - 可灵 AI Secret Key"
    echo ""

    # 检查是否有 .env.example
    if [ -f "$SKILL_DIR/.env.example" ]; then
        print_info "创建 .env 文件..."
        cp "$SKILL_DIR/.env.example" "$SKILL_DIR/.env"
        print_success ".env 文件已创建"
        echo ""
        print_warning "请编辑 .env 文件，填入你的 API 密钥："
        print_info "  nano $SKILL_DIR/.env"
        print_info "  或"
        print_info "  code $SKILL_DIR/.env"
    else
        print_warning "未找到 .env.example 文件"
        print_info "请手动创建 $SKILL_DIR/.env 文件"
    fi

    # 10. 完成
    print_header "安装完成！"

    print_success "PPT Generator Pro 已成功安装为 Claude Code Skill"
    echo ""
    print_info "安装位置: $SKILL_DIR"
    echo ""
    print_info "下一步："
    print_info "  1. 配置 API 密钥（编辑 .env 文件）"
    print_info "     nano $SKILL_DIR/.env"
    echo ""
    print_info "  2. 在 Claude Code 中使用："
    print_info "     /ppt-generator-pro"
    echo ""
    print_info "  3. 或直接告诉 Claude："
    print_info "     \"我想基于以下文档生成一个 5 页的 PPT\""
    echo ""
    print_info "详细文档："
    print_info "  - Skill 使用指南: $SKILL_DIR/SKILL.md"
    print_info "  - 项目文档: $SKILL_DIR/README.md"
    print_info "  - 架构说明: $SKILL_DIR/ARCHITECTURE.md"
    echo ""
    print_success "祝使用愉快！ 🎉"
    echo ""
}

# 错误处理
trap 'print_error "安装过程中发生错误"; exit 1' ERR

# 运行主函数
main

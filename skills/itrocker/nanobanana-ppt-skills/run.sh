#!/bin/bash

# PPT生成器启动脚本
# 自动激活虚拟环境并设置API密钥

# 设置项目根目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 激活虚拟环境
source "$SCRIPT_DIR/venv/bin/activate"

# API密钥配置（优先级顺序）
# 1. 系统环境变量（最高优先级）
# 2. .env 文件（备用方案）

if [ -z "$GEMINI_API_KEY" ]; then
    # 系统环境变量未设置，尝试从 .env 文件加载
    if [ -f "$SCRIPT_DIR/.env" ]; then
        echo "📌 从 .env 文件加载API密钥"
        export $(cat "$SCRIPT_DIR/.env" | grep -v '^#' | xargs)
    else
        echo "❌ 错误: API密钥未配置"
        echo ""
        echo "请选择以下任一方式配置API密钥："
        echo ""
        echo "方式1（推荐）: 系统环境变量"
        echo "  echo 'export GEMINI_API_KEY=\"your-key\"' >> ~/.zshrc"
        echo "  source ~/.zshrc"
        echo ""
        echo "方式2: .env 文件"
        echo "  cp .env.example .env"
        echo "  编辑 .env 文件并填入您的API密钥"
        echo ""
        exit 1
    fi
else
    echo "✅ 使用系统环境变量中的API密钥"
fi

# 最终检查
if [ -z "$GEMINI_API_KEY" ]; then
    echo "❌ 错误: GEMINI_API_KEY 仍未设置"
    exit 1
fi

# 运行Python脚本，传递所有参数
python "$SCRIPT_DIR/generate_ppt.py" "$@"

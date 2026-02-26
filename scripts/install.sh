#!/bin/bash
# 微博发布技能安装脚本

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"

echo "========================================"
echo "微博发布技能 - 安装脚本"
echo "========================================"
echo ""

# 检查 Python
echo "1. 检查 Python 环境..."
if ! command -v python3 &> /dev/null; then
    echo "✗ 未找到 Python3，请先安装 Python 3.8+"
    exit 1
fi
PYTHON_VERSION=$(python3 --version)
echo "✓ $PYTHON_VERSION"

# 安装 Python 依赖
echo ""
echo "2. 安装 Python 依赖..."
cd "$SKILL_DIR"
pip3 install -r requirements.txt

# 安装 Playwright 浏览器
echo ""
echo "3. 安装 Playwright 浏览器（可能需要几分钟）..."
python3 -m playwright install chromium

# 创建配置文件
echo ""
echo "4. 创建配置文件..."
CONFIG_FILE="$SKILL_DIR/assets/config.json"
if [ ! -f "$CONFIG_FILE" ]; then
    cp "$SKILL_DIR/assets/config.example.json" "$CONFIG_FILE"
    echo "✓ 已创建配置文件：$CONFIG_FILE"
    echo "  请编辑此文件配置你的微博账号"
else
    echo "✓ 配置文件已存在"
fi

# 测试导入
echo ""
echo "5. 测试模块导入..."
python3 "$SCRIPT_DIR/test_import.py"

echo ""
echo "========================================"
echo "安装完成！"
echo "========================================"
echo ""
echo "下一步:"
echo "1. 编辑 assets/config.json 配置微博账号"
echo "2. 运行首次登录：python3 scripts/weibo_post.py --config assets/config.json --login-only"
echo "3. 测试发布：python3 scripts/weibo_post.py --config assets/config.json --content \"测试微博\" --visible self"
echo ""

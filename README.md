# 微博发布技能 (Weibo Poster)

🤖 使用无头浏览器模拟真人操作发布微博的自动化工具

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Playwright](https://img.shields.io/badge/playwright-1.40+-green.svg)](https://playwright.dev/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## ✨ 功能特性

- 📝 **文字发布** - 支持 140-2000 字微博
- 🖼️ **图片发布** - 最多 9 张图片一次上传
- 🎬 **视频发布** - 支持短视频上传
- 🏷️ **话题标签** - 自动添加 #话题#
- 👥 **@提及** - 支持@好友
- 🔒 **可见性** - 公开/好友圈/仅自己
- 🎭 **真人模拟** - 随机延迟、鼠标轨迹、字符级输入
- 🛡️ **反检测** - User-Agent 轮换、指纹保护、Cookie 持久化

## 🚀 快速开始

### 1. 安装

```bash
# 克隆项目
git clone https://github.com/your-username/weibo-poster.git
cd weibo-poster

# 运行安装脚本
bash scripts/install.sh
```

### 2. 配置

编辑 `assets/config.json`：

```json
{
  "account": {
    "username": "你的微博账号",
    "password": "你的微博密码"
  },
  "browser": {
    "headless": true
  }
}
```

### 3. 首次登录

```bash
source .venv/bin/activate
python scripts/weibo_post.py --config assets/config.json --login-only
```

在打开的浏览器中手动完成验证码，Cookie 会自动保存。

### 4. 发布微博

```bash
# 纯文字
python scripts/weibo_post.py --config assets/config.json --content "你好微博"

# 带图片
python scripts/weibo_post.py --config assets/config.json --content "美食分享" --images photo1.jpg photo2.jpg

# 带话题
python scripts/weibo_post.py --config assets/config.json --content "日常" --topics "生活" "日常"
```

## 📖 详细文档

- [使用指南](references/usage-guide.md)
- [反检测技巧](references/anti-detection.md)
- [页面选择器](references/selectors.md)

## 🔧 高级用法

### OpenClaw 集成

```bash
python scripts/openclaw_integration.py --action post --content "来自 OpenClaw" --output-json
```

### 定时发布

```bash
# 每天 9:00 发布
0 9 * * * cd /path/to/weibo-poster && source .venv/bin/activate && python scripts/weibo_post.py --config assets/config.json --content "早安！"
```

### 批量发布

```bash
#!/bin/bash
contents=("第一条" "第二条" "第三条")
for content in "${contents[@]}"; do
    python scripts/weibo_post.py --config assets/config.json --content "$content"
    sleep $((RANDOM % 300 + 300))  # 随机等待 5-10 分钟
done
```

## ⚠️ 注意事项

1. **遵守规范** - 遵守微博社区规范，不要发布违规内容
2. **频率控制** - 建议发布间隔 > 5 分钟，避免被限流
3. **账号安全** - 不要频繁切换 IP，使用稳定网络
4. **Cookie 保护** - `cookies.json` 包含登录信息，不要泄露

## 🐛 故障排除

| 问题 | 解决方案 |
|------|---------|
| 登录失败 | 检查账号密码，手动登录一次 |
| 发布失败 | 检查内容是否违规，图片格式 |
| 被检测 | 增加延迟，使用代理，降低频率 |
| Cookie 过期 | 删除 `cookies.json` 重新登录 |

## 📦 依赖

- Python 3.8+
- Playwright 1.40+
- Chromium 浏览器
- 系统依赖：`atk`, `libXcomposite`, `libXdamage`, `libXrandr`, `mesa-libgbm` 等

## 📄 许可证

MIT License

## 🙏 致谢

- [Playwright](https://playwright.dev/) - 浏览器自动化工具
- [OpenClaw](https://openclaw.ai/) - AI 助手框架

## 📮 联系方式

- GitHub: https://github.com/your-username/weibo-poster
- Issues: https://github.com/your-username/weibo-poster/issues

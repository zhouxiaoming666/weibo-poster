---
name: weibo-poster
description: 使用无头浏览器模拟真人操作发布微博。支持文字、图片（最多 9 张）、视频发布，自动处理登录、验证码、反检测。使用 Playwright 实现人类行为模拟（随机延迟、鼠标轨迹、滚动）。当用户需要发布微博、管理微博账号、批量操作微博时触发此技能。
---

# 微博发布技能 (Weibo Poster)

使用无头浏览器模拟真人操作发布微博，具备反检测能力。

## 快速开始

### 安装

```bash
# 克隆技能
cd /path/to/your/skills
git clone https://github.com/your-username/weibo-poster.git

# 安装依赖
cd weibo-poster
bash scripts/install.sh
```

### 配置

1. **编辑配置文件** `assets/config.json`：

```json
{
  "account": {
    "username": "your_weibo_username",
    "password": "your_weibo_password",
    "cookie_file": "cookies.json"
  },
  "browser": {
    "headless": true,
    "user_agent": "random",
    "proxy": null
  },
  "behavior": {
    "min_delay_ms": 1000,
    "max_delay_ms": 5000,
    "scroll_before_post": true,
    "random_typing_speed": true
  }
}
```

2. **首次登录**（手动完成验证码）：

```bash
source .venv/bin/activate
python scripts/weibo_post.py --config assets/config.json --login-only
```

3. **发布微博**：

```bash
# 纯文字
python scripts/weibo_post.py --config assets/config.json --content "你好微博"

# 带图片（最多 9 张）
python scripts/weibo_post.py --config assets/config.json --content "美食分享" --images /path/to/img1.jpg /path/to/img2.jpg

# 带话题
python scripts/weibo_post.py --config assets/config.json --content "日常" --topics "生活" "日常"
```

## 核心功能

### 1. 真人行为模拟

- **随机延迟**: 操作间插入 1-5 秒随机延迟
- **鼠标轨迹**: 贝塞尔曲线模拟人类鼠标移动
- **随机滚动**: 发布前随机滚动页面
- **输入模拟**: 字符级输入，带随机停顿

### 2. 反检测措施

- **User-Agent 轮换**: 使用真实浏览器 UA
- **指纹保护**: 禁用自动化特征
- **Cookie 持久化**: 避免重复登录
- **代理支持**: 可选 IP 代理

### 3. 发布功能

- **文字微博**: 支持 140-2000 字
- **图片微博**: 最多 9 张图片
- **视频微博**: 支持短视频上传
- **话题标签**: 自动添加 #话题#
- **@提及**: 支持@好友
- **可见性**: 公开/好友圈/仅自己

## 使用示例

### 基础发布

```bash
python scripts/weibo_post.py \
  --config assets/config.json \
  --content "这是第一条微博" \
  --images image1.jpg image2.jpg
```

### 带话题发布

```bash
python scripts/weibo_post.py \
  --config assets/config.json \
  --content "今天的学习心得" \
  --topics "学习" "成长" \
  --visible public
```

### OpenClaw 集成

```bash
python scripts/openclaw_integration.py \
  --action post \
  --content "来自 OpenClaw 的微博" \
  --output-json
```

### 定时发布（配合 cron）

```bash
# 添加到 crontab，每天 9:00 发布
0 9 * * * cd /path/to/weibo-poster && source .venv/bin/activate && python scripts/weibo_post.py --config assets/config.json --content "早安！" --visible public
```

## 脚本说明

| 脚本 | 用途 |
|------|------|
| `weibo_post.py` | 主发布脚本 |
| `human_behavior.py` | 人类行为模拟工具 |
| `openclaw_integration.py` | OpenClaw 集成接口 |
| `install.sh` | 一键安装脚本 |

## 依赖

- Python 3.8+
- Playwright
- Chromium 浏览器
- 系统依赖：`atk`, `libXcomposite`, `libXdamage`, `libXrandr`, `mesa-libgbm` 等

## 注意事项

1. **首次使用**: 先运行登录脚本，手动完成验证码
2. **Cookie 保存**: 登录成功后 Cookie 会自动保存
3. **频率限制**: 建议发布间隔 > 5 分钟
4. **内容审核**: 遵守微博社区规范
5. **账号安全**: 不要频繁切换 IP

## 故障排除

### 登录失败
- 检查账号密码
- 手动登录一次保存 Cookie
- 检查是否需要短信验证

### 发布失败
- 检查内容是否违规
- 检查图片格式（JPG/PNG）
- 检查网络连接

### 被检测为机器人
- 增加延迟时间（修改 config.json）
- 使用住宅代理
- 减少发布频率

## 项目结构

```
weibo-poster/
├── SKILL.md                          # 技能文档
├── requirements.txt                  # Python 依赖
├── scripts/
│   ├── weibo_post.py                # 主发布脚本
│   ├── human_behavior.py            # 人类行为模拟
│   ├── openclaw_integration.py      # OpenClaw 集成
│   └── install.sh                   # 安装脚本
├── references/
│   ├── selectors.md                 # 微博页面选择器
│   ├── anti-detection.md            # 反检测技巧
│   └── usage-guide.md               # 使用指南
└── assets/
    └── config.example.json          # 配置模板
```

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！

## 支持

- 文档：https://github.com/your-username/weibo-poster
- 问题反馈：https://github.com/your-username/weibo-poster/issues

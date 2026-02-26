# 微博发布技能使用指南

## 首次设置

### 1. 安装依赖

```bash
cd /path/to/weibo-poster
pip install -r requirements.txt
playwright install chromium
```

### 2. 配置账号

复制配置模板并编辑：

```bash
cp assets/config.example.json assets/config.json
```

编辑 `assets/config.json`：

```json
{
  "account": {
    "username": "你的微博账号",
    "password": "你的微博密码"
  }
}
```

### 3. 首次登录

首次使用需要手动完成验证码：

```bash
# 以有头模式运行（可以看到浏览器）
python scripts/weibo_post.py --config assets/config.json --login-only
```

在打开的浏览器中：
1. 输入账号密码
2. 完成滑块验证码（如果有）
3. 登录成功后 Cookie 会自动保存
4. 关闭浏览器

### 4. 测试发布

```bash
python scripts/weibo_post.py \
  --config assets/config.json \
  --content "测试微博，请忽略" \
  --visible self
```

## 日常使用

### 发布文字微博

```bash
python scripts/weibo_post.py \
  --config assets/config.json \
  --content "今天心情不错！"
```

### 发布带图微博

```bash
python scripts/weibo_post.py \
  --config assets/config.json \
  --content "美食分享" \
  --images /path/to/photo1.jpg /path/to/photo2.jpg
```

### 发布带话题微博

```bash
python scripts/weibo_post.py \
  --config assets/config.json \
  --content "今天的收获" \
  --topics "学习" "成长" "日常"
```

### 设置可见性

```bash
# 公开（默认）
--visible public

# 仅好友可见
--visible friends

# 仅自己可见
--visible self
```

## 高级用法

### 环境变量配置

可以将敏感信息放在环境变量中：

```bash
export WEIBO_USERNAME="your_username"
export WEIBO_PASSWORD="your_password"

python scripts/weibo_post.py --content "你好微博"
```

### 批量发布

创建发布脚本：

```bash
#!/bin/bash
# batch_post.sh

contents=(
    "早安！新的一天开始了"
    "午餐时间，今天吃了..."
    "下班啦，明天继续加油"
)

for content in "${contents[@]}"; do
    python scripts/weibo_post.py \
        --config assets/config.json \
        --content "$content"
    
    # 随机等待 5-10 分钟
    sleep $((RANDOM % 300 + 300))
done
```

### 定时发布（Cron）

编辑 crontab：

```bash
crontab -e
```

添加定时任务：

```cron
# 每天早上 9 点发布
0 9 * * * cd /path/to/weibo-poster && python scripts/weibo_post.py --config assets/config.json --content "早安！"

# 每周一发布周报
0 18 * * 1 cd /path/to/weibo-poster && python scripts/weibo_post.py --config assets/config.json --content "本周工作总结..." --topics "周报"
```

## 故障排除

### 登录失败

**问题**: 登录时提示密码错误或需要验证码

**解决**:
1. 检查账号密码是否正确
2. 使用 `--login-only` 参数手动登录一次
3. 检查是否需要短信验证
4. 尝试更换网络环境

### 发布失败

**问题**: 点击发布后没有反应或提示失败

**解决**:
1. 检查内容是否包含敏感词
2. 检查图片格式（支持 JPG/PNG）
3. 检查图片大小（单张不超过 10MB）
4. 查看浏览器控制台错误信息

### 被检测为机器人

**问题**: 账号被限制或需要频繁验证

**解决**:
1. 增加延迟时间（修改 config.json 中的 `min_delay_ms` 和 `max_delay_ms`）
2. 降低发布频率（建议间隔 > 5 分钟）
3. 使用住宅代理 IP
4. 切换到有头模式运行一段时间

### Cookie 过期

**问题**: 保存的 Cookie 失效，需要重新登录

**解决**:
```bash
# 删除旧 Cookie
rm assets/cookies.json

# 重新登录
python scripts/weibo_post.py --config assets/config.json --login-only
```

## 最佳实践

### 内容策略
- ✅ 原创内容优先
- ✅ 图文并茂更吸引人
- ✅ 合理使用话题标签
- ✅ 避免敏感话题

### 发布频率
- ✅ 每天 3-5 条为宜
- ✅ 间隔时间随机化
- ✅ 避免固定时间发布
- ✅ 新账号降低频率

### 账号安全
- ✅ 使用稳定 IP
- ✅ 定期手动登录
- ✅ 不要频繁切换设备
- ✅ 遵守社区规范

## 性能优化

### 无头模式 vs 有头模式

**无头模式**（默认）:
- ✅ 资源占用少
- ✅ 运行速度快
- ❌ 调试困难

**有头模式**:
- ✅ 可以看到操作过程
- ✅ 便于调试
- ❌ 资源占用多

切换模式：
```json
{
  "browser": {
    "headless": false
  }
}
```

### 并发处理

如需同时管理多个账号，可以：

1. 创建多个配置文件
2. 使用不同浏览器上下文
3. 错开操作时间

## 扩展开发

### 添加新功能

在 `weibo_post.py` 中添加方法：

```python
async def like_weibo(self, weibo_url: str) -> bool:
    """点赞微博"""
    await self.page.goto(weibo_url)
    like_button = await self.page.wait_for_selector('span[class*="like"]')
    await self.human_sim.human_click(like_button)
    return True
```

### 自定义选择器

如果微博页面更新，在 `references/selectors.md` 中更新选择器，然后修改 `weibo_post.py` 中的 `SELECTORS` 字典。

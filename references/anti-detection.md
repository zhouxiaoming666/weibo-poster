# 反检测技巧

## 检测原理

网站检测自动化的常见方法：

### 1. WebDriver 检测
```javascript
// 检测 navigator.webdriver
if (navigator.webdriver) {
    // 是自动化浏览器
}
```

**解决方案**:
```python
await context.add_init_script("""
    Object.defineProperty(navigator, 'webdriver', {
        get: () => undefined
    });
""")
```

### 2. 自动化特征检测
```javascript
// 检测 Chrome 自动化标志
if (navigator.plugins.length === 0) {
    // 可能是无头浏览器
}
```

**解决方案**:
```python
await context.add_init_script("""
    Object.defineProperty(navigator, 'plugins', {
        get: () => [1, 2, 3, 4, 5]
    });
    Object.defineProperty(navigator, 'languages', {
        get: () => ['zh-CN', 'zh']
    });
""")
```

### 3. 行为分析
- 鼠标移动轨迹过于直线
- 点击位置过于精确
- 操作速度过于均匀
- 无阅读时间直接操作

**解决方案**: 使用 `human_behavior.py` 模拟真实行为

## Playwright 反检测配置

### 基础配置
```python
launch_args = {
    "headless": True,  # 或 False 用于调试
    "args": [
        "--disable-blink-features=AutomationControlled",
        "--no-sandbox",
        "--disable-dev-shm-usage",
        "--disable-web-security",
        "--disable-features=IsolateOrigins,site-per-process",
    ]
}
```

### 高级配置
```python
context_args = {
    "user_agent": "Mozilla/5.0 ...",  # 真实 UA
    "viewport": {"width": 1920, "height": 1080},
    "locale": "zh-CN",
    "timezone_id": "Asia/Shanghai",
    "geolocation": {"longitude": 116.4, "latitude": 39.9},
    "permissions": ["geolocation"],
}
```

## 人类行为模拟要点

### 1. 随机延迟
```python
# 操作间插入随机延迟
await asyncio.sleep(random.uniform(1.0, 5.0))
```

### 2. 鼠标轨迹
```python
# 使用贝塞尔曲线而非直线
points = generate_bezier_curve(start_x, start_y, end_x, end_y)
for point in points:
    await page.mouse.move(point[0], point[1])
```

### 3. 打字模拟
```python
# 字符级输入，带随机停顿
for char in text:
    await element.type(char)
    await asyncio.sleep(random.uniform(0.05, 0.2))
```

### 4. 滚动行为
```python
# 随机滚动，模拟阅读
for _ in range(random.randint(1, 3)):
    await page.evaluate(f"window.scrollBy(0, {random.randint(100, 500)})")
    await asyncio.sleep(random.uniform(0.5, 1.5))
```

## Cookie 管理

### 为什么重要
- 避免每次重新登录
- 减少验证码触发
- 保持会话连续性

### 保存 Cookie
```python
cookies = await context.cookies()
with open('cookies.json', 'w') as f:
    json.dump(cookies, f)
```

### 加载 Cookie
```python
with open('cookies.json', 'r') as f:
    cookies = json.load(f)
await context.add_cookies(cookies)
```

## IP 代理

### 使用场景
- 频繁操作需要切换 IP
- 账号多地登录风险
- 突破地域限制

### 配置代理
```python
proxy_config = {
    "server": "http://proxy.example.com:8080",
    "username": "user",
    "password": "pass",
}

browser = await playwright.chromium.launch(
    proxy=proxy_config
)
```

### 住宅代理推荐
- Bright Data
- Oxylabs
- Smartproxy
- IPRoyal

## 指纹保护

### 浏览器指纹
网站收集的指纹信息：
- Canvas 指纹
- WebGL 指纹
- Audio 指纹
- 字体列表
- 屏幕分辨率
- 时区

### 保护措施
```python
# 使用 playwright-stealth
from playwright_stealth import stealth_async

await stealth_async(page)
```

## 频率限制建议

| 操作 | 建议间隔 | 说明 |
|------|---------|------|
| 发布微博 | 5-10 分钟 | 避免短时间内多次发布 |
| 点赞 | 3-5 秒 | 模拟真实阅读时间 |
| 评论 | 1-2 分钟 | 需要输入内容 |
| 转发 | 30 秒 -1 分钟 | 可较快但需随机 |
| 登录 | 每天 1 次 | 使用 Cookie 保持登录 |

## 常见检测信号

### 高风险行为
- ⚠️ 24 小时内发布超过 20 条
- ⚠️ 固定时间发布（如每分钟一条）
- ⚠️ 相同内容重复发布
- ⚠️ 新账号大量操作
- ⚠️ 异地登录 + 频繁操作

### 降低风险
- ✅ 操作时间随机化
- ✅ 模拟人类阅读和停顿
- ✅ 混合多种操作（浏览、点赞、发布）
- ✅ 使用稳定 IP
- ✅ 保持 Cookie 持久化

## 调试技巧

### 检测是否被识别
```python
# 检查 webdriver 属性
is_automated = await page.evaluate("navigator.webdriver")
print(f"WebDriver 检测：{is_automated}")

# 检查 plugins
plugins = await page.evaluate("navigator.plugins.length")
print(f"Plugins 数量：{plugins}")
```

### 截图调试
```python
await page.screenshot(path='debug.png', full_page=True)
```

### 录制视频
```python
await context.start_video_record(path='debug.webm')
# ... 操作 ...
await context.stop_video_record()
```

## 应急方案

### 如果被封禁
1. 立即停止所有自动化操作
2. 等待 24-48 小时
3. 手动登录验证账号状态
4. 更换 IP 和设备指纹
5. 降低操作频率后重试

### 验证码处理
1. 暂停自动化
2. 切换到有头模式手动完成
3. 保存新 Cookie
4. 恢复自动化

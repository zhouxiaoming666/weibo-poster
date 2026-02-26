# 微博移动端选择器参考

> ⚠️ 注意：微博页面结构可能随时更新，以下选择器需要定期验证

## 登录页面 (passport.weibo.cn)

```python
SELECTORS = {
    # 输入框
    "login_username": "input[name='username']",
    "login_password": "input[name='password']",
    "login_button": "button[type='submit']",
    
    # 验证码（如果出现）
    "captcha_image": "img[class='captcha-img']",
    "captcha_input": "input[name='captcha']",
    
    # 第三方登录
    "qq_login": "a[href*='qq.com']",
    "wechat_login": "a[href*='wechat']",
}
```

## 发布页面 (m.weibo.cn/compose)

```python
SELECTORS = {
    # 文本输入
    "compose_input": "div[role='textbox']",
    "compose_placeholder": "div[placeholder*='分享']",
    
    # 图片上传
    "add_image_button": "span:contains('添加图片')",
    "image_preview": "div[class*='image-preview']",
    "image_remove": "button[class*='remove']",
    
    # 发布按钮
    "post_button": "button:contains('发布')",
    "post_button_disabled": "button:contains('发布')[disabled]",
    
    # 可见性设置
    "visibility_button": "span:contains('公开')",
    "visibility_friends": "span:contains('好友圈')",
    "visibility_self": "span:contains'仅自己')",
    
    # 话题
    "topic_input": "input[placeholder*='话题']",
    "topic_suggestion": "div[class*='topic-suggestion']",
    
    # @提及
    "mention_input": "input[placeholder*='@']",
    "mention_suggestion": "div[class*='user-suggestion']",
    
    # 表情
    "emoji_button": "span[class*='emoji']",
    "emoji_panel": "div[class*='emoji-panel']",
}
```

## 首页/时间线 (m.weibo.cn)

```python
SELECTORS = {
    # 微博卡片
    "weibo_card": "div[class*='card-wrap']",
    "weibo_content": "div[class*='weibo-content']",
    "weibo_text": "div[class*='text']",
    
    # 用户信息
    "user_avatar": "img[class*='avatar']",
    "username": "a[class*='username']",
    "verified_icon": "img[class*='verified']",
    
    # 互动按钮
    "like_button": "span[class*='like']",
    "comment_button": "span[class*='comment']",
    "repost_button": "span[class*='repost']",
    "share_button": "span[class*='share']",
    
    # 时间
    "post_time": "span[class*='time']",
}
```

## 选择器更新检查

定期检查选择器是否有效：

```python
async def check_selectors(page):
    """检查选择器是否有效"""
    await page.goto("https://m.weibo.cn")
    
    selectors_to_check = [
        "div[role='textbox']",
        "button:contains('发布')",
        "span:contains('添加图片')",
    ]
    
    for selector in selectors_to_check:
        element = await page.query_selector(selector)
        if element:
            print(f"✓ {selector}")
        else:
            print(f"✗ {selector} - 可能需要更新")
```

## 常见更新模式

微博更新时，选择器通常按以下模式变化：

1. **类名变化**: `class="old-name"` → `class="new-name"`
   - 解决：使用属性选择器或文本选择器
   
2. **结构变化**: 元素嵌套层级变化
   - 解决：使用更灵活的选择器

3. **文本变化**: 按钮文字变化
   - 解决：使用部分文本匹配 `:contains('发布')`

## 调试技巧

```python
# 获取页面所有按钮
buttons = await page.query_selector_all('button')
for btn in buttons:
    text = await btn.inner_text()
    print(f"按钮：{text}")

# 获取元素完整 HTML
element = await page.query_selector('div[role="textbox"]')
html = await element.evaluate('el => el.outerHTML')
print(html)

# 截图调试
await page.screenshot(path='debug.png')
```

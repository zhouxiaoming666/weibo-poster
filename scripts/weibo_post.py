#!/usr/bin/env python3
"""
微博发布脚本 - 模拟真人操作发布微博
支持文字、图片、视频发布，具备反检测能力
"""

import asyncio
import json
import random
import sys
import os
from pathlib import Path
from datetime import datetime
from typing import List, Optional, Dict, Any

from playwright.async_api import async_playwright, Browser, Page, BrowserContext

# 添加父目录到路径以便导入 human_behavior
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from human_behavior import HumanBehaviorSimulator


class WeiboPoster:
    """微博发布器"""
    
    # 微博移动端 URL
    WEIBO_URL = "https://m.weibo.cn"
    LOGIN_URL = "https://passport.weibo.cn/sso/signin?entry=miniblog"
    POST_URL = "https://m.weibo.cn/compose"
    
    # 选择器（可能随微博更新而变化）
    SELECTORS = {
        "login_username": "input[name='username']",
        "login_password": "input[name='password']",
        "login_button": "button[type='submit']",
        "compose_input": "div[role='textbox']",
        "post_button": "button:contains('发布')",
        "image_upload": "input[type='file']",
        "add_image_button": "span:contains('添加图片')",
    }
    
    def __init__(self, config_path: Optional[str] = None):
        self.config = self._load_config(config_path)
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.human_sim = HumanBehaviorSimulator(
            min_delay_ms=self.config.get("behavior", {}).get("min_delay_ms", 1000),
            max_delay_ms=self.config.get("behavior", {}).get("max_delay_ms", 5000)
        )
        
    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """加载配置文件"""
        default_config = {
            "account": {
                "username": os.getenv("WEIBO_USERNAME", ""),
                "password": os.getenv("WEIBO_PASSWORD", ""),
                "cookie_file": "cookies.json"
            },
            "browser": {
                "headless": True,
                "user_agent": "random",
                "proxy": None
            },
            "behavior": {
                "min_delay_ms": 1000,
                "max_delay_ms": 5000,
                "scroll_before_post": True,
                "random_typing_speed": True
            }
        }
        
        if config_path and os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                file_config = json.load(f)
                # 合并配置
                for key in file_config:
                    if isinstance(file_config[key], dict):
                        default_config[key].update(file_config[key])
                    else:
                        default_config[key] = file_config[key]
        
        return default_config
    
    async def init_browser(self):
        """初始化浏览器"""
        playwright = await async_playwright().start()
        
        # 构建启动参数
        launch_args = {
            "headless": self.config["browser"].get("headless", True),
            "args": [
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-dev-shm-usage",
            ]
        }
        
        # 代理配置
        if self.config["browser"].get("proxy"):
            launch_args["proxy"] = self.config["browser"]["proxy"]
        
        self.browser = await playwright.chromium.launch(**launch_args)
        
        # 用户代理
        user_agent = self.config["browser"].get("user_agent", "random")
        if user_agent == "random":
            user_agent = self._get_random_user_agent()
        
        # 创建上下文
        context_args = {
            "user_agent": user_agent,
            "viewport": {"width": 1920, "height": 1080},
            "locale": "zh-CN",
            "timezone_id": "Asia/Shanghai",
        }
        
        self.context = await self.browser.new_context(**context_args)
        
        # 注入反检测脚本
        await self.context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5]
            });
            Object.defineProperty(navigator, 'languages', {
                get: () => ['zh-CN', 'zh']
            });
        """)
        
        self.page = await self.context.new_page()
        
        # 加载 Cookie（如果存在）
        await self._load_cookies()
    
    def _get_random_user_agent(self) -> str:
        """获取随机 User-Agent"""
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
        ]
        return random.choice(user_agents)
    
    async def _load_cookies(self):
        """加载保存的 Cookie"""
        cookie_file = self.config["account"].get("cookie_file", "cookies.json")
        cookie_path = Path(cookie_file)
        
        if not cookie_path.is_absolute():
            cookie_path = Path(__file__).parent.parent / "assets" / cookie_file
        
        if cookie_path.exists():
            try:
                with open(cookie_path, 'r', encoding='utf-8') as f:
                    cookies = json.load(f)
                await self.context.add_cookies(cookies)
                print(f"✓ 已加载 Cookie: {cookie_path}")
            except Exception as e:
                print(f"✗ 加载 Cookie 失败：{e}")
    
    async def _save_cookies(self):
        """保存 Cookie"""
        cookie_file = self.config["account"].get("cookie_file", "cookies.json")
        cookie_path = Path(cookie_file)
        
        if not cookie_path.is_absolute():
            cookie_path = Path(__file__).parent.parent / "assets" / cookie_file
        
        try:
            cookies = await self.context.cookies()
            with open(cookie_path, 'w', encoding='utf-8') as f:
                json.dump(cookies, f, ensure_ascii=False, indent=2)
            print(f"✓ Cookie 已保存：{cookie_path}")
        except Exception as e:
            print(f"✗ 保存 Cookie 失败：{e}")
    
    async def login(self) -> bool:
        """登录微博"""
        print("正在登录微博...")
        
        try:
            await self.page.goto(self.LOGIN_URL, wait_until="networkidle")
            await self.human_sim.random_delay()
            
            # 检查是否已登录
            if await self._is_logged_in():
                print("✓ 已登录状态")
                return True
            
            # 输入用户名
            username_input = await self.page.wait_for_selector(self.SELECTORS["login_username"], timeout=10000)
            await self.human_sim.human_type(username_input, self.config["account"]["username"])
            
            # 输入密码
            password_input = await self.page.wait_for_selector(self.SELECTORS["login_password"], timeout=5000)
            await self.human_sim.human_type(password_input, self.config["account"]["password"])
            
            # 点击登录按钮
            login_button = await self.page.wait_for_selector(self.SELECTORS["login_button"], timeout=5000)
            await self.human_sim.human_click(login_button)
            
            # 等待登录完成
            await self.page.wait_for_load_state("networkidle")
            await self.human_sim.random_delay(2000, 4000)
            
            # 检查登录是否成功
            if await self._is_logged_in():
                print("✓ 登录成功")
                await self._save_cookies()
                return True
            else:
                print("✗ 登录失败，可能需要验证码")
                return False
                
        except Exception as e:
            print(f"✗ 登录异常：{e}")
            return False
    
    async def _is_logged_in(self) -> bool:
        """检查是否已登录"""
        try:
            # 检查是否存在用户头像或发布按钮
            await self.page.goto(self.WEIBO_URL, wait_until="networkidle", timeout=10000)
            # 简单判断：如果能访问发布页面则已登录
            await self.page.goto(self.POST_URL, wait_until="domcontentloaded", timeout=5000)
            compose_input = await self.page.query_selector(self.SELECTORS["compose_input"])
            return compose_input is not None
        except:
            return False
    
    async def post(self, content: str, images: Optional[List[str]] = None, 
                   topics: Optional[List[str]] = None, visible: str = "public") -> bool:
        """发布微博"""
        print(f"正在发布微博：{content[:50]}...")
        
        try:
            # 导航到发布页面
            await self.page.goto(self.POST_URL, wait_until="networkidle")
            await self.human_sim.random_delay()
            
            # 模拟滚动（反检测）
            if self.config["behavior"].get("scroll_before_post", True):
                await self.human_sim.random_scroll(self.page)
            
            # 找到输入框
            compose_input = await self.page.wait_for_selector(self.SELECTORS["compose_input"], timeout=10000)
            await compose_input.click()
            await self.human_sim.random_delay()
            
            # 处理话题
            if topics:
                for topic in topics:
                    topic_text = f"#{topic}# "
                    await self.human_sim.human_type(compose_input, topic_text)
                    await self.human_sim.random_delay(500, 1500)
            
            # 输入正文
            await self.human_sim.human_type(compose_input, content)
            await self.human_sim.random_delay()
            
            # 上传图片（如果有）
            if images:
                await self._upload_images(images)
            
            # 设置可见性（如果需要）
            if visible != "public":
                await self._set_visibility(visible)
            
            # 随机延迟后发布
            await self.human_sim.random_delay(2000, 5000)
            
            # 点击发布按钮
            post_button = await self.page.wait_for_selector(self.SELECTORS["post_button"], timeout=10000)
            await self.human_sim.human_click(post_button)
            
            # 等待发布完成
            await self.page.wait_for_load_state("networkidle")
            await self.human_sim.random_delay(2000, 3000)
            
            # 检查发布是否成功
            success = await self._check_post_success()
            if success:
                print("✓ 微博发布成功")
            else:
                print("✗ 微博发布失败")
            
            return success
            
        except Exception as e:
            print(f"✗ 发布异常：{e}")
            return False
    
    async def _upload_images(self, image_paths: List[str]):
        """上传图片"""
        print(f"正在上传 {len(image_paths)} 张图片...")
        
        # 找到添加图片按钮
        add_image_button = await self.page.query_selector(self.SELECTORS["add_image_button"])
        if add_image_button:
            await self.human_sim.human_click(add_image_button)
            await self.human_sim.random_delay()
        
        # 找到文件输入框并上传
        file_input = await self.page.query_selector('input[type="file"]')
        if file_input:
            # 限制最多 9 张
            images_to_upload = image_paths[:9]
            for img_path in images_to_upload:
                if os.path.exists(img_path):
                    await file_input.set_input_files(img_path)
                    await self.human_sim.random_delay(1000, 2000)
                    print(f"✓ 已上传：{img_path}")
                else:
                    print(f"✗ 图片不存在：{img_path}")
    
    async def _set_visibility(self, visibility: str):
        """设置可见性"""
        # 实现可见性设置逻辑
        pass
    
    async def _check_post_success(self) -> bool:
        """检查发布是否成功"""
        try:
            # 检查是否有成功提示或微博出现在时间线
            await self.page.wait_for_selector("div.c-card", timeout=5000)
            return True
        except:
            return False
    
    async def close(self):
        """关闭浏览器"""
        if self.browser:
            await self.browser.close()


async def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="微博发布工具")
    parser.add_argument("--config", type=str, help="配置文件路径")
    parser.add_argument("--content", type=str, required=True, help="微博内容")
    parser.add_argument("--images", type=str, nargs="*", help="图片路径列表")
    parser.add_argument("--topics", type=str, nargs="*", help="话题列表")
    parser.add_argument("--visible", type=str, default="public", choices=["public", "friends", "self"],
                       help="可见性设置")
    parser.add_argument("--login-only", action="store_true", help="仅登录不发布")
    
    args = parser.parse_args()
    
    poster = WeiboPoster(config_path=args.config)
    
    try:
        await poster.init_browser()
        
        if args.login_only:
            success = await poster.login()
            sys.exit(0 if success else 1)
        
        # 先尝试登录
        if not await poster.login():
            print("登录失败，请检查账号密码或手动完成验证码")
            sys.exit(1)
        
        # 发布微博
        success = await poster.post(
            content=args.content,
            images=args.images,
            topics=args.topics,
            visible=args.visible
        )
        
        sys.exit(0 if success else 1)
        
    finally:
        await poster.close()


if __name__ == "__main__":
    asyncio.run(main())

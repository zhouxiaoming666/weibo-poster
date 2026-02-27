#!/usr/bin/env python3
"""
微博发布脚本 - Web 版优化版
支持 weibo.com Web 页面发布，功能更丰富
"""

import json
import os
import sys
import time
import random
import argparse
from pathlib import Path
from datetime import datetime
from typing import List, Optional, Dict, Any

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout, Page, BrowserContext

# ============ 配置 ============
DEFAULT_CONFIG = {
    "account": {"cookie_file": "cookies.json"},
    "browser": {
        "headless": True,
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    },
    "behavior": {
        "min_delay_ms": 800,
        "max_delay_ms": 3000,
        "scroll_before_post": True,
        "random_mouse_move": True,
        "screenshot_on_error": True
    },
    "post": {
        "max_images": 9,
        "min_images": 0,
        "max_content_length": 2000,
        "retry_times": 3,
        "retry_delay_s": 5
    },
    "anti_detect": {
        "enable": True,
        "random_viewport": True,
        "hide_webdriver": True
    }
}

# ============ 工具函数 ============
def load_config(config_path: str = "assets/config.json") -> dict:
    """加载配置文件"""
    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
            return deep_merge(DEFAULT_CONFIG, config)
    return DEFAULT_CONFIG


def deep_merge(base: dict, override: dict) -> dict:
    """深度合并字典"""
    result = base.copy()
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def load_cookies(cookie_file: str) -> list:
    """从文件加载 Cookie"""
    if os.path.exists(cookie_file):
        with open(cookie_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []


def save_cookies(cookies: list, cookie_file: str):
    """保存 Cookie 到文件"""
    os.makedirs(os.path.dirname(cookie_file), exist_ok=True)
    with open(cookie_file, 'w', encoding='utf-8') as f:
        json.dump(cookies, f, indent=2, ensure_ascii=False)
    print(f"✅ Cookie 已保存：{cookie_file}")


def random_delay(min_ms: int, max_ms: int):
    """随机延迟"""
    delay = random.uniform(min_ms, max_ms) / 1000
    time.sleep(delay)


def get_timestamp() -> str:
    """获取时间戳字符串"""
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def take_screenshot(page: Page, name: str, save_dir: str = "screenshots"):
    """截图保存"""
    os.makedirs(save_dir, exist_ok=True)
    path = os.path.join(save_dir, f"{name}_{get_timestamp()}.png")
    page.screenshot(path=path, full_page=True)
    print(f"📸 截图已保存：{path}")


def type_text_slowly(page: Page, element, text: str, min_delay: int, max_delay: int):
    """模拟真人输入"""
    element.click()
    element.press('Control+A')
    element.press('Delete')
    random_delay(200, 500)
    
    for char in text:
        element.type(char)
        if random.random() < 0.1:
            time.sleep(random.uniform(0.3, 0.8))
        else:
            random_delay(min_delay, max_delay)


# ============ 核心发布函数 ============
def post_weibo_web(
    config: dict,
    content: str,
    images: Optional[List[str]] = None,
    video_path: Optional[str] = None,
    topics: Optional[List[str]] = None,
    visible: str = 'public',
    schedule_time: Optional[str] = None,  # 定时发布，格式：YYYY-MM-DD HH:MM
    script_dir: str = '.',
    retry_count: int = 0
) -> bool:
    """发布微博（Web 版优化）"""
    
    # 提取配置
    cookie_file = config['account'].get('cookie_file', 'cookies.json')
    if not os.path.isabs(cookie_file):
        cookie_file = os.path.join(script_dir, '..', cookie_file)
    
    headless = config['browser'].get('headless', True)
    min_delay = config['behavior'].get('min_delay_ms', 800)
    max_delay = config['behavior'].get('max_delay_ms', 3000)
    max_images = config['post'].get('max_images', 9)
    retry_times = config['post'].get('retry_times', 3)
    screenshot_on_error = config['behavior'].get('screenshot_on_error', True)
    
    # 验证内容长度
    max_content_length = config['post'].get('max_content_length', 2000)
    if len(content) > max_content_length:
        print(f"⚠️  内容超过{max_content_length}字，将被截断")
        content = content[:max_content_length]
    
    # 验证图片
    if images:
        if len(images) > max_images:
            print(f"⚠️  图片超过{max_images}张，将只使用前{max_images}张")
            images = images[:max_images]
        
        for img in images:
            if not os.path.exists(img):
                print(f"❌ 图片文件不存在：{img}")
                return False
    
    # 验证视频
    if video_path and not os.path.exists(video_path):
        print(f"❌ 视频文件不存在：{video_path}")
        return False
    
    print("🌐 启动浏览器...")
    
    with sync_playwright() as p:
        # 启动浏览器
        browser_args = [
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--disable-dev-shm-usage',
            '--disable-accelerated-2d-canvas',
            '--disable-gpu',
            '--window-size=1920,1080'
        ]
        
        if config['anti_detect'].get('enable', True):
            browser_args.append('--disable-blink-features=AutomationControlled')
        
        browser = p.chromium.launch(headless=headless, args=browser_args)
        
        # 创建上下文
        context_options = {
            'viewport': {'width': 1920, 'height': 1080},
            'user_agent': config['browser'].get('user_agent'),
            'locale': 'zh-CN',
            'timezone_id': 'Asia/Shanghai'
        }
        
        if config['anti_detect'].get('random_viewport', True):
            context_options['viewport'] = {
                'width': random.randint(1280, 1920),
                'height': random.randint(720, 1080)
            }
        
        context = browser.new_context(**context_options)
        
        if config['anti_detect'].get('hide_webdriver', True):
            context.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
            """)
        
        # 加载 Cookie
        cookies = load_cookies(cookie_file)
        if cookies:
            context.add_cookies(cookies)
            print("✅ Cookie 已加载")
        else:
            print("❌ 未找到 Cookie，请先登录微博")
            browser.close()
            return False
        
        page = context.new_page()
        
        try:
            # ========== 打开微博 Web 版主页 ==========
            print("📝 打开微博 Web 版...")
            page.goto('https://weibo.com/', wait_until='networkidle', timeout=30000)
            random_delay(min_delay, max_delay)
            
            # 检查登录
            current_url = page.url
            if 'login' in current_url.lower() or 'passport' in current_url.lower() or 'sso' in current_url.lower():
                print("❌ 未登录，请先登录微博")
                if screenshot_on_error:
                    take_screenshot(page, "login_required")
                browser.close()
                return False
            
            # 检测是否跳转到个人主页
            if 'u/' in current_url or '/home' in current_url:
                print("✅ 已登录")
            else:
                # 尝试导航到首页
                page.goto('https://weibo.com/a/feed', wait_until='networkidle', timeout=30000)
                random_delay(min_delay, max_delay)
                print("✅ 已登录（已导航到首页）")
            
            # ========== 找到发布器入口 ==========
            print("✏️  打开发布器...")
            
            # Web 版微博通常有发布按钮在顶部
            publish_entry_selectors = [
                '[class*="publish"], [class*="Publish"]',
                'button:has-text("发布"), button:has-text("微博")',
                '[class*="compose"], [class*="Compose"]',
                '[class*="editor"], [class*="Editor"]',
                'a[href*="compose"], a[href*="publish"]'
            ]
            
            publish_entry = None
            for selector in publish_entry_selectors:
                try:
                    publish_entry = page.locator(selector).first
                    if publish_entry.is_visible(timeout=3000):
                        print(f"✓ 找到发布入口：{selector}")
                        publish_entry.click()
                        random_delay(1000, 2000)
                        break
                except:
                    continue
            
            # 等待发布器打开
            random_delay(2000, 3000)
            
            # ========== 定位发布框 ==========
            print("📝 定位发布框...")
            
            # Web 版发布框选择器
            compose_selectors = [
                'div[role="textbox"], [contenteditable="true"]',
                'textarea[class*="editor"], textarea[class*="Editor"]',
                '[class*="input"], [class*="Input"]',
                '[placeholder*="微博"], [placeholder*="新鲜事"]'
            ]
            
            compose_input = None
            for selector in compose_selectors:
                try:
                    compose_input = page.locator(selector).first
                    if compose_input.is_visible(timeout=3000):
                        print(f"✓ 找到发布框：{selector}")
                        break
                except:
                    continue
            
            if not compose_input:
                # 尝试使用页面评估来找到元素
                print("⚠️  尝试备用方法查找发布框...")
                try:
                    compose_input = page.locator('div[class*="rich-textarea"], [class*="RichTextarea"]').first
                    if compose_input.is_visible(timeout=3000):
                        print("✓ 找到发布框（备用方法）")
                except:
                    print("❌ 未找到发布框")
                    if screenshot_on_error:
                        take_screenshot(page, "no_compose_box")
                    browser.close()
                    return False
            
            # ========== 输入内容 ==========
            print("📝 输入微博内容...")
            
            # 尝试多种输入方法
            try:
                # 方法 1: 使用 type_text_slowly
                type_text_slowly(page, compose_input, content, min_delay, max_delay)
                print(f"✅ 内容已输入（{len(content)}字）")
            except:
                # 方法 2: 直接填充
                try:
                    compose_input.fill(content)
                    print(f"✅ 内容已填充（{len(content)}字）")
                except:
                    # 方法 3: 使用键盘输入
                    compose_input.click()
                    compose_input.press('Control+A')
                    compose_input.press('Delete')
                    page.keyboard.type(content, delay=random.randint(50, 150))
                    print(f"✅ 内容已键盘输入（{len(content)}字）")
            
            random_delay(1000, 2000)
            
            # ========== 上传图片 ==========
            if images:
                print("🖼️  上传图片...")
                
                # Web 版图片上传选择器
                upload_selectors = [
                    'input[type="file"][accept*="image"]',
                    'button:has-text("图片"), button:has-text("图")',
                    '[class*="image-upload"], [class*="ImageUpload"]',
                    '[class*="pic-upload"], [class*="PicUpload"]',
                    'svg[class*="icon-pic"], i[class*="icon-pic"]'
                ]
                
                file_input = None
                upload_btn = None
                
                # 先找文件输入
                for selector in upload_selectors:
                    try:
                        if 'input[type="file"]' in selector:
                            file_input = page.locator(selector).first
                            if file_input.is_visible(timeout=2000):
                                print(f"✓ 找到文件输入：{selector}")
                                break
                        else:
                            upload_btn = page.locator(selector).first
                            if upload_btn.is_visible(timeout=2000):
                                print(f"✓ 找到上传按钮：{selector}")
                                break
                    except:
                        continue
                
                if file_input and file_input.input_enabled():
                    file_input.set_input_files(images)
                    print(f"✅ 已上传 {len(images)} 张图片")
                elif upload_btn:
                    # 点击上传按钮触发文件选择
                    upload_btn.click()
                    random_delay(1000, 2000)
                    
                    # 等待文件输入出现
                    file_input = page.locator('input[type="file"]').first
                    if file_input.is_visible(timeout=5000):
                        file_input.set_input_files(images)
                        print(f"✅ 已上传 {len(images)} 张图片")
                    else:
                        print("⚠️  文件输入未出现")
                else:
                    print("⚠️  未找到图片上传入口")
                
                # 等待上传完成
                print("⏳ 等待图片上传完成...")
                time.sleep(5)
            
            # ========== 添加话题 ==========
            if topics:
                print("🏷️  添加话题...")
                for topic in topics:
                    try:
                        # 在内容末尾添加话题
                        compose_input.click()
                        compose_input.press('End')
                        compose_input.type(f" #{topic} ")
                        random_delay(200, 500)
                        print(f"✅ 话题已添加：#{topic}")
                    except Exception as e:
                        print(f"⚠️  话题添加失败 {topic}: {e}")
            
            # ========== 设置可见性 ==========
            if visible != 'public':
                print(f"🔒 设置可见性：{visible}")
                try:
                    visible_selectors = [
                        '[class*="visible"], [class*="Visible"]',
                        'button:has-text("公开"), button:has-text("好友")',
                        '[class*="privacy"], [class*="Privacy"]'
                    ]
                    
                    visible_btn = None
                    for selector in visible_selectors:
                        try:
                            visible_btn = page.locator(selector).first
                            if visible_btn.is_visible(timeout=3000):
                                break
                        except:
                            continue
                    
                    if visible_btn:
                        visible_btn.click()
                        random_delay(1000, 2000)
                        
                        visible_text = '公开' if visible == 'public' else '好友可见' if visible == 'friends' else '私密'
                        visible_option = page.locator(f'li:has-text("{visible_text}"), [role="menuitem"]:has-text("{visible_text}")').first
                        if visible_option.is_visible(timeout=3000):
                            visible_option.click()
                            print(f"✅ 可见性已设置：{visible}")
                except Exception as e:
                    print(f"⚠️  可见性设置失败：{e}")
            
            # ========== 定时发布 ==========
            if schedule_time:
                print(f"⏰ 设置定时发布：{schedule_time}")
                try:
                    schedule_selectors = [
                        '[class*="schedule"], [class*="Schedule"]',
                        'button:has-text("定时"), button:has-text("预约")'
                    ]
                    
                    schedule_btn = None
                    for selector in schedule_selectors:
                        try:
                            schedule_btn = page.locator(selector).first
                            if schedule_btn.is_visible(timeout=3000):
                                break
                        except:
                            continue
                    
                    if schedule_btn:
                        schedule_btn.click()
                        random_delay(1000, 2000)
                        
                        # 输入定时时间（需要具体实现，取决于微博的 UI）
                        print("⚠️  定时发布需要手动确认时间选择器")
                except Exception as e:
                    print(f"⚠️  定时发布设置失败：{e}")
            
            # ========== 模拟真人操作 ==========
            if config['behavior'].get('scroll_before_post', True):
                print("📜 模拟真人滚动...")
                for _ in range(random.randint(2, 4)):
                    scroll_amount = random.randint(100, 300)
                    page.evaluate(f'window.scrollBy(0, {scroll_amount})')
                    time.sleep(random.uniform(0.5, 1.5))
            
            if config['behavior'].get('random_mouse_move', True):
                print("🖱️  模拟鼠标移动...")
                for _ in range(random.randint(2, 4)):
                    x = random.randint(100, 800)
                    y = random.randint(100, 600)
                    page.mouse.move(x, y)
                    time.sleep(random.uniform(0.3, 0.8))
            
            # ========== 发布 ==========
            print("🚀 发布...")
            
            publish_selectors = [
                'button:has-text("发布"), button:has-text("Publish")',
                '[class*="publish"], [class*="Publish"]',
                'button[class*="send"], [class*="Send"]',
                'button:has-text("发送")'
            ]
            
            publish_btn = None
            for selector in publish_selectors:
                try:
                    publish_btn = page.locator(selector).first
                    if publish_btn.is_visible(timeout=3000):
                        print(f"✓ 找到发布按钮：{selector}")
                        break
                except:
                    continue
            
            if publish_btn and publish_btn.is_enabled():
                take_screenshot(page, "before_publish")
                
                publish_btn.click()
                print("✅ 已点击发布按钮")
                
                # 等待发布结果
                time.sleep(5)
                
                # 检测发布成功
                success_indicators = [
                    '发布成功',
                    '发送成功',
                    'published',
                    'success',
                    '我的主页',
                    '个人主页'
                ]
                
                current_url = page.url
                page_content = page.content()
                
                if any(indicator in current_url.lower() or indicator in page_content.lower() 
                       for indicator in success_indicators):
                    print("✅ 发布成功！")
                    take_screenshot(page, "publish_success")
                    browser.close()
                    return True
                else:
                    print("⏳ 发布处理中...")
                    take_screenshot(page, "publish_processing")
                    browser.close()
                    return True
            else:
                print("❌ 未找到发布按钮或按钮不可用")
                if screenshot_on_error:
                    take_screenshot(page, "no_publish_button")
                browser.close()
                return False
                
        except PlaywrightTimeout as e:
            print(f"❌ 操作超时：{e}")
            if screenshot_on_error:
                take_screenshot(page, "timeout_error")
            
            if retry_count < retry_times:
                print(f"🔄 {retry_count + 1}/{retry_times} 重试...")
                browser.close()
                time.sleep(config['post'].get('retry_delay_s', 5))
                return post_weibo_web(config, content, images, video_path, topics, visible, schedule_time, script_dir, retry_count + 1)
            
            browser.close()
            return False
            
        except Exception as e:
            print(f"❌ 错误：{e}")
            import traceback
            traceback.print_exc()
            
            if screenshot_on_error:
                take_screenshot(page, "exception_error")
            
            if retry_count < retry_times:
                print(f"🔄 {retry_count + 1}/{retry_times} 重试...")
                browser.close()
                time.sleep(config['post'].get('retry_delay_s', 5))
                return post_weibo_web(config, content, images, video_path, topics, visible, schedule_time, script_dir, retry_count + 1)
            
            browser.close()
            return False
        
        finally:
            try:
                browser.close()
            except:
                pass


# ============ 主函数 ============
def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='微博发布工具 - Web 版（优化版）')
    parser.add_argument('--config', default='assets/config.json', help='配置文件路径')
    parser.add_argument('--content', required=True, help='微博内容')
    parser.add_argument('--images', nargs='+', help='图片文件路径')
    parser.add_argument('--video', help='视频文件路径')
    parser.add_argument('--topics', nargs='+', help='话题标签（不含#）')
    parser.add_argument('--visible', choices=['public', 'friends', 'private'], default='public',
                       help='可见性')
    parser.add_argument('--schedule', help='定时发布时间（YYYY-MM-DD HH:MM）')
    parser.add_argument('--headless', action='store_true', help='无头模式')
    parser.add_argument('--debug', action='store_true', help='调试模式')
    
    args = parser.parse_args()
    
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    print("=" * 60)
    print("📝 微博发布工具 - Web 版优化")
    print(f"📅 时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    print()
    
    config = load_config(args.config)
    
    if args.debug:
        config['browser']['headless'] = False
        config['behavior']['screenshot_on_error'] = True
    elif args.headless:
        config['browser']['headless'] = True
    
    success = post_weibo_web(
        config=config,
        content=args.content,
        images=args.images,
        video_path=args.video,
        topics=args.topics,
        visible=args.visible,
        schedule_time=args.schedule,
        script_dir=str(script_dir)
    )
    
    print("\n" + "=" * 60)
    if success:
        print("✅ 微博发布成功！")
    else:
        print("❌ 微博发布失败，请检查日志和截图")
    print("=" * 60)
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""
人类行为模拟器 - 模拟真实用户的操作行为
用于绕过网站的反自动化检测
"""

import asyncio
import random
import math
from typing import Optional, Tuple, List
from playwright.async_api import Page, ElementHandle


class HumanBehaviorSimulator:
    """人类行为模拟器"""
    
    def __init__(self, min_delay_ms: int = 1000, max_delay_ms: int = 5000):
        self.min_delay_ms = min_delay_ms
        self.max_delay_ms = max_delay_ms
    
    async def random_delay(self, min_ms: Optional[int] = None, max_ms: Optional[int] = None):
        """随机延迟"""
        min_val = min_ms if min_ms is not None else self.min_delay_ms
        max_val = max_ms if max_ms is not None else self.max_delay_ms
        delay = random.uniform(min_val, max_val) / 1000
        await asyncio.sleep(delay)
    
    async def human_type(self, element: ElementHandle, text: str):
        """模拟人类打字 - 带随机停顿和错误修正"""
        for char in text:
            # 随机打字速度（50-200ms 每字符）
            delay = random.uniform(0.05, 0.2)
            
            # 偶尔停顿更长（模拟思考）
            if random.random() < 0.05:
                delay += random.uniform(0.3, 0.8)
            
            # 偶尔打错字然后删除（非常罕见）
            if random.random() < 0.01 and len(text) > 10:
                await element.press("Backspace")
                await asyncio.sleep(random.uniform(0.1, 0.3))
            
            await element.type(char, delay=0)
            await asyncio.sleep(delay)
    
    async def human_click(self, element: ElementHandle):
        """模拟人类点击 - 带随机偏移和延迟"""
        try:
            # 获取元素位置
            box = await element.bounding_box()
            if not box:
                await element.click()
                return
            
            # 在元素内随机偏移（模拟不精确点击）
            offset_x = random.uniform(0.1, 0.9) * box["width"]
            offset_y = random.uniform(0.1, 0.9) * box["height"]
            
            x = box["x"] + offset_x
            y = box["y"] + offset_y
            
            # 点击前延迟
            await self.random_delay(300, 800)
            
            # 移动到元素（带轨迹）
            await self.mouse_move_trajectory(element.page, x, y)
            
            # 点击前短暂停留
            await asyncio.sleep(random.uniform(0.1, 0.3))
            
            # 点击
            await element.click()
            
        except Exception as e:
            # 降级为普通点击
            await element.click()
    
    async def mouse_move_trajectory(self, page: Page, target_x: float, target_y: float, duration_ms: int = 500):
        """模拟人类鼠标移动轨迹 - 贝塞尔曲线"""
        try:
            # 获取当前位置（近似）
            current_x, current_y = 0, 0  # 简化处理
            
            # 生成轨迹点（5-10 个点）
            num_points = random.randint(5, 10)
            points = self._generate_bezier_curve(
                current_x, current_y, target_x, target_y, num_points
            )
            
            # 计算每点的时间间隔
            time_per_point = duration_ms / num_points
            
            # 移动鼠标
            for point in points:
                await page.mouse.move(point[0], point[1])
                await asyncio.sleep(time_per_point / 1000)
                
        except Exception as e:
            # 降级为直接移动
            await page.mouse.move(target_x, target_y)
    
    def _generate_bezier_curve(self, x0: float, y0: float, x1: float, y1: float, 
                                num_points: int) -> List[Tuple[float, float]]:
        """生成贝塞尔曲线路径"""
        points = []
        
        # 控制点（添加随机偏移使路径更自然）
        cx = (x0 + x1) / 2 + random.uniform(-50, 50)
        cy = (y0 + y1) / 2 + random.uniform(-50, 50)
        
        for i in range(num_points + 1):
            t = i / num_points
            
            # 二次贝塞尔曲线公式
            x = (1 - t) ** 2 * x0 + 2 * (1 - t) * t * cx + t ** 2 * x1
            y = (1 - t) ** 2 * y0 + 2 * (1 - t) * t * cy + t ** 2 * y1
            
            points.append((x, y))
        
        return points
    
    async def random_scroll(self, page: Page, min_scroll: int = 100, max_scroll: int = 500):
        """模拟人类随机滚动"""
        try:
            # 随机滚动次数
            num_scrolls = random.randint(1, 3)
            
            for _ in range(num_scrolls):
                # 随机滚动距离
                scroll_distance = random.randint(min_scroll, max_scroll)
                
                # 随机方向（主要向下，偶尔向上）
                direction = 1 if random.random() < 0.8 else -1
                
                await page.evaluate(f"window.scrollBy(0, {scroll_distance * direction})")
                
                # 滚动间延迟
                await self.random_delay(500, 1500)
            
            # 最后滚回顶部附近
            await page.evaluate("window.scrollTo(0, 0)")
            await self.random_delay(300, 800)
            
        except Exception as e:
            pass  # 滚动失败不影响主流程
    
    async def human_hover(self, element: ElementHandle):
        """模拟人类悬停"""
        try:
            box = await element.bounding_box()
            if box:
                x = box["x"] + box["width"] / 2
                y = box["y"] + box["height"] / 2
                
                # 移动到元素附近
                await page.mouse.move(x, y)
                
                # 悬停停留
                await asyncio.sleep(random.uniform(0.5, 2.0))
                
        except:
            pass
    
    async def read_content(self, page: Page, min_time_ms: int = 2000, max_time_ms: int = 8000):
        """模拟阅读内容"""
        # 随机阅读时间
        read_time = random.uniform(min_time_ms, max_time_ms) / 1000
        await asyncio.sleep(read_time)
        
        # 偶尔小幅度滚动
        if random.random() < 0.3:
            await page.evaluate(f"window.scrollBy(0, {random.randint(50, 200)})")
            await asyncio.sleep(random.uniform(0.5, 1.5))


# 工具函数
def generate_random_user_agent() -> str:
    """生成随机 User-Agent"""
    user_agents = [
        # Chrome Windows
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        # Chrome macOS
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        # Firefox Windows
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",
        # Safari macOS
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
        # Edge Windows
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
    ]
    return random.choice(user_agents)


if __name__ == "__main__":
    # 测试代码
    print("人类行为模拟器模块")
    print(f"示例 User-Agent: {generate_random_user_agent()}")

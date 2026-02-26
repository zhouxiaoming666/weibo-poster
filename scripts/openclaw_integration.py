#!/usr/bin/env python3
"""
OpenClaw 集成接口 - 使微博发布技能可通过 OpenClaw 调用
"""

import asyncio
import json
import sys
import os
from pathlib import Path

# 添加脚本目录到路径
SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))

from weibo_post import WeiboPoster


async def post_weibo(content: str, images: list = None, topics: list = None, 
                     visible: str = "public", config_path: str = None) -> dict:
    """
    发布微博 - OpenClaw 调用接口
    
    Args:
        content: 微博内容
        images: 图片路径列表
        topics: 话题列表
        visible: 可见性 (public/friends/self)
        config_path: 配置文件路径
    
    Returns:
        dict: {success: bool, message: str, data: any}
    """
    result = {
        "success": False,
        "message": "",
        "data": {}
    }
    
    poster = WeiboPoster(config_path=config_path)
    
    try:
        print(f"[微博发布] 初始化浏览器...")
        await poster.init_browser()
        
        print(f"[微博发布] 登录微博...")
        login_success = await poster.login()
        
        if not login_success:
            result["message"] = "登录失败，请检查账号密码或手动完成验证码"
            return result
        
        print(f"[微博发布] 发布内容：{content[:50]}...")
        post_success = await poster.post(
            content=content,
            images=images,
            topics=topics,
            visible=visible
        )
        
        if post_success:
            result["success"] = True
            result["message"] = "微博发布成功"
            result["data"] = {
                "content": content,
                "images_count": len(images) if images else 0,
                "topics": topics or []
            }
        else:
            result["message"] = "发布失败，请稍后重试"
            
    except Exception as e:
        result["message"] = f"发布异常：{str(e)}"
        import traceback
        traceback.print_exc()
        
    finally:
        await poster.close()
    
    return result


def main():
    """命令行入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description="微博发布 - OpenClaw 接口")
    parser.add_argument("--action", type=str, default="post", 
                       choices=["post", "login", "status"],
                       help="操作类型")
    parser.add_argument("--content", type=str, help="微博内容")
    parser.add_argument("--images", type=str, nargs="*", help="图片路径")
    parser.add_argument("--topics", type=str, nargs="*", help="话题")
    parser.add_argument("--visible", type=str, default="public",
                       help="可见性")
    parser.add_argument("--config", type=str, help="配置文件")
    parser.add_argument("--output-json", action="store_true",
                       help="输出 JSON 格式结果")
    
    args = parser.parse_args()
    
    if args.action == "login":
        async def login_only():
            poster = WeiboPoster(config_path=args.config)
            await poster.init_browser()
            success = await poster.login()
            await poster.close()
            return {"success": success, "message": "登录成功" if success else "登录失败"}
        
        result = asyncio.run(login_only())
        
    elif args.action == "post":
        if not args.content:
            print("错误：发布操作需要 --content 参数")
            sys.exit(1)
        
        result = asyncio.run(post_weibo(
            content=args.content,
            images=args.images,
            topics=args.topics,
            visible=args.visible,
            config_path=args.config
        ))
        
    elif args.action == "status":
        result = {"success": True, "message": "微博发布技能就绪", "data": {"version": "1.0.0"}}
    
    # 输出结果
    if args.output_json:
        print(json.dumps(result, ensure_ascii=False))
    else:
        status = "✓" if result["success"] else "✗"
        print(f"{status} {result['message']}")
        if result.get("data"):
            print(f"数据：{json.dumps(result['data'], ensure_ascii=False, indent=2)}")
    
    sys.exit(0 if result["success"] else 1)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2024-present Microsoft <autogen@microsoft.com>
#
# SPDX-License-Identifier: MIT

"""
MarkItDown API PDF URL 转换演示

这个脚本演示如何使用 MarkItDown API 将 PDF URL 转换为 Markdown。
"""

import requests
import json
import time
from markitdown_api import MarkItDownClient


def test_api_server_conversion():
    """测试 API 服务器转换功能"""
    print("=== MarkItDown API PDF URL 转换演示 ===\n")
    
    # 测试 URL
    test_url = "https://uat.yunstars.com/upload/百年福享宝贝少儿教育年金保险.pdf"
    api_base_url = "http://localhost:8000"
    
    print(f"测试 PDF URL: {test_url}")
    print(f"API 服务器: {api_base_url}")
    print()
    
    # 1. 使用客户端 SDK
    print("1. 使用 MarkItDown 客户端 SDK:")
    try:
        client = MarkItDownClient(base_url=api_base_url)
        result = client.convert_url(test_url)
        
        print(f"   ✓ 转换成功!")
        print(f"   ✓ 处理时间: {result.get('processing_time', 'N/A')} 秒")
        print(f"   ✓ Markdown 长度: {len(result['markdown'])} 字符")
        print(f"   ✓ 标题: {result.get('title', 'N/A')}")
        print(f"   ✓ 内容预览: {result['markdown'][:200]}...")
        print()
        
    except Exception as e:
        print(f"   ✗ 客户端转换失败: {e}")
        print()
    
    # 2. 使用直接 HTTP 请求
    print("2. 使用直接 HTTP 请求:")
    try:
        url = f"{api_base_url}/api/v1/convert/url"
        data = {
            'url': test_url,
            'keep_data_uris': False,
            'enable_plugins': False
        }
        
        start_time = time.time()
        response = requests.post(url, json=data, timeout=60)
        response.raise_for_status()
        request_time = time.time() - start_time
        
        result = response.json()
        
        print(f"   ✓ HTTP 请求成功!")
        print(f"   ✓ 状态码: {response.status_code}")
        print(f"   ✓ 请求时间: {request_time:.3f} 秒")
        print(f"   ✓ 处理时间: {result.get('processing_time', 'N/A')} 秒")
        print(f"   ✓ Markdown 长度: {len(result['markdown'])} 字符")
        print(f"   ✓ 内容预览: {result['markdown'][:200]}...")
        print()
        
    except Exception as e:
        print(f"   ✗ HTTP 请求失败: {e}")
        print()
    
    # 3. 测试错误处理
    print("3. 测试错误处理:")
    try:
        url = f"{api_base_url}/api/v1/convert/url"
        data = {
            'url': 'https://invalid-url-that-does-not-exist.com/file.pdf',
            'keep_data_uris': False,
            'enable_plugins': False
        }
        
        response = requests.post(url, json=data, timeout=30)
        result = response.json()
        
        if response.status_code != 200:
            print(f"   ✓ 错误处理正常!")
            print(f"   ✓ 状态码: {response.status_code}")
            print(f"   ✓ 错误信息: {result.get('error', 'N/A')}")
        else:
            print(f"   ✗ 预期错误但得到成功响应")
        print()
        
    except Exception as e:
        print(f"   ✓ 错误处理正常: {e}")
        print()


def test_direct_conversion():
    """测试直接使用 MarkItDown 转换"""
    print("=== 直接使用 MarkItDown 转换 ===\n")
    
    try:
        from markitdown import MarkItDown
        
        test_url = "https://uat.yunstars.com/upload/百年福享宝贝少儿教育年金保险.pdf"
        
        print(f"转换 URL: {test_url}")
        
        md = MarkItDown()
        start_time = time.time()
        result = md.convert_uri(test_url)
        conversion_time = time.time() - start_time
        
        print(f"✓ 直接转换成功!")
        print(f"✓ 转换时间: {conversion_time:.3f} 秒")
        print(f"✓ Markdown 长度: {len(result.text_content)} 字符")
        print(f"✓ 内容预览: {result.text_content[:200]}...")
        print()
        
    except Exception as e:
        print(f"✗ 直接转换失败: {e}")
        print()


def show_curl_examples():
    """显示 cURL 使用示例"""
    print("=== cURL 使用示例 ===\n")
    
    test_url = "https://uat.yunstars.com/upload/百年福享宝贝少儿教育年金保险.pdf"
    
    print("1. 转换 PDF URL:")
    print(f"""curl -X POST \\
  -H "Content-Type: application/json" \\
  -d '{{"url": "{test_url}", "keep_data_uris": false, "enable_plugins": false}}' \\
  http://localhost:8000/api/v1/convert/url""")
    print()
    
    print("2. 健康检查:")
    print("curl http://localhost:8000/api/v1/health")
    print()
    
    print("3. 查看支持的格式:")
    print("curl http://localhost:8000/api/v1/formats")
    print()
    
    print("4. 查看 API 信息:")
    print("curl http://localhost:8000/api/v1/info")
    print()


if __name__ == "__main__":
    print("MarkItDown API PDF URL 转换功能演示")
    print("=" * 50)
    print()
    
    # 显示 cURL 示例
    show_curl_examples()
    
    # 测试直接转换
    test_direct_conversion()
    
    # 检查 API 服务器是否运行
    try:
        response = requests.get("http://localhost:8000/api/v1/health", timeout=5)
        if response.status_code == 200:
            # 测试 API 服务器
            test_api_server_conversion()
        else:
            print("API 服务器未运行或响应异常")
            print("请先启动 API 服务器:")
            print("  markitdown-api --host 0.0.0.0 --port 8000")
            print()
    except Exception as e:
        print("无法连接到 API 服务器")
        print("请先启动 API 服务器:")
        print("  markitdown-api --host 0.0.0.0 --port 8000")
        print()

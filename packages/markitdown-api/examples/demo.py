#!/usr/bin/env python3
"""
MarkItDown API 使用示例

这个脚本演示如何使用 MarkItDown API 进行文档转换
"""

import requests
import json
import sys
from pathlib import Path


def test_health_check(base_url="http://localhost:8000"):
    """测试健康检查"""
    print("🔍 检查 API 健康状态...")
    
    try:
        response = requests.get(f"{base_url}/api/v1/health", timeout=10)
        response.raise_for_status()
        
        data = response.json()
        print(f"✅ API 状态: {data['status']}")
        print(f"📦 版本: {data['version']}")
        print(f"📁 支持格式数量: {len(data['supported_formats'])}")
        return True
        
    except Exception as e:
        print(f"❌ 健康检查失败: {e}")
        return False


def convert_text_file(base_url="http://localhost:8000"):
    """转换文本文件示例"""
    print("\n📄 测试文本文件转换...")
    
    # 创建测试文件
    test_content = """# 测试文档

这是一个测试文档，用于演示 MarkItDown API 的功能。

## 功能特性

- 支持多种文档格式
- 提供 RESTful API
- 易于集成

## 使用示例

```python
import requests

response = requests.post('/api/v1/convert', files={'file': open('test.txt', 'rb')})
result = response.json()
print(result['markdown'])
```

> 更多信息请访问: https://github.com/microsoft/markitdown
"""
    
    test_file = Path("test_document.txt")
    test_file.write_text(test_content, encoding='utf-8')
    
    try:
        # 上传并转换文件
        with open(test_file, 'rb') as f:
            files = {'file': (test_file.name, f, 'text/plain')}
            data = {
                'keep_data_uris': 'false',
                'enable_plugins': 'false'
            }
            
            response = requests.post(
                f"{base_url}/api/v1/convert",
                files=files,
                data=data,
                timeout=30
            )
            response.raise_for_status()
        
        result = response.json()
        
        if result['success']:
            print("✅ 文件转换成功")
            print(f"📊 处理时间: {result['processing_time']}秒")
            print(f"📝 Markdown 长度: {len(result['markdown'])} 字符")
            print("\n📖 转换结果预览:")
            print("-" * 50)
            print(result['markdown'][:500] + "..." if len(result['markdown']) > 500 else result['markdown'])
            print("-" * 50)
        else:
            print("❌ 文件转换失败")
            
    except Exception as e:
        print(f"❌ 转换失败: {e}")
    finally:
        # 清理测试文件
        if test_file.exists():
            test_file.unlink()


def convert_url_example(base_url="http://localhost:8000"):
    """转换 URL 示例"""
    print("\n🌐 测试 URL 转换...")
    
    # 使用一个公开的 HTML 页面进行测试
    test_url = "data:text/html,<html><head><title>Test Page</title></head><body><h1>Hello World</h1><p>This is a test page.</p></body></html>"
    
    try:
        data = {
            'url': test_url,
            'keep_data_uris': False,
            'enable_plugins': False
        }
        
        response = requests.post(
            f"{base_url}/api/v1/convert/url",
            json=data,
            timeout=30
        )
        response.raise_for_status()
        
        result = response.json()
        
        if result['success']:
            print("✅ URL 转换成功")
            print(f"📊 处理时间: {result['processing_time']}秒")
            print("\n📖 转换结果:")
            print("-" * 50)
            print(result['markdown'])
            print("-" * 50)
        else:
            print("❌ URL 转换失败")
            
    except Exception as e:
        print(f"❌ URL 转换失败: {e}")


def get_api_info(base_url="http://localhost:8000"):
    """获取 API 信息"""
    print("\n📋 获取 API 信息...")
    
    try:
        response = requests.get(f"{base_url}/api/v1/info", timeout=10)
        response.raise_for_status()
        
        data = response.json()
        print(f"📦 API 名称: {data['name']}")
        print(f"🔢 版本: {data['version']}")
        print(f"📝 描述: {data['description']}")
        print(f"📁 最大文件大小: {data['max_file_size']}")
        
        print("\n🔗 可用端点:")
        for endpoint, description in data['endpoints'].items():
            print(f"  {endpoint}: {description}")
            
    except Exception as e:
        print(f"❌ 获取 API 信息失败: {e}")


def get_supported_formats(base_url="http://localhost:8000"):
    """获取支持的格式"""
    print("\n📁 获取支持的文件格式...")
    
    try:
        response = requests.get(f"{base_url}/api/v1/formats", timeout=10)
        response.raise_for_status()
        
        data = response.json()
        print(f"📊 支持 {data['count']} 种格式:")
        
        # 按类别分组显示
        formats = data['formats']
        categories = {
            '文档': ['pdf', 'docx', 'pptx', 'xlsx', 'xls'],
            '图片': ['jpg', 'jpeg', 'png', 'gif', 'bmp'],
            '音频': ['mp3', 'wav', 'm4a'],
            '网页': ['html', 'htm'],
            '文本': ['txt', 'md', 'csv', 'json', 'xml'],
            '其他': []
        }
        
        # 分类显示
        used_formats = set()
        for category, category_formats in categories.items():
            available_formats = [f for f in category_formats if f in formats]
            if available_formats:
                print(f"  {category}: {', '.join(available_formats)}")
                used_formats.update(available_formats)
        
        # 显示其他格式
        other_formats = [f for f in formats if f not in used_formats]
        if other_formats:
            print(f"  其他: {', '.join(other_formats)}")
            
    except Exception as e:
        print(f"❌ 获取支持格式失败: {e}")


def main():
    """主函数"""
    print("🚀 MarkItDown API 示例程序")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    
    # 检查 API 是否可用
    if not test_health_check(base_url):
        print("\n❌ API 服务不可用，请确保服务已启动:")
        print("   markitdown-api --host 127.0.0.1 --port 8000")
        sys.exit(1)
    
    # 运行各种测试
    get_api_info(base_url)
    get_supported_formats(base_url)
    convert_text_file(base_url)
    convert_url_example(base_url)
    
    print("\n🎉 所有示例执行完成!")
    print("💡 尝试访问以下地址获取更多信息:")
    print(f"   - API 信息: {base_url}/api/v1/info")
    print(f"   - 健康检查: {base_url}/api/v1/health")
    print(f"   - 支持格式: {base_url}/api/v1/formats")


if __name__ == "__main__":
    main()

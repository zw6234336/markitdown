# SPDX-FileCopyrightText: 2024-present Microsoft <autogen@microsoft.com>
#
# SPDX-License-Identifier: MIT

import pytest
import json
import requests
import time
from markitdown_api.app import create_app


@pytest.fixture
def app():
    """创建测试应用"""
    app = create_app({'TESTING': True})
    return app


@pytest.fixture
def client(app):
    """创建测试客户端"""
    return app.test_client()


class TestPDFUrlConversion:
    """测试 PDF URL 转换功能"""
    
    TEST_PDF_URL = "https://uat.yunstars.com/upload/百年福享宝贝少儿教育年金保险.pdf"
    
    def test_convert_pdf_url_success(self, client):
        """测试成功转换 PDF URL"""
        # 准备请求数据
        data = {
            'url': self.TEST_PDF_URL,
            'keep_data_uris': False,
            'enable_plugins': False
        }
        
        # 发送请求
        response = client.post('/api/v1/convert/url', 
                              json=data,
                              content_type='application/json')
        
        # 检查响应状态
        assert response.status_code == 200
        
        # 解析响应数据
        result = json.loads(response.data)
        
        # 验证响应结构
        assert result['success'] is True
        assert 'markdown' in result
        assert isinstance(result['markdown'], str)
        assert len(result['markdown']) > 0
        
        # 验证处理时间字段
        assert 'processing_time' in result
        assert isinstance(result['processing_time'], (int, float))
        assert result['processing_time'] > 0
        
        # 验证时间戳字段
        assert 'timestamp' in result
        
        # 检查 PDF 内容是否正确转换
        markdown_content = result['markdown']
        
        # 验证包含保险相关内容（根据文件名推测）
        expected_keywords = ['保险', '年金', '教育', '福享', '宝贝']
        found_keywords = []
        
        for keyword in expected_keywords:
            if keyword in markdown_content:
                found_keywords.append(keyword)
        
        # 至少应该找到一些相关关键字
        print(f"找到的关键字: {found_keywords}")
        print(f"Markdown 内容长度: {len(markdown_content)} 字符")
        print(f"Markdown 内容预览: {markdown_content[:500]}...")
        
    def test_convert_pdf_url_with_plugins(self, client):
        """测试启用插件的 PDF URL 转换"""
        data = {
            'url': self.TEST_PDF_URL,
            'keep_data_uris': False,
            'enable_plugins': True
        }
        
        response = client.post('/api/v1/convert/url', 
                              json=data,
                              content_type='application/json')
        
        assert response.status_code == 200
        result = json.loads(response.data)
        assert result['success'] is True
        assert 'markdown' in result
        
    def test_convert_pdf_url_with_data_uris(self, client):
        """测试保留数据 URI 的 PDF URL 转换"""
        data = {
            'url': self.TEST_PDF_URL,
            'keep_data_uris': True,
            'enable_plugins': False
        }
        
        response = client.post('/api/v1/convert/url', 
                              json=data,
                              content_type='application/json')
        
        assert response.status_code == 200
        result = json.loads(response.data)
        assert result['success'] is True
        assert 'markdown' in result
        
    def test_convert_url_no_data(self, client):
        """测试无数据的 URL 转换请求"""
        response = client.post('/api/v1/convert/url', 
                              json={},
                              content_type='application/json')
        assert response.status_code == 400
        
        result = json.loads(response.data)
        assert 'error' in result
        
    def test_convert_url_no_url_field(self, client):
        """测试缺少 URL 字段的请求"""
        data = {
            'keep_data_uris': False,
            'enable_plugins': False
        }
        
        response = client.post('/api/v1/convert/url', 
                              json=data,
                              content_type='application/json')
        
        assert response.status_code == 400
        result = json.loads(response.data)
        assert 'error' in result
        
    def test_convert_invalid_url(self, client):
        """测试无效 URL"""
        data = {
            'url': 'not-a-valid-url',
            'keep_data_uris': False,
            'enable_plugins': False
        }
        
        response = client.post('/api/v1/convert/url', 
                              json=data,
                              content_type='application/json')
        
        # 应该返回错误
        assert response.status_code == 500
        result = json.loads(response.data)
        assert 'error' in result
        
    def test_convert_nonexistent_url(self, client):
        """测试不存在的 URL"""
        data = {
            'url': 'https://nonexistent-domain-12345.com/file.pdf',
            'keep_data_uris': False,
            'enable_plugins': False
        }
        
        response = client.post('/api/v1/convert/url', 
                              json=data,
                              content_type='application/json')
        
        # 应该返回错误
        assert response.status_code == 500
        result = json.loads(response.data)
        assert 'error' in result


class TestDirectPDFConversion:
    """使用 MarkItDown 直接测试 PDF 转换功能"""
    
    TEST_PDF_URL = "https://uat.yunstars.com/upload/百年福享宝贝少儿教育年金保险.pdf"
    
    def test_direct_markitdown_conversion(self):
        """直接使用 MarkItDown 测试 URL 转换"""
        from markitdown import MarkItDown
        
        md = MarkItDown()
        
        try:
            # 测试 URL 转换
            result = md.convert_uri(self.TEST_PDF_URL)
            
            assert result is not None
            assert hasattr(result, 'text_content')
            assert len(result.text_content) > 0
            
            print(f"直接转换结果长度: {len(result.text_content)} 字符")
            print(f"直接转换内容预览: {result.text_content[:500]}...")
            
            # 检查是否包含预期内容
            content = result.text_content
            assert isinstance(content, str)
            
        except Exception as e:
            pytest.fail(f"直接转换失败: {str(e)}")
    
    def test_requests_download_pdf(self):
        """测试直接下载 PDF 文件"""
        try:
            response = requests.get(self.TEST_PDF_URL, timeout=30)
            response.raise_for_status()
            
            # 检查响应头
            content_type = response.headers.get('content-type', '').lower()
            print(f"Content-Type: {content_type}")
            print(f"Content-Length: {response.headers.get('content-length', 'N/A')}")
            
            # 验证是 PDF 文件
            assert 'application/pdf' in content_type or response.content.startswith(b'%PDF')
            
            # 检查文件大小
            assert len(response.content) > 1000  # PDF 应该有一定大小
            
            print(f"PDF 文件大小: {len(response.content)} 字节")
            
        except Exception as e:
            pytest.fail(f"下载 PDF 失败: {str(e)}")


if __name__ == "__main__":
    """直接运行测试"""
    import sys
    import os
    
    # 添加项目路径
    sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
    
    # 运行直接转换测试
    test_direct = TestDirectPDFConversion()
    
    print("=== 测试直接下载 PDF ===")
    try:
        test_direct.test_requests_download_pdf()
        print("✓ PDF 下载测试通过")
    except Exception as e:
        print(f"✗ PDF 下载测试失败: {e}")
    
    print("\n=== 测试 MarkItDown 直接转换 ===")
    try:
        test_direct.test_direct_markitdown_conversion()
        print("✓ MarkItDown 直接转换测试通过")
    except Exception as e:
        print(f"✗ MarkItDown 直接转换测试失败: {e}")
    
    print("\n=== 测试 API 转换 ===")
    app = create_app({'TESTING': True})
    
    with app.test_client() as client:
        test_api = TestPDFUrlConversion()
        try:
            test_api.test_convert_pdf_url_success(client)
            print("✓ API URL 转换测试通过")
        except Exception as e:
            print(f"✗ API URL 转换测试失败: {e}")

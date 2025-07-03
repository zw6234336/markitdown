# SPDX-FileCopyrightText: 2024-present Microsoft <autogen@microsoft.com>
#
# SPDX-License-Identifier: MIT

import pytest
import tempfile
from pathlib import Path
from markitdown_api.client import MarkItDownClient, convert_file


@pytest.fixture
def test_file():
    """创建测试文件"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write('Hello, World!\nThis is a test file for MarkItDown API.')
        return f.name


@pytest.fixture  
def client():
    """创建测试客户端"""
    return MarkItDownClient(base_url="http://localhost:8000")


def test_client_init():
    """测试客户端初始化"""
    client = MarkItDownClient()
    assert client.base_url == "http://localhost:8000"
    assert client.timeout == 300


def test_client_init_custom():
    """测试客户端自定义初始化"""
    client = MarkItDownClient(base_url="http://example.com:9000", timeout=60)
    assert client.base_url == "http://example.com:9000"
    assert client.timeout == 60


def test_get_content_type():
    """测试获取内容类型"""
    client = MarkItDownClient()
    
    assert client._get_content_type(Path('test.pdf')) == 'application/pdf'
    assert client._get_content_type(Path('test.docx')) == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    assert client._get_content_type(Path('test.txt')) == 'text/plain'
    assert client._get_content_type(Path('test.unknown')) == 'application/octet-stream'


def test_context_manager():
    """测试上下文管理器"""
    with MarkItDownClient() as client:
        assert client.session is not None
    
    # 会话应该已关闭（但这个测试可能不会完全验证）


def test_convenience_functions():
    """测试便捷函数 - 这些函数需要服务器运行才能真正测试"""
    # 这里只测试函数存在性
    assert callable(convert_file)
    
    # 实际的网络调用测试应该在集成测试中进行
    with pytest.raises(Exception):  # 预期会失败，因为服务器可能未运行
        convert_file("nonexistent.txt")

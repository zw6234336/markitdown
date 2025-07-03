# SPDX-FileCopyrightText: 2024-present Microsoft <autogen@microsoft.com>
#
# SPDX-License-Identifier: MIT

import pytest
import json
import io
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


def test_health_check(client):
    """测试健康检查接口"""
    response = client.get('/api/v1/health')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert data['status'] == 'healthy'
    assert 'version' in data
    assert 'supported_formats' in data


def test_api_info(client):
    """测试 API 信息接口"""
    response = client.get('/api/v1/info')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert data['name'] == 'MarkItDown API'
    assert 'version' in data
    assert 'endpoints' in data


def test_supported_formats(client):
    """测试支持格式接口"""
    response = client.get('/api/v1/formats')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert 'formats' in data
    assert isinstance(data['formats'], list)
    assert 'pdf' in data['formats']


def test_convert_file_no_file(client):
    """测试文件转换接口 - 无文件"""
    response = client.post('/api/v1/convert')
    assert response.status_code == 400
    
    data = json.loads(response.data)
    assert 'error' in data


def test_convert_file_empty_filename(client):
    """测试文件转换接口 - 空文件名"""
    response = client.post('/api/v1/convert', data={'file': (io.BytesIO(b''), '')})
    assert response.status_code == 400


def test_convert_file_unsupported_format(client):
    """测试文件转换接口 - 不支持的格式"""
    data = {'file': (io.BytesIO(b'test content'), 'test.unsupported')}
    response = client.post('/api/v1/convert', data=data)
    assert response.status_code == 400


def test_convert_file_text(client):
    """测试文件转换接口 - 文本文件"""
    content = b'Hello, World!\nThis is a test.'
    data = {'file': (io.BytesIO(content), 'test.txt')}
    response = client.post('/api/v1/convert', data=data)
    assert response.status_code == 200
    
    result = json.loads(response.data)
    assert result['success'] is True
    assert 'markdown' in result
    assert 'Hello, World!' in result['markdown']


def test_convert_url_no_data(client):
    """测试 URL 转换接口 - 无数据"""
    response = client.post('/api/v1/convert/url')
    assert response.status_code == 400


def test_convert_url_no_url(client):
    """测试 URL 转换接口 - 无 URL"""
    response = client.post('/api/v1/convert/url', json={})
    assert response.status_code == 400


def test_index_redirect(client):
    """测试首页重定向"""
    response = client.get('/')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert 'message' in data
    assert 'version' in data

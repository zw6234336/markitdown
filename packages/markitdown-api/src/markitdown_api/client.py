# SPDX-FileCopyrightText: 2024-present Microsoft <autogen@microsoft.com>
#
# SPDX-License-Identifier: MIT

import requests
from typing import Optional, Dict, Any, Union
from pathlib import Path
import json


class MarkItDownClient:
    """MarkItDown API 客户端"""
    
    def __init__(self, base_url: str = "http://localhost:8000", timeout: int = 300):
        """
        初始化客户端
        
        Args:
            base_url: API 服务器地址
            timeout: 请求超时时间（秒）
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.session = requests.Session()
        
        # 设置默认 headers
        self.session.headers.update({
            'User-Agent': 'MarkItDown-API-Client/0.1.0'
        })
    
    def convert_file(
        self, 
        file_path: Union[str, Path], 
        keep_data_uris: bool = False,
        enable_plugins: bool = False
    ) -> Dict[str, Any]:
        """
        转换本地文件
        
        Args:
            file_path: 文件路径
            keep_data_uris: 是否保留数据 URI
            enable_plugins: 是否启用插件
            
        Returns:
            转换结果字典
            
        Raises:
            requests.RequestException: 请求错误
            FileNotFoundError: 文件不存在
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        url = f"{self.base_url}/api/v1/convert"
        
        with open(file_path, 'rb') as f:
            files = {'file': (file_path.name, f, self._get_content_type(file_path))}
            data = {
                'keep_data_uris': str(keep_data_uris).lower(),
                'enable_plugins': str(enable_plugins).lower()
            }
            
            response = self.session.post(
                url, 
                files=files, 
                data=data, 
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
    
    def convert_url(
        self, 
        url: str, 
        keep_data_uris: bool = False,
        enable_plugins: bool = False
    ) -> Dict[str, Any]:
        """
        转换 URL 指向的文件
        
        Args:
            url: 文件 URL
            keep_data_uris: 是否保留数据 URI
            enable_plugins: 是否启用插件
            
        Returns:
            转换结果字典
            
        Raises:
            requests.RequestException: 请求错误
        """
        api_url = f"{self.base_url}/api/v1/convert/url"
        
        data = {
            'url': url,
            'keep_data_uris': keep_data_uris,
            'enable_plugins': enable_plugins
        }
        
        response = self.session.post(
            api_url, 
            json=data, 
            timeout=self.timeout
        )
        response.raise_for_status()
        return response.json()
    
    def health_check(self) -> Dict[str, Any]:
        """
        健康检查
        
        Returns:
            健康状态字典
            
        Raises:
            requests.RequestException: 请求错误
        """
        url = f"{self.base_url}/api/v1/health"
        response = self.session.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    
    def get_supported_formats(self) -> Dict[str, Any]:
        """
        获取支持的文件格式
        
        Returns:
            支持格式字典
            
        Raises:
            requests.RequestException: 请求错误
        """
        url = f"{self.base_url}/api/v1/formats"
        response = self.session.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    
    def get_api_info(self) -> Dict[str, Any]:
        """
        获取 API 信息
        
        Returns:
            API 信息字典
            
        Raises:
            requests.RequestException: 请求错误
        """
        url = f"{self.base_url}/api/v1/info"
        response = self.session.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    
    def _get_content_type(self, file_path: Path) -> str:
        """根据文件扩展名获取 Content-Type"""
        suffix = file_path.suffix.lower()
        content_types = {
            '.pdf': 'application/pdf',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            '.pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
            '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            '.xls': 'application/vnd.ms-excel',
            '.html': 'text/html',
            '.htm': 'text/html',
            '.txt': 'text/plain',
            '.csv': 'text/csv',
            '.json': 'application/json',
            '.xml': 'application/xml',
            '.zip': 'application/zip',
            '.epub': 'application/epub+zip',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.mp3': 'audio/mpeg',
            '.wav': 'audio/wav',
            '.m4a': 'audio/mp4'
        }
        return content_types.get(suffix, 'application/octet-stream')
    
    def close(self):
        """关闭会话"""
        self.session.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


# 便捷函数
def convert_file(
    file_path: Union[str, Path],
    base_url: str = "http://localhost:8000",
    **kwargs
) -> Dict[str, Any]:
    """快速转换文件的便捷函数"""
    with MarkItDownClient(base_url) as client:
        return client.convert_file(file_path, **kwargs)


def convert_url(
    url: str,
    base_url: str = "http://localhost:8000", 
    **kwargs
) -> Dict[str, Any]:
    """快速转换 URL 的便捷函数"""
    with MarkItDownClient(base_url) as client:
        return client.convert_url(url, **kwargs)

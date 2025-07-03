# SPDX-FileCopyrightText: 2024-present Microsoft <autogen@microsoft.com>
#
# SPDX-License-Identifier: MIT

from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from datetime import datetime


@dataclass
class ConvertRequest:
    """文件转换请求模型"""
    keep_data_uris: bool = False
    enable_plugins: bool = False


@dataclass
class ConvertUrlRequest:
    """URL 转换请求模型"""
    url: str
    keep_data_uris: bool = False
    enable_plugins: bool = False


@dataclass
class ConvertResponse:
    """转换响应模型"""
    success: bool
    markdown: str
    title: Optional[str] = None
    metadata: Dict[str, Any] = None
    processing_time: Optional[float] = None
    timestamp: str = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
        if self.timestamp is None:
            self.timestamp = datetime.utcnow().isoformat()


@dataclass
class ErrorResponse:
    """错误响应模型"""
    error: str
    error_type: str = "ConversionError"
    timestamp: str = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow().isoformat()


@dataclass
class HealthResponse:
    """健康检查响应模型"""
    status: str
    version: str
    supported_formats: List[str]
    timestamp: str = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow().isoformat()

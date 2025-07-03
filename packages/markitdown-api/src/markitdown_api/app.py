# SPDX-FileCopyrightText: 2024-present Microsoft <autogen@microsoft.com>
#
# SPDX-License-Identifier: MIT

import os
import time
import tempfile
import logging
import json
from typing import Optional, Dict, Any
from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge
from markitdown import MarkItDown
from .__about__ import __version__
from .models import ConvertResponse, ErrorResponse, HealthResponse

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 支持的文件格式
SUPPORTED_EXTENSIONS = {
    'pdf', 'docx', 'pptx', 'xlsx', 'xls',
    'html', 'htm', 'csv', 'json', 'xml', 
    'zip', 'epub', 'txt', 'md', 'msg',
    'jpg', 'jpeg', 'png', 'gif', 'bmp',
    'mp3', 'wav', 'm4a', 'ipynb'
}

def create_app(config: Optional[Dict[str, Any]] = None) -> Flask:
    """创建 Flask 应用"""
    app = Flask(__name__)
    
    # 启用 CORS
    CORS(app, origins=["*"])
    
    # 默认配置
    app.config.update({
        'MAX_CONTENT_LENGTH': 50 * 1024 * 1024,  # 50MB 最大文件大小
        'UPLOAD_FOLDER': tempfile.gettempdir(),
        'JSON_SORT_KEYS': False,
        'JSONIFY_PRETTYPRINT_REGULAR': True,
        'JSON_AS_ASCII': False,  # 确保中文字符不被转义
    })
    
    # 应用自定义配置
    if config:
        app.config.update(config)
    
    # 自定义 JSON 响应函数，确保中文正确显示
    def json_response(data, status_code=200):
        """创建 JSON 响应，确保中文字符正确显示"""
        response = Response(
            json.dumps(data, ensure_ascii=False, indent=2),
            status=status_code,
            mimetype='application/json; charset=utf-8'
        )
        return response
    
    # 初始化 MarkItDown 实例
    markitdown_default = MarkItDown(enable_plugins=False)
    markitdown_with_plugins = MarkItDown(enable_plugins=True)
    
    def _allowed_file(filename: str) -> bool:
        """检查文件扩展名是否支持"""
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in SUPPORTED_EXTENSIONS
    
    def _get_markitdown_instance(enable_plugins: bool = False) -> MarkItDown:
        """获取 MarkItDown 实例"""
        return markitdown_with_plugins if enable_plugins else markitdown_default
    
    def _handle_conversion_error(e: Exception) -> tuple:
        """处理转换错误"""
        logger.error(f"转换错误: {str(e)}", exc_info=True)
        error_response = ErrorResponse(
            error=str(e),
            error_type=type(e).__name__
        )
        return json_response(error_response.__dict__, 500)
    
    @app.errorhandler(413)
    @app.errorhandler(RequestEntityTooLarge)
    def handle_file_too_large(e):
        """处理文件过大错误"""
        error_response = ErrorResponse(
            error="文件大小超过限制 (50MB)",
            error_type="FileTooLargeError"
        )
        return json_response(error_response.__dict__, 413)
    
    @app.errorhandler(400)
    def handle_bad_request(e):
        """处理错误请求"""
        error_response = ErrorResponse(
            error="请求参数错误",
            error_type="BadRequestError"
        )
        return json_response(error_response.__dict__, 400)
    
    @app.errorhandler(500)
    def handle_internal_error(e):
        """处理内部服务器错误"""
        logger.error(f"内部服务器错误: {str(e)}", exc_info=True)
        error_response = ErrorResponse(
            error="内部服务器错误",
            error_type="InternalServerError"
        )
        return json_response(error_response.__dict__, 500)
    
    @app.route('/api/v1/convert', methods=['POST'])
    def convert_file():
        """转换上传的文件为 Markdown"""
        start_time = time.time()
        
        try:
            # 检查文件是否在请求中
            if 'file' not in request.files:
                error_response = ErrorResponse(error="未提供文件")
                return json_response(error_response.__dict__, 400)
            
            file = request.files['file']
            
            if file.filename == '':
                error_response = ErrorResponse(error="未选择文件")
                return json_response(error_response.__dict__, 400)
            
            if not _allowed_file(file.filename):
                error_response = ErrorResponse(
                    error=f"不支持的文件类型。支持的格式: {', '.join(sorted(SUPPORTED_EXTENSIONS))}"
                )
                return json_response(error_response.__dict__, 400)
            
            # 获取可选参数
            keep_data_uris = request.form.get('keep_data_uris', 'false').lower() == 'true'
            enable_plugins = request.form.get('enable_plugins', 'false').lower() == 'true'
            
            # 获取 MarkItDown 实例
            md_instance = _get_markitdown_instance(enable_plugins)
            
            # 转换文件
            result = md_instance.convert(
                file.stream,
                stream_info={
                    'filename': secure_filename(file.filename),
                    'mimetype': file.content_type
                },
                keep_data_uris=keep_data_uris
            )
            
            # 构建响应
            processing_time = time.time() - start_time
            response = ConvertResponse(
                success=True,
                markdown=result.text_content,
                title=getattr(result, 'title', None),
                metadata=getattr(result, 'metadata', {}),
                processing_time=round(processing_time, 3)
            )
            
            logger.info(f"文件转换成功: {file.filename}, 耗时: {processing_time:.3f}s")
            return json_response(response.__dict__)
            
        except Exception as e:
            return _handle_conversion_error(e)
    
    @app.route('/api/v1/convert/url', methods=['POST'])
    def convert_url():
        """通过 URL 转换文件为 Markdown"""
        start_time = time.time()
        
        try:
            data = request.get_json()
            if not data or 'url' not in data:
                error_response = ErrorResponse(error="缺少 URL 参数")
                return json_response(error_response.__dict__, 400)
            
            url = data['url']
            keep_data_uris = data.get('keep_data_uris', False)
            enable_plugins = data.get('enable_plugins', False)
            
            # 获取 MarkItDown 实例
            md_instance = _get_markitdown_instance(enable_plugins)
            
            # 转换 URL
            result = md_instance.convert_uri(
                url,
                keep_data_uris=keep_data_uris
            )
            
            # 构建响应
            processing_time = time.time() - start_time
            response = ConvertResponse(
                success=True,
                markdown=result.text_content,
                title=getattr(result, 'title', None),
                metadata=getattr(result, 'metadata', {}),
                processing_time=round(processing_time, 3)
            )
            
            logger.info(f"URL 转换成功: {url}, 耗时: {processing_time:.3f}s")
            return json_response(response.__dict__)
            
        except Exception as e:
            return _handle_conversion_error(e)
    
    @app.route('/api/v1/health', methods=['GET'])
    def health_check():
        """健康检查接口"""
        try:
            response = HealthResponse(
                status="healthy",
                version=__version__,
                supported_formats=sorted(list(SUPPORTED_EXTENSIONS))
            )
            return json_response(response.__dict__)
        except Exception as e:
            return _handle_conversion_error(e)
    
    @app.route('/api/v1/formats', methods=['GET'])
    def supported_formats():
        """获取支持的文件格式"""
        return json_response({
            'formats': sorted(list(SUPPORTED_EXTENSIONS)),
            'description': '支持的文件格式列表',
            'count': len(SUPPORTED_EXTENSIONS)
        })
    
    @app.route('/api/v1/info', methods=['GET'])
    def api_info():
        """获取 API 信息"""
        return json_response({
            'name': 'MarkItDown API',
            'version': __version__,
            'description': '将各种文档格式转换为 Markdown 的 HTTP API',
            'endpoints': {
                'POST /api/v1/convert': '上传文件并转换为 Markdown',
                'POST /api/v1/convert/url': '通过 URL 转换文件为 Markdown',
                'GET /api/v1/health': '健康检查',
                'GET /api/v1/formats': '获取支持的文件格式',
                'GET /api/v1/info': '获取 API 信息'
            },
            'max_file_size': '50MB',
            'supported_formats_count': len(SUPPORTED_EXTENSIONS)
        })
    
    @app.route('/', methods=['GET'])
    def index():
        """首页重定向到 API 信息"""
        return json_response({
            'message': '欢迎使用 MarkItDown API',
            'version': __version__,
            'docs': '/api/v1/info'
        })
    
    return app

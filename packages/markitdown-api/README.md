# MarkItDown API

[![PyPI](https://img.shields.io/pypi/v/markitdown-api.svg)](https://pypi.org/project/markitdown-api/)
[![Built by AutoGen Team](https://img.shields.io/badge/Built%20by-AutoGen%20Team-blue)](https://github.com/microsoft/autogen)

**MarkItDown API** 是一个基于 [MarkItDown](https://github.com/microsoft/markitdown) 的 HTTP API 服务器，提供文档转换为 Markdown 的 RESTful 接口。

## ✨ 特性

- 🚀 **高性能**: 基于 Flask/Gunicorn 的高性能 Web 服务
- 📄 **多格式支持**: 支持 PDF、Word、PowerPoint、Excel、图片、音频等多种格式
- 🔌 **插件系统**: 支持 MarkItDown 第三方插件
- 🐳 **Docker 支持**: 提供开箱即用的 Docker 镜像
- 📊 **完整 API**: RESTful API 设计，支持文件上传和 URL 转换
- 🛡️ **安全性**: 文件类型验证、大小限制、错误处理
- 📖 **易于集成**: 提供 Python 客户端 SDK

## 🚀 快速开始

### 安装

```bash
pip install markitdown-api
```

### 启动服务

```bash
# 开发模式
markitdown-api --host 127.0.0.1 --port 8000

# 生产模式
markitdown-api --host 0.0.0.0 --port 8000 --production --workers 4
```

### Docker 方式

```bash
# 构建镜像
docker build -t markitdown-api .

# 运行容器
docker run -p 8000:8000 markitdown-api

# 或使用 docker-compose
docker-compose up -d
```

## 📋 API 接口

### 基本信息

- **基础 URL**: `http://localhost:8000`
- **API 版本**: `v1`
- **最大文件大小**: 50MB (可配置)

### 接口列表

#### 1. 文件上传转换

```http
POST /api/v1/convert
Content-Type: multipart/form-data

file: <文件>
keep_data_uris: false (可选)
enable_plugins: false (可选)
```

**响应示例**:
```json
{
  "success": true,
  "markdown": "# 文档标题\n\n文档内容...",
  "title": "文档标题",
  "metadata": {},
  "processing_time": 1.234,
  "timestamp": "2024-01-01T12:00:00Z"
}
```

#### 2. URL 转换

```http
POST /api/v1/convert/url
Content-Type: application/json

{
  "url": "https://example.com/document.pdf",
  "keep_data_uris": false,
  "enable_plugins": false
}
```

#### 3. 健康检查

```http
GET /api/v1/health
```

**响应示例**:
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "supported_formats": ["pdf", "docx", "pptx", ...]
}
```

#### 4. 支持格式

```http
GET /api/v1/formats
```

#### 5. API 信息

```http
GET /api/v1/info
```

## 🐍 Python 客户端

### 安装客户端

```bash
pip install markitdown-api
```

### 使用示例

```python
from markitdown_api import MarkItDownClient

# 创建客户端
client = MarkItDownClient(base_url="http://localhost:8000")

# 转换本地文件
result = client.convert_file("document.pdf")
print(result['markdown'])

# 转换 URL
result = client.convert_url("https://example.com/document.pdf")
print(result['markdown'])

# 健康检查
health = client.health_check()
print(health['status'])

# 使用上下文管理器
with MarkItDownClient() as client:
    result = client.convert_file("document.pdf")
```

### 便捷函数

```python
from markitdown_api import convert_file, convert_url

# 快速转换
result = convert_file("document.pdf")
result = convert_url("https://example.com/document.pdf")
```

## 🔧 配置选项

### 命令行参数

```bash
markitdown-api --help
```

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `--host` | 127.0.0.1 | 绑定主机地址 |
| `--port` | 8000 | 绑定端口 |
| `--debug` | False | 启用调试模式 |
| `--max-file-size` | 50 | 最大文件大小(MB) |
| `--workers` | 4 | Gunicorn worker 数 |
| `--production` | False | 生产模式 |

### 环境变量

```bash
export MARKITDOWN_API_HOST=0.0.0.0
export MARKITDOWN_API_PORT=8000
export MARKITDOWN_API_MAX_FILE_SIZE=100
```

## 🐳 Docker 部署

### Dockerfile

```dockerfile
FROM markitdown-api:latest
EXPOSE 8000
CMD ["markitdown-api", "--host", "0.0.0.0", "--production"]
```

### docker-compose.yml

```yaml
version: '3.8'
services:
  markitdown-api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - PYTHONUNBUFFERED=1
    restart: unless-stopped
```

## 📁 支持的文件格式

| 格式 | 扩展名 | 说明 |
|------|--------|------|
| PDF | .pdf | PDF 文档 |
| Word | .docx | Word 文档 |
| PowerPoint | .pptx | PowerPoint 演示文稿 |
| Excel | .xlsx, .xls | Excel 电子表格 |
| 图片 | .jpg, .png, .gif | 图像文件 (OCR) |
| 音频 | .mp3, .wav, .m4a | 音频文件 (转录) |
| 网页 | .html, .htm | HTML 文件 |
| 文本 | .txt, .md | 纯文本文件 |
| 数据 | .csv, .json, .xml | 结构化数据 |
| 压缩 | .zip | ZIP 压缩包 |
| 电子书 | .epub | EPUB 电子书 |
| 其他 | .msg, .ipynb | Outlook 邮件、Jupyter 笔记本 |

## 🔌 插件支持

启用第三方插件:

```python
# API 调用时启用插件
result = client.convert_file("document.rtf", enable_plugins=True)
```

```bash
# 命令行启用插件
curl -X POST -F "file=@document.rtf" -F "enable_plugins=true" \
     http://localhost:8000/api/v1/convert
```

## 🛡️ 安全考虑

1. **文件大小限制**: 默认 50MB，可配置
2. **文件类型验证**: 只允许支持的文件类型
3. **输入清理**: 自动清理文件名和路径
4. **错误处理**: 完善的错误处理和日志记录
5. **资源限制**: 防止资源耗尽攻击

## 📊 监控和日志

### 健康检查

```bash
curl http://localhost:8000/api/v1/health
```

### 日志配置

```python
import logging
logging.basicConfig(level=logging.INFO)
```

### 指标监控

- 请求计数
- 响应时间
- 错误率
- 文件处理统计

## 🧪 测试

```bash
# 安装测试依赖
pip install markitdown-api[dev]

# 运行测试
pytest tests/

# 运行覆盖率测试
pytest --cov=markitdown_api tests/
```

## 🤝 贡献

欢迎贡献代码！请查看 [贡献指南](https://github.com/microsoft/markitdown/blob/main/CONTRIBUTING.md)。

## 📄 许可证

MIT License - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🔗 相关链接

- [MarkItDown 主项目](https://github.com/microsoft/markitdown)
- [MarkItDown MCP 服务器](https://github.com/microsoft/markitdown/tree/main/packages/markitdown-mcp)
- [问题反馈](https://github.com/microsoft/markitdown/issues)

# MarkItDown API 部署指南

本文档介绍如何部署 MarkItDown API 服务到生产环境。

## 📋 目录

- [系统要求](#系统要求)
- [安装部署](#安装部署)
- [配置选项](#配置选项)
- [生产部署](#生产部署)
- [Docker 部署](#docker-部署)
- [反向代理](#反向代理)
- [监控和日志](#监控和日志)
- [故障排除](#故障排除)

## 🖥️ 系统要求

### 硬件要求
- **CPU**: 2 核心及以上
- **内存**: 4GB 及以上 (推荐 8GB)
- **存储**: 10GB 及以上可用空间
- **网络**: 稳定的网络连接

### 软件要求
- **操作系统**: Linux (Ubuntu 20.04+, CentOS 8+) / macOS / Windows
- **Python**: 3.10 或更高版本
- **Docker**: 20.10+ (可选)
- **Nginx**: 1.18+ (可选，用于反向代理)

## 🚀 安装部署

### 1. 环境准备

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip python3-venv curl

# CentOS/RHEL
sudo yum update
sudo yum install python3 python3-pip curl

# macOS (使用 Homebrew)
brew install python@3.11 curl
```

### 2. 创建虚拟环境

```bash
# 创建项目目录
mkdir /opt/markitdown-api
cd /opt/markitdown-api

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 升级 pip
pip install --upgrade pip
```

### 3. 安装应用

```bash
# 从源码安装
git clone https://github.com/microsoft/markitdown.git
cd markitdown/packages/markitdown-api

# 安装依赖
pip install -e "../markitdown[all]"
pip install -e ".[dev]"
pip install gunicorn

# 或从 PyPI 安装 (未来版本)
# pip install markitdown-api[all]
```

### 4. 基本测试

```bash
# 启动开发服务器
markitdown-api --host 127.0.0.1 --port 8000

# 在另一个终端测试
curl http://127.0.0.1:8000/api/v1/health
```

## ⚙️ 配置选项

### 环境变量

创建 `.env` 文件:

```bash
# 服务配置
MARKITDOWN_API_HOST=0.0.0.0
MARKITDOWN_API_PORT=8000
MARKITDOWN_API_MAX_FILE_SIZE=100  # MB

# 日志配置
MARKITDOWN_API_LOG_LEVEL=INFO
MARKITDOWN_API_LOG_FILE=/var/log/markitdown-api.log

# 安全配置
MARKITDOWN_API_ALLOWED_ORIGINS=*
MARKITDOWN_API_MAX_REQUESTS_PER_MINUTE=60
```

### 配置文件

创建 `config.py`:

```python
import os

class Config:
    MAX_CONTENT_LENGTH = int(os.getenv('MARKITDOWN_API_MAX_FILE_SIZE', 50)) * 1024 * 1024
    JSON_SORT_KEYS = False
    JSONIFY_PRETTYPRINT_REGULAR = True
    
class ProductionConfig(Config):
    DEBUG = False
    TESTING = False
    
class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
```

## 🏭 生产部署

### 1. 使用 Gunicorn

创建 `gunicorn.conf.py`:

```python
# Gunicorn 配置文件

# 服务器套接字
bind = "0.0.0.0:8000"
backlog = 2048

# Worker 进程
workers = 4
worker_class = "sync"
worker_connections = 1000
timeout = 300
keepalive = 5

# 重启和优雅关闭
max_requests = 1000
max_requests_jitter = 100
preload_app = True
graceful_timeout = 30

# 日志
accesslog = "/var/log/markitdown-api/access.log"
errorlog = "/var/log/markitdown-api/error.log"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# 进程命名
proc_name = "markitdown-api"

# 安全
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190
```

启动服务:

```bash
# 创建日志目录
sudo mkdir -p /var/log/markitdown-api
sudo chown $USER:$USER /var/log/markitdown-api

# 启动 Gunicorn
gunicorn --config gunicorn.conf.py "markitdown_api.app:create_app()"
```

### 2. 使用 Systemd

创建 `/etc/systemd/system/markitdown-api.service`:

```ini
[Unit]
Description=MarkItDown API Server
After=network.target

[Service]
Type=forking
User=www-data
Group=www-data
WorkingDirectory=/opt/markitdown-api
Environment=PATH=/opt/markitdown-api/venv/bin
ExecStart=/opt/markitdown-api/venv/bin/gunicorn --config gunicorn.conf.py --daemon --pid /var/run/markitdown-api.pid "markitdown_api.app:create_app()"
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true
PIDFile=/var/run/markitdown-api.pid

[Install]
WantedBy=multi-user.target
```

管理服务:

```bash
# 重新加载 systemd
sudo systemctl daemon-reload

# 启动服务
sudo systemctl start markitdown-api

# 开机自启
sudo systemctl enable markitdown-api

# 查看状态
sudo systemctl status markitdown-api

# 查看日志
sudo journalctl -u markitdown-api -f
```

## 🐳 Docker 部署

### 1. 单容器部署

```bash
# 构建镜像
docker build -t markitdown-api:latest .

# 运行容器
docker run -d \
  --name markitdown-api \
  --restart unless-stopped \
  -p 8000:8000 \
  -v /var/log/markitdown:/app/logs \
  markitdown-api:latest
```

### 2. Docker Compose 部署

`docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  markitdown-api:
    build: .
    container_name: markitdown-api
    restart: unless-stopped
    ports:
      - "8000:8000"
    environment:
      - PYTHONUNBUFFERED=1
      - MARKITDOWN_API_LOG_LEVEL=INFO
    volumes:
      - ./logs:/app/logs
      - ./uploads:/app/uploads
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/v1/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: '1.0'
        reservations:
          memory: 1G
          cpus: '0.5'

  nginx:
    image: nginx:alpine
    container_name: markitdown-nginx
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - markitdown-api

volumes:
  logs:
  uploads:
```

启动:

```bash
docker-compose -f docker-compose.prod.yml up -d
```

## 🔄 反向代理

### Nginx 配置

`/etc/nginx/sites-available/markitdown-api`:

```nginx
upstream markitdown_backend {
    server 127.0.0.1:8000;
    # 如果有多个实例，可以添加更多服务器
    # server 127.0.0.1:8001;
    # server 127.0.0.1:8002;
}

server {
    listen 80;
    server_name api.markitdown.example.com;
    
    # HTTP 重定向到 HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.markitdown.example.com;
    
    # SSL 配置
    ssl_certificate /path/to/ssl/certificate.crt;
    ssl_certificate_key /path/to/ssl/private.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    
    # 安全头
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload";
    
    # 客户端最大请求大小 (用于文件上传)
    client_max_body_size 100M;
    
    # 代理设置
    location / {
        proxy_pass http://markitdown_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # 超时设置
        proxy_connect_timeout 60s;
        proxy_send_timeout 300s;
        proxy_read_timeout 300s;
        
        # 缓冲设置
        proxy_buffering on;
        proxy_buffer_size 4k;
        proxy_buffers 8 4k;
    }
    
    # 健康检查 (不记录访问日志)
    location /api/v1/health {
        proxy_pass http://markitdown_backend;
        access_log off;
    }
    
    # 静态文件 (如果有)
    location /static/ {
        alias /opt/markitdown-api/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # 日志配置
    access_log /var/log/nginx/markitdown-api.access.log;
    error_log /var/log/nginx/markitdown-api.error.log;
}
```

启用站点:

```bash
# 创建符号链接
sudo ln -s /etc/nginx/sites-available/markitdown-api /etc/nginx/sites-enabled/

# 测试配置
sudo nginx -t

# 重新加载 Nginx
sudo systemctl reload nginx
```

## 📊 监控和日志

### 1. 应用监控

安装监控依赖:

```bash
pip install prometheus-client
```

添加监控端点到应用:

```python
# 在 app.py 中添加
from prometheus_client import Counter, Histogram, generate_latest

# 指标
REQUEST_COUNT = Counter('requests_total', 'Total requests', ['method', 'endpoint'])
REQUEST_DURATION = Histogram('request_duration_seconds', 'Request duration')

@app.route('/metrics')
def metrics():
    return generate_latest()
```

### 2. 日志聚合

使用 ELK Stack 或类似工具:

```yaml
# docker-compose.monitoring.yml
version: '3.8'

services:
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:7.14.0
    environment:
      - discovery.type=single-node
    volumes:
      - elasticsearch_data:/usr/share/elasticsearch/data

  logstash:
    image: docker.elastic.co/logstash/logstash:7.14.0
    volumes:
      - ./logstash.conf:/usr/share/logstash/pipeline/logstash.conf

  kibana:
    image: docker.elastic.co/kibana/kibana:7.14.0
    ports:
      - "5601:5601"
    environment:
      - ELASTICSEARCH_HOSTS=http://elasticsearch:9200

volumes:
  elasticsearch_data:
```

### 3. 健康检查脚本

`health_check.sh`:

```bash
#!/bin/bash

API_URL="http://localhost:8000/api/v1/health"
TIMEOUT=10

response=$(curl -s -w "%{http_code}" --max-time $TIMEOUT "$API_URL")
http_code="${response: -3}"

if [ "$http_code" -eq 200 ]; then
    echo "✅ API 健康检查通过"
    exit 0
else
    echo "❌ API 健康检查失败 (HTTP $http_code)"
    exit 1
fi
```

## 🐛 故障排除

### 常见问题

1. **服务启动失败**
   ```bash
   # 检查端口占用
   sudo netstat -tlnp | grep :8000
   
   # 检查日志
   sudo journalctl -u markitdown-api -f
   ```

2. **内存不足**
   ```bash
   # 查看内存使用
   free -h
   
   # 调整 worker 数量
   # 在 gunicorn.conf.py 中减少 workers 数量
   ```

3. **文件上传失败**
   - 检查文件大小限制
   - 检查磁盘空间
   - 检查权限设置

4. **依赖缺失**
   ```bash
   # 安装可选依赖
   pip install 'markitdown[all]'
   ```

### 性能优化

1. **调整 Worker 数量**
   ```python
   # 推荐公式: (CPU核心数 × 2) + 1
   workers = 4
   ```

2. **启用 Gzip 压缩**
   ```nginx
   gzip on;
   gzip_types text/plain application/json;
   ```

3. **缓存策略**
   - 对相同文件的转换结果进行缓存
   - 使用 Redis 存储缓存

### 安全建议

1. **访问控制**
   - 使用防火墙限制访问
   - 实现 API 密钥认证
   - 配置速率限制

2. **文件安全**
   - 验证文件类型
   - 扫描恶意内容
   - 限制文件大小

3. **HTTPS 部署**
   - 使用有效的 SSL 证书
   - 配置 HSTS 头
   - 禁用不安全的 SSL 协议

## 📞 支持

如果遇到问题，可以：

1. 查看 [GitHub Issues](https://github.com/microsoft/markitdown/issues)
2. 阅读 [MarkItDown 文档](https://github.com/microsoft/markitdown)
3. 提交新的 Issue 报告问题

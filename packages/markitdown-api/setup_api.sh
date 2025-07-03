#!/bin/bash

# MarkItDown API 安装和测试脚本
# 使用方法: ./setup_api.sh [install|test|start|stop]

set -e

API_DIR="packages/markitdown-api"
API_PORT=8000

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查 Python 版本
check_python() {
    log_info "检查 Python 版本..."
    if ! python3 --version | grep -q "Python 3.1[0-9]"; then
        log_error "需要 Python 3.10 或更高版本"
        exit 1
    fi
    log_success "Python 版本检查通过"
}

# 安装依赖
install_dependencies() {
    log_info "安装 MarkItDown API..."
    
    cd $API_DIR
    
    # 安装主包依赖
    log_info "安装核心包..."
    pip install -e "../markitdown[all]"
    
    # 安装 API 包
    log_info "安装 API 包..."
    pip install -e ".[dev]"
    
    # 安装额外依赖
    log_info "安装额外依赖..."
    pip install flask-cors gunicorn
    
    cd - > /dev/null
    log_success "依赖安装完成"
}

# 运行测试
run_tests() {
    log_info "运行测试..."
    
    cd $API_DIR
    
    # 运行单元测试
    log_info "运行单元测试..."
    pytest tests/ -v
    
    cd - > /dev/null
    log_success "测试完成"
}

# 启动服务
start_service() {
    log_info "启动 MarkItDown API 服务..."
    
    cd $API_DIR
    
    # 检查端口是否被占用
    if lsof -Pi :$API_PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
        log_warning "端口 $API_PORT 已被占用"
        log_info "尝试停止现有服务..."
        pkill -f "markitdown-api" || true
        sleep 2
    fi
    
    # 启动服务
    log_info "在端口 $API_PORT 启动服务..."
    nohup python -m markitdown_api --host 0.0.0.0 --port $API_PORT > api.log 2>&1 &
    
    # 等待服务启动
    sleep 3
    
    # 检查服务状态
    if curl -f http://localhost:$API_PORT/api/v1/health > /dev/null 2>&1; then
        log_success "API 服务启动成功"
        log_info "服务地址: http://localhost:$API_PORT"
        log_info "API 文档: http://localhost:$API_PORT/api/v1/info"
        log_info "健康检查: http://localhost:$API_PORT/api/v1/health"
    else
        log_error "API 服务启动失败"
        tail api.log
        exit 1
    fi
    
    cd - > /dev/null
}

# 停止服务
stop_service() {
    log_info "停止 MarkItDown API 服务..."
    
    pkill -f "markitdown-api" || true
    
    log_success "服务已停止"
}

# 测试 API
test_api() {
    log_info "测试 API 接口..."
    
    # 等待服务准备就绪
    sleep 2
    
    # 测试健康检查
    log_info "测试健康检查..."
    if curl -f http://localhost:$API_PORT/api/v1/health; then
        log_success "健康检查通过"
    else
        log_error "健康检查失败"
        return 1
    fi
    
    # 测试支持格式
    log_info "测试支持格式..."
    if curl -f http://localhost:$API_PORT/api/v1/formats; then
        log_success "支持格式查询通过"
    else
        log_error "支持格式查询失败"
        return 1
    fi
    
    # 创建测试文件
    echo "Hello, World! This is a test document for MarkItDown API." > /tmp/test.txt
    
    # 测试文件转换
    log_info "测试文件转换..."
    if curl -f -X POST -F "file=@/tmp/test.txt" http://localhost:$API_PORT/api/v1/convert; then
        log_success "文件转换测试通过"
    else
        log_error "文件转换测试失败"
        return 1
    fi
    
    # 清理测试文件
    rm -f /tmp/test.txt
    
    log_success "所有 API 测试通过"
}

# 构建 Docker 镜像
build_docker() {
    log_info "构建 Docker 镜像..."
    
    cd $API_DIR
    
    docker build -t markitdown-api:latest .
    
    cd - > /dev/null
    log_success "Docker 镜像构建完成"
}

# 运行 Docker 容器
run_docker() {
    log_info "运行 Docker 容器..."
    
    # 停止现有容器
    docker stop markitdown-api-container 2>/dev/null || true
    docker rm markitdown-api-container 2>/dev/null || true
    
    # 运行新容器
    docker run -d \
        --name markitdown-api-container \
        -p $API_PORT:8000 \
        markitdown-api:latest
    
    # 等待容器启动
    sleep 5
    
    # 检查容器状态
    if docker ps | grep -q markitdown-api-container; then
        log_success "Docker 容器运行成功"
        log_info "服务地址: http://localhost:$API_PORT"
    else
        log_error "Docker 容器启动失败"
        docker logs markitdown-api-container
        exit 1
    fi
}

# 显示使用说明
show_usage() {
    echo "使用说明:"
    echo "  $0 install          - 安装依赖"
    echo "  $0 test             - 运行测试"
    echo "  $0 start            - 启动服务"
    echo "  $0 stop             - 停止服务"
    echo "  $0 restart          - 重启服务"
    echo "  $0 test-api         - 测试 API"
    echo "  $0 docker-build     - 构建 Docker 镜像"
    echo "  $0 docker-run       - 运行 Docker 容器"
    echo "  $0 all              - 完整安装和启动流程"
}

# 主逻辑
case "${1:-help}" in
    "install")
        check_python
        install_dependencies
        ;;
    "test")
        run_tests
        ;;
    "start")
        start_service
        ;;
    "stop")
        stop_service
        ;;
    "restart")
        stop_service
        start_service
        ;;
    "test-api")
        test_api
        ;;
    "docker-build")
        build_docker
        ;;
    "docker-run")
        build_docker
        run_docker
        ;;
    "all")
        check_python
        install_dependencies
        run_tests
        start_service
        test_api
        ;;
    "help"|*)
        show_usage
        ;;
esac

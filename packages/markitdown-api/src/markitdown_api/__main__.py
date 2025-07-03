# SPDX-FileCopyrightText: 2024-present Microsoft <autogen@microsoft.com>
#
# SPDX-License-Identifier: MIT

import argparse
import sys
import os
from .__about__ import __version__
from .app import create_app


def main():
    """主入口函数"""
    parser = argparse.ArgumentParser(
        description='MarkItDown HTTP API Server',
        prog='markitdown-api'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version=f'%(prog)s {__version__}'
    )
    
    parser.add_argument(
        '--host',
        default='127.0.0.1',
        help='绑定的主机地址 (默认: 127.0.0.1)'
    )
    
    parser.add_argument(
        '--port',
        type=int,
        default=8000,
        help='绑定的端口号 (默认: 8000)'
    )
    
    parser.add_argument(
        '--debug',
        action='store_true',
        help='启用调试模式'
    )
    
    parser.add_argument(
        '--max-file-size',
        type=int,
        default=50,
        help='最大文件大小限制 (MB，默认: 50)'
    )
    
    parser.add_argument(
        '--workers',
        type=int,
        default=4,
        help='Gunicorn worker 进程数 (默认: 4)'
    )
    
    parser.add_argument(
        '--production',
        action='store_true',
        help='生产模式，使用 Gunicorn 启动'
    )
    
    args = parser.parse_args()
    
    # 配置应用
    config = {
        'MAX_CONTENT_LENGTH': args.max_file_size * 1024 * 1024,
        'DEBUG': args.debug
    }
    
    app = create_app(config)
    
    if args.production:
        # 生产模式使用 Gunicorn
        try:
            import gunicorn.app.wsgiapp as wsgi
            sys.argv = [
                'gunicorn',
                '--bind', f'{args.host}:{args.port}',
                '--workers', str(args.workers),
                '--worker-class', 'sync',
                '--timeout', '300',
                '--max-requests', '1000',
                '--max-requests-jitter', '100',
                '--preload',
                'markitdown_api.app:create_app()'
            ]
            wsgi.run()
        except ImportError:
            print("错误: 生产模式需要安装 gunicorn")
            print("请运行: pip install gunicorn")
            sys.exit(1)
    else:
        # 开发模式
        print(f"🚀 启动 MarkItDown API 服务器")
        print(f"📍 地址: http://{args.host}:{args.port}")
        print(f"🔧 调试模式: {'开启' if args.debug else '关闭'}")
        print(f"📁 最大文件大小: {args.max_file_size}MB")
        print(f"🔗 API 文档: http://{args.host}:{args.port}/api/v1/info")
        print(f"❤️  健康检查: http://{args.host}:{args.port}/api/v1/health")
        
        app.run(
            host=args.host,
            port=args.port,
            debug=args.debug,
            threaded=True
        )


if __name__ == '__main__':
    main()

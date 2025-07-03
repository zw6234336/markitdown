# SPDX-FileCopyrightText: 2024-present Microsoft <autogen@microsoft.com>
#
# SPDX-License-Identifier: MIT

from .__about__ import __version__

# 延迟导入以避免循环依赖
def create_app(*args, **kwargs):
    from .app import create_app as _create_app
    return _create_app(*args, **kwargs)

class MarkItDownClient:
    def __new__(cls, *args, **kwargs):
        from .client import MarkItDownClient as _MarkItDownClient
        return _MarkItDownClient(*args, **kwargs)

__all__ = ["__version__", "create_app", "MarkItDownClient"]

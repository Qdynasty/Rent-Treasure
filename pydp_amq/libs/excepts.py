# -*- coding: utf-8 -*-
# Author: chao
# Version: 1.0.0
# Date: 2021-12-27

class ExceptionBase(Exception):
    """基础异常"""
    pass


class ExceptionService(ExceptionBase):
    """服务异常"""
    pass


class ExceptionServer(ExceptionBase):
    """服务异常"""
    pass


class ExceptionError(ExceptionBase):
    """错误异常"""
    pass


class ExceptionWarning(ExceptionBase):
    """警告异常"""
    pass


class ExceptionInfo(ExceptionBase):
    """消息异常"""
    pass


class ExceptionDocumentTooLarge(ExceptionBase):
    """mongo docs DocumentTooLarge"""
    pass

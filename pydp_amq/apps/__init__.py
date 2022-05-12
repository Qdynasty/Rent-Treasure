#!/usr/bin/env python
# -*- coding:utf-8 -*-

# Intro: Component connector
# Author: Q.dynasty
# Version: 1.2.0

import threading
import logging
from typing import List
from queue import Queue
from concurrent.futures import ThreadPoolExecutor

from pydp_amq.apps.core import signals
from pydp_amq.apps.core.signals import SignalAgent
from pydp_amq.apps.managers import ManageConnector
from pydp_amq.libs.config_file import ConfigFile
from pydp_amq.libs.registry import Registry

logger = logging.getLogger(__name__)

ServerAlias = List[str]


class AMQSection(object):

    def __init__(self, config_dir, maxsize):
        """
        配置参数 ：
        @param config_dir :  配置目录
        @param maxsize :  最大队列容量
        @warning: 队列容量更具实际需求配置默认 1000*60
        """
        self.server_options = dict()  # 服务别名映射服务配置
        self.load_config(config_dir)
        self.manger = ManageConnector()
        self.thread_pool = ThreadPoolExecutor(max_workers=4)
        self.signal_agent = SignalAgent(self.server_options)
        self.callback_queue = Queue(maxsize=maxsize or 1000 * 60)

    def load_config(self, config_dir):
        """配置加载"""
        config_file = ConfigFile(config_dir)
        server_options = Registry(config_file.load_app("server"))  # 别名开关
        self.server_switch = {server: value for server, value in server_options.get("server_switch").items() if value}
        for server_alias in self.server_switch:
            self.server_options[server_alias] = Registry(config_file.load_app(server_alias))

    def listening(self, server_alias: ServerAlias):
        """
        被动触发惰性链接
        @server_alias: 启动链接服务别名
        @return:
        """

        self.manger.registe_connector(server_switch=self.server_switch)
        self.manger.registe_handler(server_switch=self.server_switch)

        # fixme 优化连接池
        threads = []
        for alias in server_alias:
            client = self.get_client(alias)
            threads.append(threading.Thread(target=self.handler_consuming,
                                            args=(
                                                self.signal_agent,
                                                client,
                                                self.callback_queue,
                                                self.server_options,
                                                alias)
                                            )
                           )
        for thread in threads:
            thread.setDaemon(True)
            thread.start()


    def get_client(self, server_alias):
        return self.manger.conn_server(
            server_alias=server_alias,
            server_options=self.server_options.get(server_alias)
        )

    def handler_consuming(self, signal_agent, client, callback_queue, server_options, server_alias):
        handler = self.manger.handler_dispatch(
            signal_agent=signal_agent,
            client=client,
            callback_queue=callback_queue,
            server_options=server_options,
            server_alias=server_alias
        )
        handler.handle()

    def disconnect(self):
        self.thread_pool.shutdown()

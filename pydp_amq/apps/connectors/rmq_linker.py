#!/usr/bin/env python
# -*- coding:utf-8 -*-

# Intro: Component connector
# Author: Q.dynasty
# Version: 1.0.0

import pika
import time
import logging
from pika.exceptions import ConnectionClosed, AMQPError
from pika.exchange_type import ExchangeType

logger = logging.getLogger()


class Service(object):

    def __init__(self, **option):
        self.host = option.get("host")
        self.port = option.get("port")
        self.user = option.get("user")
        self.pwd = option.get("password")
        self.retry_count = option.get("retry_count")
        self.virtual_host = option.get("virtual_host")
        self.current_count =  0
        self._get_channel()

    def _get_channel(self):
        self._conn()

    def auth(self):
        # create connection parameters
        credentials = pika.PlainCredentials(self.user, self.pwd)
        return credentials

    def publish_msg(self, data, exchange , routing_key, queue=None):
        """消息发送"""
        self._exchange_declare(exchange=exchange)
        if queue:
            self._queue_declare(queue=queue,durable=False)
        self.channel.basic_publish(
            exchange=exchange,          # 交换机
            routing_key=routing_key,    # 路由键，写明将消息发往哪个队列
            body=data)                  # 生产者要发送的消息
        logger.info("[生产者] send \n\r exchange:  <{}>  \n\r   data:  < {} >".format(exchange, data))

    def _exchange_declare(self, exchange):
        self.channel.exchange_declare(exchange=exchange,exchange_type='topic')

    def _queue_declare(self, queue, durable):
        """队列声明"""
        self.q_name = queue
        self.channel.queue_declare(queue=queue,durable=durable)

    def _queue_bind(self, exchange, binding_key):
        """绑定队列"""
        self.routing_key = binding_key
        self.channel.queue_bind(exchange=exchange,
                                queue=self.q_name,
                                routing_key=binding_key)

    def _basic_consume(self, on_message_callback, auto_ack=True):
        """绑定回调"""
        self.channel.basic_consume(queue=self.q_name,
                                   on_message_callback=on_message_callback,
                                   auto_ack=auto_ack)

    def _start_consuming(self):
        self.channel.start_consuming()

    def _conn(self):
        self.parameters = pika.ConnectionParameters(
            self.host,
            self.port,
            self.virtual_host,
            self.auth(),
            heartbeat=0
        )
        try:
            # create connection & channel
            self.connection = pika.BlockingConnection(self.parameters)
            self.channel = self.connection.channel()
            logger.info("Rabbitmq server connection successful (p≧w≦q) ")
        except pika.exceptions.AMQPConnectionError as e:
            logger.error(f" 核心通信: Rabbitmq server Not available => {e} username: {self.auth().username} \r\n"
                         f" 准备重连 ......")
            time.sleep(2)
            self.current_count += 1
            if self.current_count <= self.retry_count:
                self._conn()
        except pika.exceptions.ConnectionClosedByBroker as e:
            logger.error(
                f" Rabbitmq server 关闭请检测: Rabbitmq server not available => {e}  username: {self.auth().username} \r\n"
                f" 等待服务重启即将,重连 ......")
            time.sleep(5)
            if self.current_count <= self.retry_count:
                self._conn()
        except Exception as  e:
            logger.error(f"Rabbitmq server Abnormal connection {e}")

    def _get_ack(self):
        """ack"""
        pass

    def heart_beat(fn):
        """
        rabbitmq 连接心跳检测, 所有执行RabbitMQ操作的动作需要加该装饰器
        :param fn:
        :return:
        """

        def wrapper(cls, *args, **kwargs):
            if not cls.connection or not cls.connection.is_open:
                connection = cls.conn()
                if not connection:
                    logger.error('Can not connect to the rabbitmq server, abort')
                    return False

            return fn(cls, *args, **kwargs)

        return wrapper

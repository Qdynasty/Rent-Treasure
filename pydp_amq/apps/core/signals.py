#!/usr/bin/env python
# -*- coding:utf-8 -*-

from pydp_amq.libs import signal

# act_orders_signal = signal.Signal(
#     name='act_orders_signal',
#     providing_args={'sender', 'ch', 'method', 'properties', 'body'}
# )


class SignalAgent:

    def __init__(self, server_options):
        self.generate(server_options)

    def generate(self, server_option):
        """生成指定链接器 signal"""
        rmq_providing_args  = {'sender', 'ch', 'method', 'properties', 'body'}
        mqtt_providing_args  = {'sender','topic', 'msg'}
        for alise, bind_config in server_option.items():
            interface_option = bind_config.get("interface_bind")
            for interface, options in interface_option.items():
                callback_agent = options.get("callback_agent")

                if alise.startswith("rmq"):
                    setattr(self, callback_agent,
                            signal.Signal(
                                name=callback_agent,
                                providing_args=rmq_providing_args
                                )
                            )

                elif alise.startswith("mqtt"):
                    setattr(self, callback_agent,
                            signal.Signal(
                                name=callback_agent,
                                providing_args=mqtt_providing_args
                                )
                            )
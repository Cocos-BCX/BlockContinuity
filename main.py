# -*- coding:utf-8 -*-

import os
import re
import json
import logging
import requests
import datetime as dt
from time import sleep
from logging.handlers import RotatingFileHandler
from logging.handlers import TimedRotatingFileHandler
from PythonMiddleware.notify import Notify
from PythonMiddleware.graphene import Graphene
from PythonMiddlewarebase.operationids import operations

from threading import Thread

class SubFormatter(logging.Formatter):
    converter=dt.datetime.fromtimestamp
    def formatTime(self, record, datefmt=None):
        ct = self.converter(record.created)
        if datefmt:
            s = ct.strftime(datefmt)
        else:
            t = ct.strftime("%Y-%m-%d %H:%M:%S")
            s = "%s,%03d" % (t, record.msecs)
        return s

class Logging(object):
    def __init__(self, log_dir='./logs', log_name='server', console=True):
        self.logger = logging.getLogger(log_name)
        self.logger.setLevel(logging.DEBUG)
        formatter = SubFormatter(fmt='%(asctime)s [%(name)s] [%(funcName)s:%(lineno)s] [%(levelname)s]: %(message)s', datefmt='%Y-%m-%d %H:%M:%S.%f')

        # file handler
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        log_file = log_dir + '/' + log_name
        fh = TimedRotatingFileHandler(filename=log_file, when="H", interval=1, backupCount=3*24)
        fh.suffix = "%Y-%m-%d_%H-%M.log"
        fh.extMatch = re.compile(r"^\d{4}-\d{2}-\d{2}_\d{2}-\d{2}.log$")
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(formatter)
        self.logger.addHandler(fh)

        # console handler
        if console:
            ch = logging.StreamHandler()
            ch.setLevel(logging.DEBUG)
            ch.setFormatter(formatter)
            self.logger.addHandler(ch)

    def getLogger(self):
        return self.logger

headers = {"content-type": "application/json"}

node_address_dict = {"mainnet-fn": "wss://api.cocosbcx.net", "testnet-fn": "wss://test.cocosbcx.net"}

token = "00fe2e1e62a1db837133d5078fb5c5c4053c1383b20ac1b1d773458a096d9df9"
alert_address = "https://oapi.dingtalk.com/robot/send?access_token="+token

logger = Logging().getLogger()

global_last_block_num = {}

def initial():
    for key in node_address_dict:
        global_last_block_num[key] = -1

def send_message(messages, label=['test']):
    try:
        body_relay = {
            "jsonrpc": "2.0",
            "msgtype": "text",
            "text": {
                "content": str(label) + str(messages)
            },
            "id":1
        }
        response = json.loads(requests.post(alert_address, data = json.dumps(body_relay), headers = headers).text)
        logger.debug('request response: {}'.format(response))
    except Exception as e:
        logger.error("task error: '{}'".format(repr(e)))

def listen_block(args):
    def on_block_callback(recv_block_id):
        try:
            global global_last_block_num
            last_block_num = global_last_block_num[node_label]
            info = gph.info()
            # logger.debug('info: {}'.format(info))
            head_block_id = info['head_block_id']
            head_block_number = info['head_block_number']
            flag = False
            message = ""
            if recv_block_id == head_block_id:
                if head_block_number != last_block_num+1:
                    if last_block_num > 0:
                        flag = True
                        logger.warn('[{}] current block num: {}, last block num: {}'.format(node_label, head_block_number, last_block_num))
                global_last_block_num[node_label] = head_block_number
            else:
                try:
                    flag = True
                    block = gph.rpc.get_block(last_block_num+1)
                    global_last_block_num[node_label] = last_block_num+1
                    logger.warn('[{}] >> get_block {}, recv_block_id: {}, head_block_id: {}, get block response： {}'.format(
                        node_label, last_block_num+1, recv_block_id, head_block_id, block['block_id']))
                except Exception as e:
                    logger.error('[{}] get_block exception. block {}, error {}'.format(node_label, last_block_num+1, repr(e)))
            if flag:
                if head_block_number != last_block_num: # testnet-fn和mainnet-fn对应多个节点有bug, 一个ws url对应一个node不需要这里的判断
                    message = "[{}]最新区块:{}，上一个区块:{}".format(node_label, head_block_number, last_block_num)
                    send_message(message)
                logger.info('[{}] head_block_num {}, recv_block_id: {}, head_block_id {}, last_block_num:{}'.format(node_label,
                    head_block_number, recv_block_id, head_block_id, last_block_num))
        except Exception as e:
            logger.error('[{}] on_block_callback exception. recv_block_id {}, last block num {}, error {}'.format(node_label,
                recv_block_id, last_block_num+1, repr(e)))

    node_label = args[0]
    node_address = args[1]
    gph = Graphene(node=node_address)
    from PythonMiddleware.instance import set_shared_graphene_instance
    set_shared_graphene_instance(gph)
    notify = Notify(
        on_block = on_block_callback,
        graphene_instance = gph
    )
    notify.listen()

def main():
    initial()
    for key in node_address_dict:
        args = [key, node_address_dict[key]]
        t = Thread(target=listen_block, args=(args,))
        t.start()

if __name__ == '__main__':
    main()

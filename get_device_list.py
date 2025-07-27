# https://zenn.dev/niku9mofumofu/articles/cee3da204fd721
# coding: utf-8
import json

import requests

# Import the token from the config file
from config_private import SWITCHBOT_API_TOKEN

#-------------------------------
# SwitchBot Hub miniとの接続設定
#-------------------------------
TOKEN = SWITCHBOT_API_TOKEN
API_HOST = 'https://api.switch-bot.com'


class SwitchBot:
    def __init__(self, token, host):
        self.token = token
        self.host  = host
        self.devlist_url = f'{self.host}/v1.0/devices'
        self.headers = {
            'Authorization': self.token,
            'Content-Type': 'application/json; charset=utf8'
        }

    def print_device_list(self):
        """
        デバイス一覧を出力する
        """
        devices = self.get_device_list()

        # SwitchBot関連のデバイスリストを取得する。
        self.pub_device_list = devices.get('deviceList')
        # 赤外線操作対象のデバイスリストを取得する。
        self.ir_device_list  = devices.get('infraredRemoteList')

        # 湿温度計の情報を取得
        print('デバイスID一覧')
        for device in self.pub_device_list:
            print(device)

        print('\n赤外線リモコン操作ID一覧')
        # 赤外線操作対象
        for device in self.ir_device_list:
            print(device)

    def get_device_list(self):
        '''
        デバイスIDの一覧を取得する
        '''
        try:
            return self.get_request(self.devlist_url)['body']
        except:
            print('デバイスIDを検出できませんでした')
            return None

    def get_request(self, url):
        try:
            res = requests.get(url, headers=self.headers, timeout=2.0)
            data = res.json()
            if data['message'] == 'success':
                return res.json()
            else:
                print(data['statusCode'])
                print(data['message'])
        except requests.Timeout:
            print('コマンド送信がタイムアウトしました')
        except Exception as err:
            print(err)
        return {}


if __name__ == '__main__':
    sb = SwitchBot(TOKEN, API_HOST)
    sb.print_device_list()
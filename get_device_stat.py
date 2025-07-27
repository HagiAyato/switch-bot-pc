# coding: utf-8
import json
import requests
import tkinter as tk
from tkinter import ttk
import threading
import time
from datetime import datetime

# Import the token from the config file
from config_private import SWITCHBOT_API_TOKEN

# --- SwitchBot Hub miniとの接続設定 ---
# IMPORTANT: Replace 'YOUR_TOKEN_HERE' with your actual SwitchBot API token.
# You can get your token from the SwitchBot app under Profile -> Integration -> Developer Options.
TOKEN = SWITCHBOT_API_TOKEN
API_HOST = 'https://api.switch-bot.com'

class SwitchBot:
    def __init__(self, token, host):
        self.token = token
        self.host = host
        self.devlist_url = f'{self.host}/v1.0/devices'
        self.headers = {
            'Authorization': self.token,
            'Content-Type': 'application/json; charset=utf8'
        }
        self.pub_device_list = []
        self.ir_device_list = []

    def get_device_list(self):
        '''
        デバイスIDの一覧を取得する
        '''
        try:
            response_body = self.get_request(self.devlist_url)
            if response_body:
                return response_body['body']
            else:
                return None
        except Exception as e:
            print(f'デバイスIDを検出できませんでした: {e}')
            return None

    def get_request(self, url):
        try:
            res = requests.get(url, headers=self.headers, timeout=5.0) # Increased timeout
            data = res.json()
            if data['message'] == 'success':
                return data
            else:
                print(f"Error {data['statusCode']}: {data['message']}")
                return None
        except requests.Timeout:
            print('コマンド送信がタイムアウトしました')
            return None
        except requests.exceptions.RequestException as err:
            print(f"リクエストエラー: {err}")
            return None
        except json.JSONDecodeError:
            print("JSONデコードエラー: 無効な応答")
            return None
        except Exception as err:
            print(f"予期せぬエラー: {err}")
            return None

    def get_device_status(self, device_id):
        '''
        指定されたデバイスのステータスを取得する
        '''
        status_url = f'{self.host}/v1.0/devices/{device_id}/status'
        try:
            response = self.get_request(status_url)
            return response['body'] if response else None
        except Exception as e:
            print(f"デバイスID {device_id} のステータスを取得できませんでした: {e}")
            return None

    def find_devices(self):
        '''
        SwitchBot 温湿度計、接触センサー、およびロックデバイスを見つける
        '''
        devices = self.get_device_list()
        meter_devices = []
        contact_sensors = []
        lock_devices = []
        if devices:
            self.pub_device_list = devices.get('deviceList', [])
            for device in self.pub_device_list:
                if device.get('deviceType') == 'MeterPlus' or device.get('deviceType') == 'Meter':
                    meter_devices.append(device)
                elif device.get('deviceType') == 'Contact Sensor':
                    contact_sensors.append(device)
                elif device.get('deviceType') == 'Smart Lock':
                    lock_devices.append(device)
        return meter_devices, contact_sensors, lock_devices

class SwitchBotApp:
    def __init__(self, master):
        self.master = master
        master.title("SwitchBot デバイスモニタ")
        master.geometry("600x550") # Adjust initial window size to accommodate new sections

        self.switchbot = SwitchBot(TOKEN, API_HOST)
        self.meter_devices = []
        self.contact_sensors = []
        self.lock_devices = []

        # --- 更新時刻表示 ---
        self.last_updated_label = ttk.Label(master, text="最終更新: --:--:--", font=("Helvetica", 10))
        self.last_updated_label.pack(pady=(5, 0), anchor='e')

        # --- 温湿度計セクション ---
        ttk.Label(master, text="--- 温湿度計 ---", font=("Helvetica", 14, "bold")).pack(pady=(10, 5))
        self.meter_frame = ttk.Frame(master)
        self.meter_frame.pack(fill='x', padx=10, pady=5)
        self.meter_labels = {} # To hold labels for each meter device

        # --- 接触センサーセクション ---
        ttk.Label(master, text="--- 接触センサー ---", font=("Helvetica", 14, "bold")).pack(pady=(10, 5))
        self.contact_frame = ttk.Frame(master)
        self.contact_frame.pack(fill='x', padx=10, pady=5)
        self.contact_sensor_labels = {} # To hold labels for each contact sensor

        # --- ロックデバイスセクション ---
        ttk.Label(master, text="--- スマートロック ---", font=("Helvetica", 14, "bold")).pack(pady=(10, 5))
        self.lock_frame = ttk.Frame(master)
        self.lock_frame.pack(fill='x', padx=10, pady=5)
        self.lock_labels = {} # To hold labels for each lock device

        self.status_label = ttk.Label(master, text="ステータス: 初期化中...", font=("Helvetica", 12))
        self.status_label.pack(side='bottom', pady=5)

        self.update_interval_minutes = 1 # Update every 1 minutes
        self.stop_event = threading.Event()

        self.find_devices_and_start_updates()

    def find_devices_and_start_updates(self):
        """Finds the devices and starts the update thread."""
        self.status_label.config(text="ステータス: デバイスを検索中...")
        self.master.update_idletasks() # Update GUI immediately

        meter_devs, contact_sens, lock_devs = self.switchbot.find_devices()
        self.meter_devices = meter_devs
        self.contact_sensors = contact_sens
        self.lock_devices = lock_devs

        if self.meter_devices or self.contact_sensors or self.lock_devices:
            print("以下のデバイスが見つかりました:")
            if self.meter_devices:
                for device in self.meter_devices:
                    print(f"  温湿度計: {device.get('deviceName')} (ID: {device.get('deviceId')})")
                    # Create labels for each meter device
                    label_text = tk.StringVar(value=f"{device.get('deviceName')}: 温度: --.-- °C, 湿度: --.-- %")
                    label = ttk.Label(self.meter_frame, textvariable=label_text, font=("Helvetica", 16))
                    label.pack(anchor='w', pady=2)
                    self.meter_labels[device.get('deviceId')] = label_text
            if self.contact_sensors:
                for device in self.contact_sensors:
                    print(f"  接触センサー: {device.get('deviceName')} (ID: {device.get('deviceId')})")
                    # Create labels for each contact sensor
                    label_text = tk.StringVar(value=f"{device.get('deviceName')}: 開閉状態: 未取得, 照度: 未取得")
                    label = ttk.Label(self.contact_frame, textvariable=label_text, font=("Helvetica", 16))
                    label.pack(anchor='w', pady=2)
                    self.contact_sensor_labels[device.get('deviceId')] = label_text
            if self.lock_devices:
                for device in self.lock_devices:
                    print(f"  スマートロック: {device.get('deviceName')} (ID: {device.get('deviceId')})")
                    # Create labels for each lock device
                    label_text = tk.StringVar(value=f"{device.get('deviceName')}: 鍵の状態: 未取得")
                    label = ttk.Label(self.lock_frame, textvariable=label_text, font=("Helvetica", 16))
                    label.pack(anchor='w', pady=2)
                    self.lock_labels[device.get('deviceId')] = label_text

            self.status_label.config(text="ステータス: デバイス接続済み")
            self.start_update_thread()
        else:
            self.status_label.config(text="ステータス: デバイスが見つかりませんでした。TOKENを確認してください。")

    def update_data(self):
        """Fetches and updates sensor data."""
        current_time = datetime.now().strftime("%H:%M:%S")
        self.last_updated_label.config(text=f"最終更新: {current_time}")

        self.status_label.config(text="ステータス: データ取得中...")
        self.master.update_idletasks() # Update GUI

        # Update Meter devices
        for device in self.meter_devices:
            device_id = device.get('deviceId')
            device_name = device.get('deviceName')
            status = self.switchbot.get_device_status(device_id)
            if status:
                temperature = status.get('temperature')
                humidity = status.get('humidity')
                temp_str = f"{temperature:.2f} °C" if temperature is not None else "N/A"
                hum_str = f"{humidity:.2f} %" if humidity is not None else "N/A"
                self.meter_labels[device_id].set(f"{device_name}: 温度: {temp_str}, 湿度: {hum_str}")
            else:
                self.meter_labels[device_id].set(f"{device_name}: データ取得失敗")

        # Update Contact Sensor devices
        for device in self.contact_sensors:
            device_id = device.get('deviceId')
            device_name = device.get('deviceName')
            status = self.switchbot.get_device_status(device_id)
            if status:
                open_closed_state = status.get('openState') # 'open', 'close', 'timeout'
                illuminance = status.get('brightness') # bright or dim
                
                if open_closed_state == 'open':
                    state_text = "開"
                elif open_closed_state == 'close':
                    state_text = "閉"
                elif open_closed_state == 'timeout':
                    state_text = "タイムアウト"
                else:
                    state_text = "不明"

                # Map illuminance to descriptive text
                if illuminance == 'dim':
                    light_text = "暗い"
                elif illuminance == 'bright':
                    light_text = "明るい"
                else:
                    light_text = "不明"
                
                self.contact_sensor_labels[device_id].set(f"{device_name}: 開閉状態: {state_text}, 照度: {light_text}")
            else:
                self.contact_sensor_labels[device_id].set(f"{device_name}: データ取得失敗")

        # Update Lock devices
        for device in self.lock_devices:
            device_id = device.get('deviceId')
            device_name = device.get('deviceName')
            status = self.switchbot.get_device_status(device_id)
            if status:
                lock_state = status.get('lockState') # 'locked', 'unlocked', 'locking', 'unlocking', 'jammed', 'unknown'
                
                if lock_state == 'locked':
                    state_text = "施錠"
                elif lock_state == 'unlocked':
                    state_text = "開錠"
                elif lock_state == 'locking':
                    state_text = "施錠中"
                elif lock_state == 'unlocking':
                    state_text = "開錠中"
                elif lock_state == 'jammed':
                    state_text = "ジャム"
                else:
                    state_text = "不明"
                
                self.lock_labels[device_id].set(f"{device_name}: 鍵の状態: {state_text}")
            else:
                self.lock_labels[device_id].set(f"{device_name}: データ取得失敗")

        self.status_label.config(text="ステータス: 最新")


    def periodic_update(self):
        """Runs the data update in a loop."""
        while not self.stop_event.is_set():
            self.update_data()
            for _ in range(self.update_interval_minutes * 60):
                if self.stop_event.is_set():
                    break
                time.sleep(1) # Sleep for 1 second at a time to allow quicker shutdown

    def start_update_thread(self):
        """Starts the periodic update in a separate thread."""
        self.update_thread = threading.Thread(target=self.periodic_update)
        self.update_thread.daemon = True # Allow the thread to exit when the main program exits
        self.update_thread.start()

    def on_closing(self):
        """Handles closing the application."""
        print("アプリケーションを終了します...")
        self.stop_event.set() # Signal the thread to stop
        if hasattr(self, 'update_thread') and self.update_thread.is_alive():
            self.update_thread.join(timeout=5) # Wait for the thread to finish
        self.master.destroy()

if __name__ == '__main__':
    if TOKEN == 'YOUR_TOKEN_HERE':
        print("WARNING: Please replace 'YOUR_TOKEN_HERE' in config.py with your actual SwitchBot API token.")
        print("Exiting application. Update the TOKEN and rerun.")
    else:
        root = tk.Tk()
        app = SwitchBotApp(root)
        root.protocol("WM_DELETE_WINDOW", app.on_closing) # Handle window close event
        root.mainloop()
# SwitchBot デバイス操作・監視スクリプト

このリポジトリには、SwitchBot API を使用してデバイス情報を取得し、そのステータスを監視するためのPythonスクリプトが含まれています。

## 概要

  * `get_device_list.py`: SwitchBot アカウントに紐付けられたデバイス（ハブミニ、温湿度計、赤外線リモコンデバイスなど）の一覧を出力します。

  * `get_device_stat.py`: 温湿度計、接触センサー、スマートロックなどのデバイスのリアルタイムステータスをGUIで表示し、定期的に更新します。

## 機能

### `get_device_list.py`

  * SwitchBot デバイス（`deviceList`）と赤外線リモコンデバイス（`infraredRemoteList`）の両方を取得し、コンソールに表示します。

### `get_device_stat.py`

  * 温湿度計 (`MeterPlus`, `Meter`) の温度と湿度をリアルタイムで表示します。

  * 接触センサー (`Contact Sensor`) の開閉状態と照度（明るい/暗い）をリアルタイムで表示します。

  * スマートロック (`Smart Lock`) の施錠状態をリアルタイムで表示します。

  * Tkinter を使用したシンプルなGUIを提供します。

  * 設定された間隔（デフォルトは1分）で自動的にデータを更新します。

  * 最終更新時刻と現在のステータスをGUIに表示します。

## 前提条件

  * Python 3.x

  * `requests` ライブラリ

  * `tkinter` (Pythonに標準で含まれています)

## インストール

1.  このリポジトリのコードをクローンまたはダウンロードします。

    ```
    git clone https://github.com/your-username/switchbot-scripts.git
    cd switchbot-scripts

    ```

2.  必要なPythonライブラリをインストールします。

    ```
    pip install requests

    ```

3.  SwitchBot APIトークンを設定するための `config_private.py` ファイルを作成します。

    プロジェクトのルートディレクトリに `config_private.py` という名前の新しいファイルを作成し、以下の内容を記述してください。`YOUR_SWITCHBOT_API_TOKEN` の部分を実際のAPIトークンに置き換えてください。

    ```
    # config_private.py
    SWITCHBOT_API_TOKEN = 'YOUR_SWITCHBOT_API_TOKEN'

    ```

    **注意:** `config_private.py` は機密情報を含むため、公開リポジトリにアップロードしないように `.gitignore` に追加することを強くお勧めします。

    ```
    # .gitignore
    config_private.py

    ```

## 使用方法

### 1\. デバイスリストの取得 (`get_device_list.py`)

登録されているSwitchBotデバイスの一覧をコンソールに表示するには、以下のコマンドを実行します。

```
python get_device_list.py

```

実行すると、以下のような出力が表示されます（デバイスによって内容は異なります）。

```
デバイスID一覧
{'deviceId': 'C123456789AB', 'deviceName': 'リビング温湿度計', 'deviceType': 'MeterPlus', 'enableCloudService': True, ...}
...

赤外線リモコン操作ID一覧
{'deviceId': 'D987654321EF', 'deviceName': 'リビングエアコン', 'remoteType': 'Air Conditioner', ...}
...

```

### 2\. デバイスステータスの監視 (`get_device_stat.py`)

温湿度計、接触センサー、スマートロックのステータスをGUIでリアルタイムに監視するには、以下のコマンドを実行します。

````
python get_device_stat.py
```config_private.py` に有効なAPIトークンが設定されていれば、GUIウィンドウが開き、検出されたデバイスのステータスが表示され、定期的に更新されます。

**警告:** `config_private.py` の `TOKEN` が `'YOUR_TOKEN_HERE'` のままの場合、アプリケーションは警告メッセージを表示して終了します。

## SwitchBot APIトークンの取得方法

SwitchBot APIトークンは、SwitchBotアプリから取得できます。

1.  SwitchBotアプリを開きます。
2.  「プロフィール」タブに移動します。
3.  「連携サービス」または「統合」を選択します。
4.  「開発者向けオプション」を選択します。
5.  APIトークンが生成され、表示されます。このトークンを `config_private.py` にコピーしてください。

## 参照

このコードは、以下のZennの記事を参考にしています。
- [SwitchBot APIをPythonで操作する](https://zenn.dev/niku9mofumofu/articles/cee3da204fd721)

````
"""BLE通信に関連する定数定義"""

# DARTSLIVE HOME のBLE UART サービスUUID
DARTSLIVE_UART_UUID = "6e40fff6-b5a3-f393-e0a9-e50e24dcca9e"

# デバイス名のパターン (DARTSLIVE HOMEデバイスを識別するため)
DARTSLIVE_DEVICE_NAME_PATTERNS = ["DARTSLIVE", "DARTS"]

# スキャン設定
SCAN_TIMEOUT = 10.0  # デバイススキャンのタイムアウト(秒)
SCAN_RETRY_MAX = 3   # 最大リトライ回数
SCAN_RETRY_DELAY = 5.0  # リトライ間隔(秒)

# 接続設定
CONNECTION_TIMEOUT = 15.0  # 接続タイムアウト(秒)
RECONNECT_RETRY_MAX = 3    # 再接続最大リトライ回数
RECONNECT_DELAY = 3.0      # 再接続間隔(秒)

# データフォーマット
DATA_PACKET_SIZE = 5  # 受信データのサイズ(バイト)
SEGMENT_BYTE_INDEX = 2  # セグメント番号が格納されているバイトのインデックス

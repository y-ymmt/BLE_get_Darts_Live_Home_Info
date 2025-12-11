# DARTSLIVE HOME Webアプリケーション

DARTSLIVE HOMEのデータをWebブラウザで可視化・管理するアプリケーションです。

## 機能

- **投擲一覧**: リアルタイムで投擲データを表示
- **分析画面**: 統計情報、セグメント分布、得点分布を可視化
- **ゼロワンゲーム**: 301/501/701などのゼロワンゲームをプレイ可能
  - 複数プレイヤー対応
  - ダブルアウト、マスターアウト、ストレートアウト選択可能
  - リアルタイムスコア更新

## セットアップ

### 1. バックエンド依存関係のインストール

```bash
pip install -r requirements-web.txt
```

### 2. フロントエンド依存関係のインストール

```bash
cd frontend
npm install
```

## 開発モードで起動

### ターミナル1: バックエンドサーバー起動

```bash
python web_app.py
```

バックエンドサーバーが http://localhost:5000 で起動します。

### ターミナル2: フロントエンド開発サーバー起動

```bash
cd frontend
npm run dev
```

フロントエンドが http://localhost:3000 で起動します。

ブラウザで http://localhost:3000 を開いてください。

## 本番ビルド

### 1. フロントエンドをビルド

```bash
cd frontend
npm run build
```

ビルドされたファイルは `frontend/dist/` に出力されます。

### 2. バックエンドから配信

```bash
python web_app.py
```

http://localhost:5000 にアクセスすると、ビルドされたフロントエンドが表示されます。

## アーキテクチャ

### バックエンド (Flask + Socket.IO)

```
backend/
├── app.py              # Flaskアプリケーション
├── ble_manager.py      # BLE接続管理
├── event_bus.py        # Pub/Subイベントバス
├── api/                # REST APIエンドポイント
│   ├── throws.py
│   ├── stats.py
│   └── games.py
└── games/              # ゲームロジック
    ├── base.py
    ├── zero_one.py
    └── state.py
```

### フロントエンド (React + Vite)

```
frontend/src/
├── App.jsx                 # メインアプリ
├── services/               # API/WebSocketクライアント
│   ├── api.js
│   └── socket.js
├── hooks/                  # カスタムフック
│   ├── useSocket.js
│   └── useGame.js
├── components/             # 共通コンポーネント
│   └── Layout.jsx
└── pages/                  # ページコンポーネント
    ├── ThrowsList.jsx
    ├── AnalysisPage.jsx
    └── ZeroOnePage.jsx
```

## WebSocketイベント

### サーバー → クライアント

- `throw`: 投擲データ検出時
- `player_change`: プレイヤー交代ボタン押下時
- `ble_connected`: BLE接続成功時
- `ble_error`: BLEエラー発生時
- `ble_status`: BLE接続状態

### クライアント → サーバー

- `request_status`: BLE接続状態をリクエスト

## REST API

### 投擲データ

- `GET /api/throws` - 投擲一覧取得
- `GET /api/throws/count` - 投擲数取得

### 統計

- `GET /api/stats` - 基本統計情報
- `GET /api/stats/segments` - セグメント分布
- `GET /api/stats/scores` - 得点分布
- `GET /api/stats/daily` - 日別サマリー
- `GET /api/stats/recent` - 直近の投擲

### ゲーム

- `POST /api/games` - ゲーム作成
- `GET /api/games/:id` - ゲーム状態取得
- `DELETE /api/games/:id` - ゲーム削除
- `GET /api/games` - ゲーム一覧
- `POST /api/games/:id/throw` - 投擲処理

## CLIアプリとの共存

WebアプリとCLIアプリは同じBLE接続を共有できません（BLEデバイスは1接続のみ）。

- **Webアプリ起動中**: バックグラウンドでBLE接続を維持
- **CLIアプリ起動時**: 既にWebアプリが起動していると接続エラー

どちらか一方を使用してください。

## トラブルシューティング

### BLE接続ができない

1. DARTSLIVE HOMEの電源を確認
2. Bluetoothがオンになっているか確認
3. 他のアプリケーションでBLE接続していないか確認
4. バックエンドログを確認: `python web_app.py`

### フロントエンドがバックエンドに接続できない

開発モード時、Viteのプロキシ設定を確認：
- `frontend/vite.config.js`
- バックエンドが http://localhost:5000 で起動しているか確認

### ゲームが動作しない

1. ブラウザのコンソールでエラーを確認
2. WebSocketが接続されているか確認（ヘッダーのWS/BLEインジケーター）
3. バックエンドログを確認

## ライセンス

MITライセンス

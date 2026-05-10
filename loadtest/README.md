# Load Test (Locust)

對 `backend/` 的 API 做壓力測試。

## 安裝

```bash
cd loadtest
uv sync
```

## 使用

**前提：** `backend/` 那邊的 Django 已經跑起來在 `http://localhost:8000`，且有測試帳號。

### 1. Web UI 模式（推薦）

```bash
uv run locust -f locustfile.py --host http://localhost:8000
```

開瀏覽器 → http://localhost:8089

填：

- **Number of users**：模擬並發數（例如 50）
- **Spawn rate**：每秒新增幾個 user（例如 5）
- **Host**：`http://localhost:8000`

按 **Start swarming**，即時看 RPS / 回應時間 / 失敗率 / 圖表。

### 2. 無 UI 模式（自動化 / CI）

```bash
uv run locust -f locustfile.py --host http://localhost:8000 \
    --headless -u 50 -r 5 -t 1m
```

- `-u 50`：50 個 user
- `-r 5`：每秒生 5 個
- `-t 1m`：跑 1 分鐘

### 3. 匯出報告

```bash
uv run locust -f locustfile.py --host http://localhost:8000 \
    --headless -u 50 -r 5 -t 1m \
    --html report.html --csv result
```

會產生 `report.html`、`result_*.csv`。

## 設定測試帳號

打開 `locustfile.py` 改：

```python
TEST_USERNAME = "你的帳號"
TEST_PASSWORD = "你的密碼"
```

## 測試的 endpoint

| 任務 | 權重 | 路徑 |
|---|---|---|
| 登入 | (on_start) | POST /api/token/ |
| 列表使用者 | 5 | GET /api/userextend/users/ |
| 取得自己 | 3 | GET /api/userextend/users/me/ |
| 列表部門 | 2 | GET /api/userextend/departments/ |
| 發 email 訊息 | 2 | POST /api/mq/publish/ |
| 發通知訊息 | 1 | POST /api/mq/publish/ |
| 匿名亂登入 | (AnonymousUser) | POST /api/token/ |

# NextjsDjangoPostgre

一個全端練習專案，採用 **Next.js + Django REST Framework + PostgreSQL** 三層架構，並整合 **RabbitMQ** 處理非同步任務。專案另保留一個 `ginbackend/` 資料夾作為 Go (Gin) 版本後端的擴充空間。

---

## 專案結構

```
NextjsDjangoPostgre/
├── frontend/          # Next.js 前端
├── backend/           # Django + DRF 後端 (主要)
├── ginbackend/        # Go (Gin) 後端 (預留)
└── ReadMe.md
```

---

## 技術棧

### 前端 — Next.js

- **Next.js**：React 全端框架，支援 SSR / SSG / App Router
- **TypeScript**：型別安全
- 透過 REST API 與後端溝通，CORS 已在後端設定 `http://localhost:3000` 白名單

### 後端 — Django + DRF

| 套件 | 用途 |
|---|---|
| `django` 6.0 | Web 框架 |
| `djangorestframework` | 提供 RESTful API（ViewSet / Router / Serializer） |
| `rest_framework.authtoken` | Token 認證 |
| `django-cors-headers` | 跨域設定 |
| `django-unfold` | 美化 Django Admin |
| `whitenoise` | 靜態檔案處理 |
| `psycopg[binary]` | PostgreSQL 驅動 |
| `pika` | RabbitMQ 客戶端 |
| `uvicorn` | ASGI server |

**App 結構：**

- `backend/` — Django 專案設定（settings、urls、wsgi、asgi）
- `UserExtend/` — 使用者擴充模型（UserInfo、Department）+ 完整 CRUD API
- `mq/` — RabbitMQ 整合（producer、consumer、management command）

**主要 API：**

```
POST   /api/userextend/auth/login/      登入取得 token
POST   /api/userextend/auth/logout/     登出
GET    /api/userextend/users/           使用者 CRUD (支援 search / ordering / pagination)
GET    /api/userextend/users/me/        當前登入使用者
GET    /api/userextend/departments/     部門 CRUD
GET    /api/userextend/userinfos/       UserInfo CRUD
POST   /api/mq/publish/                 發送訊息到 RabbitMQ
```

### 資料庫 — PostgreSQL

- 資料庫：`Django-DB1`
- 預設連線：`localhost:5432`
- 透過 `psycopg` 連接

### 訊息佇列 — RabbitMQ

用於 Django 後端的非同步任務（如寄信、通知）：

- **Producer**：`mq/producer.py`，透過 `publish()` 發訊息
- **Consumer**：`mq/consumer.py` + `python manage.py run_consumer`
- **Task Registry**：`mq/tasks.py`，集中註冊 queue 對應的 handler

### 套件管理 — uv

專案使用 [uv](https://github.com/astral-sh/uv) 管理 Python 依賴，配置在 `backend/pyproject.toml`。

---

## 啟動方式

### 1. 啟動 PostgreSQL

確保本機 PostgreSQL 已啟動，並建立資料庫 `Django-DB1`（帳密見 `backend/backend/settings.py`）。

### 2. 啟動 RabbitMQ（Docker）

```bash
docker run -d --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:3-management
```

管理介面：http://localhost:15672 （`guest` / `guest`）

### 3. 啟動 Django 後端

```bash
cd backend
uv sync                              # 安裝依賴
uv run python manage.py migrate       # 建表
uv run python manage.py createsuperuser
uv run python manage.py runserver     # http://localhost:8000
```

另開一個 terminal 跑 RabbitMQ consumer：

```bash
cd backend
uv run python manage.py run_consumer
```

### 4. 啟動 Next.js 前端

```bash
cd frontend
npm install
npm run dev                           # http://localhost:3000
```

---

## 認證流程

1. 前端 `POST /api/userextend/auth/login/` 帶 `username` / `password`，拿回 `token`
2. 之後每個 request 帶 header：

   ```
   Authorization: Token <token>
   ```

3. 登出打 `POST /api/userextend/auth/logout/`

---

## 開發備註

- DRF 已啟用 pagination（每頁 20 筆）、throttle（匿名 60/min、登入 300/min）
- Admin 介面用 `django-unfold` 美化，網址 `/admin/`
- Browsable API 登入按鈕走 `/api-auth/`

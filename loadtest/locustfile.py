"""
Locust 壓力測試腳本
執行方式 (在 loadtest/ 目錄下):
    uv run locust -f locustfile.py --host http://localhost:8000

之後開瀏覽器 http://localhost:8089 設定 user 數與 spawn rate

無 UI 模式 (CI 用):
    uv run locust -f locustfile.py --host http://localhost:8000 \
        --headless -u 50 -r 5 -t 1m
"""
import random
from locust import HttpUser, task, between, events


# ===== 測試帳號 (請改成自己有的) =====
TEST_USERNAME = "admin"
TEST_PASSWORD = "admin123"


# uv run python -m locust -f locustfile.py --host http://127.0.0.1:8000
class ApiUser(HttpUser):
    """一般 API 使用者: 登入後操作各種 endpoint"""

    # 每次 request 間隔 1~3 秒, 模擬真人操作節奏
    wait_time = between(1, 3)

    # def on_start(self):
    #     # user 啟動時先登入拿 JWT token
    #     res = self.client.post(
    #         "/api/token/",
    #         json={"username": TEST_USERNAME, "password": TEST_PASSWORD},
    #         name="[Auth] 登入取 token",
    #     )
    #     if res.status_code == 200:
    #         self.token = res.json().get("access")
    #         # 後續所有 request 自動帶上 Bearer header
    #         self.client.headers.update({"Authorization": f"Bearer {self.token}"})
    #     else:
    #         print(f"[!] 登入失敗 status={res.status_code}, body={res.text}")
    #         self.token = None


    # ===== 任務 (數字越大越常被執行) =====
    @task(100)
    def OnlineStoreTest(self):
        self.client.get("/api/store/test/", name="test publishs")

    # @task(1)
    # def list_users(self):
    #     # 列表 API
    #     self.client.get("/api/userextend/users/", name="GET users 列表")

    # @task(3)
    # def get_me(self):
    #     # 取得目前使用者
    #     self.client.get("/api/userextend/users/me/", name="GET 我自己")

    # @task(2)
    # def list_departments(self):
    #     self.client.get("/api/userextend/departments/", name="GET departments")

    # @task(2)
    # def publish_email(self):
    #     # 發送 RabbitMQ 訊息
    #     self.client.post(
    #         "/api/mq/publish/",
    #         json={
    #             "queue": "send_email",
    #             "payload": {
    #                 "to": f"user{random.randint(1, 1000)}@test.com",
    #                 "subject": "load test",
    #             },
    #         },
    #         name="POST mq publish (email)",
    #     )

    # @task(1)
    # def publish_notification(self):
    #     self.client.post(
    #         "/api/mq/publish/",
    #         json={
    #             "queue": "notification",
    #             "payload": {
    #                 "user_id": random.randint(1, 100),
    #                 "message": "hello from locust",
    #             },
    #         },
    #         name="POST mq publish (notification)",
    #     )


class AnonymousUser(HttpUser):
    """匿名使用者: 只打開放 endpoint, 測 throttle 限制"""

    wait_time = between(1, 2)
    weight = 1  # 比例: 相對於 ApiUser 出現的機率

    @task
    def hit_login(self):
        # 故意用錯密碼測登入端點承受度
        self.client.post(
            "/api/token/",
            json={"username": "noone", "password": "wrong"},
            name="[Anon] 嘗試登入",
        )


# ===== 事件鉤子 (可選) =====

@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    print(">>> 壓測開始")


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    print(">>> 壓測結束")

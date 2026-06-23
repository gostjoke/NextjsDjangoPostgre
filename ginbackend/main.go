package main

// 進入點: 載入設定 -> 連 DB -> 建 JWT 管理器 -> 啟動 gin。

import (
	"log"

	"github.com/gin-gonic/gin"

	"ginbackend/config"
	"ginbackend/internal/auth"
	"ginbackend/internal/database"
	"ginbackend/internal/router"
)

func main() {
	cfg := config.Load()
	gin.SetMode(cfg.GinMode)

	// 連 Postgres (與 Django 同一個 DB)
	if err := database.Init(cfg.DBDsn); err != nil {
		log.Fatalf("[db] 連線失敗: %v", err)
	}

	// JWT 管理器 (secret 等同 Django SECRET_KEY => token 雙向互通)
	jwtMgr := auth.NewManager(cfg.JWTSecret, cfg.AccessExpire, cfg.RefreshExpire)

	r := router.Setup(cfg, jwtMgr)

	log.Printf("[server] 監聽 :%s", cfg.ServerPort)
	if err := r.Run(":" + cfg.ServerPort); err != nil {
		log.Fatalf("[server] 啟動失敗: %v", err)
	}
}

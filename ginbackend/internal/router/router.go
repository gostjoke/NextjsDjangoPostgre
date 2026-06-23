package router

// 路由與中介層註冊。

import (
	"net/http"

	"github.com/gin-gonic/gin"

	"ginbackend/config"
	"ginbackend/internal/auth"
	"ginbackend/internal/handler"
	"ginbackend/internal/middleware"
)

// Setup 組裝 gin engine
func Setup(cfg *config.Config, jwtMgr *auth.Manager) *gin.Engine {
	r := gin.New()

	// 全域 middleware
	r.Use(middleware.Logger())
	r.Use(gin.Recovery()) // panic 自動回 500
	r.Use(middleware.CORS(cfg.CORSOrigins))

	authH := handler.NewAuthHandler(jwtMgr)

	// 健康檢查
	r.GET("/health", func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{"status": "ok"})
	})

	api := r.Group("/api")
	{
		// 公開端點 (路徑對齊 Django userextend 的 JWT 登入)
		api.POST("/auth/jwt/login/", authH.Login)
		api.POST("/auth/jwt/refresh/", authH.Refresh)

		// 受保護端點: 需帶 access token
		authed := api.Group("")
		authed.Use(middleware.JWTAuth(jwtMgr))
		{
			authed.GET("/me", authH.Me)
		}
	}

	return r
}

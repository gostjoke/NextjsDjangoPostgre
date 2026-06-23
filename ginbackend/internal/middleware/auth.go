package middleware

// JWT 驗證中介層: 檢查 Authorization: Bearer <token>,只放行 access token。

import (
	"net/http"
	"strings"

	"github.com/gin-gonic/gin"

	"ginbackend/internal/auth"
)

// context key (供 handler 取用)
const (
	ContextUserID   = "user_id"
	ContextUsername = "username"
	ContextClaims   = "claims"
)

// JWTAuth 回傳一個會驗證 token 的 gin middleware
func JWTAuth(m *auth.Manager) gin.HandlerFunc {
	return func(c *gin.Context) {
		header := c.GetHeader("Authorization")
		if header == "" {
			unauthorized(c, "缺少 Authorization header")
			return
		}

		// 格式必須是 "Bearer <token>"
		parts := strings.SplitN(header, " ", 2)
		if len(parts) != 2 || parts[0] != "Bearer" {
			unauthorized(c, "Authorization 格式錯誤,應為 Bearer <token>")
			return
		}

		claims, err := m.Parse(parts[1])
		if err != nil {
			unauthorized(c, "token 無效或已過期")
			return
		}
		// 受保護端點只接受 access token
		if claims.TokenType != auth.TokenTypeAccess {
			unauthorized(c, "需要 access token")
			return
		}

		// 把使用者資訊塞進 context,後續 handler 可直接取用
		c.Set(ContextUserID, claims.UserID)
		c.Set(ContextUsername, claims.Username)
		c.Set(ContextClaims, claims)
		c.Next()
	}
}

func unauthorized(c *gin.Context, msg string) {
	c.AbortWithStatusJSON(http.StatusUnauthorized, gin.H{"detail": msg})
}

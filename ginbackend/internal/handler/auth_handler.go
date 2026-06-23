package handler

// 認證相關 handler: 登入、refresh、受保護的 /me 範例。
// 回傳格式刻意對齊 Django userextend 的 JWT 端點。

import (
	"net/http"

	"github.com/gin-gonic/gin"

	"ginbackend/internal/auth"
	"ginbackend/internal/database"
	"ginbackend/internal/middleware"
	"ginbackend/internal/models"
)

type AuthHandler struct {
	jwt *auth.Manager
}

func NewAuthHandler(m *auth.Manager) *AuthHandler {
	return &AuthHandler{jwt: m}
}

type loginRequest struct {
	Username string `json:"username" binding:"required"`
	Password string `json:"password" binding:"required"`
}

// Login POST /api/auth/jwt/login/
// body: { "username": "...", "password": "..." }
func (h *AuthHandler) Login(c *gin.Context) {
	var req loginRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"detail": "username 與 password 為必填"})
		return
	}

	// 用 username 查 auth_user
	var user models.User
	if err := database.DB.Where("username = ?", req.Username).First(&user).Error; err != nil {
		// 帳號不存在,回 401 (不洩漏帳號是否存在)
		c.JSON(http.StatusUnauthorized, gin.H{"detail": "帳號或密碼錯誤"})
		return
	}
	if !user.IsActive {
		c.JSON(http.StatusUnauthorized, gin.H{"detail": "帳號已停用"})
		return
	}

	// 比對 Django PBKDF2 密碼
	ok, err := auth.CheckDjangoPassword(req.Password, user.Password)
	if err != nil || !ok {
		c.JSON(http.StatusUnauthorized, gin.H{"detail": "帳號或密碼錯誤"})
		return
	}

	tu := toTokenUser(user)
	access, err := h.jwt.GenerateAccess(tu)
	if err != nil {
		serverError(c)
		return
	}
	refresh, err := h.jwt.GenerateRefresh(tu)
	if err != nil {
		serverError(c)
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"access":  access,
		"refresh": refresh,
		"user": gin.H{
			"id":           user.ID,
			"username":     user.Username,
			"email":        user.Email,
			"first_name":   user.FirstName,
			"last_name":    user.LastName,
			"is_staff":     user.IsStaff,
			"is_superuser": user.IsSuperuser,
		},
	})
}

type refreshRequest struct {
	Refresh string `json:"refresh" binding:"required"`
}

// Refresh POST /api/auth/jwt/refresh/
// 用 refresh token 換一個新的 access token (不查 DB,與 simplejwt 行為一致)
func (h *AuthHandler) Refresh(c *gin.Context) {
	var req refreshRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"detail": "refresh 為必填"})
		return
	}

	claims, err := h.jwt.Parse(req.Refresh)
	if err != nil || claims.TokenType != auth.TokenTypeRefresh {
		c.JSON(http.StatusUnauthorized, gin.H{"detail": "refresh token 無效或已過期"})
		return
	}

	access, err := h.jwt.GenerateAccess(auth.TokenUser{
		ID:          claims.UserID,
		Username:    claims.Username,
		Email:       claims.Email,
		IsStaff:     claims.IsStaff,
		IsSuperuser: claims.IsSuperuser,
	})
	if err != nil {
		serverError(c)
		return
	}
	c.JSON(http.StatusOK, gin.H{"access": access})
}

// Me GET /api/me  (受保護) 從 token 取 user_id,再查 DB 回傳使用者資料
func (h *AuthHandler) Me(c *gin.Context) {
	uid := c.GetInt64(middleware.ContextUserID)

	var user models.User
	if err := database.DB.First(&user, uid).Error; err != nil {
		c.JSON(http.StatusNotFound, gin.H{"detail": "找不到使用者"})
		return
	}
	c.JSON(http.StatusOK, user)
}

// toTokenUser 把 DB model 轉成簽 token 用的精簡結構
func toTokenUser(u models.User) auth.TokenUser {
	return auth.TokenUser{
		ID:          u.ID,
		Username:    u.Username,
		Email:       u.Email,
		IsStaff:     u.IsStaff,
		IsSuperuser: u.IsSuperuser,
	}
}

func serverError(c *gin.Context) {
	c.JSON(http.StatusInternalServerError, gin.H{"detail": "伺服器錯誤"})
}

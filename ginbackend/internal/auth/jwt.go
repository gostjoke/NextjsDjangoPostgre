package auth

// JWT 簽發/驗證。Claims 結構與 Django simplejwt + 專案自訂的
// CustomTokenObtainPairSerializer 完全一致,所以兩邊簽的 token 可互相驗證。

import (
	"errors"
	"strings"
	"time"

	"github.com/golang-jwt/jwt/v5"
	"github.com/google/uuid"
)

const (
	TokenTypeAccess  = "access"
	TokenTypeRefresh = "refresh"
)

// TokenUser 是簽 token 需要的最小使用者資料
type TokenUser struct {
	ID          int64
	Username    string
	Email       string
	IsStaff     bool
	IsSuperuser bool
}

// Claims 對齊 simplejwt payload:
// 標準: token_type, exp, iat, jti, user_id
// 自訂: username, email, is_staff, is_superuser
type Claims struct {
	TokenType   string `json:"token_type"`
	UserID      int64  `json:"user_id"`
	Username    string `json:"username,omitempty"`
	Email       string `json:"email,omitempty"`
	IsStaff     bool   `json:"is_staff"`
	IsSuperuser bool   `json:"is_superuser"`
	jwt.RegisteredClaims
}

// Manager 持有簽章 secret 與兩種 token 的壽命
type Manager struct {
	secret        []byte
	accessExpire  time.Duration
	refreshExpire time.Duration
}

func NewManager(secret string, access, refresh time.Duration) *Manager {
	return &Manager{secret: []byte(secret), accessExpire: access, refreshExpire: refresh}
}

// newJTI 產生 simplejwt 風格的 jti (uuid4 的 hex,去掉 dash)
func newJTI() string {
	return strings.ReplaceAll(uuid.NewString(), "-", "")
}

func (m *Manager) buildClaims(tokenType string, u TokenUser, ttl time.Duration) Claims {
	now := time.Now()
	return Claims{
		TokenType:   tokenType,
		UserID:      u.ID,
		Username:    u.Username,
		Email:       u.Email,
		IsStaff:     u.IsStaff,
		IsSuperuser: u.IsSuperuser,
		RegisteredClaims: jwt.RegisteredClaims{
			ID:        newJTI(),                          // jti
			IssuedAt:  jwt.NewNumericDate(now),           // iat
			ExpiresAt: jwt.NewNumericDate(now.Add(ttl)),  // exp
		},
	}
}

func (m *Manager) sign(c Claims) (string, error) {
	// simplejwt 預設用 HS256 + SECRET_KEY
	return jwt.NewWithClaims(jwt.SigningMethodHS256, c).SignedString(m.secret)
}

// GenerateAccess 簽 access token
func (m *Manager) GenerateAccess(u TokenUser) (string, error) {
	return m.sign(m.buildClaims(TokenTypeAccess, u, m.accessExpire))
}

// GenerateRefresh 簽 refresh token
func (m *Manager) GenerateRefresh(u TokenUser) (string, error) {
	return m.sign(m.buildClaims(TokenTypeRefresh, u, m.refreshExpire))
}

// Parse 驗證簽章與過期時間,回傳 claims
func (m *Manager) Parse(tokenStr string) (*Claims, error) {
	claims := &Claims{}
	token, err := jwt.ParseWithClaims(tokenStr, claims, func(t *jwt.Token) (interface{}, error) {
		// 只接受 HMAC,避免 alg 混淆攻擊
		if _, ok := t.Method.(*jwt.SigningMethodHMAC); !ok {
			return nil, errors.New("非預期的簽章演算法")
		}
		return m.secret, nil
	})
	if err != nil {
		return nil, err
	}
	if !token.Valid {
		return nil, errors.New("token 無效")
	}
	return claims, nil
}

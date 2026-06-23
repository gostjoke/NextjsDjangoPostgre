package config

// 設定載入: 從環境變數 (或 .env) 讀取,所有預設值都對齊 Django 端,
// 確保 JWT 與資料庫可以直接互通。

import (
	"log"
	"os"
	"strconv"
	"time"

	"github.com/joho/godotenv"
)

type Config struct {
	ServerPort string
	GinMode    string

	JWTSecret     string        // 必須等同 Django SECRET_KEY
	AccessExpire  time.Duration // access token 壽命
	RefreshExpire time.Duration // refresh token 壽命

	DBDsn string // GORM 連線字串

	CORSOrigins []string
}

// Load 讀取 .env (若存在) 並組成 Config
func Load() *Config {
	// .env 不存在不算錯,純粹方便本機開發
	_ = godotenv.Load()

	accessMin := getInt("ACCESS_TOKEN_MINUTES", 60)
	refreshDay := getInt("REFRESH_TOKEN_DAYS", 7)

	cfg := &Config{
		ServerPort:    getEnv("SERVER_PORT", "8080"),
		GinMode:       getEnv("GIN_MODE", "debug"),
		JWTSecret:     getEnv("JWT_SECRET", "django-insecure-n$%*)n(3w2+hqlqbzij7yxvrp6c9&$wwib0kca(lk7!o^pqp%x"),
		AccessExpire:  time.Duration(accessMin) * time.Minute,
		RefreshExpire: time.Duration(refreshDay) * 24 * time.Hour,
		DBDsn:         buildDSN(),
		CORSOrigins:   splitCSV(getEnv("CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000")),
	}
	return cfg
}

// buildDSN 組 Postgres 連線字串 (預設對齊 Django settings.py)
func buildDSN() string {
	host := getEnv("DB_HOST", "localhost")
	port := getEnv("DB_PORT", "5432")
	user := getEnv("DB_USER", "postgres")
	pass := getEnv("DB_PASSWORD", "123")
	name := getEnv("DB_NAME", "Django-DB1")
	ssl := getEnv("DB_SSLMODE", "disable")
	return "host=" + host + " port=" + port + " user=" + user +
		" password=" + pass + " dbname=" + name + " sslmode=" + ssl
}

func getEnv(key, def string) string {
	if v := os.Getenv(key); v != "" {
		return v
	}
	return def
}

func getInt(key string, def int) int {
	if v := os.Getenv(key); v != "" {
		if n, err := strconv.Atoi(v); err == nil {
			return n
		}
		log.Printf("[config] %s 不是數字,改用預設 %d", key, def)
	}
	return def
}

// splitCSV 把 "a,b,c" 切成 []string 並去掉空白
func splitCSV(s string) []string {
	var out []string
	start := 0
	for i := 0; i <= len(s); i++ {
		if i == len(s) || s[i] == ',' {
			item := trim(s[start:i])
			if item != "" {
				out = append(out, item)
			}
			start = i + 1
		}
	}
	return out
}

func trim(s string) string {
	for len(s) > 0 && (s[0] == ' ' || s[0] == '\t') {
		s = s[1:]
	}
	for len(s) > 0 && (s[len(s)-1] == ' ' || s[len(s)-1] == '\t') {
		s = s[:len(s)-1]
	}
	return s
}

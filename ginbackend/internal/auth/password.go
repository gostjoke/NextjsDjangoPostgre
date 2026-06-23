package auth

// 驗證 Django 預設密碼雜湊 (PBKDF2-SHA256),這樣就能直接用 auth_user 既有的密碼登入。
// Django 雜湊格式: pbkdf2_sha256$<iterations>$<salt>$<base64 hash>

import (
	"crypto/sha256"
	"crypto/subtle"
	"encoding/base64"
	"errors"
	"strconv"
	"strings"

	"golang.org/x/crypto/pbkdf2"
)

// CheckDjangoPassword 比對明文密碼與 Django 雜湊字串
func CheckDjangoPassword(raw, encoded string) (bool, error) {
	parts := strings.Split(encoded, "$")
	if len(parts) != 4 {
		return false, errors.New("不支援的密碼雜湊格式")
	}
	algorithm, iterStr, salt, hash := parts[0], parts[1], parts[2], parts[3]
	if algorithm != "pbkdf2_sha256" {
		return false, errors.New("不支援的雜湊演算法: " + algorithm)
	}

	iterations, err := strconv.Atoi(iterStr)
	if err != nil {
		return false, err
	}
	expected, err := base64.StdEncoding.DecodeString(hash)
	if err != nil {
		return false, err
	}

	// 用相同 salt / 迭代次數重算;dklen 取雜湊長度 (sha256 = 32)
	dk := pbkdf2.Key([]byte(raw), []byte(salt), iterations, len(expected), sha256.New)

	// 定時比較,避免 timing attack
	return subtle.ConstantTimeCompare(dk, expected) == 1, nil
}

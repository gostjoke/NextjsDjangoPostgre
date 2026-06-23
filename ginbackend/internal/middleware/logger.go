package middleware

// 請求記錄中介層: 印出 狀態碼 / 耗時 / 方法 / 路徑。

import (
	"log"
	"time"

	"github.com/gin-gonic/gin"
)

// Logger 記錄每筆請求的處理結果
func Logger() gin.HandlerFunc {
	return func(c *gin.Context) {
		start := time.Now()
		c.Next() // 先處理請求
		log.Printf("[gin] %3d | %13v | %-7s %s",
			c.Writer.Status(),
			time.Since(start),
			c.Request.Method,
			c.Request.URL.Path,
		)
	}
}

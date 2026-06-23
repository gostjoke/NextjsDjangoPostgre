package database

// GORM + Postgres 連線初始化。連的是 Django 同一個 DB (Django-DB1)。

import (
	"log"
	"time"

	"gorm.io/driver/postgres"
	"gorm.io/gorm"
	"gorm.io/gorm/logger"
)

// DB 為全域連線實例
var DB *gorm.DB

// Init 建立連線並設定連線池
func Init(dsn string) error {
	db, err := gorm.Open(postgres.Open(dsn), &gorm.Config{
		Logger: logger.Default.LogMode(logger.Warn), // 只印 slow query / error
	})
	if err != nil {
		return err
	}

	// 連線池設定
	sqlDB, err := db.DB()
	if err != nil {
		return err
	}
	sqlDB.SetMaxOpenConns(20)
	sqlDB.SetMaxIdleConns(10)
	sqlDB.SetConnMaxLifetime(time.Hour)

	DB = db
	log.Println("[db] PostgreSQL 連線成功")
	return nil
}

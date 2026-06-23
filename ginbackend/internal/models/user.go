package models

// User 直接對應 Django 內建的 auth_user 表 (simplejwt 綁的就是這張表)。
// 不用 GORM AutoMigrate,欄位由 Django migration 維護,這裡只負責讀取。

import "time"

type User struct {
	ID          int64     `gorm:"column:id;primaryKey" json:"id"`
	Password    string    `gorm:"column:password" json:"-"` // Django PBKDF2 雜湊字串,不外洩
	LastLogin   *time.Time `gorm:"column:last_login" json:"last_login"`
	IsSuperuser bool      `gorm:"column:is_superuser" json:"is_superuser"`
	Username    string    `gorm:"column:username" json:"username"`
	FirstName   string    `gorm:"column:first_name" json:"first_name"`
	LastName    string    `gorm:"column:last_name" json:"last_name"`
	Email       string    `gorm:"column:email" json:"email"`
	IsStaff     bool      `gorm:"column:is_staff" json:"is_staff"`
	IsActive    bool      `gorm:"column:is_active" json:"is_active"`
	DateJoined  time.Time `gorm:"column:date_joined" json:"date_joined"`
}

// TableName 指定實體表名 (Django 慣例: <app>_<model>)
func (User) TableName() string {
	return "auth_user"
}

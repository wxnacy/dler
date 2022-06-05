// Package godler  provides ...
package godler

import (
	"io/fs"
	"os"
)

const (
	PermFile fs.FileMode = 0666
	PermDir              = 0755
)

// 判断地址是否存在
func FileExists(filepath string) bool {
	if _, err := os.Stat(filepath); os.IsNotExist(err) {
		return false
	}
	return true
}

// 判断地址是否为目录
func DirExists(dirpath string) bool {
	info, err := os.Stat(dirpath)
	if os.IsNotExist(err) {
		return false
	}
	return info.IsDir()
}

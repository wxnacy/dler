// Package godler  provides ...
package godler

import (
	"io/fs"
	"io/ioutil"
	"os"
	"path"
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

func WriteFile(filePath string, b []byte) error {

	dirpath := path.Dir(filePath)
	if !DirExists(dirpath) {
		os.MkdirAll(dirpath, PermDir)
	}
	return ioutil.WriteFile(filePath, b, PermFile)
}

func AppendFile(filePath string, b []byte) error {

	f, err := os.OpenFile(filePath,
		os.O_APPEND|os.O_CREATE|os.O_WRONLY, PermFile)
	if err != nil {
		return err
	}
	defer f.Close()
	if _, err := f.Write(b); err != nil {
		return err
	}
	return nil
}

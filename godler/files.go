// Package godler  provides ...
package godler

import (
	"io/fs"
	"io/ioutil"
	"os"
	"path"

	"github.com/wxnacy/gotool"
)

const (
	PermFile fs.FileMode = 0666
	PermDir              = 0755
)

// 判断地址是否存在
func FileExists(filepath string) bool {
	return gotool.FileExists(filepath)
}

func WriteFile(filePath string, b []byte) error {

	dirpath := path.Dir(filePath)
	if !gotool.DirExists(dirpath) {
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

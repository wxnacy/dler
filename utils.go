package dler

import (
	"io/ioutil"
	"os"
	"path/filepath"

	"github.com/wxnacy/go-tools"
)

func WriteFile(filePath string, b []byte) error {
	dirpath := filepath.Dir(filePath)
	if !tools.DirExists(dirpath) {
		os.MkdirAll(dirpath, tools.PermDir)
	}
	return ioutil.WriteFile(filePath, b, tools.PermFile)
}

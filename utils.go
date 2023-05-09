package dler

import (
	"bufio"
	"bytes"
	"io"
	"io/ioutil"
	"os"
	"path/filepath"
	"strings"

	"github.com/wxnacy/go-tools"
)

// 从地址获取 io.Reader
func GetReaderFromURI(uri string) (io.Reader, error) {
	var reader io.Reader
	if strings.HasPrefix(uri, "http") {
		b, err := GetGlobalRequst().GetBytes(uri)
		if err != nil {
			return nil, err
		}
		reader = bytes.NewReader(b)
	} else {
		f, err := os.Open(uri)
		if err != nil {
			return nil, err
		}
		reader = bufio.NewReader(f)
	}
	return reader, nil
}

func WriteFile(filePath string, b []byte) error {
	dirpath := filepath.Dir(filePath)
	if !tools.DirExists(dirpath) {
		os.MkdirAll(dirpath, tools.PermDir)
	}
	return ioutil.WriteFile(filePath, b, tools.PermFile)
}

// Package godler  provides ...
package dler

import (
	"bufio"
	"bytes"
	"io"
	"os"
	"strings"
)

type IURIFormater interface {
	FormatURI(string) string
}

type IPathFormater interface {
	FormatPath(string) string
}

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

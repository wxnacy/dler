// Package godler  provides ...
package godler

import (
	"bufio"
	"errors"
	"io"
	"os"
	"strings"

	"github.com/imroc/req/v3"
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
		resp := req.MustGet(uri)
		if resp.IsError() {
			return nil, errors.New(resp.Status)
		}

		if resp.Err != nil {
			return nil, resp.Err
		}
		reader = strings.NewReader(string(resp.Bytes()))
	} else {

		f, err := os.Open(uri)
		if err != nil {
			return nil, err
		}
		reader = bufio.NewReader(f)
	}
	return reader, nil
}

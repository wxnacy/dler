// Package godler  provides ...
package godler

import (
	"bufio"
	"fmt"
	"io"
	"net/url"
	"os"
	"path"
	"strings"

	"github.com/asmcos/requests"
)

type IURIFormater interface {
	FormatURI(string) string
}

type IPathFormater interface {
	FormatPath(string) string
}

type URI struct {
	// URL      *url.URL
	URI      string
	Name     string
	FullName string
	Homepage string
	Dirname  string
}

// 解析地址
func ParseURI(uri string) (*URI, error) {
	URL, err := url.Parse(uri)
	if err != nil {
		return nil, err
	}
	var uriItem URI
	// uriItem := URI{URL: URL}
	uriItem.URI = uri
	uriItem.Homepage = fmt.Sprintf("%s://%s", URL.Scheme, URL.Host)
	uriItem.FullName = path.Base(URL.Path)
	uriItem.Dirname = uriItem.Homepage + strings.Replace(
		URL.Path, uriItem.FullName, "", 1,
	)
	uriItem.Dirname = uriItem.Dirname[:len(uriItem.Dirname)-1]
	uriItem.Name = strings.Replace(
		uriItem.FullName, path.Ext(uriItem.FullName), "", 1)
	return &uriItem, nil
}

// 从地址获取 io.Reader
func GetReaderFromURI(uri string) (io.Reader, error) {

	var reader io.Reader
	if strings.HasPrefix(uri, "http") {

		resp, err := requests.Get(uri)
		if err != nil {
			return nil, err
		}
		reader = strings.NewReader(resp.Text())
	} else {

		f, err := os.Open(uri)
		if err != nil {
			return nil, err
		}
		reader = bufio.NewReader(f)
	}
	return reader, nil
}

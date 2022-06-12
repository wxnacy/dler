// Package godler  provides ...
package godler

import (
	"regexp"
)

type FileDownloader struct {
	DownloadTasker
}

func (m FileDownloader) Match() bool {
	flag, err := regexp.Match("http.*", []byte(m.URI.URI))
	if err != nil {
		return false
	}
	return flag
}

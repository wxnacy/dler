// Package godler  provides ...
package godler

import (
	"errors"
	"fmt"
	"regexp"
)

type DownloadType string

const (
	TYPE_M3U8 DownloadType = "m3u8"
	TYPE_FILE              = "file"
)

type IType interface {
	Match(string) DownloadType
}

type UrlType struct {
}

func (ut UrlType) Match(uri string) (DownloadType, error) {

	reg_type_map := map[string]DownloadType{
		"http.*m3u8.*": TYPE_M3U8,
	}

	for k, v := range reg_type_map {
		flag, err := regexp.Match(k, []byte(uri))
		if err != nil {
			return "", err
		}
		if flag {
			return v, nil
		}
	}
	return "", errors.New(fmt.Sprintf("%s not match download type", uri))
}

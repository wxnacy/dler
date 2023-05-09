// Package godler  provides ...
package dler

import (
	"testing"

	"github.com/wxnacy/go-tools"
)

func TestGetReaderFromURI(t *testing.T) {
	uri := "https://ipconfig.io/country"
	str := "China\n"
	r, err := GetReaderFromURI(uri)
	if err != nil {
		t.Error(err)
	}
	s, _ := tools.StringFromReader(r)
	if s != str {
		t.Error(s)
	}
}

// Package godler  provides ...
package godler

import (
	"testing"
)

func TestParseURI(t *testing.T) {
	uri := "https://b.baobuzz.com/m3u8/566008.m3u8?sign=01de7dde6556f2f8cd01d2b85a170585"

	URI, err := ParseURI(uri)
	if err != nil {
		t.Fatal(err)
	}
	if URI.URI != uri {
		t.Errorf("%v URI is error", URI)
	}
	if URI.FullName != "566008.m3u8" {
		t.Errorf("%v FullName is error", URI)
	}

	if URI.Name != "566008" {
		t.Errorf("%v Name is error", URI)
	}

	if URI.Homepage != "https://b.baobuzz.com" {
		t.Errorf("%v Homepage is error", URI)
	}

	if URI.Dirname != "https://b.baobuzz.com/m3u8" {
		t.Errorf("%v Dirname is error", URI)
	}
}

func TestGetReaderFromURI(t *testing.T) {
	uri := "https://ipconfig.io/country"
	str := "China\n"
	r, err := GetReaderFromURI(uri)
	if err != nil {
		t.Error(err)
	}
	s, _ := ReaderToString(r)
	if s != str {
		t.Error(s)
	}
}

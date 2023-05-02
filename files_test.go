// Package godler  provides ...
package dler

import (
	"testing"
)

func TestFileExists(t *testing.T) {

	if !FileExists("files_test.go") {
		t.Error("files_test.go is exists")
	}
	if FileExists("123files_test.go") {
		t.Error("123files_test.go is not exists")
	}
}

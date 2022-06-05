// Package godler  provides ...
package godler

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

func TestDirExists(t *testing.T) {
	if !DirExists("main") {
		t.Error("main is dir")
	}
	if DirExists("files.go") {
		t.Error("files.go is not dir")
	}
}

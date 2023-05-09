// Package godler  provides ...
package dler

import (
	"path/filepath"

	"github.com/mitchellh/go-homedir"
	"github.com/wxnacy/go-tools"
)

const (
	DOWNLOAD_DIR string = "~/Downloads"
)

var (
	LoggerPath  string
	cacheDir, _ = homedir.Expand("~/.cache/dler")
)

func init() {
	tools.DirExistsOrCreate(cacheDir)
	LoggerPath = filepath.Join(cacheDir, "dler.log")
}

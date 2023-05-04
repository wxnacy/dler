// Package godler  provides ...
package dler

import (
	"os"
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

func GetDefaultDownloadDir() string {
	path, err := homedir.Expand(DOWNLOAD_DIR)
	if err != nil {
		panic(err)
	}
	return path
}

func GetDownloadDir() string {
	envDir := os.Getenv("DLER_DOWNLOAD_DIR")
	envDir, err := homedir.Expand(envDir)
	if err != nil {
		panic(err)
	}
	if envDir != "" {
		return envDir
	}
	return GetDefaultDownloadDir()
}

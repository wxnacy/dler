// Package godler  provides ...
package godler

import (
	"os"

	"github.com/mitchellh/go-homedir"
)

const (
	DOWNLOAD_DIR string = "~/Downloads"
)

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

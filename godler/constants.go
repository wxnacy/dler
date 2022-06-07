// Package godler  provides ...
package godler

import "github.com/mitchellh/go-homedir"

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

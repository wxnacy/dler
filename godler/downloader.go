// Package godler  provides ...
package godler

import (
	"errors"
	"io/ioutil"
	"net/http"
	"os"
	"path/filepath"
)

func Download(url string, path string) error {
	if FileExists(path) {
		return nil
	}
	resp, err := http.Get(url)
	if err != nil {
		return err
	}
	if resp.StatusCode != http.StatusOK {
		b, _ := ioutil.ReadAll(resp.Body)
		return errors.New(string(b))
	}

	b, err := ioutil.ReadAll(resp.Body)
	if err != nil {
		return err
	}
	dirpath := filepath.Dir(path)
	if !DirExists(dirpath) {
		os.MkdirAll(dirpath, PermDir)
	}
	ioutil.WriteFile(path, b, PermFile)
	return nil
}

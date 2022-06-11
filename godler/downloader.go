// Package godler  provides ...
package godler

import (
	"errors"
	"io/ioutil"
	"net/http"
	"os"
	"path/filepath"
)

func Download(uri string, path string) error {
	if FileExists(path) {
		return nil
	}
	resp, err := http.Get(uri)
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

type Segment struct {
	Url  string `json:"url"`
	Path string `json:"path"`
}

// 下载接口
type IDownloader interface {
	Match() bool
	RunTask(*Task) error
}

// 下载器父类
type Downloader struct {
	URI string
}

func (d Downloader) Match() bool {
	return false
}

// 运行下载任务
func (d Downloader) RunTask(task *Task) error {
	if task.Extra != nil {
		seg := task.Extra.(Segment)
		return Download(seg.Url, seg.Path)
	}
	return errors.New("emtry task")
}

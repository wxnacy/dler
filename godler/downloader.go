// Package godler  provides ...
package godler

import (
	"errors"
	"fmt"
	"io/ioutil"
	"net/http"
	"path"
	"strings"
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
	return WriteFile(path, b)
}

type Segment struct {
	Url  string `json:"url"`
	Path string `json:"path"`
}

type DownloadInfo struct {
	Segment
	Type  string
	Extra interface{}
}

func NewDownloadConfig(downloadDir string) *DownloadConfig {
	dlDir := GetDownloadDir()
	if downloadDir != "" {
		dlDir = downloadDir
	}
	return &DownloadConfig{DownloadDir: dlDir}
}

type DownloadConfig struct {
	DownloadDir string
}

// 下载接口
type IDownloader interface {
	Match() bool
	BuildDownloader()
	Download(*DownloadInfo) error
}

// 初始化 Downloader
func NewDownloader(uri string, config *DownloadConfig) (*Downloader, error) {
	URI, err := ParseURI(uri)
	if err != nil {
		return nil, err
	}
	return &Downloader{URI: URI, Config: config}, nil
}

// 下载器父类
type Downloader struct {
	*URI
	// DownloadDir string
	Config *DownloadConfig
}

func (d Downloader) Match() bool {
	return false
}

func (d *Downloader) BuildDownloader() {
}

func (d Downloader) Download(info *DownloadInfo) error {
	return Download(info.Url, info.Path)
}

func (d Downloader) FormatURI(uri string) string {
	if strings.HasPrefix(uri, "http") {
		return uri
	} else if strings.HasPrefix(uri, "/") {
		return d.Homepage + uri
	}
	return fmt.Sprintf("%s/%s", d.Dirname, uri)
}

func (d Downloader) FormatPath(uri string) string {
	return path.Join(d.Config.DownloadDir, path.Base(uri))
}

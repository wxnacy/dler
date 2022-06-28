// Package godler  provides ...
package godler

import (
	"errors"
	"fmt"
	"io/ioutil"
	"net/http"
	"path"
	"strconv"
	"strings"

	"github.com/mitchellh/go-homedir"
)

func HttpGet(uri string, header map[string]string) (*http.Response, error) {
	req, err := http.NewRequest("GET", uri, nil)
	if err != nil {
		return nil, err
	}
	for k, v := range header {
		req.Header.Set(k, v)
	}
	client := &http.Client{}
	return client.Do(req)
}

func Download(uri string, path string, header map[string]string) error {
	if FileExists(path) {
		return nil
	}
	resp, err := HttpGet(uri, header)
	if err != nil {
		return err
	}
	if resp.StatusCode >= http.StatusMultipleChoices {
		b, _ := ioutil.ReadAll(resp.Body)
		return errors.New(string(b))
	}

	b, err := ioutil.ReadAll(resp.Body)
	if err != nil {
		return err
	}
	defer resp.Body.Close()
	return WriteFile(path, b)
}

type Segment struct {
	Url    string            `json:"url"`
	Path   string            `json:"path"`
	Header map[string]string `json:"header"`
}

type DownloadInfo struct {
	Segment
	Type  string      `json:"type"`
	Extra interface{} `json:"extra"`
}

func NewDownloadConfig(downloadDir string, name string) *DownloadConfig {
	dlDir := GetDownloadDir()
	if downloadDir != "" {
		downloadDir, err := homedir.Expand(downloadDir)
		if err != nil {
			panic(err)
		}
		dlDir = downloadDir

	}
	return &DownloadConfig{DownloadDir: dlDir, Name: name}
}

type DownloadConfig struct {
	DownloadDir string
	Name        string
}

// 下载接口
type IDownloader interface {
	Match() bool
	Build()
	Download(*DownloadInfo) error
	Process() float64
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
	Config   *DownloadConfig
	Segments *[]Segment
}

func (d Downloader) GetName() string {
	name := d.URI.FullName
	if d.Config.Name != "" {
		name = d.Config.Name
	}
	return name
}

func (d Downloader) GetPath() string {
	return path.Join(d.Config.DownloadDir, d.GetName())
}

func (d Downloader) GetDir() string {
	return d.Config.DownloadDir
}

func (d Downloader) GetCacheDir() string {
	return path.Join(d.GetDir(), ".dler")
}

func (d Downloader) Match() bool {
	return false
}

func (d *Downloader) Build() {
}

// 获取进度
func (d Downloader) Process() float64 {
	totalNum := len(*d.Segments)
	processNum := 0
	for _, seg := range *d.Segments {
		if FileExists(seg.Path) {
			processNum++
		}
	}
	process := float64(processNum) / float64(totalNum)
	process, _ = strconv.ParseFloat(fmt.Sprintf("%.2f", process), 64)
	return process
}

func (d Downloader) Download(info *DownloadInfo) error {
	return Download(info.Url, info.Path, info.Header)
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
	return path.Join(d.GetDir(), path.Base(uri))
}

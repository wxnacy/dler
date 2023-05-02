// Package godler  provides ...
package dler

import (
	"errors"
	"fmt"
	"log"
	"os"
	"path"
	"strconv"
	"strings"
	"time"

	"github.com/imroc/req/v3"
	"github.com/mitchellh/go-homedir"
	"github.com/wxnacy/go-tools"
)

// func HttpGet(uri string, header map[string]string) (*http.Response, error) {
// req, err := http.NewRequest("GET", uri, nil)
// if err != nil {
// return nil, err
// }
// for k, v := range header {
// req.Header.Set(k, v)
// }
// client := &http.Client{}
// return client.Do(req)
// }

// func Download(uri string, path string, header map[string]string) error {
// if FileExists(path) {
// return nil
// }
// resp, err := HttpGet(uri, header)
// if err != nil {
// return err
// }
// if resp.StatusCode >= http.StatusMultipleChoices {
// b, _ := ioutil.ReadAll(resp.Body)
// return errors.New(string(b))
// }
// b, err := ioutil.ReadAll(resp.Body)
// if err != nil {
// return err
// }
// defer resp.Body.Close()
// return WriteFile(path, b)
// }

type Segment struct {
	Url    string            `json:"url"`  // 下载片段地址
	Path   string            `json:"path"` // 保存地址
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
	return &DownloadConfig{DownloadDir: dlDir, Name: name, Debug: true}
}

type DownloadConfig struct {
	DownloadDir string
	Name        string
	Debug       bool
}

// 下载接口
type IDownloader interface {
	Match() bool
	Build() error
	Download(*DownloadInfo) error
	Process() float64
}

// 初始化 Downloader
func NewDownloader(uri string, config *DownloadConfig) (*Downloader, error) {
	URI, err := tools.URLParse(uri)
	if err != nil {
		return nil, err
	}
	client := req.C().SetTimeout(5 * time.Second)
	if config.Debug {
		log_file, _ := os.OpenFile(LoggerPath, os.O_RDWR|os.O_CREATE|os.O_APPEND, 0666)
		client.DevMode().
			SetLogger(req.NewLogger(log_file, "[REQ] ", log.Ldate|log.Lmicroseconds)).
			EnableDumpAllToFile(LoggerPath).
			EnableDumpAllWithoutBody()
	}
	return &Downloader{URL: URI, Config: config, client: client}, nil
}

// 下载器父类
type Downloader struct {
	*tools.URL
	Config   *DownloadConfig // 下载配置
	Segments *[]Segment      // 下载片段集合
	client   *req.Client     // 网络请求客户端
}

func (d Downloader) GetName() string {
	name := d.URL.FullName
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

func (d *Downloader) Build() error {
	return nil
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

// 对 req 结果报错进行统一处理
func (d Downloader) checkResponseError(r *req.Response, err error) error {
	if err != nil {
		return err
	}
	if r.IsError() {
		return errors.New(r.Status)
	}
	return nil
}

func (d Downloader) Download(info *DownloadInfo) error {
	if FileExists(info.Path) {
		return nil
	}
	// r, err := d.client.R().Head(info.Url)
	// err = d.checkResponseError(r, err)
	// if err != nil {
	// return err
	// }

	// Download to the absolute file path.
	r, err := d.client.R().SetOutputFile(info.Path).Get(info.Url)
	err = d.checkResponseError(r, err)
	if err != nil {
		os.Remove(info.Path)
		return err
	}
	return nil
}

func (d Downloader) FormatURI(uri string) string {
	if strings.HasPrefix(uri, "http") {
		return uri
	} else if strings.HasPrefix(uri, "/") {
		return d.Homepage + uri
	}
	return fmt.Sprintf("%s/%s", d.Dir, uri)
}

func (d Downloader) FormatPath(uri string) string {
	return path.Join(d.GetDir(), path.Base(uri))
}

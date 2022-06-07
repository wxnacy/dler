// Package godler  provides ...
package godler

import (
	"errors"
	"fmt"
	"io/ioutil"
	"net/http"
	"os"
	"path/filepath"
	"sync"

	"github.com/cheggaaa/pb/v3"
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

type ResourceSegment struct {
	URI       string `json:"uri"`
	Path      string `json:"path"`
	RetryTime int    `json:"retry_count"`
	Err       error  `json:"err"`
}

// 异步下载资源片段
func AsyncDownloadSegment(
	seg *ResourceSegment, wg *sync.WaitGroup, processChan chan bool,
	responseChan chan<- *ResourceSegment,
) {
	wg.Add(1)
	go DownloadSegment(seg, wg, processChan, responseChan)
}

// 下载资源片段
func DownloadSegment(
	seg *ResourceSegment, wg *sync.WaitGroup, processChan chan bool,
	responseChan chan<- *ResourceSegment,
) {
	defer wg.Done()
	processChan <- true
	err := Download(seg.URI, seg.Path)
	seg.Err = err
	<-processChan
	responseChan <- seg
}

type DownloadConfig struct {
	ProcessNum     int
	RetryMaxTime   int
	UseProgressBar bool
}

func NewDefaultConfig() *DownloadConfig {
	return &DownloadConfig{
		ProcessNum:     20,
		RetryMaxTime:   99999999,
		UseProgressBar: true,
	}
}

// 下载片段集合
func DownloadSegments(dtos []*ResourceSegment, config *DownloadConfig) {

	process := config.ProcessNum
	processChan := make(chan bool, process)
	// begin := time.Now()

	var wg sync.WaitGroup
	responseChan := make(chan *ResourceSegment)
	for _, dto := range dtos {
		AsyncDownloadSegment(dto, &wg, processChan, responseChan)
	}

	go func() {
		wg.Wait()
		close(responseChan)
		close(processChan)
	}()

	RetryTime := 0
	var bar *pb.ProgressBar
	if config.UseProgressBar {
		bar = pb.Full.Start(len(dtos))
	}
	// 获取结果
	for res := range responseChan {
		// 判断是否需要重试
		if res.Err != nil && res.RetryTime < config.RetryMaxTime {
			res.RetryTime++
			RetryTime++
			AsyncDownloadSegment(res, &wg, processChan, responseChan)
		} else {
			if config.UseProgressBar {

				bar.Increment()
			}
		}
	}
	if config.UseProgressBar {

		bar.Finish()
	}

	fmt.Println(fmt.Sprintf("retry %d", RetryTime))
}

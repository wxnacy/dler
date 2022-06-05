// Package main provides ...
package main

import (
	"encoding/json"
	"fmt"
	"io/ioutil"
	"os"
	"path/filepath"
	"sync"
	"time"

	"github.com/cheggaaa/pb/v3"
	"github.com/wxnacy/dler/godler"
)

const URL string = "https://pic.rmb.bdstatic.com/bjh/ab46afd587c1e0c19e49d78d2a3461e8.jpeg"

type DownloadDTO struct {
	Url  string `json:"url"`
	Path string `json:"path"`
}

type DownloadResDTO struct {
	DownloadDTO
	err error
}

func DoWork() {
	// time.Sleep(1 * time.Second)
}

func GetDTOList(total int) []DownloadDTO {
	result := make([]DownloadDTO, 0)
	for i := 0; i < total; i++ {
		path := fmt.Sprintf(
			"/Users/wxnacy/Downloads/godler/test-%d-%d.jpeg",
			time.Now().Unix(), i)
		dto := DownloadDTO{URL, path}
		result = append(result, dto)
	}
	return result
}

func Deliver(works []DownloadDTO, deliver chan<- DownloadDTO) {
	for _, work := range works {
		deliver <- work
	}
	close(deliver)
}

func Consumption(consum chan<- DownloadResDTO, deliver <-chan DownloadDTO) {
	for work := range deliver {
		// go func(dto DownloadDTO) {
		dto := work
		err := godler.Download(dto.Url, dto.Path)
		consum <- DownloadResDTO{dto, err}
		// }(work)
	}
	close(consum)
}

func AsyncDownloadOne(
	dto DownloadDTO, wg *sync.WaitGroup, processChan chan bool,
	resultChan chan<- DownloadResDTO,
) {
	wg.Add(1)
	go DownloadOne(dto, wg, processChan, resultChan)
}

func DownloadOne(
	dto DownloadDTO, wg *sync.WaitGroup, processChan chan bool,
	resultChan chan<- DownloadResDTO,
) {
	defer wg.Done()
	processChan <- true
	err := godler.Download(dto.Url, dto.Path)
	<-processChan
	resultChan <- DownloadResDTO{dto, err}
}

func DownloadProcess() {

	process := 3
	processChan := make(chan bool, process)

	var wg sync.WaitGroup
	ch1 := make(chan time.Time)
	for i := 0; i < 5; i++ {
		wg.Add(1)
		go func(i int) {
			defer wg.Done()
			// dto := works[i]
			processChan <- true
			// godler.Download(dto.Url, dto.Path)
			DoWork()
			<-processChan
			// time.Sleep(1 * time.Second)
			ch1 <- time.Now()
			// fmt.Println(i)
		}(i)
	}

	go func() {
		wg.Wait()
		close(ch1)
	}()

	for v := range ch1 {
		fmt.Println(v.UnixMicro())
	}
}

func DownloadDTOList(dtos []DownloadDTO) {

	process := 20
	processChan := make(chan bool, process)
	// begin := time.Now()

	var wg sync.WaitGroup
	resultChan := make(chan DownloadResDTO)
	for _, dto := range dtos {
		AsyncDownloadOne(dto, &wg, processChan, resultChan)
	}

	go func() {
		wg.Wait()
		close(resultChan)
		close(processChan)
	}()

	total := len(dtos)
	processNum := 0
	retryNum := 0
	bar := pb.Full.Start(total)

	for result := range resultChan {
		if result.err != nil {
			// fmt.Println("retry " + result.Url)
			retryNum++
			// fmt.Println(fmt.Sprintf("retry %d", retryNum))
			AsyncDownloadOne(result.DownloadDTO, &wg, processChan, resultChan)
		} else {
			bar.Increment()
			processNum++
			// fmt.Println(total, processNum)
			// if processNum%10 == 0 {
			// fmt.Println(time.Now().Sub(begin).Seconds())
			// }

		}
	}
	bar.Finish()
	fmt.Println(fmt.Sprintf("retry %d", retryNum))
}

func ListDir(dir string) []string {
	files, err := ioutil.ReadDir(dir)
	if err != nil {
		return []string{}
	}

	result := make([]string, len(files))
	for _, file := range files {
		result = append(result, filepath.Join(dir, file.Name()))
	}
	return result
}

func GetMapFromFile(path string) (map[string]interface{}, error) {
	bytes, err := ioutil.ReadFile(path)
	if err != nil {
		return nil, err
	}
	result := make(map[string]interface{})
	err = json.Unmarshal(bytes, &result)
	if err != nil {
		return nil, err
	}
	return result, nil
}

func DownloadById(id string) {
	filepaths := ListDir("/Users/wxnacy/.lfsdb/data/download/sub_task-" + id)
	dtos := make([]DownloadDTO, 0)
	for _, path := range filepaths {
		result, err := GetMapFromFile(path)
		if err != nil {
			continue
		}
		dto := DownloadDTO{
			result["download_url"].(string),
			result["download_path"].(string),
		}
		dtos = append(dtos, dto)
	}
	DownloadDTOList(dtos)
}

func main() {

	begin := time.Now()

	action := os.Args[1]

	switch action {
	case "video":
		id := os.Args[2]
		DownloadById(id)
	case "test":
		count := 10000

		// start bar from 'full' template
		bar := pb.Full.Start(count)

		for i := 0; i < count; i++ {
			bar.Increment()
			time.Sleep(time.Millisecond)
		}

		// finish bar
		bar.Finish()
	case "m3u8":
		godler.ParseM3U8("/Users/wxnacy/Downloads/23371.m3u8")
	default:
		fmt.Println("不支持的命令")
	}

	fmt.Println(time.Now().Sub(begin))
}

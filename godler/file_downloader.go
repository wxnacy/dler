// Package godler  provides ...
package godler

import (
	"encoding/json"
	"fmt"
	"io/ioutil"
	"net/http"
	"os"
	"path"
	"regexp"
	"strconv"

	"github.com/wxnacy/gotool"
)

const (
	SEGMENT_SIZE int = 16 * 1024 * 1024
)

type RangeSegment struct {
	Start int
	End   int
}

type Header struct {
	ContentLength []string `json:"Content-Length"`
	AcceptRanges  []string `json:"Accept-Ranges"`
}

func (h Header) GetAcceptRanges() string {
	return h.AcceptRanges[0]
}

func (h Header) GetContentLength() int {
	if h.ContentLength == nil || len(h.ContentLength) < 1 {
		return 0
	}
	val, err := strconv.Atoi(h.ContentLength[0])
	if err != nil {
		panic(err)
	}
	return val
}

func (h Header) GetRangeSegments(SegmentSize int) []RangeSegment {
	length := h.GetContentLength()
	page := int(length/SegmentSize) + 1
	segments := make([]RangeSegment, 0)
	for i := 0; i < page; i++ {
		seg := RangeSegment{i * SegmentSize, (i+1)*SegmentSize - 1}
		if seg.Start >= length {
			break
		}
		if seg.End >= length {
			seg.End = length - 1
		}

		segments = append(segments, seg)
	}
	return segments
}

func (h *Header) ConverHttpHeader(header http.Header) error {
	b, err := json.Marshal(header)
	if err != nil {
		return err
	}
	return json.Unmarshal(b, h)
}

func NewFileDownloader(dt *DownloadTasker) *FileDownloader {
	segments := make([]Segment, 0)
	rangeSegments := make([]RangeSegment, 0)
	cacheDir := path.Join(dt.GetCacheDir(), dt.GetName())
	f := &FileDownloader{
		DownloadTasker: dt,
		RangeSegments:  &rangeSegments,
		CacheDir:       cacheDir,
	}
	f.Segments = &segments
	return f
}

type FileDownloader struct {
	*DownloadTasker
	RangeSegments *[]RangeSegment
	WithPart      bool
	CacheDir      string
}

// 获取缓存目录
// func (f FileDownloader) GetCacheDir() string {
// return path.Join(f.GetDir(), f.GetName())
// }

func (f FileDownloader) Match() bool {
	flag, err := regexp.Match("http.*", []byte(f.URI.URI))
	if err != nil {
		return false
	}
	return flag
}

func (f *FileDownloader) Build() error {
	if !gotool.DirExists(f.CacheDir) {
		os.MkdirAll(f.CacheDir, PermDir)
	}
	resp, err := http.Head(f.URI.URI)
	if err != nil {
		return nil
	}
	header := &Header{}
	err = header.ConverHttpHeader(resp.Header)
	if err != nil {
		return nil
	}
	if resp.ContentLength > int64(SEGMENT_SIZE) {
		f.WithPart = true
	}
	defer resp.Body.Close()
	rangeSegments := header.GetRangeSegments(SEGMENT_SIZE)
	*f.RangeSegments = rangeSegments
	return nil
}

func (f *FileDownloader) buildRangeTasks() {

	for _, rangeSeg := range *f.RangeSegments {
		header := make(map[string]string)
		headerRange := fmt.Sprintf("bytes=%d-%d", rangeSeg.Start, rangeSeg.End)
		header["Range"] = headerRange

		p := path.Join(f.CacheDir, headerRange)
		seg := Segment{
			Url:    f.URI.URI,
			Path:   p,
			Header: header,
		}
		*f.Segments = append(*f.Segments, seg)
		f.AddTask(&Task{Info: DownloadInfo{
			Segment: seg,
		}})
	}
}

func (f *FileDownloader) BuildTasks() error {

	if f.WithPart {
		f.buildRangeTasks()
	} else {
		seg := Segment{
			Url:  f.URI.URI,
			Path: f.GetPath(),
		}
		*f.Segments = append(*f.Segments, seg)
		f.AddTask(&Task{Info: DownloadInfo{Segment: seg}})
	}
	return nil
}

func (f FileDownloader) MergeFile() {
	fmt.Println("开始合并文件")
	filePath := f.GetPath()
	os.Remove(filePath)
	for _, seg := range *f.Segments {
		b, err := ioutil.ReadFile(seg.Path)
		if err != nil {
			panic(err)
		}
		err = AppendFile(filePath, b)
		if err != nil {
			panic(err)
		}
	}
	fmt.Println("合并文件成功")
}

func (f *FileDownloader) AfterRun() error {
	if f.WithPart {
		f.MergeFile()
	}
	f.DownloadTasker.AfterRun()
	os.RemoveAll(f.CacheDir)
	return nil
}

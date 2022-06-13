// Package godler  provides ...
package godler

import (
	"encoding/json"
	"fmt"
	"net/http"
	"path"
	"regexp"
	"strconv"
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

type FileDownloader struct {
	*DownloadTasker
	Segments *[]Segment
}

func (f FileDownloader) Match() bool {
	flag, err := regexp.Match("http.*", []byte(f.URI.URI))
	if err != nil {
		return false
	}
	return flag
}

func (f *FileDownloader) BuildDownloader() {
	// http.Head(f.URI.URI)

}

func (f *FileDownloader) BuildTasks() {

	resp, err := http.Head(f.URI.URI)
	if err != nil {
		panic(err)
	}
	header := &Header{}
	err = header.ConverHttpHeader(resp.Header)
	if err != nil {
		panic(err)
	}
	rangeSegments := header.GetRangeSegments(16 * 1024 * 1024)
	for _, rangeSeg := range rangeSegments {
		header := make(map[string]string)
		headerRange := fmt.Sprintf("bytes=%d-%d", rangeSeg.Start, rangeSeg.End)
		header["Range"] = headerRange

		p := path.Join(
			f.Downloader.Config.DownloadDir,
			headerRange,
		)
		seg := Segment{
			Url:    f.URI.URI,
			Path:   p,
			Header: header,
		}
		fmt.Println(seg)
		f.AddTask(&Task{Info: DownloadInfo{
			Segment: seg,
		}})
	}
}

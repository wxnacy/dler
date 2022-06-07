// Package godler  provides ...
package godler

import (
	"bufio"
	"errors"
	"fmt"
	"io"
	"net/url"
	"os"
	"path"
	"path/filepath"
	"strings"

	"github.com/asmcos/requests"
	"github.com/grafov/m3u8"
)

type Segment struct {
	Url  string `json:"url"`
	Path string `json:"path"`
}

type Resource struct {
	URI      string `json:"uri"`
	Segments *[]Segment
}

type M3U8 struct {
	URI         string
	ID          string
	homepage    string
	dirname     string
	downloadDir string
}

func (m *M3U8) Build(uri string) {
	m.URI = uri
	m.ID = strings.Replace(path.Base(uri), path.Ext(uri), "", 1)
	URL, err := url.Parse(m.URI)
	if err != nil {
		panic(err)
	}
	m.homepage = fmt.Sprintf("%s://%s", URL.Scheme, URL.Host)
	m.dirname = filepath.Dir(m.URI)
	m.downloadDir = path.Join(GetDefaultDownloadDir(), m.ID)
}

func (m *M3U8) FormatURI(uri string) string {
	if strings.HasPrefix(uri, "http") {
		return uri
	} else if strings.HasPrefix(uri, "/") {
		return m.homepage + uri
	}
	return filepath.Join(m.dirname, uri)
}

func (m *M3U8) FormatPath(uri string) string {
	return path.Join(m.downloadDir, path.Base(uri))
}

func ParseM3U8(uri string) *Resource {
	// http.NewRequest("GET", uri)

	var reader io.Reader
	if strings.HasPrefix(uri, "http") {

		resp, err := requests.Get(uri)
		if err != nil {
			panic(err)
		}
		fmt.Println(resp.R.StatusCode)
		fmt.Println(resp.Text())
		reader = strings.NewReader(resp.Text())
	} else {

		f, err := os.Open(uri)
		if err != nil {
			panic(err)
		}
		reader = bufio.NewReader(f)
	}

	p, listType, err := m3u8.DecodeFrom(reader, true)
	if err != nil {
		panic(err)
	}
	var res Resource
	res.URI = uri
	var m3 M3U8
	m3.Build(uri)
	switch listType {
	case m3u8.MEDIA:
		medias := p.(*m3u8.MediaPlaylist)
		segments := make([]Segment, 0)

		// 添加当前地址
		segments = append(segments, Segment{
			m3.FormatURI(uri), m3.FormatPath(uri),
		})

		key := medias.Key
		if key != nil {
			segments = append(segments, Segment{
				m3.FormatURI(key.URI), m3.FormatPath(key.URI),
			})
		}
		fmt.Println(segments)

		for _, seg := range medias.Segments {
			if seg == nil {
				continue
			}
			// fmt.Println(i, seg.URI)
			segments = append(segments, Segment{
				m3.FormatURI(seg.URI), m3.FormatPath(seg.URI),
			})

		}
		res.Segments = &segments
		fmt.Println(len(*res.Segments))
	case m3u8.MASTER:
		masterpl := p.(*m3u8.MasterPlaylist)
		fmt.Printf("%+v\n", masterpl)
		fmt.Println("master")
	}
	return &res
}

type M3U8Downloader struct {
	Tasker
}

func (m *M3U8Downloader) BuildTasks() {
	res := ParseM3U8("https://v3.cdtlas.com/20211220/SxMZSDqv/1100kb/hls/index.m3u8")
	fmt.Println(len(*res.Segments))
	for _, seg := range *res.Segments {
		m.AddTask(&Task{Extra: seg})
	}
}

func (m *M3U8Downloader) RunTask(task *Task) error {
	if task.Extra != nil {
		seg := task.Extra.(Segment)
		return Download(seg.Url, seg.Path)
	}
	return errors.New("emtry task")
}

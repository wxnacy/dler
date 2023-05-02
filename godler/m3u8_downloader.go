// Package godler  provides ...
package godler

import (
	"io/ioutil"
	"path"
	"regexp"
	"strings"

	"github.com/grafov/m3u8"
	"github.com/wxnacy/go-tools"
)

func NewM3U8Downloader(dt *DownloadTasker) *M3U8Downloader {
	m := &M3U8Downloader{
		DownloadTasker: dt,
	}
	segments := make([]Segment, 0)
	m.Segments = &segments
	return m
}

type M3U8Downloader struct {
	*DownloadTasker
	M3U8PlayList m3u8.Playlist
	M3U8ListType m3u8.ListType
}

func (m M3U8Downloader) Match() bool {
	flag, err := regexp.Match("http.*m3u8.*", []byte(m.URL.String()))
	if err != nil {
		return false
	}
	return flag
}

func (m *M3U8Downloader) addSegment(seg Segment) {
	*m.Segments = append(*m.Segments, seg)
}

func (m *M3U8Downloader) Build() error {

	// 解析 m3u8 文件
	reader, err := GetReaderFromURI(m.URL.String())
	if err != nil {
		return err
	}
	m.M3U8PlayList, m.M3U8ListType, err = m3u8.DecodeFrom(reader, true)
	if err != nil {
		return err
	}

	m.ParserM3U8()
	return nil
}

func (m *M3U8Downloader) BuildTasks() error {

	for _, seg := range *m.Segments {
		info := DownloadInfo{Segment: seg}
		m.AddTask(&Task{Info: info})
	}
	return nil
}

func (m M3U8Downloader) FormatPath(uri string) string {
	return path.Join(m.GetDir(), m.Name, path.Base(uri))
}

// 解析 m3u8
func (m *M3U8Downloader) ParserM3U8() {
	switch m.M3U8ListType {
	case m3u8.MEDIA:
		medias := m.M3U8PlayList.(*m3u8.MediaPlaylist)

		key := medias.Key
		if key != nil {

			m.addSegment(Segment{
				Url: m.FormatURI(key.URI), Path: m.FormatPath(key.URI),
			})

			_URI, err := tools.URLParse(key.URI)
			if err != nil {
				panic(err)
			}
			if key.URI != _URI.FullName {
				key.URI = _URI.FullName
			}
		}

		for _, seg := range medias.Segments {
			if seg == nil {
				continue
			}
			// 添加下载片段
			m.addSegment(Segment{
				Url: m.FormatURI(seg.URI), Path: m.FormatPath(seg.URI),
			})

			_URI, err := tools.URLParse(seg.URI)
			if err != nil {
				panic(err)
			}
			if seg.URI != _URI.FullName {
				seg.URI = _URI.FullName
			}
		}
		m.SaveM3U8(medias)

	}
}

// 保存 m3u8 数据
func (m M3U8Downloader) SaveM3U8(mediaPlaylist *m3u8.MediaPlaylist) {
	b, err := ioutil.ReadAll(mediaPlaylist.Encode())
	if err != nil {
		panic(err)
	}

	// 去掉多余 Key
	m3u8Text := string(b)
	texts := strings.Split(m3u8Text, "\n")
	res := make([]string, 0)
	for _, t := range texts {
		if strings.HasPrefix(t, "#EXT-X-KEY") {
			if strings.Contains(t, "URI=\"/") {
				continue
			}
		}
		res = append(res, t)
	}
	b = []byte(strings.Join(res, "\n"))

	WriteFile(m.FormatPath(m.GetName()), b)
}

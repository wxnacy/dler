// Package godler  provides ...
package godler

import (
	"io/ioutil"
	"path"
	"regexp"

	"github.com/grafov/m3u8"
)

type Resource struct {
	URI      string `json:"uri"`
	Segments *[]Segment
}

type M3U8Downloader struct {
	DownloadTasker
	M3U8PlayList m3u8.Playlist
	M3U8ListType m3u8.ListType
	Segments     []Segment
}

func (m M3U8Downloader) Match() bool {
	flag, err := regexp.Match("http.*m3u8.*", []byte(m.URI.URI))
	if err != nil {
		return false
	}
	return flag
}

func (m *M3U8Downloader) addSegment(seg Segment) {
	m.Segments = append(m.Segments, seg)
}

func (m *M3U8Downloader) BuildDownloader() {
	m.Segments = make([]Segment, 0)
	m.DownloadDir = path.Join(m.DownloadDir, m.Name)

	// 解析 m3u8 文件
	reader, err := GetReaderFromURI(m.URI.URI)
	if err != nil {
		panic(err)
	}
	m.M3U8PlayList, m.M3U8ListType, err = m3u8.DecodeFrom(reader, true)
	if err != nil {
		panic(err)
	}

	m.ParserM3U8()
}

func (m *M3U8Downloader) BuildTasks() {

	for _, seg := range m.Segments {
		// fmt.Println(seg)
		info := DownloadInfo{Segment: seg}
		m.AddTask(&Task{Info: info})
	}
}

func (m *M3U8Downloader) ParserM3U8() {
	switch m.M3U8ListType {
	case m3u8.MEDIA:
		medias := m.M3U8PlayList.(*m3u8.MediaPlaylist)

		key := medias.Key
		if key != nil {

			m.addSegment(Segment{
				m.FormatURI(key.URI), m.FormatPath(key.URI),
			})

			_URI, err := ParseURI(key.URI)
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
				m.FormatURI(seg.URI), m.FormatPath(seg.URI),
			})

			_URI, err := ParseURI(seg.URI)
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

func (m M3U8Downloader) SaveM3U8(mediaPlaylist *m3u8.MediaPlaylist) {
	b, err := ioutil.ReadAll(mediaPlaylist.Encode())
	if err != nil {
		panic(err)
	}

	WriteFile(m.FormatPath(m.URI.FullName), b)
}

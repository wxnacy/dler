// Package godler  provides ...
package godler

import (
	"bufio"
	"fmt"
	"net/url"
	"os"
	"strings"

	"github.com/grafov/m3u8"
)

type M3U8 struct {
	URI            string
	SegmentURIList []string
}

// func (m *M3U8) Format() {

// }

func ParseM3U8(uri string) *M3U8 {
	f, err := os.Open(uri)
	if err != nil {
		panic(err)
	}
	p, listType, err := m3u8.DecodeFrom(bufio.NewReader(f), true)
	if err != nil {
		panic(err)
	}
	var m3 M3U8
	switch listType {
	case m3u8.MEDIA:
		medias := p.(*m3u8.MediaPlaylist)
		// fmt.Printf("%+v\n", medias)
		fmt.Println("media")
		fmt.Println(medias.Key.URI)

		segmentURIList := make([]string, 0)
		for i, seg := range medias.Segments {
			if seg == nil {
				continue
			}
			fmt.Println(i, seg.URI)
			uri := seg.URI

			segmentURIList = append(segmentURIList, uri)

		}
		// fmt.Println(len(segmentURIList))
		fmt.Println(medias.Segments[0])
		fmt.Println(medias.Segments[1])
		fmt.Println(len(medias.Segments))
	case m3u8.MASTER:
		masterpl := p.(*m3u8.MasterPlaylist)
		fmt.Printf("%+v\n", masterpl)
		fmt.Println("master")
	}
	// fmt.Println(filepath.Base("https://hot-box-gen.mushroomtrack.com/hls/HaJjNnw642RqIF3i4gNjMQ/1654442836/23000/23371/23371.m3u8"))
	// fmt.Println(filepath.Dir("https://hot-box-gen.mushroomtrack.com/hls/HaJjNnw642RqIF3i4gNjMQ/1654442836/23000/23371/23371.m3u8"))
	URL, _ := url.Parse("https://hot-box-gen.mushroomtrack.com/hls/HaJjNnw642RqIF3i4gNjMQ/1654442836/23000/23371/23371.m3u8")
	fmt.Println(URL.Host, URL.Scheme)
	return &m3
}

// 格式化地址
func FormatURI(uri string, homepage string) string {

	if strings.HasPrefix(uri, "http") {
		return uri
	} else if strings.HasPrefix(uri, "/") {
		return homepage + uri
	}

}

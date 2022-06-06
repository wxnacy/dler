// Package godler  provides ...
package godler

import (
	"bufio"
	"fmt"
	"os"

	"github.com/grafov/m3u8"
)

type M3U8 struct {
	URI            string
	SegmentURIList []string
}

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
	return &m3
}

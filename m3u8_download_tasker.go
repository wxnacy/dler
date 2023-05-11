package dler

import (
	"fmt"
	"io/ioutil"
	"os"
	"path/filepath"
	"strings"
	"time"

	"github.com/grafov/m3u8"
	"github.com/wxnacy/go-tasker"
	"github.com/wxnacy/go-tools"
)

func NewM3U8DownloadTasker(fdlTasker *FileDownloadTasker) *M3U8DownloadTasker {
	return &M3U8DownloadTasker{
		FileDownloadTasker: fdlTasker,
	}
}

type M3U8DownloadTaskInfo struct {
	Url  string
	Path string
}

type M3U8DownloadTasker struct {
	*FileDownloadTasker
	m3u8PlayList m3u8.Playlist
	m3u8ListType m3u8.ListType
}

func (m *M3U8DownloadTasker) Build() error {
	var err error
	err = m.FileDownloadTasker.Build()
	if err != nil {
		return err
	}
	// 解析 m3u8 文件
	reader, err := GetReaderFromURI(m.RawURL)
	if err != nil {
		return err
	}
	m.m3u8PlayList, m.m3u8ListType, err = m3u8.DecodeFrom(reader, true)
	if err != nil {
		return err
	}
	return err
}

func (d *M3U8DownloadTasker) AfterRun() error {
	return nil
}

func (m *M3U8DownloadTasker) BuildTasks() error {
	switch m.m3u8ListType {
	case m3u8.MEDIA:
		medias := m.m3u8PlayList.(*m3u8.MediaPlaylist)

		key := medias.Key
		if key != nil {
			m.AddUrlTask(key.URI)
			_URI, err := tools.URLParse(key.URI)
			if err != nil {
				return err
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
			m.AddUrlTask(seg.URI)
			_URI, err := tools.URLParse(seg.URI)
			if err != nil {
				return err
			}
			if seg.URI != _URI.FullName {
				seg.URI = _URI.FullName
			}
		}
		err := m.saveM3U8(medias)
		if err != nil {
			return err
		}

	}
	return nil
}

// 保存修改过的 m3u8 数据
func (m *M3U8DownloadTasker) saveM3U8(mediaPlaylist *m3u8.MediaPlaylist) error {
	b, err := ioutil.ReadAll(mediaPlaylist.Encode())
	if err != nil {
		return err
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
	path := m.formatPath(m.GetDownloadPath())
	if !strings.HasSuffix(path, ".m3u8") {
		path += ".m3u8"
	}
	err = tools.DirExistsOrCreate(m.GetDownloadPath())
	if err != nil {
		return err
	}
	return tools.FileWriteWithInterface(path, b)
}

func (m *M3U8DownloadTasker) BeforeRun() error {
	return nil
}

func (m M3U8DownloadTasker) RunTask(task *tasker.Task) error {
	info := task.Info.(M3U8DownloadTaskInfo)
	// 已存在的文件不重复下载
	if tools.FileExists(info.Path) {
		return nil
	}
	bytes, err := m.Request.GetBytes(info.Url)
	if err != nil {
		return err
	}
	return os.WriteFile(info.Path, bytes, tools.PermFile)
}

func (m *M3U8DownloadTasker) AddUrlTask(uri string) {
	path := m.formatPath(uri)
	var done bool
	if tools.FileExists(path) {
		done = true
	}
	info := M3U8DownloadTaskInfo{Url: m.formatURI(uri), Path: path}
	m.AddTask(tasker.NewTask(info, done))
}

func (m *M3U8DownloadTasker) formatURI(uri string) string {
	if strings.HasPrefix(uri, "http") {
		return uri
	} else if strings.HasPrefix(uri, "/") {
		return m.URL.Homepage + uri
	}
	return fmt.Sprintf("%s/%s", m.URL.Dir, uri)
}

func (m *M3U8DownloadTasker) formatPath(uri string) string {
	return filepath.Join(m.GetDownloadPath(), filepath.Base(uri))
}

func (d *M3U8DownloadTasker) Exec() error {
	begin := time.Now()
	err := tasker.ExecTasker(d, d.isSync)
	if err == nil {
		out := fmt.Sprintf("下载完成，耗时：%v", time.Now().Sub(begin))
		d.OutputFunc(d.Out, out)
	}
	return err
}

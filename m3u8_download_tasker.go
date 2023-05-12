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

// 定义获取视频源的方法
type FilterMediaFunc func(v []*m3u8.Variant) *m3u8.Variant

func NewM3U8DownloadTasker(fdlTasker *FileDownloadTasker) *M3U8DownloadTasker {
	return &M3U8DownloadTasker{
		FileDownloadTasker: fdlTasker,
		filterMediaFunc: func(variants []*m3u8.Variant) *m3u8.Variant {
			return variants[0]
		},
	}
}

type M3U8DownloadTaskInfo struct {
	Url  string
	Path string
}

type M3U8DownloadTasker struct {
	*FileDownloadTasker
	m3u8PlayList    m3u8.Playlist
	m3u8ListType    m3u8.ListType
	downloadRawUrl  string // 真正下载的地址
	downloadURL     *tools.URL
	filterMediaFunc FilterMediaFunc
}

// 选择下载地址
// 只有当给定地址为 playlist 时才会生效
func (m *M3U8DownloadTasker) SetFilterMediaFunc(fn FilterMediaFunc) *M3U8DownloadTasker {
	m.filterMediaFunc = fn
	return m
}

func (m *M3U8DownloadTasker) Build() error {
	var err error
	err = m.FileDownloadTasker.Build()
	if err != nil {
		return err
	}
	m.downloadRawUrl = m.RawURL
	m.downloadURL = m.URL
	// 解析给定 m3u8 文件
	m3u8PlayList, m3u8ListType, err := m.parseM3U8(m.RawURL)
	if err != nil {
		return err
	}
	// 判定文件是否为视频列表，并过滤
	switch m3u8ListType {
	case m3u8.MASTER:
		medias := m3u8PlayList.(*m3u8.MasterPlaylist)
		v := m.filterMediaFunc(medias.Variants)
		// 重新设置 downloadRawUrl
		m.downloadRawUrl = m.formatURI(v.URI)
		m.downloadURL, err = tools.URLParse(m.downloadRawUrl)
		if err != nil {
			return err
		}
	}
	// 解析视频 m3u8 文件
	m.m3u8PlayList, m.m3u8ListType, err = m.parseM3U8(m.downloadRawUrl)
	if err != nil {
		return err
	}
	out := fmt.Sprintf("下载地址: %s", m.downloadRawUrl)
	m.OutputFunc(m.Out, out)
	return err
}

func (d *M3U8DownloadTasker) AfterRun() error {
	return nil
}

func (m *M3U8DownloadTasker) BuildTasks() error {
	switch m.m3u8ListType {
	case m3u8.MEDIA:
		medias := m.m3u8PlayList.(*m3u8.MediaPlaylist)
		// 解析 key
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

		// 解析 ts 文件
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
	out := fmt.Sprintf("保存地址: %s", m.GetDownloadPath())
	m.OutputFunc(m.Out, out)
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
	// 设置任务是否已经完成
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
		return m.downloadURL.Homepage + uri
	}
	return fmt.Sprintf("%s/%s", m.downloadURL.Dir, uri)
}

func (m *M3U8DownloadTasker) formatPath(uri string) string {
	return filepath.Join(m.GetDownloadPath(), filepath.Base(uri))
}

func (m *M3U8DownloadTasker) parseM3U8(uri string) (p m3u8.Playlist, l m3u8.ListType, err error) {
	reader, err := m.Request.GetReader(uri)
	if err != nil {
		return
	}
	p, l, err = m3u8.DecodeFrom(reader, true)
	if err != nil {
		return
	}
	return
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

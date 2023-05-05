package dler

import (
	"fmt"
	"io"
	"mime"
	"os"
	"path/filepath"
	"strconv"
	"time"

	"github.com/wxnacy/go-tasker"
	"github.com/wxnacy/go-tools"
)

func NewFileDownloadTasker(url string) *FileDownloadTasker {
	t := tasker.NewTasker()
	return &FileDownloadTasker{
		Tasker:      t,
		RawURL:      url,
		segmentSize: 8 * (1 << 20), // 单个分片大小
		Out:         os.Stdout,
	}
}

type FileDownloadTaskInfo struct {
	Index      int
	RangeStart int
	RangeEnd   int
	Path       string
}

type FileDownloadTasker struct {
	*tasker.Tasker
	// 迁移的地址
	RawURL string
	URL    *tools.URL
	Out    io.Writer

	contentLength int
	segmentSize   int
	to            string
	isSync        bool // 是否同步执行
	cacheDir      string
	id            string
	filename      string
	outputDir     string // 手动置顶的保存目录
	outputPath    string // 手动指定的保存地址，优先级比 dir 高
	downloadPath  string
}

func (d *FileDownloadTasker) Build() error {
	var err error
	d.id = tools.Md5(d.RawURL)
	d.cacheDir = filepath.Join(cacheDir, d.id)
	// 构建 URL
	d.URL, err = tools.URLParse(d.RawURL)
	if err != nil {
		return err
	}
	// 获取头信息
	headers, err := GetGlobalRequst().Head(d.RawURL)
	if err != nil {
		return err
	}
	d.contentLength, err = strconv.Atoi(headers.Get("content-length"))
	if err != nil {
		return err
	}
	disposition := headers.Get("Content-Disposition")
	if disposition != "" {
		_, params, err := mime.ParseMediaType(disposition)
		if err != nil {
			return err
		}
		filename, ok := params["filename"]
		if ok {
			d.filename = filename
		}
	}
	d.buildDownloadPath()
	return nil
}

func (d *FileDownloadTasker) AfterRun() error {
	// 写入总文件
	defer os.RemoveAll(d.cacheDir)
	sources := make([]string, 0)
	for _, task := range d.GetTasks() {
		info := task.Info.(FileDownloadTaskInfo)
		sources = append(sources, info.Path)
	}
	return tools.FilesMerge(d.GetDownloadPath(), sources, tools.PermFile)
}

func (d *FileDownloadTasker) BuildTasks() error {
	length := d.contentLength
	page := int(length/d.segmentSize) + 1
	for i := 0; i < page; i++ {
		info := FileDownloadTaskInfo{
			Index:      i,
			RangeStart: i * d.segmentSize,
			RangeEnd:   (i+1)*d.segmentSize - 1,
			Path:       filepath.Join(d.cacheDir, fmt.Sprintf("%s-%d", d.id, i)),
		}
		d.AddTask(&tasker.Task{Info: info})
		if info.RangeStart >= length {
			break
		}
		if info.RangeEnd >= length {
			info.RangeEnd = length - 1
		}
	}
	return nil
}

func (d FileDownloadTasker) RunTask(task *tasker.Task) error {
	info := task.Info.(FileDownloadTaskInfo)
	bytes, err := GetGlobalRequst().GetBytesByRange(d.RawURL, info.RangeStart, info.RangeEnd)
	if err != nil {
		return err
	}
	return os.WriteFile(info.Path, bytes, tools.PermFile)
}

func (d *FileDownloadTasker) BeforeRun() error {
	tools.DirExistsOrCreate(d.cacheDir)
	fmt.Fprintf(d.Out, "下载地址: %s\n", d.GetDownloadPath())
	return nil
}

func (d *FileDownloadTasker) Exec() error {
	begin := time.Now()
	err := tasker.ExecTasker(d, d.isSync)
	if err == nil {
		fmt.Fprintf(d.Out, "下载完成，耗时：%v\n", time.Now().Sub(begin))
	}
	return err
}

// 获取下载地址
func (d *FileDownloadTasker) GetDownloadPath() string {
	// 优先使用 outputPath
	if d.downloadPath == "" {
		d.buildDownloadPath()
	}
	return d.downloadPath
}
func (d *FileDownloadTasker) buildDownloadPath() {
	// 优先使用 outputPath
	if d.outputPath != "" {
		d.downloadPath = d.outputPath
	}
	var dir, filename string
	if d.outputDir != "" {
		dir = d.outputDir
	} else {
		dir, _ = os.Getwd()
	}
	if d.filename != "" {
		filename = d.filename
	} else {
		filename = filepath.Base(d.RawURL)
	}
	d.downloadPath = tools.FileAutoReDownloadName(filepath.Join(dir, filename))
}

func (d *FileDownloadTasker) SetSegmentSize(s int) *FileDownloadTasker {
	d.segmentSize = s
	return d
}

func (d *FileDownloadTasker) SetDownloadPath(path string) *FileDownloadTasker {
	d.outputPath = path
	return d
}

func (d *FileDownloadTasker) SetDownloadDir(dir string) *FileDownloadTasker {
	d.outputDir = dir
	return d
}

func (d *FileDownloadTasker) SetOutput(w io.Writer) *FileDownloadTasker {
	d.Out = w
	return d
}

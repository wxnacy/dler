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

type OutputFunc func(w io.Writer, out string)

func outputFunc(w io.Writer, out string) {
	fmt.Fprintln(w, out)
}

func NewFileDownloadTasker(url string) *FileDownloadTasker {
	t := tasker.NewTasker()
	id := tools.Md5(url)
	return &FileDownloadTasker{
		Tasker:      t,
		RawURL:      url,
		Out:         os.Stdout,
		OutputFunc:  outputFunc,
		Request:     GetGlobalRequst(),
		segmentSize: 8 * (1 << 20), // 单个分片大小
		id:          id,
		cacheDir:    filepath.Join(cacheDir, id),
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
	RawURL     string
	URL        *tools.URL
	OutputFunc OutputFunc
	Out        io.Writer
	Request    *Request
	IsNotCover bool

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
	// 构建 URL
	d.URL, err = tools.URLParse(d.RawURL)
	if err != nil {
		return err
	}
	// 获取头信息
	headers, err := d.Request.Head(d.RawURL)
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
	if d.IsNotCover && d.downloadPath != "" && tools.FileExists(d.GetDownloadPath()) {
		return ErrFileExists
	}
	// 检查下载地址是否合法
	downloadDir := filepath.Dir(d.downloadPath)
	if !tools.DirExists(downloadDir) {
		return fmt.Errorf("%s 目录不存在", downloadDir)
	}
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
	bytes, err := d.Request.GetBytesByRange(d.RawURL, info.RangeStart, info.RangeEnd)
	if err != nil {
		return err
	}
	return os.WriteFile(info.Path, bytes, tools.PermFile)
}

func (d *FileDownloadTasker) BeforeRun() error {
	tools.DirExistsOrCreate(d.cacheDir)
	out := fmt.Sprintf("保存地址: %s", d.GetDownloadPath())
	d.OutputFunc(d.Out, out)
	return nil
}

func (d *FileDownloadTasker) Exec() error {
	begin := time.Now()
	err := tasker.ExecTasker(d, d.isSync)
	if err == nil {
		out := fmt.Sprintf("下载完成，耗时：%v", time.Now().Sub(begin))
		d.OutputFunc(d.Out, out)
	}
	return err
}

func (d *FileDownloadTasker) GetProgress() (float64, error) {
	return tasker.GetTaskerProgress(d)
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
		return
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

func (d *FileDownloadTasker) SetCacheDir(dir string) *FileDownloadTasker {
	d.cacheDir = filepath.Join(dir, d.id)
	return d
}

func (d *FileDownloadTasker) SetNotCover(flag bool) *FileDownloadTasker {
	d.IsNotCover = flag
	return d
}

func (d *FileDownloadTasker) SetRequest(req *Request) *FileDownloadTasker {
	d.Request = req
	return d
}

func (d *FileDownloadTasker) SetProxyURL(url string) *FileDownloadTasker {
	d.Request.Client.SetProxyURL(url)
	return d
}

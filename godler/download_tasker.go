// Package godler  provides ...
package godler

import (
	"errors"
	"fmt"
)

func NewDownloadTaskConfig(
	downloadDir string, name string,
) *DownloadTaskConfig {
	return &DownloadTaskConfig{
		DownloadConfig: NewDownloadConfig(downloadDir, name),
		TaskerConfig:   NewTaskerConfig(),
	}
}

type DownloadTaskConfig struct {
	*TaskerConfig
	*DownloadConfig
}

// 下载任务管理器
type IDownloadTasker interface {
	ITasker
	IDownloader
	RunTask(*Task) error
}

func NewDownloadTasker(
	uri string, config *DownloadTaskConfig,
) (*DownloadTasker, error) {
	downloader, err := NewDownloader(uri, config.DownloadConfig)
	if err != nil {
		return nil, err
	}
	return &DownloadTasker{
		Downloader: downloader, Tasker: NewTasker(config.TaskerConfig),
	}, nil
}

type DownloadTasker struct {
	*Tasker
	*Downloader
}

func (d DownloadTasker) parseTask(task *Task) DownloadInfo {
	if task.Info == nil {
		panic(errors.New("emtry task"))
	}
	info := task.Info.(DownloadInfo)
	return info
}

func (dt *DownloadTasker) AfterRun() {
	fmt.Println("文件下载完成:", dt.GetPath())
}

// 运行下载任务
func (d DownloadTasker) RunTask(task *Task) error {
	info := d.parseTask(task)
	return d.Download(&info)
}

func RunDownloadTasker(t IDownloadTasker) {
	t.Build()
	t.BuildTasks()
	t.BeforeRun()
	t.Run(t.RunTask)
	t.AfterRun()
}

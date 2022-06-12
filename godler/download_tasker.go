// Package godler  provides ...
package godler

import (
	"errors"
)

func NewDownloadTaskConfig(downloadDir string) *DownloadTaskConfig {
	return &DownloadTaskConfig{
		DownloadConfig: NewDownloadConfig(downloadDir),
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

// 运行下载任务
func (d DownloadTasker) RunTask(task *Task) error {
	info := d.parseTask(task)
	return d.Download(&info)
}

func RunDownloadTasker(t IDownloadTasker) {
	t.BuildDownloader()
	t.BuildTasker()
	t.BuildTasks()
	t.BeforeRun()
	t.Run(t.RunTask)
	t.AfterRun()
}

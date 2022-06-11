// Package godler  provides ...
package godler

import (
	"errors"
)

// 下载任务管理器
type IDownloadTasker interface {
	ITasker
	IDownloader
	RunTask(*Task) error
}

type DownloadTasker struct {
	Tasker
	Downloader
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

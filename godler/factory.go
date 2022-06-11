// Package godler  provides ...
package godler

import "errors"

// 下载任务管理器
type IDownloadTasker interface {
	ITasker
	IDownloader
}

// 匹配下载任务器
func MatchDownloadTasker(
	uri string, config *TaskerConfig,
) (IDownloadTasker, error) {
	downloaders := []IDownloadTasker{
		// m3u8 下载
		&M3U8Downloader{
			Downloader: Downloader{URI: uri},
			Tasker:     Tasker{Config: config},
		},
	}
	for _, d := range downloaders {
		if d.Match() {
			return d, nil
		}
	}
	return nil, errors.New("No Downloader Match")
}

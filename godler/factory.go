// Package godler  provides ...
package godler

import "errors"

// 匹配下载任务器
func MatchDownloadTasker(
	uri string, config *TaskerConfig,
) (IDownloadTasker, error) {

	downloader, err := NewDownloader(uri, NewDownloadConfig(""))
	if err != nil {
		return nil, err
	}

	tasker := NewTasker(config)
	dt := DownloadTasker{
		Downloader: downloader,
		Tasker:     tasker,
	}

	taskers := []IDownloadTasker{
		// m3u8 下载
		&M3U8Downloader{
			DownloadTasker: dt,
		},
	}
	for _, d := range taskers {
		if d.Match() {
			return d, nil
		}
	}
	return nil, errors.New("No Downloader Match")
}

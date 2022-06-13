// Package godler  provides ...
package godler

import "errors"

// 匹配下载任务器
func MatchDownloadTasker(
	uri string, config *DownloadTaskConfig,
) (IDownloadTasker, error) {

	dt, err := NewDownloadTasker(uri, config)
	if err != nil {
		return nil, err
	}

	taskers := []IDownloadTasker{
		// m3u8 下载
		&M3U8Downloader{DownloadTasker: dt},
		// 文件下载
		&FileDownloader{DownloadTasker: dt},
	}
	for _, d := range taskers {
		if d.Match() {
			return d, nil
		}
	}
	return nil, errors.New("No Downloader Match")
}

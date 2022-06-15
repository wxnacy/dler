// Package godler  provides ...
package godler

import "errors"

type NewDownloaderFunc func(*DownloadTasker) IDownloadTasker

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
		NewM3U8Downloader(dt),
		// 文件下载
		NewFileDownloader(dt),
	}
	for _, d := range taskers {
		if d.Match() {
			return d, nil
		}
	}
	return nil, errors.New("No Downloader Match")
}

// func MatchDownloaderInitFunc(uri string) (NewDownloaderFunc, error) {
// // dtype, err := UrlType{}.Match(uri)
// // if err != nil {
// // return nil, err
// // }

// // switch dtype {
// // case TYPE_M3U8:
// // return NewM3U8Downloader, nil
// // }
// var TypeDownloaderFuncMap map[DownloadType]func(*DownloadTasker) IDownloader
// TypeDownloaderFuncMap[TYPE_M3U8] = NewM3U8Downloader
// return nil, nil
// }

// Package main provides ...
package main

import (
	"fmt"
	"os"
	"time"

	"github.com/cheggaaa/pb/v3"
	"github.com/wxnacy/dler/godler"
)

func main() {

	begin := time.Now()

	action := os.Args[1]

	switch action {
	case "video":
		id := os.Args[2]
		godler.DownloadById(id)
	case "test":
		count := 10000

		// start bar from 'full' template
		bar := pb.Full.Start(count)

		for i := 0; i < count; i++ {
			bar.Increment()
			time.Sleep(time.Millisecond)
		}

		// finish bar
		bar.Finish()
	case "m3u8":
		// godler.ParseM3U8("/Users/wxnacy/Downloads/23371.m3u8")
		fmt.Println("")
	case "start":
		// godler.ParseM3U8("/Users/wxnacy/Downloads/23371.m3u8")
		fmt.Println("")
	case "task":
		tasker := godler.M3U8Downloader{
			Tasker: godler.Tasker{Config: godler.NewDefaultTaskerConfig()},
		}
		tasker.Build()
		tasker.BuildTasks()
		tasker.Run(tasker.RunTask)
	default:
		fmt.Println("不支持的命令")
	}

	fmt.Println(time.Now().Sub(begin))
}

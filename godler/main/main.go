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
	args := os.Args[1:]

	action := args[0]

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
		uri := args[1]
		t, err := godler.MatchDownloadTasker(
			uri, godler.NewDefaultTaskerConfig(),
		)
		if err != nil {
			panic(err)
		}
		t.Build()
		t.BuildTasks()
		t.Run(t.RunTask)
	case "task":
		uri := args[1]
		t, err := godler.MatchDownloadTasker(uri, godler.NewDefaultTaskerConfig())
		if err != nil {
			panic(err)
		}
		t.Build()
		t.BuildTasks()
		t.Run(t.RunTask)
	default:
		fmt.Println("不支持的命令")
	}

	fmt.Println(time.Now().Sub(begin))
}

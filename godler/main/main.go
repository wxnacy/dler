// Package main provides ...
package main

import (
	"fmt"
	"os"
	"time"

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
		fmt.Println("")
	case "m3u8":
		fmt.Println("")
	case "start":
		uri := args[1]
		t, err := godler.MatchDownloadTasker(
			uri, godler.NewDefaultTaskerConfig(),
		)
		if err != nil {
			panic(err)
		}
		godler.RunDownloadTasker(t)
	case "task":
		fmt.Println("task")
	default:
		fmt.Println("不支持的命令")
	}

	fmt.Println(time.Now().Sub(begin))
}

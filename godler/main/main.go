// Package main provides ...
package main

import (
	"fmt"
	"os"
	"regexp"
	"time"

	"github.com/akamensky/argparse"
	"github.com/wxnacy/dler/godler"
)

var (
	uriArg         string
	downloadDirArg *string
	nameArg        *string

	testCommand *argparse.Command
)

func init() {
	ParserURIArg()
	InitArgparse()
}

func InitArgparse() {
	parser := argparse.NewParser("godler", "Download file manager")

	// Create string flag
	downloadDirArg = parser.String("", "download-dir", &argparse.Options{Required: false, Help: "String to print"})
	// 下载名称
	nameArg = parser.String("n", "name", &argparse.Options{Required: false, Help: "Download Name"})

	// 测试命令
	testCommand = parser.NewCommand("test", "测试程序")
	// Parse input
	err := parser.Parse(os.Args)
	if err != nil && uriArg == "" {
		// In case of error print error and print usage
		// This can also be done by passing -h or --help flags
		fmt.Print(parser.Usage(err))
	}
}

// 解析地址参数
func ParserURIArg() {
	args := os.Args[1:]
	for _, arg := range args {
		flag, _ := regexp.Match("^http.*$", []byte(arg))
		if flag {
			uriArg = arg
		}
	}
}

// 运行下载命令
func RunDownloadCommand() {
	t, err := godler.MatchDownloadTasker(
		uriArg, godler.NewDownloadTaskConfig(*downloadDirArg, *nameArg),
	)
	if err != nil {
		panic(err)
	}
	godler.RunDownloadTasker(t)

}

func main() {

	begin := time.Now()
	if testCommand.Happened() {
		path := fmt.Sprintf("/Users/wxnacy/Downloads/%d", time.Now().Unix())
		err := godler.Download(
			"https://v3-default.ixigua.com/70050e6d79f5ccf082a85126c8f6ed55/62a749b2/video/tos/cn/tos-cn-v-6f4170/9a2aa8ac131d4ab2ba49724c8ce22bbc/?zxzjtv&filename=1.mp4",
			path,
			map[string]string{"Range": "bytes=0-1024"},
		)
		fmt.Println(err)
	} else {
		RunDownloadCommand()
	}

	fmt.Println(time.Now().Sub(begin))
}

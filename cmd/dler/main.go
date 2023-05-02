// Package main provides ...
package main

import (
	"fmt"
	"os"
	"regexp"
	"time"

	"github.com/akamensky/argparse"
	"github.com/wxnacy/dler"
)

var (
	uriArg         string
	downloadDirArg *string
	nameArg        *string
	processArg     *bool

	testCommand *argparse.Command
)

func init() {
	ParserURIArg()
	InitArgparse()
}

func InitArgparse() {
	parser := argparse.NewParser("dler", "Download file manager")

	// Create string flag
	downloadDirArg = parser.String("d", "download-dir", &argparse.Options{Required: false, Help: "String to print"})
	// 下载名称
	nameArg = parser.String("n", "name", &argparse.Options{Required: false, Help: "Download Name"})
	// 获取进度
	processArg = parser.Flag("p", "--process", &argparse.Options{Required: false, Help: "获取进度"})

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
	t, err := dler.MatchDownloadTasker(
		uriArg, dler.NewDownloadTaskConfig(*downloadDirArg, *nameArg),
	)
	if err != nil {
		panic(err)
	}

	if *processArg {
		dler.ProcessDownloadTasker(t)
		return
	}
	err = dler.RunDownloadTasker(t)
	if err != nil {
		panic(err)
	}

}

func main() {

	begin := time.Now()
	if testCommand.Happened() {
		dler.Log.Infof("w")
	} else {
		RunDownloadCommand()
	}

	fmt.Printf("进程耗时：%v\n", time.Now().Sub(begin))
}

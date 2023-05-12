/*
Copyright © 2023 NAME HERE <EMAIL ADDRESS>

*/
package cmd

import (
	"fmt"
	"os"
	"regexp"
	"strings"

	"github.com/grafov/m3u8"
	"github.com/spf13/cobra"
	"github.com/wxnacy/dler"
	"github.com/wxnacy/go-tasker"
	"github.com/wxnacy/go-tools"
)

var (
	rootCommand = &RootCommand{}
)

type RootCommand struct {
	url            string
	outputPath     string
	outputDir      string
	isShowProgress bool
	isNotCover     bool
	isToM3u8       bool
	headers        []string
	isVerbose      bool
	downloadIndex  int
}

func (r RootCommand) GetHeaders() map[string]string {
	headers := make(map[string]string, 0)
	for _, h := range r.headers {
		hArr := strings.SplitN(h, ":", 2)
		headers[hArr[0]] = strings.TrimLeft(hArr[1], " ")
	}
	return headers
}

func (r *RootCommand) check() error {
	isUrl, err := regexp.MatchString("^http.*", r.url)
	if err != nil {
		return err
	}
	if !isUrl {
		return fmt.Errorf("%s 不符合 URL 标准", r.url)
	}
	return nil
}

func (r *RootCommand) Run(args []string) error {
	if len(args) > 0 {
		r.url = args[0]
	}
	r.check()
	var dlTasker dler.IDLTasker
	var itasker tasker.ITasker
	fdlTasker := dler.NewFileDownloadTasker(r.url).
		SetDownloadDir(r.outputDir).
		SetDownloadPath(r.outputPath).
		SetNotCover(r.isNotCover)
	// 开启赘余输出
	if r.isVerbose {
		fdlTasker.Request.EnableVerbose()
	}
	// 设置 headers
	headers := r.GetHeaders()
	if len(headers) > 0 {
		fdlTasker.Request.SetHeaders(headers)
	}

	dlTasker = fdlTasker
	itasker = fdlTasker
	if r.isToM3u8 {
		mdlTasker := dler.NewM3U8DownloadTasker(fdlTasker).SetFilterMediaFunc(func(variants []*m3u8.Variant) *m3u8.Variant {
			return variants[r.downloadIndex]
		})
		dlTasker = mdlTasker
		itasker = mdlTasker
	}
	// 展示完成进度
	if r.isShowProgress {
		p, err := tasker.GetTaskerProgress(itasker)
		if err != nil {
			return err
		}
		fmt.Println(tools.FormatFloat(p, 2))
		return nil
	}
	err := dlTasker.Exec()
	return err
}

// rootCmd represents the base command when called without any subcommands
var rootCmd = &cobra.Command{
	Use:     "dler",
	Short:   "文件下载器",
	Version: dler.Version,
	Example: `  dler https://example.com/index.html				下载文件到当前目录
  dler https://example.com/index.html -o ~/Downloads/dler.html	下载文件到指定文件
  dler https://example.com/index.html -d ~/Downloads		下载文件到指定目录
  dler https://example.com/index.m3u8 --to-m3u8			将文件作为 m3u8 下载到本地
`,
	Run: func(cmd *cobra.Command, args []string) {
		if len(args) == 0 {
			cmd.Help()
			return
		}
		err := rootCommand.Run(args)
		if err != nil {
			fmt.Printf("Error: %v\n", err)
		}
	},
}

// Execute adds all child commands to the root command and sets flags appropriately.
// This is called by main.main(). It only needs to happen once to the rootCmd.
func Execute() {
	err := rootCmd.Execute()
	if err != nil {
		os.Exit(1)
	}
}

func init() {
	pwd, _ := os.Getwd()
	rootCmd.Flags().StringVarP(&rootCommand.outputDir, "output-dir", "d", pwd, "保存目录。默认为当前目录")
	rootCmd.Flags().StringVarP(&rootCommand.outputPath, "output-path", "o", "", "保存地址。覆盖已存在文件，优先级比 --output-dir 高")
	rootCmd.Flags().BoolVarP(&rootCommand.isShowProgress, "progress", "p", false, "仅展示已下载的进度")
	rootCmd.Flags().BoolVarP(&rootCommand.isNotCover, "not-cover", "", false, "是否不要覆盖本地文件，当 --path 有值时生效")
	rootCmd.Flags().BoolVarP(&rootCommand.isToM3u8, "to-m3u8", "", false, "下载为 m3u8 文件")
	rootCmd.Flags().IntVarP(&rootCommand.downloadIndex, "index", "i", 0, "当出现下载列表时，需要下载的索引")
	rootCmd.Flags().StringArrayVarP(&rootCommand.headers, "header", "H", []string{}, "携带的头信息")
	rootCmd.PersistentFlags().BoolVarP(&rootCommand.isVerbose, "verbose", "v", false, "打印赘余信息")
}

/*
Copyright © 2023 NAME HERE <EMAIL ADDRESS>

*/
package cmd

import (
	"fmt"
	"os"
	"regexp"
	"strings"

	"github.com/spf13/cobra"
	"github.com/wxnacy/dler"
)

var (
	rootCommand = &RootCommand{}
)

type RootCommand struct {
	url           string
	outputPath    string
	outputDir     string
	IsShowProcess bool
	isNotCover    bool
	headers       []string
	isVerbose     bool
}

func (r RootCommand) GetHeaders() map[string]string {
	headers := make(map[string]string, 0)
	for _, h := range r.headers {
		hArr := strings.SplitN(h, ":", 2)
		headers[hArr[0]] = strings.TrimLeft(hArr[1], " ")
	}
	return headers
}

func (r *RootCommand) init() error {
	isUrl, err := regexp.MatchString("^http.*", r.url)
	if err != nil {
		return err
	}
	if !isUrl {
		return fmt.Errorf("%s 不符合 URL 标准", r.url)
	}
	if r.isVerbose {
		dler.GetGlobalRequst().EnableVerbose()
	}
	// 设置 headers
	headers := r.GetHeaders()
	if len(headers) > 0 {
		dler.GetGlobalRequst().SetHeaders(headers)
	}
	return nil
}

func (r *RootCommand) Run(args []string) error {
	if len(args) > 0 {
		r.url = args[0]
	}
	r.init()
	dlTasker := dler.NewFileDownloadTasker(r.url).
		SetDownloadDir(r.outputDir).
		SetDownloadPath(r.outputPath)
	dlTasker.IsNotCover = r.isNotCover
	err := dlTasker.Exec()
	return err
}

// rootCmd represents the base command when called without any subcommands
var rootCmd = &cobra.Command{
	Use:   "dler",
	Short: "文件下载器",
	// Uncomment the following line if your bare application
	// has an action associated with it:
	Run: func(cmd *cobra.Command, args []string) {
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
	rootCmd.Flags().BoolVarP(&rootCommand.IsShowProcess, "process", "p", false, "仅展示已下载的进度")
	rootCmd.Flags().BoolVarP(&rootCommand.isNotCover, "not-cover", "", false, "是否不要覆盖本地文件，当 --path 有值时生效")
	rootCmd.Flags().StringArrayVarP(&rootCommand.headers, "header", "H", []string{}, "携带的头信息")
	rootCmd.PersistentFlags().BoolVarP(&rootCommand.isVerbose, "verbose", "v", false, "打印赘余信息")
}

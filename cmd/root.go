/*
Copyright © 2023 NAME HERE <EMAIL ADDRESS>

*/
package cmd

import (
	"fmt"
	"os"
	"path/filepath"
	"regexp"
	"time"

	"github.com/spf13/cobra"
	"github.com/wxnacy/dler"
	"github.com/wxnacy/go-tools"
)

var (
	rootCommand = &RootCommand{}
)

type RootCommand struct {
	url           string
	output        string
	IsShowProcess bool
}

func (r *RootCommand) Run(args []string) error {
	if len(args) > 0 {
		r.url = args[0]
	}
	isUrl, err := regexp.MatchString("^http.*", r.url)
	if err != nil {
		return err
	}
	if !isUrl {
		return fmt.Errorf("%s 不符合 URL 标准", r.url)
	}

	var downloadDir, name string
	path := r.output
	if path != "" {
		if tools.DirExists(path) {
			downloadDir = path
		} else {
			dir := filepath.Dir(path)
			if tools.DirExists(dir) {
				downloadDir = dir
				// name = filepath.Base(path)
			} else {
				return fmt.Errorf("%s 文件夹不存在", dir)
			}
		}
	}
	t, err := dler.MatchDownloadTasker(
		r.url, dler.NewDownloadTaskConfig(downloadDir, name),
	)
	if err != nil {
		return err
	}
	if r.IsShowProcess {
		dler.ProcessDownloadTasker(t)
		return nil
	}
	begin := time.Now()
	err = dler.RunDownloadTasker(t)
	fmt.Printf("下载完成耗时：%v\n", time.Now().Sub(begin))
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
	rootCmd.Flags().StringVarP(&rootCommand.output, "output", "o", "", "保存地址。如果指定文件夹则使用地址名称保存该文件夹中，如果不是则覆盖文件保存")
	rootCmd.Flags().BoolVarP(&rootCommand.IsShowProcess, "process", "p", false, "仅展示已下载的进度")
}

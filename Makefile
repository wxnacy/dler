# Makefile for dler - A file downloader written in Go

# 获取当前版本号
VERSION := $(shell grep -E 'var Version = "([^"]+)"' version.go | sed -E 's/.*"([^"]+)".*/\1/')

# 项目名称
BINARY_NAME := dler
BINARY_UNIX := $(BINARY_NAME)_unix
BINARY_WINDOWS := $(BINARY_NAME)_windows.exe
BINARY_DARWIN := $(BINARY_NAME)_darwin

# Go 相关变量
GO := go
GOBUILD := $(GO) build
GOCLEAN := $(GO) clean
GOTEST := $(GO) test
GOGET := $(GO) get
GOMOD := $(GO) mod
GOFMT := $(GO) fmt
GOVET := $(GO) vet
GOPATH := $(shell go env GOPATH)
GOBIN := $(GOPATH)/bin

# 源文件目录
MAIN_DIR := cmd/dler
MAIN_PKG := ./$(MAIN_DIR)
SRCS := $(wildcard *.go cmd/*.go cmd/*/*.go)

# 构建标志
BUILD_FLAGS := -v
LDFLAGS := 

# 安装目录
PREFIX ?= /usr/local
BINDIR ?= $(PREFIX)/bin
COMPLETION_DIR_ZSH ?= ~/.zsh/completions

# 默认目标
.DEFAULT_GOAL := help

# 帮助信息
.PHONY: help
help: ## 显示帮助信息
	@echo "Usage: make [target]"
	@echo ""
	@echo "General targets:"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

# 构建二进制文件
.PHONY: build
build: ## 构建项目
	$(GOBUILD) $(BUILD_FLAGS) -o $(BINARY_NAME) $(MAIN_PKG)

# 安装二进制文件
.PHONY: install
install: build ## 构建并安装二进制文件到 GOPATH
	install -m 755 $(BINARY_NAME) $(GOBIN)/$(BINARY_NAME)

# 安装自动补全脚本
.PHONY: install-completion
install-completion: ## 安装 zsh 自动补全脚本到用户目录
	@echo "Installing zsh completion script to user directory..."
	./scripts/completion/install_completion.sh

# 清理构建文件
.PHONY: clean
clean: ## 清理构建产物
	$(GOCLEAN)
	rm -f $(BINARY_NAME) $(BINARY_UNIX) $(BINARY_WINDOWS) $(BINARY_DARWIN)

# 运行测试
.PHONY: test
test: ## 运行测试
	$(GOTEST) -v ./...

# 检查代码格式
.PHONY: fmt
fmt: ## 格式化代码
	$(GOFMT) ./...

# 代码静态检查
.PHONY: vet
vet: ## 静态检查代码
	$(GOVET) ./...

# 代码质量检查
.PHONY: check
check: fmt vet ## 代码质量检查

# 下载依赖
.PHONY: deps
deps: ## 下载项目依赖
	$(GOMOD) download

# 整理依赖
.PHONY: tidy
tidy: ## 整理 go.mod 文件
	$(GOMOD) tidy

# 更新依赖
.PHONY: update
update: ## 更新项目依赖
	$(GOGET) -u ./...

# 构建跨平台二进制文件
.PHONY: build-all
build-all: build-linux build-windows build-darwin ## 构建所有平台的二进制文件

.PHONY: build-linux
build-linux: ## 构建 Linux 二进制文件
	GOOS=linux GOARCH=amd64 $(GOBUILD) $(BUILD_FLAGS) -o $(BINARY_UNIX) $(MAIN_PKG)

.PHONY: build-windows
build-windows: ## 构建 Windows 二进制文件
	GOOS=windows GOARCH=amd64 $(GOBUILD) $(BUILD_FLAGS) -o $(BINARY_WINDOWS) $(MAIN_PKG)

.PHONY: build-darwin
build-darwin: ## 构建 macOS 二进制文件
	GOOS=darwin GOARCH=amd64 $(GOBUILD) $(BUILD_FLAGS) -o $(BINARY_DARWIN) $(MAIN_PKG)

# 发布新版本
.PHONY: release
release: check tidy ## 发布新版本
	@echo "当前版本: $(VERSION)"
	@echo "正在创建并推送 Git 标签 v$(VERSION)..."
	./scripts/version/release.sh

# 递增版本号
.PHONY: incr-version
incr-version: ## 递增版本号
	./scripts/version/incr-version.sh

# 显示当前版本
.PHONY: version
version: ## 显示当前版本号
	@echo "当前版本: $(VERSION)"
	@./scripts/version/show-version.sh

# 运行程序
.PHONY: run
run: ## 运行程序，使用方式: make run ARGS="your args"
	$(GO) run $(MAIN_PKG) $(ARGS)

# 运行程序（带参数）
.PHONY: run-args
run-args: ## 运行程序（带参数），使用方式: make run-args ARGS="your args"
	$(GO) run $(MAIN_PKG) $(ARGS)

# 查看模块依赖图
.PHONY: mod-graph
mod-graph: ## 查看模块依赖图
	$(GOMOD) graph | dot -Tpng -o mod-graph.png
	@echo "依赖图已保存到 mod-graph.png"

# 生成文档
.PHONY: docs
docs: ## 生成项目文档
	$(GO) doc -all ./...

# 检查安全问题
.PHONY: security
security: ## 检查安全问题
	$(GO) list -m all | nancy sleuth || echo "警告: 发现安全问题"

# 性能测试
.PHONY: bench
bench: ## 运行性能测试
	$(GOTEST) -bench=. -benchmem ./...

# 代码覆盖率
.PHONY: cover
cover: ## 运行测试并生成覆盖率报告
	$(GOTEST) -coverprofile=coverage.out ./...
	$(GO) tool cover -html=coverage.out -o coverage.html
	@echo "覆盖率报告已保存到 coverage.html"

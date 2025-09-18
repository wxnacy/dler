#compdef dler

# dler 命令自动补全脚本 (zsh)
# 兼容 Warp 终端和其他现代 zsh 环境

# Warp 终端兼容性检查和增强
if [[ $TERM_PROGRAM == "WarpTerminal" ]]; then
    # 启用 Warp 特定优化
    zstyle ':completion:*' menu select
    zstyle ':completion:*' list-colors ''
    zstyle ':completion:*:descriptions' format '%B%d%b'

    # 强制刷新补全（在 Warp 中）
    autoload -Uz compinit
    compinit -u &>/dev/null
fi

_dler() {
    local -a opts
    local curcontext="$curcontext" state line

    # 支持的选项
    opts=(
        '(-H --header)'{-H,--header}'[HTTP头信息 (格式: Key: Value)]:header:'
        '(-h --help)'{-h,--help}'[显示帮助信息]'
        '(-i --index)'{-i,--index}'[指定索引]:index:'
        '--not-cover[不覆盖已存在的文件]'
        '(-d --output-dir)'{-d,--output-dir}'[输出目录]:output-dir:_files -/'
        '(-o --output-path)'{-o,--output-path}'[输出文件路径]:output-path:_files'
        '(-p --progress)'{-p,--progress}'[显示下载进度]'
        '(-s --segment-size)'{-s,--segment-size}'[分片大小 (字节)]:segment-size:'
        '--to-m3u8[转换为m3u8格式]'
        '(-v --verbose)'{-v,--verbose}'[详细输出]'
        '--version[显示版本信息]'
    )

    _arguments -s -S \
        ':URL:_urls' \
        $opts && return 0
}

_dler "$@"


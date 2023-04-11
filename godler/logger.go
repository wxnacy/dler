package godler

import (
	"fmt"
	"io"
	"log"
	"os"
	"path/filepath"
	"runtime"
)

var (
	Log Logger
)

func init() {
	Log = createDefaultLogger()
}

type Logger interface {
	Infof(format string, v ...interface{})
	Errorf(format string, v ...interface{})
	Warnf(format string, v ...interface{})
	Debugf(format string, v ...interface{})
}

// NewLogger create a Logger wraps the *log.Logger
func NewLogger(output io.Writer, prefix string, flag int) Logger {
	return &logger{l: log.New(output, prefix, flag)}
}

func createDefaultLogger() Logger {
	log_file, _ := os.OpenFile(LoggerPath, os.O_RDWR|os.O_CREATE|os.O_APPEND, 0666)
	return NewLogger(log_file, "[DLER] ", log.Ldate|log.Lmicroseconds)
}

var _ Logger = (*logger)(nil)

type logger struct {
	l *log.Logger
}

func (l *logger) Infof(format string, v ...interface{}) {
	l.output("INFO", format, v...)
}

func (l *logger) Errorf(format string, v ...interface{}) {
	l.output("EROR", format, v...)
}

func (l *logger) Warnf(format string, v ...interface{}) {
	l.output("WARN", format, v...)
}

func (l *logger) Debugf(format string, v ...interface{}) {
	l.output("DBUG", format, v...)
}

func (l *logger) output(level, format string, v ...interface{}) {
	caller := "dler"
	// 获取日志的调用栈信息
	_, file, no, ok := runtime.Caller(2)
	if ok {
		filename := filepath.Base(file)
		caller = fmt.Sprintf("%s:%d", filename, no)
	}
	format = fmt.Sprintf("%s [%s] %s", level, caller, format)
	if len(v) == 0 {
		l.l.Print(format)
		return
	}
	l.l.Printf(format, v...)
}

// Package godler  provides ...
package godler

import (
	"sync"

	"github.com/cheggaaa/pb/v3"
)

type TaskFunc func(*Task) error

type ITasker interface {
	BuildTasker()
	BuildTasks()
	AddTask(*Task)
	asyncRunTask(TaskFunc, *Task)
	Run(TaskFunc)
	AfterRun()
	BeforeRun()
}

type Task struct {
	RetryTime int   `json:"retry_count"`
	Err       error `json:"err"`
	Info      interface{}
}

type TaskerConfig struct {
	ProcessNum     int
	RetryMaxTime   int
	UseProgressBar bool
}

func NewDefaultTaskerConfig() *TaskerConfig {
	return &TaskerConfig{
		ProcessNum:   20,
		RetryMaxTime: 99999999,
		// RetryMaxTime:   2,
		UseProgressBar: true,
	}
}

type Tasker struct {
	TaskId      string
	Config      *TaskerConfig
	Tasks       []*Task
	processChan chan bool
	resultChan  chan *Task
	WaitGroup   sync.WaitGroup
}

func (t *Tasker) BuildTasks() {
}

func (t *Tasker) BuildTasker() {
	t.processChan = make(chan bool, t.Config.ProcessNum)
	t.resultChan = make(chan *Task)
	t.Tasks = make([]*Task, 0)
}

func (t *Tasker) AddTask(task *Task) {
	t.Tasks = append(t.Tasks, task)
}

func (t *Tasker) asyncRunTask(runTaskFunc TaskFunc, task *Task) {
	t.WaitGroup.Add(1)
	go func(task *Task) {
		defer t.WaitGroup.Done()
		t.processChan <- true
		err := runTaskFunc(task)
		task.Err = err
		<-t.processChan
		t.resultChan <- task
	}(task)
}

func (t *Tasker) Run(runTaskFunc TaskFunc) {

	for _, task := range t.Tasks {
		t.asyncRunTask(runTaskFunc, task)
	}

	go func() {
		t.WaitGroup.Wait()
		close(t.resultChan)
		close(t.processChan)
	}()

	RetryTime := 0
	var bar *pb.ProgressBar
	if t.Config.UseProgressBar {
		bar = pb.Full.Start(len(t.Tasks))
	}
	// 获取结果
	for res := range t.resultChan {
		// 判断是否需要重试
		if res.Err != nil && res.RetryTime < t.Config.RetryMaxTime {
			res.RetryTime++
			RetryTime++
			t.asyncRunTask(runTaskFunc, res)
		} else {
			if t.Config.UseProgressBar {
				bar.Increment()
			}
		}
	}
	if t.Config.UseProgressBar {
		bar.Finish()
	}
}
func (t *Tasker) AfterRun()  {}
func (t *Tasker) BeforeRun() {}

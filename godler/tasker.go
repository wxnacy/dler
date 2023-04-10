// Package godler  provides ...
package godler

import (
	"fmt"
	"sync"

	"github.com/cheggaaa/pb/v3"
)

type TaskFunc func(*Task) error

type ITasker interface {
	Build()
	BuildTasks()
	AddTask(*Task)
	GetTasks() []*Task
	Run(TaskFunc)
	SyncRun(TaskFunc)
	AfterRun()
	BeforeRun()
}

type Task struct {
	RetryTime int         `json:"retry_count"`
	Err       error       `json:"err"`
	Info      interface{} `json:"info"`
}

type TaskerConfig struct {
	ProcessNum     int
	RetryMaxTime   int
	UseProgressBar bool
}

func NewTaskerConfig() *TaskerConfig {
	return &TaskerConfig{
		ProcessNum:   20,
		RetryMaxTime: 99999999,
		// RetryMaxTime:   2,
		UseProgressBar: true,
	}
}

func NewTasker(config *TaskerConfig) *Tasker {
	return &Tasker{
		Config:      config,
		processChan: make(chan bool, config.ProcessNum),
		resultChan:  make(chan *Task),
		Tasks:       make([]*Task, 0),
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

func (t *Tasker) BuildTasks() {}

func (t *Tasker) Build() {}

func (t *Tasker) AfterRun() {}

func (t *Tasker) BeforeRun() {}

func (t *Tasker) AddTask(task *Task) {
	t.Tasks = append(t.Tasks, task)
}

func (t Tasker) GetTasks() []*Task {
	return t.Tasks
}

func (t *Tasker) asyncRunTask(runTaskFunc TaskFunc, task *Task) {
	t.WaitGroup.Add(1)
	go func(task *Task) {
		defer t.WaitGroup.Done()
		t.processChan <- true
		err := runTaskFunc(task)
		// fmt.Println(err)
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
			// fmt.Println(res.Err)
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

func (t *Tasker) SyncRun(runTaskFunc TaskFunc) {

	var bar *pb.ProgressBar
	if t.Config.UseProgressBar {
		bar = pb.Full.Start(len(t.Tasks))
	}
	for _, task := range t.Tasks {
		err := runTaskFunc(task)
		fmt.Println(err)
		if t.Config.UseProgressBar {
			bar.Increment()
		}
	}

	if t.Config.UseProgressBar {
		bar.Finish()
	}
}

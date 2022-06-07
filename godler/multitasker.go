// Package godler  provides ...
package godler

import (
	"sync"

	"github.com/cheggaaa/pb/v3"
)

type TaskerInterface interface {
	Build()
	BuildTasks()
	AddTask(task *Task)
	runTask(*Task) error
	asyncRunTask(func(*Task) error, *Task)
	Run()
}

type Task struct {
	RetryTime int   `json:"retry_count"`
	Err       error `json:"err"`
	Extra     interface{}
}

type TaskerConfig struct {
	ProcessNum     int
	RetryMaxTime   int
	UseProgressBar bool
}

func NewDefaultTaskerConfig() *TaskerConfig {
	return &TaskerConfig{
		ProcessNum:     20,
		RetryMaxTime:   99999999,
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

func (t *Tasker) Build() {
	t.processChan = make(chan bool, t.Config.ProcessNum)
	t.resultChan = make(chan *Task)
	t.Tasks = make([]*Task, 0)
}

func (t *Tasker) AddTask(task *Task) {
	t.Tasks = append(t.Tasks, task)
}

func (t *Tasker) runTask(task *Task) error {

	return nil
}

func (t *Tasker) asyncRunTask(runTaskFunc func(*Task) error, task *Task) {
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

func (t *Tasker) Run(runTaskFunc func(*Task) error) {

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

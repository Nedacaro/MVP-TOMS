package main

import "sync"

var (
	Buf   []int
	mutex sync.Mutex
)

func Write(num int) {
	mutex.Lock()
	Buf = append(Buf, num)
	mutex.Unlock()
}

func Consume() int {
	mutex.Lock()
	defer mutex.Unlock()
	if len(Buf) == 0 {
		return 0
	}
	first := Buf[0]

	Buf = Buf[1:]

	return first
}

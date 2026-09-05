package main

import "sync"

type Counter struct {
	value int
	mu    sync.RWMutex
}

type Count interface {
	Increment()
	GetValue() int
}

func (c *Counter) Increment() {
	c.mu.RLock()
	c.value++
	c.mu.RUnlock()
}

func (c *Counter) GetValue() int {
	c.mu.RLock()
	defer c.mu.RUnlock()

	return c.value
}

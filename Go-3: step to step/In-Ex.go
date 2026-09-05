package main

import (
	"context"
	"sync"
)

func ParallelMapCtx(ctx context.Context, inputs []int, fn func(int) int, workers int) ([]int, error) {
	var wg sync.WaitGroup

	if len(inputs) == 0 {
		return inputs, nil
	}
	results := make([]int, len(inputs))

	sem := make(chan struct{}, workers)

	for i, v := range inputs {
		select {
		case sem <- struct{}{}:

		case <-ctx.Done():
			return nil, ctx.Err()
		}

		wg.Add(1)

		go func(index, value int) {
			defer wg.Done()
			defer func() {
				<-sem
			}()

			if ctx.Err() != nil {
				return
			}
			results[index] = fn(value)

		}(i, v)
	}
	wg.Wait()

	return results, nil

}

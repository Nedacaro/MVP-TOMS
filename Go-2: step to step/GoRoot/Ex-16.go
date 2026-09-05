package main

import (
	"context"
	"os"
)

func readJSON(ctx context.Context, path string, result chan<- []byte) {

	defer close(result)

	data, err := os.ReadFile(path)
	if err != nil {
		return
	}

	select {
	case <-ctx.Done():
		return
	case result <- data:

	}
}

package main

import (
	"bytes"
	"context"
	"io"
)

func Contains(ctx context.Context, r io.Reader, seq []byte) (bool, error) {
	buf := make([]byte, 4096)

	for {

		if ctx.Err() != nil {
			return false, ctx.Err()
		}

		n, err := r.Read(buf)

		if n > 0 && bytes.Contains(buf[:n], seq) {
			return true, nil
		}

		if err == io.EOF {
			return false, nil
		}

		if err != nil {
			return false, err
		}
	}
	return false, nil
}

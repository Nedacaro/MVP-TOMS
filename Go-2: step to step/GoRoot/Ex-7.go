package main

import (
	"context"
	"io"
	"net/http"
	"time"
)

type APiResponse struct {
	Data       string
	StatusCode int
}

func fetchAPI(ctx context.Context, url string, timeout time.Duration) (*APiResponse, error) {

	ctx, cancel := context.WithTimeout(ctx, timeout)
	defer cancel()

	client := &http.Client{}

	req, err := http.NewRequest("GET", url, nil)

	if err != nil {
		return nil, err
	}

	if ctx.Err() != nil {
		return nil, ctx.Err()
	}

	resp, err := client.Do(req.WithContext(ctx))

	if err != nil {

		if ctx.Err() != nil {
			return nil, ctx.Err()
		}

		return nil, err
	}

	defer resp.Body.Close()

	if ctx.Err() != nil {
		return nil, ctx.Err()
	}

	bodyBytes, err := io.ReadAll(resp.Body)

	if err != nil {
		if ctx.Err() != nil {
			return nil, ctx.Err()
		}
		return nil, err
	}

	return &APiResponse{
		Data:       string(bodyBytes),
		StatusCode: resp.StatusCode,
	}, nil
}

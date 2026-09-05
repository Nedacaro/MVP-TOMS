package main

import (
	"context"
	"io"
	"net/http"
	"sync"
	"time"
)

type APIResponse struct {
	URL        string
	Data       string
	StatusCode int
	Err        error
}

func FetchAPI(ctx context.Context, urls []string, timeout time.Duration) []*APIResponse {
	var wg sync.WaitGroup

	ch := make(chan *APIResponse, len(urls))

	for _, url := range urls {
		wg.Add(1)

		go func(u string) {
			defer wg.Done()

			ctx, cancel := context.WithTimeout(ctx, timeout)
			defer cancel()

			client := &http.Client{}

			req, err := http.NewRequest("GET", u, nil)

			if err != nil {
				ch <- &APIResponse{
					URL: u,
					Err: err,
				}
				return
			}

			if ctx.Err() != nil {
				ch <- &APIResponse{
					URL: u,
					Err: context.DeadlineExceeded,
				}
				return
			}

			resp, err := client.Do(req.WithContext(ctx))

			if err != nil {
				if ctx.Err() != nil {
					ch <- &APIResponse{
						URL: u,
						Err: ctx.Err(),
					}
					return
				}
				ch <- &APIResponse{
					URL: u,
					Err: err,
				}
				return
			}

			defer resp.Body.Close()

			if ctx.Err() != nil {
				ch <- &APIResponse{
					URL: u,
					Err: ctx.Err(),
				}
				return
			}

			bodyBytes, err := io.ReadAll(resp.Body)

			if err != nil {
				if ctx.Err() != nil {
					ch <- &APIResponse{
						URL: u,
						Err: ctx.Err(),
					}
					return
				}
				ch <- &APIResponse{
					URL: u,
					Err: err,
				}
				return
			}

			ch <- &APIResponse{
				URL:        u,
				Data:       string(bodyBytes),
				StatusCode: resp.StatusCode,
				Err:        nil,
			}

		}(url)
	}
	wg.Wait()
	close(ch)

	var result []*APIResponse
	for res := range ch {
		result = append(result, res)
	}

	return result

}

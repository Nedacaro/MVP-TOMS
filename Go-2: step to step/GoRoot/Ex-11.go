package main

import (
	"fmt"
	"io"
	"net/http"
	"strconv"
	"sync"
)

type Student struct {
	Name  string
	Point int
	Err   error
}

func Average(names []string) (int, error) {
	client := &http.Client{}

	var wg sync.WaitGroup

	ch := make(chan *Student, len(names))

	for _, nm := range names {
		wg.Add(1)

		go func(name string) {
			defer wg.Done()

			url := fmt.Sprintf("http://localhost:8082/mark?name=%s", name)
			resp, err := client.Get(url)

			if err != nil {
				ch <- &Student{
					Err: err,
				}
				return
			}
			defer resp.Body.Close()

			if resp.StatusCode != http.StatusOK {
				ch <- &Student{
					Err: fmt.Errorf("Error"),
				}
				return
			}

			body, err := io.ReadAll(resp.Body)

			if err != nil {
				ch <- &Student{
					Err: err,
				}
				return
			}

			grade, err := strconv.Atoi(string(body))

			if err != nil {
				ch <- &Student{
					Err: err,
				}
				return
			}

			ch <- &Student{
				Point: grade,
			}

		}(nm)
	}
	wg.Wait()
	close(ch)

	sum := 0

	for st := range ch {
		if st.Err != nil {
			return 0, st.Err
		}
		sum += st.Point
	}

	return sum / len(names), nil
}

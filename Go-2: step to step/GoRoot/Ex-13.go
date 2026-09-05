package main

import (
	"fmt"
	"io"
	"net/http"
	"strconv"
	"sync"
)

type Compare_List struct {
	Name  string
	Grade int
	Err   error
}

func CompareList(names []string) (map[string]string, error) {
	user := &http.Client{}

	var wg sync.WaitGroup

	chanel := make(chan *Compare_List, len(names))

	for _, ms := range names {
		wg.Add(1)

		go func(name string) {
			defer wg.Done()

			url := fmt.Sprintf("http://localhost:8082/mark?name=%s", name)
			resp, err := user.Get(url)

			if err != nil {
				chanel <- &Compare_List{
					Err: err,
				}
				return
			}

			if resp.StatusCode != http.StatusOK {
				chanel <- &Compare_List{
					Err: fmt.Errorf("ERRor"),
				}
				return
			}
			body, err := io.ReadAll(resp.Body)

			if err != nil {
				chanel <- &Compare_List{
					Err: err,
				}
				return
			}

			grade, err := strconv.Atoi(string(body))

			if err != nil {
				chanel <- &Compare_List{
					Err: err,
				}
				return
			}

			chanel <- &Compare_List{
				Name:  name,
				Grade: grade,
			}
		}(ms)
	}
	wg.Wait()
	close(chanel)

	sum := 0
	var AllStudent []*Compare_List
	for mg := range chanel {
		if mg.Err != nil {
			return nil, mg.Err
		}
		sum += mg.Grade
		AllStudent = append(AllStudent, mg)
	}
	middle_grade := sum / len(names)

	resultMap := make(map[string]string)

	for _, value := range AllStudent {
		if value.Grade > middle_grade {
			resultMap[value.Name] = ">"
		}
		if value.Grade < middle_grade {
			resultMap[value.Name] = "<"
		}
		if value.Grade == middle_grade {
			resultMap[value.Name] = "="
		}
	}
	return resultMap, nil
}

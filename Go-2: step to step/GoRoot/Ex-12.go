package main

import (
	"fmt"
	"io"
	"net/http"
	"sort"
	"strconv"
	"strings"
	"sync"
)

type Study struct {
	Name  string
	Grade int
	Err   error
}

func BestStudents(names []string) (string, error) {
	client := &http.Client{}

	var wg sync.WaitGroup

	ch := make(chan *Study, len(names))

	for _, nm := range names {
		wg.Add(1)

		go func(name string) {
			defer wg.Done()

			url := fmt.Sprintf("http://localhost:8082/mark?name=%s", name)
			resp, err := client.Get(url)

			if err != nil {
				ch <- &Study{
					Err: err,
				}
				return
			}
			defer resp.Body.Close()

			if resp.StatusCode != http.StatusOK {
				ch <- &Study{
					Err: fmt.Errorf("Error"),
				}
				return
			}

			body, err := io.ReadAll(resp.Body)

			if err != nil {
				ch <- &Study{
					Err: err,
				}
				return
			}

			grade, err := strconv.Atoi(string(body))

			if err != nil {
				ch <- &Study{
					Err: err,
				}
				return
			}

			ch <- &Study{
				Name:  name,
				Grade: grade,
			}

		}(nm)
	}
	wg.Wait()
	close(ch)

	sum := 0
	var AllStudent []*Study
	for mg := range ch {
		if mg.Err != nil {
			return "", mg.Err
		}
		sum += mg.Grade
		AllStudent = append(AllStudent, mg)
	}

	middle_grade := sum / len(names)

	var best_students []string

	for _, bm_g := range AllStudent {
		if bm_g.Grade > middle_grade {
			best_students = append(best_students, bm_g.Name)
		}
	}
	sort.Strings(best_students)
	res_str := strings.Join(best_students, ", ")

	return res_str, nil
}

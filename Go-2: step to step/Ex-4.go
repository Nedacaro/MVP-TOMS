package main

import (
	"errors"
	"fmt"
	"sort"
)

var (
	Error_Name       = errors.New("Поле с именем не может быть пустым!")
	Error_Salary     = errors.New("Зп не может быть отрицательным числом")
	Error_Experience = errors.New("Cтаж не может быть отрицательным числом")
)

type CompanyInterface interface {
	AddWorkerInfo(name, position string, salary, experience uint) error
	SortWorkers() ([]string, error)
}

type Worker struct {
	Name       string
	Position   string
	Salary     uint
	Experience uint
}

type Company struct {
	Workers []Worker
}

func (c *Company) AddWorkerInfo(name, position string, salary, experience uint) error {
	if name == "" {
		return Error_Name
	}

	if salary < 0 {
		return Error_Salary
	}

	if experience < 0 {
		return Error_Experience
	}

	add := Worker{
		Name:       name,
		Position:   position,
		Salary:     salary,
		Experience: experience,
	}
	c.Workers = append(c.Workers, add)

	return nil
}
func getPosition(pos string) int {
	switch pos {
	case "директор":
		return 5
	case "зам. директора":
		return 4
	case "начальник цеха":
		return 3
	case "мастер":
		return 2
	case "рабочий":
		return 1
	default:
		return 0
	}
}
func (c *Company) SortWorkers() ([]string, error) {
	sort.Slice(c.Workers, func(i int, j int) bool {
		expI := c.Workers[i].Salary * c.Workers[i].Experience
		expJ := c.Workers[j].Salary * c.Workers[j].Experience

		if expI != expJ {
			return expI > expJ
		}

		return getPosition(c.Workers[i].Position) > getPosition(c.Workers[j].Position)
	})

	result := make([]string, 0, len(c.Workers))

	for _, w := range c.Workers {
		income := w.Salary * w.Experience

		str := fmt.Sprintf("%s - %d - %s", w.Name, income, w.Position)

		result = append(result, str)
	}
	return result, nil
}

package main

import (
	"fmt"
	"io"
	"net/http"
	"strconv"
)

func Compare(name1, name2 string) (string, error) {
	client := &http.Client{}

	url_1 := fmt.Sprintf("http://localhost:8082/mark?name=%s", name1)

	resp_1, err_1 := client.Get(url_1)

	if err_1 != nil {
		return "", err_1
	}
	defer resp_1.Body.Close()

	if resp_1.StatusCode != http.StatusOK {
		return "", fmt.Errorf("Error")
	}

	body_1, err := io.ReadAll(resp_1.Body)
	if err != nil {
		return "", err
	}
	grade_1, err := strconv.Atoi(string(body_1))
	if err != nil {
		return "", err
	}

	url_2 := fmt.Sprintf("http://localhost:8082/mark?name=%s", name2)

	resp_2, err_2 := client.Get(url_2)

	if err_2 != nil {
		return "", err_2
	}

	defer resp_2.Body.Close()

	if resp_2.StatusCode != http.StatusOK {
		return "", fmt.Errorf("Error")
	}

	body_2, err := io.ReadAll(resp_2.Body)
	if err != nil {
		return "", err
	}

	grade_2, err := strconv.Atoi(string(body_2))

	if err != nil {
		return "", err
	}

	if grade_1 > grade_2 {
		return ">", nil
	}
	if grade_1 < grade_2 {
		return "<", nil
	}
	if grade_1 == grade_2 {
		return "=", nil
	}

	return "", nil
}

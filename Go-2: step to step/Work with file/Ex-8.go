package main

import (
	"bufio"
	"errors"
	"os"
	"time"
)

func ExtractLog(inputFilename string, start, end time.Time) ([]string, error) {
	f, _ := os.Open(inputFilename)
	defer f.Close()

	var result []string

	scanner := bufio.NewScanner(f)

	for scanner.Scan() {
		line := scanner.Text()
		dateStr := line[:10]

		logTime, err := time.Parse("02.01.2006", dateStr)

		if err != nil {
			continue
		}

		if !logTime.Before(start) && !logTime.After(end) {
			result = append(result, line)

		}
	}
	if len(result) == 0 {
		return nil, errors.New("logs not found")
	}

	return result, nil
}

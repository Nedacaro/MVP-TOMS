package main

import (
	"bufio"
	"os"
	"strings"
)

func LineByNum(inputFilename string, lineNum int) string {
	f, err := os.Open(inputFilename)
	if err != nil {
		return ""
	}
	defer f.Close()

	scanner := bufio.NewScanner(f)

	currentLine := 0

	for scanner.Scan() {
		if currentLine == lineNum {

			return strings.TrimRight(scanner.Text(), "\r")
		}
		currentLine++
	}

	return ""
}

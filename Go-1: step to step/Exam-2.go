package main

import (
	"bufio"
	"fmt"
	"os"
	"strings"
)

func main() {
	reader := bufio.NewReader(os.Stdin)
	box := [5]string{}
	occupied := 0

	for {
		line, _ := reader.ReadString('\n')
		line = strings.TrimSpace(line)

		if line == "" {
			continue
		}

		if line == "очередь" {
			for i := 0; i < 5; i++ {
				if box[i] == "" {
					fmt.Printf("%d. -\n", i+1)
				} else {
					fmt.Printf("%d. %s\n", i+1, box[i])
				}
			}
			continue
		}

		if line == "количество" {
			free := 5 - occupied
			fmt.Printf("Осталось свободных мест: %d\n", free)
			fmt.Printf("Всего человек в очереди: %d\n", occupied)
			continue
		}

		if line == "конец" {
			for i := 0; i < 5; i++ {
				if box[i] == "" {
					fmt.Printf("%d. -\n", i+1)
				} else {
					fmt.Printf("%d. %s\n", i+1, box[i])
				}
			}
			return
		}

		parts := strings.Fields(line)
		if len(parts) != 2 {
			fmt.Println("некорректный ввод")
			continue
		}

		name := parts[0]
		var place int
		fmt.Sscan(parts[1], &place)

		if place < 1 || place > 5 {
			fmt.Printf("Запись на место номер %d невозможна: некорректный ввод\n", place)
			continue
		}

		if occupied >= 5 {
			fmt.Printf("Запись на место номер %d невозможна: очередь переполнена\n", place)
			continue
		}

		if box[place-1] != "" {
			fmt.Printf("Запись на место номер %d невозможна: место уже занято\n", place)
			continue
		}

		box[place-1] = name
		occupied++
	}
}

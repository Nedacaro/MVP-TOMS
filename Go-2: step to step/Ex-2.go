package main

import (
	"strings"
	"time"
)

type Ticket struct {
	Ticket string
	User   string
	Status string
	Date   time.Time
}

func GetTasks(text string, user *string, status *string) []Ticket {
	lines := strings.Split(text, "\n")

	var result []Ticket
	for _, s := range lines {
		s = strings.TrimSpace(s)
		if !strings.HasPrefix(s, "TICKET-") {
			continue
		}

		parts := strings.Split(s, "_")

		if len(parts) != 4 {
			continue
		}
		statusCheck := parts[2]

		if statusCheck != "Готово" && statusCheck != "В работе" && statusCheck != "Не будет сделано" {
			continue
		}

		parsedDate, err := time.Parse("2006-01-02", parts[3])

		if err != nil {
			continue
		}

		ticket := Ticket{
			Ticket: parts[0],
			User:   parts[1],
			Status: parts[2],
			Date:   parsedDate,
		}

		matches := true

		if user != nil && *user != ticket.User {
			matches = false
		}

		if status != nil && *status != ticket.Status {
			matches = false
		}

		if matches {
			result = append(result, ticket)
		}
	}
	return result
}

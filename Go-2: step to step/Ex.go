package main

import (
	"context"
	"encoding/json"
	"errors"
	"io"
	"strings"
	"time"
)

type Ticket struct {
	Ticket string
	User   string
	Status string
	Date   time.Time
}

func GetTasks(ctx context.Context, r io.Reader, w io.Writer, user *string, status *string, timeout time.Duration) error {
	ctx, cancel := context.WithTimeout(ctx, timeout)
	defer cancel()

	data, err := io.ReadAll(r)

	if err != nil {
		return errors.New("Ошибка в чтении файла")
	}

	lines := strings.Split(string(data), "\n")

	var result []Ticket
	var allTickets []Ticket

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

		allTickets = append(allTickets, ticket)
	}

	for _, ticket := range allTickets {
		select {
		case <-ctx.Done():
			return ctx.Err()
		default:
		}

		if user != nil && ticket.User != *user {
			continue
		}
		if status != nil && ticket.Status != *status {
			continue
		}
		result = append(result, ticket)
	}

	err = json.NewEncoder(w).Encode(result)
	if err != nil {
		return errors.New("ошибка записи JSON")
	}
	return nil
}

package main

import "fmt"

type Order struct {
	OrderNumber int
	CustomeName string
	OrderAmount float64
}

type OrderLogger struct{}

func NewOrderLogger() *OrderLogger {
	return &OrderLogger{}
}

func (logger *OrderLogger) AddOrder(order Order) {
	fmt.Printf("Добавлен заказ #%d, Имя клиента: %s, Сумма заказа: $%.2f\n", order.OrderNumber, order.CustomeName, order.OrderAmount)
}

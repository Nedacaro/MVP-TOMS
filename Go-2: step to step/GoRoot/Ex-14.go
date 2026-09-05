package main

import (
	"errors"
	"time"
)

func Fib(n int) int {
	if n < 2 {
		return n
	}

	return Fib(n-1) + Fib(n-2)
}

func TimeoutFibonacci(n int, timeout time.Duration) (int, error) {
	ch := make(chan int, 1)

	go func() {
		res := Fib(n)
		ch <- res
	}()

	select {

	case result := <-ch:
		return result, nil
	case <-time.After(timeout):
		return 0, errors.New("Err")
	}
}

//Сгенерируйте N-е число Фибоначчи.
// Установите ограничение на время вычисления.
//  Если число будет вычислено в течение указанного времени, верните число Фибоначчи, в противном случае выдайте ошибку.

package main

import "time"

func IsPrime(num int) bool {
	if num < 2 {
		return false
	}

	for i := 2; i*i <= num; i++ {
		if num%i == 0 {
			return false
		}
	}
	return true
}

func GeneratePrimeNumbers(stop chan struct{}, prime_nums chan int, N int) {
	defer close(prime_nums)

	timer := time.NewTimer(100 * time.Millisecond)

	defer timer.Stop()

	for i := 2; i <= N; i++ {
		if IsPrime(i) {
			select {
			case <-stop:
				return
			case <-timer.C:
				return
			case prime_nums <- i:
			}
		}
	}
}

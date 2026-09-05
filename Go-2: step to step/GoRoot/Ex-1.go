package main

import (
	"fmt"
	"time"
)

/*func Process(nums []int) chan int {

	transfer := make(chan int, 10)

	for _, v := range nums {
		transfer <- v
	}

	return transfer
}*/

func LoveYulia() {
	for {
		fmt.Println("Я люблю Юлю")

		time.Sleep(2 * time.Second)
	}
}

func main() {
	LoveYulia()
}

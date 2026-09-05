package main

import "testing"

func TestSortIntegers(t *testing.T) {
	my_int := []int{5, 2, 3, 1, 7, 9, 4, 8, 6}
	res_int := []int{1, 2, 3, 4, 5, 6, 7, 8, 9}

	t.Parallel()

	//SortIntegers(my_int)

	for i := range res_int {
		if my_int[i] != res_int[i] {
			t.Errorf("индекс %d: ожидалось %d, получено %d", i, res_int[i], my_int[i])
		}
	}
}

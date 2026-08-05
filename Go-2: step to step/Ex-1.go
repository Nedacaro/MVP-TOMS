package main

import "slices"

func SortAndMerge(left, right []int) []int {
	result := make([]int, 0, len(left)+len(right))

	i := 0
	j := 0

	slices.Sort(left)
	slices.Sort(right)

	for i < len(left) && j < len(right) {
		if left[i] < right[j] {
			result = append(result, left[i])
			i++
		} else {
			result = append(result, right[j])
			j++
		}
	}

	for i < len(left) {
		result = append(result, left[i])
		i++
	}

	for j < len(right) {
		result = append(result, right[j])
		j++
	}

	return result
}

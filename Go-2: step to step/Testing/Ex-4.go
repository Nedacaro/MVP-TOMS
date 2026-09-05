package main

func Filter[T any](arr []T, predicant func(T) bool) []T {
	result := []T{}

	for _, element := range arr {
		if predicant(element) {
			result = append(result, element)
		}
	}
	return result
}

package main

import "reflect"

func Sum(sum interface{}) interface{} {
	v := reflect.ValueOf(sum)

	if v.Len() == 0 {
		return 0
	}

	firstElement := v.Index(0)
	elementType := firstElement.Kind()

	if elementType == reflect.Int {
		sumInt := 0
		for i := 0; i < v.Len(); i++ {
			element := v.Index(i)
			sumInt += int(element.Int())
		}
		return sumInt
	}

	if elementType == reflect.Float64 {
		sumFloat := 0.0
		for i := 0; i < v.Len(); i++ {
			element := v.Index(i)
			sumFloat += element.Float()
		}
		return sumFloat
	}

	return 0
}

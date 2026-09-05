package main

import (
	"testing"
)

func TestReverse(t *testing.T) {
	//rune_test := "JULIA"
	rune_output := "AILUJ"

	got := "a"

	if got != rune_output {
		t.Errorf("error")
	}
}

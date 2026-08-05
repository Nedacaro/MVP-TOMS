package main

import (
	"fmt"
	"sort"
	"strings"
)

func AnalyzeText(text string) {
	words := strings.ReplaceAll(text, ",", " ")
	words = strings.ReplaceAll(words, ".", " ")
	words = strings.ReplaceAll(words, "!", " ")
	words = strings.ReplaceAll(words, "?", " ")

	words_clean := strings.Fields(words)

	fmt.Printf("Количество слов: %d\n", len(words_clean))

	words_map := make(map[string]int)

	for i := 0; i < len(words_clean); i++ {
		s := words_clean[i]
		s_low := strings.ToLower(s)
		words_map[s_low]++
	}

	maxCount := 0
	var maxWord string
	for word, count := range words_map {
		if count > maxCount {
			maxCount = count
			maxWord = word
		}
	}

	fmt.Printf("Количество уникальных слов: %d\n", len(words_map))
	fmt.Printf("Самое часто встречающееся слово: \"%s\" (встречается %d раз)\n", maxWord, maxCount)

	top := getTopWords(words_map, 5)

	fmt.Println("Топ-5 самых часто встречающихся слов:")

	for _, word := range top {
		fmt.Printf("\"%s\": %d раз\n", word, words_map[word])
	}
}

func getTopWords(wordMap map[string]int, n int) []string {
	str := make([]string, 0, len(wordMap))

	for word := range wordMap {
		str = append(str, word)
	}

	sort.Slice(str, func(i, j int) bool {
		word_a := str[i]
		word_b := str[j]

		return wordMap[word_a] > wordMap[word_b]
	})

	return str[:n]
}

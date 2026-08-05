package main

import "sort"

type Player struct {
	Name   string
	Goals  int
	Misses int
	Assist int
	Rating float64
}

func (p *Player) calculateRating() {
	if p.Misses != 0 {
		p.Rating = (float64(p.Goals) + float64(p.Assist)/2.0) / float64(p.Misses)
	} else {
		p.Rating = (float64(p.Goals) + float64(p.Assist)/2.0)
	}
}

func NewPlayer(name string, goals, misses, assist int) Player {

	player := Player{
		Name:   name,
		Goals:  goals,
		Misses: misses,
		Assist: assist,
	}

	player.calculateRating()

	return player
}

func goalsSort(players []Player) []Player {
	sort.Slice(players, func(i int, j int) bool {
		players_1 := players[i].Goals
		players_2 := players[j].Goals

		if players_1 != players_2 {
			return players_1 > players_2
		} else {
			return players[i].Name < players[j].Name
		}
	})
	return players
}

func ratingSort(players []Player) []Player {
	sort.Slice(players, func(i int, j int) bool {
		players_1 := players[i].Rating
		players_2 := players[j].Rating

		if players_1 != players_2 {
			return players_1 > players_2
		} else {
			return players[i].Name < players[j].Name
		}
	})
	return players
}

func gmSort(players []Player) []Player {
	var ratioI float64
	var ratioJ float64
	sort.Slice(players, func(i int, j int) bool {
		if players[i].Misses == 0 {
			ratioI = float64(players[i].Goals)
		} else {
			ratioI = float64(players[i].Goals) / float64(players[i].Misses)
		}

		if players[j].Misses == 0 {
			ratioJ = float64(players[j].Goals)
		} else {
			ratioJ = float64(players[j].Goals) / float64(players[j].Misses)
		}

		if ratioI != ratioJ {
			return ratioI > ratioJ
		} else {
			return players[i].Name < players[j].Name
		}
	})

	return players
}

package main

import (
	"errors"
)

var (
	Error_time = errors.New("исправь свой ответ, а лучше ложись поспать")
)

/*func currentDayOfTheWeek() string {
	//weekday := TimeNow().Weekday()

	var day string
	switch weekday {
	case time.Monday:
		day = "Понедельник"
	case time.Tuesday:
		day = "Вторник"
	case time.Wednesday:
		day = "Среда"
	case time.Thursday:
		day = "Четверг"
	case time.Friday:
		day = "Пятница"
	case time.Saturday:
		day = "Суббота"
	case time.Sunday:
		day = "Воскресенье"
	}
	return day
}
*/
/*func dayOrNight() string {
	hour := TimeNow().Hour()
	if hour >= 10 && hour < 22 {
		return "День"
	}

	return "Ночь"
}

func nextFriday() int {
	now := TimeNow()
	weekday := now.Weekday()
	todayNum := int(weekday)

	Friday_day := (5 - todayNum + 7) % 7
	return Friday_day
}*/

/*func CheckCurrentDayOfTheWeek(answer string) bool {
	weekday := currentDayOfTheWeek()

	if strings.ToLower(answer) == strings.ToLower(weekday) {
		return true
	}
	return false
}

func CheckNowDayOrNight(answer string) (bool, error) {
	timer := dayOrNight()
	if utf8.RuneCountInString(answer) != 4 {
		return false, Error_time
	}

	if strings.ToLower(timer) == strings.ToLower(answer) {
		return true, nil
	}

	return false, nil
}*/

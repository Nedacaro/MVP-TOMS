package main

import (
	"fmt"
	"time"
)

func m_ain() {
	var f_name, l_name, surname, t string
	var m_1, m_2, m_3 float64
	fmt.Scanln(&t)
	fmt.Scanln(&f_name)
	fmt.Scanln(&l_name)
	fmt.Scanln(&surname)
	fmt.Scanln(&m_1)
	fmt.Scanln(&m_2)
	fmt.Scanln(&m_3)

	data, _ := time.Parse("02.01.2006", t)
	newDate := data.AddDate(0, 0, 15)
	total := m_1 + m_2 + m_3
	rub := int(total)
	kop := int((total-float64(rub))*100 + 0.5)

	fmt.Printf("Уважаемый, %s %s %s, доводим до вашего сведения, что бухгалтерия сформировала документы по факту выполненной вами работы.\n", l_name, f_name, surname)
	fmt.Printf("Дата подписания договора: %02d.%02d.%04d. Просим вас подойти в офис в любое удобное для вас время в этот день.\n", newDate.Day(), newDate.Month(), newDate.Year())
	fmt.Printf("Общая сумма выплат составит %d руб. %d коп.\n", rub, kop)

	fmt.Println("")
	fmt.Println("С уважением,")
	fmt.Println("Гл. бух. Иванов А.Е.")
}

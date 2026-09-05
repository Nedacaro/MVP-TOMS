package main

import (
	"io"
	"net/http"
	"time"
)

func StartServer(maxTimeout time.Duration) {

	// 1. Описываем ДЕЙСТВИЕ, которое защищаем секундомером
	myAction := http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		// А) Делаем исходящий звонок на склад:
		resp, err := http.Get("http://localhost:8081/provideData")
		if err != nil {
			return
		}
		defer resp.Body.Close()

		// Б) Читаем данные из ответа склада через io.ReadAll:
		body, _ := io.ReadAll(resp.Body)

		// В) Отдаем эти данные в руки Пользователю:
		w.Write(body)
	})

	// 2. Оборачиваем наше ДЕЙСТВИЕ в секундомер (Твой TimeoutHandler)
	handlerWithTimeout := http.TimeoutHandler(myAction, maxTimeout, "Service Unavailable")

	// 3. Вешаем этот защищенный хендлер на нужную дверь (путь)
	http.Handle("/readSource", handlerWithTimeout)

	// 4. Открываем клуб для гостей на порту 8080
	http.ListenAndServe(":8080", nil)
}

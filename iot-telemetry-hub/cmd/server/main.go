package main

import (
	"iot-telemetry-hub/internal/parser"
	"iot-telemetry-hub/internal/sensor"
	"iot-telemetry-hub/internal/storage"
	"log"
	"time"
)

func main() {
	db, err := storage.NewStorage("telemetry.db")

	if err != nil {
		log.Fatal(err)
	}

	err = db.InitDB()

	if err != nil {
		log.Fatal(err)
	}

	mySensor := sensor.NewSensor(10)

	for {
		data, err := parser.ParserNew(mySensor)
		if err != nil {
			log.Println("Предупреждение: битая строка телеметрии:", err)
			continue
		}

		if data.IsViolation {
			db.SaveDB(data)
			log.Printf("НАРУШЕНИЕ! Машина %s ехала со скоростью %d км/ч. Запись сохранена в SQLite!\n", data.NumberCar, data.Speed)
		} else {
			log.Printf("Поток чистый: машина %s ехала со скоростью %d км/ч.\n", data.NumberCar, data.Speed)
		}
		time.Sleep(1 * time.Second)
	}

}

package sensor

import (
	"fmt"
	"time"
)

type Telemetry struct {
	SensorID    int
	NumberCar   string
	Speed       int
	Timestamp   time.Time
	IsViolation bool
}

type Sensor struct {
	idIoT    int
	carCount int
}

func NewSensor(id int) *Sensor {
	return &Sensor{
		idIoT: id,
	}
}

func (s *Sensor) Read(p []byte) (n int, err error) {
	s.carCount++

	str := fmt.Sprintf("TICKET-%d_Sensor-%d_Speed-%d_Date-2026-08-04\n", s.carCount, s.idIoT, 85)

	n = copy(p, []byte(str))

	return n, nil
}

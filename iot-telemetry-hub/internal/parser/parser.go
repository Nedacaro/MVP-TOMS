package parser

import (
	"bufio"
	"errors"
	"io"
	"iot-telemetry-hub/internal/sensor"
	"strconv"
	"strings"
	"time"
)

var (
	Error_value_input = errors.New("Ошибка в передачи аргументов")
)

func ParserNew(r io.Reader) (sensor.Telemetry, error) {
	var t sensor.Telemetry
	reader := bufio.NewReader(r)

	line, err := reader.ReadString('\n')

	_ = line

	if err != nil {
		return t, err
	}
	parts := strings.Split(line, "_")

	if len(parts) != 4 {
		return t, Error_value_input
	}

	parts[0] = strings.TrimSpace(parts[0])
	if !strings.HasPrefix(parts[0], "TICKET-") {
		return t, Error_value_input
	}
	t.NumberCar = parts[0]

	if !strings.HasPrefix(parts[1], "Sensor-") {
		return t, Error_value_input
	}
	idStr_1 := strings.TrimPrefix(parts[1], "Sensor-")
	idSen, _ := strconv.Atoi(idStr_1)
	t.SensorID = idSen

	if !strings.HasPrefix(parts[2], "Speed-") {
		return t, Error_value_input
	}
	idStr_2 := strings.TrimPrefix(parts[2], "Speed-")
	idNum, _ := strconv.Atoi(idStr_2)
	t.Speed = idNum

	t.Timestamp = time.Now()

	if t.Speed > 60 {
		t.IsViolation = true
	}

	return t, nil
}

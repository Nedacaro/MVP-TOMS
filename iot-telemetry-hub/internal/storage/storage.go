package storage

import (
	"database/sql"
	"errors"
	"iot-telemetry-hub/internal/sensor"

	_ "github.com/glebarez/go-sqlite"
)

var (
	Error_ConnectDB = errors.New("Ошибка в подключении базы данных")
	Error_InitDB    = errors.New("Ошибка в создании базы данных")
	Error_BreakDB   = errors.New("Диск переполнен или файл заблокирован")
)

type Storage struct {
	db *sql.DB
}

func NewStorage(dbPath string) (*Storage, error) {
	db, err := sql.Open("sqlite", dbPath)

	if err != nil {
		return nil, Error_ConnectDB
	}

	return &Storage{db: db}, nil
}

func (s *Storage) InitDB() error {
	query := `
	CREATE TABLE IF NOT EXISTS telemetry (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		sensor_id INTEGER,
		car_number TEXT,
		speed INTEGER,
		timestamp TEXT,
		is_violation INTEGER
	);`

	_, err := s.db.Exec(query)

	if err != nil {
		return Error_InitDB
	}

	return nil
}

// Метод принимает готовую телеметрию 't' и возвращает ошибку, если запись сорвётся
func (s *Storage) SaveDB(t sensor.Telemetry) error {

	timeStr := t.Timestamp.Format("2006-01-02 15:04:05")

	query := `
	INSERT INTO telemetry (sensor_id, car_number, speed, timestamp, is_violation) 
	VALUES (?, ?, ?, ?, ?);`

	_, err := s.db.Exec(query, t.SensorID, t.NumberCar, t.Speed, timeStr, t.IsViolation)

	if err != nil {
		return Error_BreakDB
	}

	return nil
}

package main

import (
	"io"
	"os"
)

func CopyFilePart(inputFilename, outFilename string, startpos int) error {
	f, err := os.Open(inputFilename)

	if err != nil {
		return err
	}
	defer f.Close()

	f_1, err := os.Create(outFilename)

	if err != nil {
		return err
	}
	defer f_1.Close()

	f.Seek(int64(startpos), 0)

	_, error := io.Copy(f_1, f)

	if error != nil {
		return error
	}

	return nil
}

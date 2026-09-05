package main

import (
	"bufio"
	"bytes"
	"io"
)

/*func ReadString(r io.Reader) (string, error) {
	dataBytes, err := io.ReadAll(r)

	if err != nil {
		return "", err
	}

	return string(dataBytes), nil
}*/

/*type UpperWriter struct {
	UpperString string
}

func (uw *UpperWriter) Write(p []byte) (n int, err error) {
	uw.UpperString = strings.ToUpper(string(p))

	/*if len(p) != len(uw.UpperString) {
		return 0, err
	}*/

/*return len(p), nil


}*/

func Copy(r io.Reader, w io.Writer, n uint) error {
	LimitedReader := io.LimitReader(r, int64(n))
	_, err := io.Copy(w, LimitedReader)

	if err != nil {
		return err
	}

	return nil
}

const maxBytes = 30 * 1024 * 1024

func Contains(r io.Reader, seq []byte) (bool, error) {
	/*LimitedReader := io.LimitReader(r, maxBytes)

	Outputdata, err := io.ReadAll(LimitedReader)

	if err != nil && err != io.EOF {
		return false, err
	}

	return bytes.Contains(Outputdata, seq), nil*/

	delim := seq[len(seq)-1]

	reader := bufio.NewReader(r)

	for {
		part, err := reader.ReadSlice(delim)
		if bytes.Contains(part, seq) {
			return true, nil
		}

		if err == io.EOF {
			return false, nil
		}
		if err != nil {
			return false, err
		}
	}
}

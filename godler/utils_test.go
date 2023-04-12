package godler

import (
	"strings"
	"testing"
)

func TestReaderToString(t *testing.T) {
	str := "wxnacy"
	r := strings.NewReader(str)
	s, err := ReaderToString(r)
	if s != str {
		t.Errorf("%s ! %s", str, s)
	}
	if err != nil {
		t.Errorf("err is %v", err)
	}

}

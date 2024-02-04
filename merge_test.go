package main

import (
	"bytes"
	"embed"
	"testing"
)

func Test(t *testing.T) {
	got, err := merge(files, "test-main.json", "test-linux.json", "", "")
	if err != nil {
		t.Error(err)
	}
	if !bytes.Equal(got, merged) {
		t.Errorf("got:\n%s\n\nwant:\n%s", got, merged)
	}
}

//go:embed test-*.json
var files embed.FS

//go:embed test-merged.json
var merged []byte

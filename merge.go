// Copyright 2024 Philipp Stephani
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

package main

import (
	"encoding/json"
	"fmt"
	"io/fs"
	"slices"
	"strings"
)

func merge(linux, macOS, windows []byte) ([]byte, error) {
	var lock map[string]json.RawMessage
	if err := loadOrMerge(&lock, linux, "linux"); err != nil {
		return nil, fmt.Errorf("error processing GNU/Linux lockfile: %s", err)
	}
	if err := loadOrMerge(&lock, macOS, "macos", "osx"); err != nil {
		return nil, fmt.Errorf("error processing macOS lockfile: %s", err)
	}
	if err := loadOrMerge(&lock, windows, "windows"); err != nil {
		return nil, fmt.Errorf("error processing Windows lockfile: %s", err)
	}
}

func merge23() {
	if err := load(fs, main, &lock); err != nil {
		return nil, err
	}
	const extKey = "moduleExtensions"
	var exts map[string]map[string]json.RawMessage
	if err := json.Unmarshal(lock[extKey], &exts); err != nil {
		return nil, err
	}
	for _, a := range []struct {
		file string
		keys []string
	}{
		{linux, []string{"linux"}},
		{macOS, []string{"macos", "osx"}},
		{windows, []string{"windows"}},
	} {
		if a.file != "" {
			mergeKernel(&exts, fs, a.file, a.keys)
		}
	}
	const indent = "  "
	b, err := json.MarshalIndent(exts, indent, indent)
	if err != nil {
		return nil, err
	}
	lock[extKey] = json.RawMessage(b)
	return json.MarshalIndent(lock, "", indent)
}

func mergeKernel(dest *map[string]map[string]json.RawMessage, fs fs.FS, file string, kernels []string) error {
	var lock struct {
		Exts map[string]map[string]json.RawMessage `json:"moduleExtensions"`
	}
	if err := load(fs, file, &lock); err != nil {
		return err
	}
	for label, platforms := range lock.Exts {
		for platform, val := range platforms {
			if matches(platform, kernels) {
				if dest == nil {
					*dest = make(map[string]map[string]json.RawMessage)
				}
				exts := *dest
				m := exts[label]
				if m == nil {
					m = make(map[string]json.RawMessage)
				}
				m[platform] = val
				exts[label] = m
			}
		}
	}
	return nil
}

func matches(platform string, kernels []string) bool {
	pieces := strings.Split(platform, ",")
	for _, piece := range pieces {
		kernel, ok := strings.CutPrefix(piece, "os:")
		if ok && slices.Contains(kernels, kernel) {
			return true
		}
	}
	return false
}

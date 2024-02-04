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
	"flag"
	"fmt"
	"os"
)

func main() {
	var linux, macOS, windows string
	flag.StringVar(&linux, "linux", "", "")
	flag.StringVar(&macOS, "macos", "", "")
	flag.StringVar(&windows, "windows", "", "")
	flag.Parse()
	if flag.NArg() != 0 {
		flag.Usage()
		os.Exit(2)
	}
	if err := run(linux, macOS, windows); err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
}

func run(linuxFile, macOSFile, windowsFile string) error {
	linux, err := readMaybe(linuxFile)
	if err != nil {
		return err
	}
	macOS, err := readMaybe(macOSFile)
	if err != nil {
		return err
	}
	windows, err := readMaybe(windowsFile)
	if err != nil {
		return err
	}
	merged, err := merge(linux, macOS, windows)
	if err != nil {
		return err
	}
	_, err = os.Stdout.Write(merged)
	return err
}

func readMaybe(file string) ([]byte, error) {
	if file == "" {
		return nil, nil
	}
	return os.ReadFile(file)
}

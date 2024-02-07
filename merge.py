#!/usr/bin/env python3

# Copyright 2024 Philipp Stephani
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Tool to merge MODULE.bazel.lock files."""

import argparse
import contextlib
import json
import sys
from typing import Optional, TextIO


def merge(*, output: TextIO,
          linux: Optional[TextIO] = None,
          macos: Optional[TextIO] = None,
          windows: Optional[TextIO] = None) -> None:
    """Merge multiple MODULE.bazel.lock files into one.

    Args:
      output: where to write the merged file
      linux, macos, windows: input files for GNU/Linux, macOS, and Windows,
         respectively; all are optional, but at least one must be present
    """
    inputs = (
        (linux, {'os:linux'}),
        (macos, {'os:macos', 'os:osx'}),
        (windows, {'os:windows'}),
    )
    inputs = [(stream, keys) for (stream, keys) in inputs if stream]
    if not inputs:
        raise ValueError('no input streams given')
    (first, _), *rest = inputs
    lock = json.load(first)
    exts_key = 'moduleExtensions'
    for (stream, keys) in rest:
        for label, ext in json.load(stream)[exts_key].items():
            for platform, val in ext.items():
                if not set(platform.split(',')).isdisjoint(keys):
                    lock.setdefault(
                        exts_key, {}).setdefault(label, {})[platform] = val
    json.dump(lock, output, indent=2)
    output.write('\n')


def _main() -> None:
    parser = argparse.ArgumentParser(allow_abbrev=False)
    parser.add_argument('--linux', '-l',
                        type=argparse.FileType(mode='r', encoding='utf-8'))
    parser.add_argument('--macos', '-m',
                        type=argparse.FileType(mode='r', encoding='utf-8'))
    parser.add_argument('--windows', '-w',
                        type=argparse.FileType(mode='r', encoding='utf-8'))
    parser.add_argument('--output', '-o',
                        type=argparse.FileType(mode='w', encoding='utf-8'))
    args = parser.parse_args()
    with contextlib.ExitStack() as stack:
        for file in (args.linux, args.macos, args.windows, args.output):
            if file:
                stack.enter_context(file)
        merge(output=args.output or sys.stdout,
              linux=args.linux,
              macos=args.macos,
              windows=args.windows)


if __name__ == '__main__':
    _main()

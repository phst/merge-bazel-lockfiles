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
import json
import pathlib
from typing import Optional


def merge(*,
          linux: Optional[str] = None,
          macos: Optional[str] = None,
          windows: Optional[str] = None) -> str:
    """Merge multiple MODULE.bazel.lock files into one.

    Args:
      linux, macos, windows: input files for GNU/Linux, macOS, and Windows,
         respectively; all are optional, but at least one must be present

    Returns:
      the merged lockfile content
    """
    inputs = (
        (linux, {'os:linux'}),
        (macos, {'os:macos', 'os:osx'}),
        (windows, {'os:windows'}),
    )
    inputs = [(file, keys) for (file, keys) in inputs if file]
    if not inputs:
        raise ValueError('no input streams given')
    (first, _), *rest = inputs
    lock = json.loads(first)
    exts_key = 'moduleExtensions'
    for (file, keys) in rest:
        for label, ext in json.loads(file)[exts_key].items():
            for platform, val in ext.items():
                if not set(platform.split(',')).isdisjoint(keys):
                    lock.setdefault(
                        exts_key, {}).setdefault(label, {})[platform] = val
    return json.dumps(lock, indent=2) + '\n'


def _main() -> None:
    parser = argparse.ArgumentParser(allow_abbrev=False)
    parser.add_argument('--linux', '-l', type=_input)
    parser.add_argument('--macos', '-m', type=_input)
    parser.add_argument('--windows', '-w', type=_input)
    parser.add_argument('--output', '-o', type=pathlib.Path, required=True)
    args = parser.parse_args()
    output = merge(linux=args.linux, macos=args.macos, windows=args.windows)
    args.output.write_text(output, encoding='utf-8')


def _input(string: str) -> str:
    return pathlib.Path(string).read_text(encoding='utf-8')


if __name__ == '__main__':
    _main()

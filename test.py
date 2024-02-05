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

"""Unit tests for merge.py."""

import io
import pathlib
import unittest

import merge


class Test(unittest.TestCase):
    """Unit tests for merge.py."""

    maxDiff = 1000

    def test_merge(self) -> None:
        """Unit test for the merge function."""
        output = io.StringIO()
        base = pathlib.Path(__file__).parent
        with ((base / 'test-linux.json').open('r', encoding='utf-8') as linux,
              (base / 'test-macos.json').open('r', encoding='utf-8') as macos):
            merge.merge(output=output, linux=linux, macos=macos)
        self.assertEqual(output.getvalue(),
                         (base / 'test-merged.json').read_text())


if __name__ == '__main__':
    unittest.main()

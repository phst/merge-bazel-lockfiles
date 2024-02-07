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

import pathlib
import unittest

import merge


class Test(unittest.TestCase):
    """Unit tests for merge.py."""

    maxDiff = 1000

    def test_merge(self) -> None:
        """Unit test for the merge function."""
        base = pathlib.Path(__file__).parent
        output = merge.merge(
            linux=(base / 'test-linux.json').read_text(encoding='utf-8'),
            macos=(base / 'test-macos.json').read_text(encoding='utf-8'),
        )
        self.assertEqual(output,
                         (base / 'test-merged.json').read_text())


if __name__ == '__main__':
    unittest.main()

#!/usr/bin/env python3

# Copyright 2024, 2025 Philipp Stephani
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
from collections.abc import Mapping
import dataclasses
import enum
import functools
import json
import os
import pathlib
import platform
from typing import Any, Optional


@functools.total_ordering
class System(enum.Enum):
    """Known operating systems."""

    LINUX = enum.auto()
    DARWIN = enum.auto()
    WINDOWS = enum.auto()

    def __lt__(self, other: 'System') -> bool:
        return self.value < other.value

    @classmethod
    def current(cls) -> 'System':
        """Returns the current operating system."""
        return System[platform.system().upper()]


@functools.total_ordering
class Architecture(enum.Enum):
    """Known architectures."""

    ARM64 = enum.auto()
    AMD64 = enum.auto()

    def __lt__(self, other: 'Architecture') -> bool:
        return self.value < other.value

    @classmethod
    def parse(cls, string: str) -> 'Architecture':
        """Parses an architecture name."""
        archs: dict[str, Architecture] = {
            'aarch64': cls.ARM64,
            'arm64': cls.ARM64,
            'x86_64': cls.AMD64,
            'amd64': cls.AMD64,
        }
        return archs[string]

    @classmethod
    def current(cls) -> 'Architecture':
        """Returns the current architecture."""
        return cls.parse(platform.machine())


@dataclasses.dataclass(order=True, frozen=True)
class Platform:
    """Combination of operating system and architecture."""

    system: System
    arch: Architecture

    @classmethod
    def current(cls) -> 'Platform':
        """Returns the current platform."""
        return Platform(System.current(), Architecture.current())

    @classmethod
    def parse(cls, string: str) -> 'Platform':
        """Parses a platform from a key in MODULE.bazel.lock."""
        system, _, arch = string.partition('/')
        return Platform(System[system], Architecture[arch])

    def __str__(self) -> str:
        return f'{self.system.name}/{self.arch.name}'


def merge(inputs: Mapping[Platform, str]) -> str:
    """Merge multiple MODULE.bazel.lock files into one.

    Args:
      inputs: mapping from platforms to input file contents

    Returns:
      the merged output
    """
    if not inputs:
        raise ValueError('no inputs given')
    (_, first), *rest = sorted(inputs.items())
    lock = json.loads(first)
    rest_by_system: dict[System, dict[Architecture, str]] = {}
    for plat, text in rest:
        rest_by_system.setdefault(plat.system, {})[plat.arch] = text
    for system, archs in rest_by_system.items():
        use_arch = len(archs) > 1
        for arch, text in archs.items():
            _merge_exts(lock, Platform(system, arch), text, use_arch)
    return json.dumps(lock, indent=2) + '\n'


def _merge_exts(lock: dict[str, Any], plat: Platform, text: str,
                use_arch: bool) -> None:
    exts_key = 'moduleExtensions'
    for label, ext in json.loads(text)[exts_key].items():
        for key, val in ext.items():
            ext_sys, ext_arch = _parse(key)
            matches = (plat.system == ext_sys
                       and (not use_arch or plat.arch == ext_arch))
            if matches:
                lock.setdefault(exts_key, {}).setdefault(label, {})[key] = val


def _parse(string: str) -> tuple[Optional[System], Optional[Architecture]]:
    systems: dict[str, System] = {
        'linux': System.LINUX,
        'macos': System.DARWIN,
        'osx': System.DARWIN,
        'windows': System.WINDOWS,
    }
    system: Optional[System] = None
    arch: Optional[Architecture] = None
    for piece in string.split(','):
        kind, _, val = piece.partition(':')
        if kind == 'os':
            system = systems[val]
        elif kind == 'arch':
            arch = Architecture.parse(val)
    return system, arch


def _main() -> None:
    cwd = pathlib.Path(
        os.getenv('BUILD_WORKING_DIRECTORY') or pathlib.Path.cwd())
    def path(s: str) -> pathlib.Path:
        return cwd / s
    parser = argparse.ArgumentParser(allow_abbrev=False)
    for system in System:
        for arch in Architecture:
            name = f'--{system.name}-{arch.name}'.lower()
            parser.add_argument(name, type=path,
                                dest=str(Platform(system, arch)))
    parser.add_argument('--local', '-l', type=path,
                        dest=str(Platform.current()))
    parser.add_argument('--output', '-o', type=path, required=True)
    args = parser.parse_args()
    inputs: dict[Platform, str] = {
        Platform.parse(key): val.read_text(encoding='utf-8')
        for key, val in vars(args).items()
        if val and key != 'output'
    }
    output = merge(inputs)
    args.output.write_text(output, encoding='utf-8')


if __name__ == '__main__':
    _main()

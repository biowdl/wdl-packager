# Copyright (c) 2019 Leiden University Medical Center
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from pathlib import Path

import pytest

from wdl_packager.git import get_commit_version, get_file_last_commit_timestamp

from . import TEST_DATA_DIR

TIMESTAMP_FILES = [
    (Path(TEST_DATA_DIR, "gatk-variantcalling", "tasks", "gatk.wdl"),
     1574753755),
    (Path(TEST_DATA_DIR, "gatk-variantcalling", "gatk-variantcalling.wdl"),
     1574768480)
]


@pytest.mark.parametrize(["repo_file", "result"], TIMESTAMP_FILES)
def test_get_commit_timestamp(repo_file, result):
    assert get_file_last_commit_timestamp(repo_file) == result


def test_get_commit_version():
    assert get_commit_version(
        Path(TEST_DATA_DIR, "gatk-variantcalling")) == "v1.0.0-1-g43b8475"

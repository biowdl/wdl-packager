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

import os
from pathlib import Path

import WDL

import pytest

from wdl_packager import get_protocol, wdl_paths

TEST_DATA_DIR = Path(Path(__file__).parent) / Path("data")
PROTOCOL_TEST = [
    ("/bla/bla/bladiebla", None),
    ("http://github.com", "http"),
    ("file:///blabla/bla", "file"),
    ("sqlalchemy+psycopg2:///mydatabase?bla", "sqlalchemy+psycopg2")
]


@pytest.mark.parametrize(["uri", "result"], PROTOCOL_TEST)
def test_get_protocol(uri, result):
    assert get_protocol(uri) == result


def test_wdl_paths():
    wdl_file = (TEST_DATA_DIR / Path("gatk-variantcalling") /
                Path("gatk-variantcalling.wdl"))
    os.chdir(wdl_file.parent)
    wdl_doc = WDL.load(wdl_file.name)
    relpaths = set(relpath for abspath, relpath in wdl_paths(wdl_doc))
    assert relpaths == {
        Path("gatk-variantcalling.wdl"),
        Path("gvcf.wdl"),
        Path("tasks/biopet/biopet.wdl"),
        Path("tasks/common.wdl"),
        Path("tasks/gatk.wdl"),
        Path("tasks/picard.wdl"),
        Path("tasks/samtools.wdl")
    }


def test_wdl_paths_unresolvable():
    wdl_file = (TEST_DATA_DIR / Path("gatk-variantcalling") / Path("tasks") /
                Path("biopet") / Path("biopet.wdl"))
    os.chdir(wdl_file.parent)
    wdl_doc = WDL.load(wdl_file.name)
    with pytest.raises(ValueError) as e:
        wdl_paths(wdl_doc)
    assert e.match("../common.wdl")

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
import sys
import tempfile
import zipfile
from pathlib import Path

import WDL

import pytest

import wdl_packager
from wdl_packager import (get_protocol,
                          package_wdl,
                          resolve_path_naive,
                          wdl_paths)

TEST_DATA_DIR = Path(Path(__file__).parent, "data")
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
    wdl_file = TEST_DATA_DIR / Path("gatk-variantcalling",
                                    "gatk-variantcalling.wdl")
    wdl_doc = WDL.load(str(wdl_file))
    relpaths = set(relpath for abspath, relpath in wdl_paths(wdl_doc))
    assert relpaths == {
        Path(wdl_file.parent, "gatk-variantcalling.wdl"),
        Path(wdl_file.parent, "gvcf.wdl"),
        Path(wdl_file.parent, "tasks/biopet/biopet.wdl"),
        Path(wdl_file.parent, "tasks/common.wdl"),
        Path(wdl_file.parent, "tasks/gatk.wdl"),
        Path(wdl_file.parent, "tasks/picard.wdl"),
        Path(wdl_file.parent, "tasks/samtools.wdl")
    }


def test_package_wdl():
    wdl_file = TEST_DATA_DIR / Path("gatk-variantcalling",
                                    "gatk-variantcalling.wdl")
    output_zip = tempfile.mktemp(".zip")
    package_wdl(str(wdl_file), output_zip)
    with zipfile.ZipFile(output_zip, "r") as wdl_zip:
        wdl_zip.testzip()
        zipped_files = {zip_info.filename for zip_info in wdl_zip.filelist}
        assert zipped_files == {
            "gatk-variantcalling.wdl",
            "gvcf.wdl",
            "tasks/biopet/biopet.wdl",
            "tasks/common.wdl",
            "tasks/gatk.wdl",
            "tasks/picard.wdl",
            "tasks/samtools.wdl"
        }


def test_wdl_paths_unresolvable():
    wdl_file = TEST_DATA_DIR / Path("gatk-variantcalling", "tasks", "biopet",
                                    "biopet.wdl")
    os.chdir(wdl_file.parent)
    wdl_doc = WDL.load(wdl_file.name)
    with pytest.raises(ValueError) as e:
        wdl_paths(wdl_doc)
    assert e.match("../common.wdl")


def test_package_wdl_unresolvable():
    wdl_file = TEST_DATA_DIR / Path("gatk-variantcalling", "tasks", "biopet",
                                    "biopet.wdl")

    with pytest.raises(ValueError) as e:
        package_wdl(str(wdl_file), tempfile.mktemp(".zip"))
    assert ("Could not create import zip with sensible "
            "paths. Are there parent file ('..') type "
            "imports in the wdl?") in str(e.value)


DOTTED_URIS = [
    (Path("bla/../bla"), Path("bla")),
    (Path("/bla/../../../usr/lib"), Path("/usr/lib")),
    (Path("my_wdl/tasks/biopet/../common.wdl"),
     Path("my_wdl/tasks/common.wdl")),
    (Path("multiple/../dots/../detected"), Path("detected")),
]

UNRESOLVABLE_DOTTED_URIS = [
     Path("../my_import.wdl"),
     Path("tasks/../../my_import.wdl"),
     Path("seemingly/fine/../but/../too/many/dots/../../../../../indeed")
]


@pytest.mark.parametrize(["uri", "result"], DOTTED_URIS)
def test_resolve_path_naive(uri, result):
    assert resolve_path_naive(uri) == result


@pytest.mark.parametrize("uri", UNRESOLVABLE_DOTTED_URIS)
def test_resolve_path_naive_unsolvable(uri):
    with pytest.raises(ValueError) as e:
        resolve_path_naive(uri)
    assert e.match("unknown parent")


def test_main():
    wdl_file = TEST_DATA_DIR / Path("gatk-variantcalling",
                                    "gatk-variantcalling.wdl")
    test_zip = tempfile.mktemp(".zip")
    sys.argv = ["wdl-packager", "-o", test_zip, str(wdl_file)]
    wdl_packager.main()
    with zipfile.ZipFile(test_zip, "r") as wdl_zip:
        wdl_zip.testzip()
        zipped_files = {zip_info.filename for zip_info in wdl_zip.filelist}
        assert zipped_files == {
            "gatk-variantcalling.wdl",
            "gvcf.wdl",
            "tasks/biopet/biopet.wdl",
            "tasks/common.wdl",
            "tasks/gatk.wdl",
            "tasks/picard.wdl",
            "tasks/samtools.wdl"
        }

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

import sys
import tempfile
import zipfile
from pathlib import Path

import pytest

from wdl_packager import (package_wdl,
                          wdl_packager,
                          wdl_paths, )

from . import TEST_DATA_DIR, file_md5sum


def test_wdl_paths():
    wdl_file = TEST_DATA_DIR / Path("gatk-variantcalling",
                                    "gatk-variantcalling.wdl")

    relpaths = set(relpath for abspath, relpath in wdl_paths(str(wdl_file)))
    assert relpaths == {
        Path("gatk-variantcalling.wdl"),
        Path("gvcf.wdl"),
        Path("tasks/biopet/biopet.wdl"),
        Path("tasks/common.wdl"),
        Path("tasks/gatk.wdl"),
        Path("tasks/picard.wdl"),
        Path("tasks/samtools.wdl")
    }


def test_package_wdl():
    wdl_file = TEST_DATA_DIR / Path("gatk-variantcalling",
                                    "gatk-variantcalling.wdl")
    output_zip = tempfile.mktemp(".zip")
    package_wdl(wdl_file, output_zip)
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
    with pytest.raises(ValueError) as e:
        wdl_paths(str(wdl_file))
    assert e.match("type imports in the wdl?")


# TODO: wait for https://github.com/chanzuckerberg/miniwdl/pull/310 and new
# version.
@pytest.mark.xfail
def test_wdl_paths_file_protocol():
    wdl_file = TEST_DATA_DIR / Path("file_import.wdl")
    assert "gatk-variantcalling/gatk-variantcalling.wdl" in \
           wdl_paths(str(wdl_file))


def test_package_wdl_unresolvable():
    wdl_file = TEST_DATA_DIR / Path("gatk-variantcalling", "tasks", "biopet",
                                    "biopet.wdl")

    with pytest.raises(ValueError) as e:
        package_wdl(wdl_file, tempfile.mktemp(".zip"))
    assert ("Could not create import zip with sensible "
            "paths. Are there parent file ('..') type "
            "imports in the wdl?") in str(e.value)


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


def test_package_wdl_reproducible():
    wdl_file = TEST_DATA_DIR / Path("gatk-variantcalling",
                                    "gatk-variantcalling.wdl")
    test_zip = tempfile.mktemp(".zip")
    package_wdl(wdl_file, test_zip, use_git_timestamps=True)
    assert file_md5sum(Path(test_zip)) == "30acf24b748aa333eac0192caa8b93d5"

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
import time
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
    os.remove(output_zip)


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
    test_zip = tempfile.mktemp(".zip")
    with pytest.raises(ValueError) as e:
        package_wdl(wdl_file, test_zip)
    assert ("Could not create import zip with sensible "
            "paths. Are there parent file ('..') type "
            "imports in the wdl?") in str(e.value)

def test_main():
    wdl_file = Path(TEST_DATA_DIR, "gatk-variantcalling",
                    "gatk-variantcalling.wdl")
    # Add a LICENSE file to test additional file testing.
    add_file = Path(TEST_DATA_DIR, "gatk-variantcalling", "tasks", "LICENSE")
    # add a file outside the git repository
    add_file2 = Path(TEST_DATA_DIR, "file_import.wdl")
    test_zip = tempfile.mktemp(".zip")
    sys.argv = ["wdl-packager", "-o", test_zip, str(wdl_file),
                "--add", str(add_file), "--add", str(add_file2)]
    wdl_packager.main()
    with zipfile.ZipFile(test_zip, "r") as wdl_zip:
        wdl_zip.testzip()
        zipped_files = {zip_info.filename for zip_info in wdl_zip.filelist}
        assert zipped_files == {
            "file_import.wdl",
            "gatk-variantcalling.wdl",
            "gvcf.wdl",
            "tasks/biopet/biopet.wdl",
            "tasks/common.wdl",
            "tasks/gatk.wdl",
            "tasks/LICENSE",
            "tasks/picard.wdl",
            "tasks/samtools.wdl"
        }
    os.remove(test_zip)


# Ignore timezone warning on this test as it is triggered on systems that do
# not have their timezone set to UTC.
@pytest.mark.filterwarnings("ignore:Timezone")
def test_package_wdl_reproducible():
    """This test works perfectly in containers, but not so well in the user's
    environment."""
    wdl_file = TEST_DATA_DIR / Path("gatk-variantcalling",
                                    "gatk-variantcalling.wdl")
    test_zip = tempfile.mktemp(".zip")
    package_wdl(wdl_file, test_zip, use_git_timestamps=True)
    # Correct timestamp for UTC
    assert file_md5sum(Path(test_zip)) == "c5456ebfc6f29a6226b3a9f2714a937f"
    os.remove(test_zip)


def test_timezone_check(recwarn):
    wdl_file = TEST_DATA_DIR / Path("gatk-variantcalling",
                                    "gatk-variantcalling.wdl")
    test_zip = tempfile.mktemp(".zip")
    os.environ["TZ"] = "CET"
    time.tzset()
    package_wdl(wdl_file, test_zip, use_git_timestamps=True)
    assert len(recwarn) == 1
    wrn = recwarn.pop(UserWarning)
    assert issubclass(wrn.category, UserWarning)
    assert "Timezone 'CET' is not 'UTC'." in str(wrn.message)
    os.remove(test_zip)

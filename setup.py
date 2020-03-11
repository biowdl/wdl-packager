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

from setuptools import find_packages, setup

with open("README.rst", "r") as readme_file:
    LONG_DESCRIPTION = readme_file.read()

setup(
    name="wdl-packager",
    version="1.1.0-dev",
    description="Package a WDL and its imports into a zip file.",
    author="Leiden University Medical Center",
    author_email="sasc@lumc.nl",
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/x-rst",
    license="MIT",
    keywords="WDL wdl zip package",
    zip_safe=False,
    packages=find_packages('src'),
    package_dir={'': 'src'},
    url="https://github.com/biowdl/wdl-packager",
    classifiers=[
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: MIT License"
    ],
    python_requires=">=3.6",  # Also needed for miniwdl
    install_requires=[
       "miniwdl",
       "setuptools"
    ],
    entry_points={
        "console_scripts": [
            'wdl-packager=wdl_packager.wdl_packager:main'
        ]
    },
)

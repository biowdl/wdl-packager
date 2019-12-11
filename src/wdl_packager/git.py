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

import subprocess
from pathlib import Path


def git_command(repository: Path, *args) -> str:
    """
    Run a git command in a repository. Crashes with a CalledProcessError
    :param repository: Path to the repository
    :param args: the rest of the git arguments
    :return: a string with the output
    """
    results = subprocess.run(("git", "-C", str(repository)) + args,
                             stdout=subprocess.PIPE, check=True)
    return results.stdout.decode()


def get_commit_timestamp(repository: Path):
    """
    Gets a commit unix timestamp from a repository
    :param repository: Path to the repository
    :return: An integer that is the unix timestamp
    """
    return int(git_command(repository, "show", "-s", "--format=%at"))


def get_commit_version(repository: Path):
    """
    Produce a version string with git describe. If there are no names
    use the shortened hash instead.
    :param repository: Path to the repository
    :return: A version string produced by git.
    """
    try:
        version = git_command(repository, "describe").strip()
    except subprocess.CalledProcessError:
        # If it cannot be described fall back to the hash.
        version = git_command(repository, "show", "-s", "--format=%h")
    return version
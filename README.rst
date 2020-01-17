wdl-packager
============

.. Badges have empty alts. So nothing shows up if they do not work.
.. This fixes readthedocs issues with badges.
.. image:: https://img.shields.io/pypi/v/wdl-packager.svg
  :target: https://pypi.org/project/wdl-packager/
  :alt:

.. image:: https://img.shields.io/conda/v/conda-forge/wdl-packager.svg
  :target: https://anaconda.org/conda-forge/wdl-packager
  :alt:

.. image:: https://img.shields.io/pypi/pyversions/wdl-packager.svg
  :target: https://pypi.org/project/wdl-packager/
  :alt:

.. image:: https://img.shields.io/pypi/l/wdl-packager.svg
  :target: https://github.com/biowdl/wdl-packager/blob/master/LICENSE
  :alt:

.. image:: https://travis-ci.com/biowdl/wdl-packager.svg?branch=develop
  :target: https://travis-ci.com/biowdl/wdl-packager
  :alt:

.. image:: https://codecov.io/gh/biowdl/wdl-packager/branch/develop/graph/badge.svg
  :target: https://codecov.io/gh/biowdl/wdl-packager
  :alt:

Package a WDL and its imports into a zip file.

The zip file can be used as a valid imports zip for `cromwell
<https://github.com/broadinstitute/cromwell>`_. It can also be used to archive
your workflow.

wdl-packager currently only supports file based imports. It aims to support
http urls in the future.

Usage
-----

.. code-block:: text

    usage: wdl-packager [-h] [-o OUTPUT] [--add ADDITIONAL_FILES]
                        [--use-git-version-name] [--use-git-commit-timestamp]
                        [--reproducible] [--version]
                        WDL_FILE

    positional arguments:
      WDL_FILE              The WDL file that will be packaged.

    optional arguments:
      -h, --help            show this help message and exit
      -o OUTPUT, --output OUTPUT
                            The output zip file. By default uses the name of the
                            input. This overrides the git name option.
      --add ADDITIONAL_FILES, --additional-file ADDITIONAL_FILES
      --use-git-version-name
                            Use git describe to determine the name of the zip.
      --use-git-commit-timestamp
                            Use the git commit timestamp to timestamp all the
                            files in the zip.
      --reproducible        shorthand for --use-git-version-name and --use-git-
                            commit-timestamp
      --version             show program's version number and exit

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

Wdl-packager can create zip packages that are `binary reproducible
<https://reproducible-builds.org/>`_ when used with the ``--reproducible``
flag. It can also include additional files such as licenses, READMEs and
example configuration files. This makes it ideal for distributing WDL workflows
as packages.

Wdl-packager currently only supports file based imports.

Usage
-----

.. code-block:: text

    usage: wdl-packager [-h] [-o OUTPUT] [-a ADDITIONAL_FILES]
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
      -a ADDITIONAL_FILES, --additional-file ADDITIONAL_FILES
                            Additional files to be included in the zip.
      --use-git-version-name
                            Use git describe to determine the name of the zip.
      --use-git-commit-timestamp
                            Use the git commit timestamp to timestamp all the
                            files in the zip.
      --reproducible        shorthand for --use-git-version-name and --use-git-
                            commit-timestamp
      --version             show program's version number and exit

Reproducibility
---------------
The internal process to create a reproducible package is as follows:

+ It checks each file with ``git log --n1 --pretty=%at`` to get the unix
  timestamp of the latest commit that affected that file.
+ Each file is then copied to a temporary directory where the last modified
  time is changed to the unix timestamp found in the first step.
+ The list of files is then sorted by their destionation path in the zip. The
  sorting ensures that the files will always be added in the same order.
+ The timezone of the process is changed to UTC, as the timezone affects the
  timestamp of the files in the zip archive.
+ The files are added to the zip package in sorted order.

The name for a reproducible package consists of

+ The WDL file basename without ``.wdl``.
+ A version description by ``git describe --always``.
+ A ``.zip`` extension.

Known issues
------------
+ Old versions of `Cromwell <https://github.com/broadinstitute/cromwell>`_
  contain a bug that causes a crash when opening zip files with nested
  directories. This was fixed in cromwell version 49.
+ ``http://`` imports are currently not supported. Wdl-packager could be an
  ideal tool to fetch WDLs from the web and package their imports in such a
  way that they can be used locally. Unfortunately this requires rewriting the
  import paths inside the WDL files before they are packaged. This is
  non-trivial to implement and it may have unintentioned side effects.

wdl-packager
============

Package a WDL and its imports into a zip file.

The zip file can be used as a valid imports zip for `cromwell
<https://github.com/broadinstitute/cromwell>`_. It can also be used to archive
your workflow.

wdl-packager currently only supports file based imports. It aims to support
http urls in the future.

Usage
-----

.. code-block::

    usage: wdl-packager [-h] [-o OUTPUT] WDL_FILE

    positional arguments:
      WDL_FILE              The WDL file that will be packaged.

    optional arguments:
      -h, --help            show this help message and exit
      -o OUTPUT, --output OUTPUT
                            The output zip file. By default uses the name of the
                            input.


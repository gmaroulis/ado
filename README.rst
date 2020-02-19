========
Overview
========

.. start-badges

.. list-table::
    :stub-columns: 1

    * - tests
      - |
        |
    * - package
      - | |version| |wheel| |supported-versions| |supported-implementations|
        | |commits-since|

.. |version| image:: https://img.shields.io/pypi/v/ado.svg
    :alt: PyPI Package latest release
    :target: https://pypi.org/project/ado

.. |wheel| image:: https://img.shields.io/pypi/wheel/ado.svg
    :alt: PyPI Wheel
    :target: https://pypi.org/project/ado

.. |supported-versions| image:: https://img.shields.io/pypi/pyversions/ado.svg
    :alt: Supported versions
    :target: https://pypi.org/project/ado

.. |supported-implementations| image:: https://img.shields.io/pypi/implementation/ado.svg
    :alt: Supported implementations
    :target: https://pypi.org/project/ado

.. |commits-since| image:: https://img.shields.io/github/commits-since/itsvipa/ado/v0.0.0.svg
    :alt: Commits since latest release
    :target: https://github.com/itsvipa/ado/compare/v0.0.0...master



.. end-badges

AWS Step functions CLI and State Machine / Job Generator

* Free software: Apache Software License 2.0

Installation
============

::

    pip install ado

You can also install the in-development version with::

    pip install https://github.com/gmaroulis/ado/archive/master.zip


Documentation
=============


To use the project:

.. code-block:: python

    import ado
    ado.longest()


Development
===========

To run the all tests run::

    tox

Note, to combine the coverage data from all the tox environments run:

.. list-table::
    :widths: 10 90
    :stub-columns: 1

    - - Windows
      - ::

            set PYTEST_ADDOPTS=--cov-append
            tox

    - - Other
      - ::

            PYTEST_ADDOPTS=--cov-append tox

pytest-sort
===========

.. image:: https://img.shields.io/pypi/v/pytest-sort
   :alt: PyPI - Version
   :target: https://pypi.org/project/pytest-sort

This pytest plugin is used to help identify application state leaks in your test suite.  It does this by automatically changing the execution order of test cases.

How fustrating is it to have a test case that works fine when runs by itself, but fails when run with the rest of the suite?  By running tests in a random order, the culprit of such problems can be identified much earlier in the development process.  Alternately, running in ordered and reverse order can help find the cause of the problem in existing test suites.

Features
--------

* Multiple sort options including: Random, Fastest, Reverse, and more.
* Group test cases into buckets that are each sorted separately.
* Control sort order of the buckets.
* Use Pytest markers to always run specific test cases in order.

Installation::

   pip install pytest-sort --upgrade

Running with pytest-sort::

   pytest --sort-mode=random


.. toctree::
   :maxdepth: 2
   :caption: Contents

   problem
   usage
   how
   markers
   options


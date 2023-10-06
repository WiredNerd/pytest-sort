pytest-sort
===========

.. image:: https://img.shields.io/pypi/v/pytest-sort
   :alt: PyPI - Version
   :target: https://pypi.org/project/pytest-sort

pytest-sort is a pytest plugin to automatically change the execution order of test cases.
Changing the order of execution can help find test cases that only succeed because of a favorable state.

This plugin provides several options for controlling how the test cases are reordered.

Installation::

   pip install pytest-sort --upgrade

Running with pytest-sort::

   pytest --sort-mode=random


.. toctree::
   :maxdepth: 2
   :caption: Contents

   usage
   how
   markers
   options


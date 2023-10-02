pytest-sort
===========

*
   .. image:: https://img.shields.io/badge/python->=3.8-blue
      :alt: python>=3.8
   .. image:: https://img.shields.io/pypi/dm/pytest-sort
      :alt: PyPI - Downloads
   .. image:: https://img.shields.io/pypi/l/pytest-sort
      :alt: PyPI - License
   .. image:: https://img.shields.io/pypi/v/pytest-sort
      :alt: PyPI - Version
*
   .. image:: https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2FWiredNerd%2Fpytest-sort%2Fmain%2Fcode-coverage.json&query=%24.totals.percent_covered_display&suffix=%25&label=Code%20Coverage&color=teal
      :alt: Code Coverage
      :target: https://pytest-cov.readthedocs.io
   .. image:: https://img.shields.io/badge/dynamic/xml?url=https%3A%2F%2Fraw.githubusercontent.com%2FWiredNerd%2Fpytest-sort%2Fmain%2Fmutation-testing-report.xml&query=round((%2F%2Ftestsuites%5B1%5D%2F%40tests%20-%20%2F%2Ftestsuites%5B1%5D%2F%40disabled%20-%20%2F%2Ftestsuites%5B1%5D%2F%40failures%20-%20%2F%2Ftestsuites%5B1%5D%2F%40errors)div(%2F%2Ftestsuites%5B1%5D%2F%40tests%20-%20%2F%2Ftestsuites%5B1%5D%2F%40disabled)*100)&suffix=%25&label=Mutation%20Coverage&color=orange
      :alt: Mutation Coverage
      :target: https://mutmut.readthedocs.io/
*
   .. image:: https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336
      :alt: Imports: isort
      :target: https://pycqa.github.io/isort/
   .. image:: https://img.shields.io/badge/Code_Style-Black-black
      :alt: Code Style: black
      :target: https://black.readthedocs.io
   .. image:: https://img.shields.io/badge/Linter-ruff-purple
      :alt: Linter: ruff
      :target: https://beta.ruff.rs/docs/
   .. image:: https://img.shields.io/badge/Snyk%20Security-monitored-FF66FF
      :alt: Snyk Security
      :target: https://snyk.io/
   .. image:: https://readthedocs.org/projects/pytest-sort/badge/?version=docs
      :alt: Documentation Status
      :target: https://pytest-sort.readthedocs.io/


pytest-sort is a pytest plugin to automatically change the execution order of test cases.
Changing the order of execution can help find test cases that only succeed because of a favorable state.

This plugin provides several options for controlling how the test cases are reordered.

.. toctree::
   :maxdepth: 2
   :caption: Contents

   quickstart
   usage
   how
   markers
   options


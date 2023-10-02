Quick Start
===========

Installation::

   pip install pytest-sort -upgrade

Running with pytest-sort::

   pytest --sort-mode=random

By default, all tests from the same module or class will run together.  This command will randomize the execution order of the tests within the module/class.

::

   pytest --help


In the pytest-sort section, all currently avaialable options will be listed.

You may also set options in any `pytest configruation file`_.

.. _pytest configruation file: https://docs.pytest.org/en/stable/reference/customize.html
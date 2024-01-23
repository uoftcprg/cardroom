========
Cardroom
========

A Django application for poker tournament and table management.

Features
--------

- Table management.
- Tournament management.

Installation
------------

.. code-block:: bash

   pip install cardroom

Usage
-----

Cardroom can run as a standalone server or can be added on to existing projects
by simply adding ``cardroom`` to the list of installed apps.

.. code-block:: python

   INSTALLED_APPS = [
       ...
       'cardroom',
       ...
   ]


Testing and Validation
----------------------

Cardroom has extensive test coverage, passes mypy static type checking, and has
been validated through extensive use in real-life scenarios.

Contributing
------------

Contributions are welcome! Please read our Contributing Guide for more
information.

License
-------

Cardroom is distributed under the MIT license.

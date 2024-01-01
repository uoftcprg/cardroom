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

Below shows a sample usage of Cardroom.

Add ``cardroom`` to the installed apps.

.. code-block:: python

   INSTALLED_APPS = [
       ...
       'cardroom',
       ...
   ]

.. code-block:: python

   from cardroom import Table
   from pokerkit import (
       BettingStructure,
       Deck,
       Opening,
       StandardHighHand,
       Street,
   )
   
   
   def callback(table, operation):
       pass
   
   
   table = Table(
       6,
       True,
       Deck.STANDARD,
       (StandardHighHand,),
       (
           Street(
               False,
               (False,) * 2,
               0,
               False,
               Opening.POSITION,
               1,
               None,
           ),
           Street(
               True,
               (),
               3,
               False,
               Opening.POSITION,
               1,
               None,
           ),
           Street(
               True,
               (),
               1,
               False,
               Opening.POSITION,
               1,
               None,
           ),
           Street(
               True,
               (),
               1,
               False,
               Opening.POSITION,
               1,
               None,
           ),
       ),
       BettingStructure.NO_LIMIT,
       True,
       None,
       (1, 2),
       0,
       range(80, 201),
       30,
       1,
       1,
       100,
       0.05,
       0.1,
       0.05,
       0.1,
       0.1,
       0.1,
       10,
       10,
       10,
       10,
       3,
       0.5,
       0.5,
       0.5,
       1,
       callback,
   )
   
   table.run()

Testing and Validation
----------------------

Cardroom has extensive test coverage, passes mypy static type checking with
strict parameter, and has been validated through extensive use in real-life
scenarios.

Contributing
------------

Contributions are welcome! Please read our Contributing Guide for more
information.

License
-------

Cardroom is distributed under the MIT license.

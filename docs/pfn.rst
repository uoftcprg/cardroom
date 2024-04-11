Poker Frame Notation
====================

This page defines the poker frame notation (PFN) standard, designed to standardize the description of the state of poker tables. Despite poker's widespread popularity in the mainstream culture as a mind sport and its prominence in the online gambling space, it lacks a consistent format that can used to specify the poker table values. To address this gap in the literature, we propose the PFN standard which provides a concise machine-friendly representation of poker tables that comprehensively captures various details of the hand, ranging from initial game parameters and actions to contextual parameters including but not limited to the venue, players, and time control information.

Introduction
------------

Poker is a popular card game with a rich history and countless regional variants. It is often played online by enthusiasts. This website introduces the poker frame notation (PFN) which seek to standardize the description of poker tables so it can be displayed to the end-user. We propose that this goal requires the following information to be supplied:

- Chips (stacks, bets, main + side pot(s));
- Cards (up/down, hole, and board cards);
- Possible end-user actions as a player;
- Ongoing hand history;
- Player information (names, etc.); and
- Optional information specific to the platform.

The PFN format is a derivative of the `JavaScript Object Notation (JSON) <https://www.json.org/>`_. This design allows PFN files to take advantage of JSON's type system and be easily machine-readable and writable.

The PFN format puts restrictions on the naming and types of the key/values, with which the poker tables are described.


Frame
-----

The root-level (i.e. frame-level) keys and the corresponding value types are shown below.

======= =========== ======================
Key     Key Name    JavaScript Native Type
======= =========== ======================
Seats   ``seats``   Array of Seats
Pot     ``pot``     Array of numbers
Board   ``board``   Array of Cards
Game    ``game``    Game
Action  ``action``  Action
History ``history`` String
======= =========== ======================

Seats
-----

This field is of type Array and contains information about the table seats.

The seat-level keys and the corresponding value types are shown below.

========= ============= =============================
Key       Key Name      JavaScript Native Type
========= ============= =============================
User      ``name``      String
Button    ``button``    Boolean
Bet       ``bet``       Number or ``null``
Stack     ``stack``     Number or ``null``
Hole      ``hole``      Array of Cards
Timestamp ``timestamp`` Array of (0, 1, or 2 strings)
Active    ``active``    Boolean
Turn      ``turn``      Boolean
========= ============= =============================

User
^^^^

This key/value denotes the seated user's name. It is an empty string if no one is sitting there.

Button
^^^^^^

This key/value denotes whether the corresponding seat has the button. No seat has buttons in stud games.

Bet
^^^

This key/value denotes the seat's bet. It may be ``null`` to denote an empty seat or an inapplicable value.

Stack
^^^^^

This key/value denotes the seat's stack. It may be ``null`` to denote an empty seat or an inapplicable value.

Hole
^^^^

This key/value denotes the seat's hole cards. It may be empty. Each item represent an individual hole card. On how a card is represented, please consult the later section on the card representation.

Timestamp
^^^^^^^^^

This key/value denotes two timestamps. It may be empty in which case the player at the seat (if any) is not acting. The 1 or 2 elements represent the following:

The timestamp at which the player...

0. Began his/her action decision making.
1. Auto-folds/checks/stands pat/showdowns (i.e. runs out of time).

The auto timestamp may be non-existent (i.e. array is a singleton) if the player has an unlimited time to choose his/her action. The strings are always valid `Date Time String Format <https://tc39.es/ecma262/multipage/numbers-and-dates.html#sec-date-time-string-format>`_.

Active
^^^^^^

This key/value denotes the player's active status. The status in this context means not sitting out. If no player is in the seat, it is always ``false``.

Turn
^^^^

This key/value denotes whether or not a player at the seat is in turn to act.

Pot
---

The pot is an array of numbers denoting the main (+ side) pot(s) in the hand. If it is empty, there is no pot. If it is a singleton, there is only one main pot. If it is of length 2 or greater, there exists at least one side pot, with the first item being the main pot.

Board
-----

This key/value denotes the board cards. It may be empty. Each item represent an individual community card. On how a card is represented, please consult the later section on the card representation.

Game
----

This field describes the game being played such as how the dealings were, are, and will be carried out. If no poker variant is chosen for the table, the values are empty. The values differ based on the played variant. All values here are of type array and have the same length equal to the number of betting rounds (if a game is chosen). The item for each array correspond to the value for that particular betting round.

The variant-level keys and the corresponding value types are shown below.

======================= ========= ==========================
Key                     Key Name  JavaScript Native Type
======================= ========= ==========================
Hole Dealings           ``hole``  Array of Array of Booleans
Board Dealings          ``board`` Array of Numbers
Standing Pat/Discarding ``draw``  Array of Booleans
======================= ========= ==========================

Hole Dealings
^^^^^^^^^^^^^

Each item is an array of Booleans on whether a hole card is dealt face up (``true``) or down (``false``).

Board Dealings
^^^^^^^^^^^^^^

Each item is a number on how many card is dealt to the board.

Standing Pat/Discarding
^^^^^^^^^^^^^^^^^^^^^^^

Each item is a Boolean on whether it is a draw stage (``true``) or not (``false``).

Action
------

This key/value denotes what action(s) can be carried out and what argument(s) is/are acceptable. If an individual action cannot be carried out, the corresponding value is ``null``. Otherwise, it may contain information about what argument(s) is/are expected.

The action-level keys and the corresponding value types are shown below.

============================= ======== ===============================================
Key                           Key Name JavaScript Native Type            
============================= ======== ===============================================
Join                          ``j``    (Array of numbers) or ``null``
Leave                         ``l``    (``true`` literal) or ``null``
Sit out                       ``s``    (``true`` literal) or ``null``
Be back                       ``b``    (``true`` literal) or ``null``
Buy-in/Rebuy/Top-off/Rat-hole ``brtr`` (Array of 2 numbers) or ``null``
Stand pat/Discard             ``sd``   (``true`` literal) or ``null``
Fold                          ``f``    (``true`` literal) or ``null``
Check/Call                    ``cc``   Number or ``null``
Post Bring-in                 ``pb``   Number or ``null``
Complete/Bet/Raise to         ``cbr``  (Array of 2 Booleans and 2 numbers) or ``null``
Show/Muck Hole Cards          ``sm``   Boolean or ``null``
============================= ======== ===============================================

Join
^^^^

This denotes joining (i.e. getting seated). The corresponding value contains possible seat indices (0-indexed) where the user can sit.

Leave
^^^^^

This denotes leaving (i.e. getting up from a seat).

Sit Out
^^^^^^^

This denotes sitting out (i.e. being idle).

Be back
^^^^^^^

This denotes being back (i.e. saying "I'm back").

Buy-In/Rebuy/Top-Off/Rat-Hole
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This denotes overriding the stack size. If not ``null`` (i.e. possible), the 2 numbers in the array represent minimum (inclusive) and maximum (inclusive) override amounts (i.e. an interval).

Stand Pat/Discard
^^^^^^^^^^^^^^^^^

This denotes standing pat or discarding.

Fold
^^^^

This denotes folding.

Check/Call
^^^^^^^^^^

This denotes checking/calling. If the value is ``0``, it is checking. If positive, it is calling with the calling amount specified by that numeric value.

Post Bring-In
^^^^^^^^^^^^^

This denotes bringing-in. The corresponding value, if not ``null``, is the bring-in amount.

Complete/Bet/Raise to
^^^^^^^^^^^^^^^^^^^^^

This denotes completion, betting, or raising. The array is composed of four elements: Boolean, Boolean, Number, and Number. The values represented are as follows:

1. ``true`` if completing else ``false`` (Boolean)
2. ``true`` if raising else ``false`` (Boolean)
3. Minimum amount (number)
4. Maximum amount (number)

Note that if the first 2 elements are ``false``, this action is a betting action.

Show/Muck Hole Cards
^^^^^^^^^^^^^^^^^^^^

This denotes showing or mucking hole cards during showdown. If not ``null``, the value is either ``true`` or ``false``. If ``true``, it means that the player is recommended to show (i.e. no one else yet showed a hand that renders the player's hand unable to win any portion of the pot). If ``false``, it means that there is no point in the player showing as the player, based on the hands shown so far by others, cannot win any portion of the pot.

History
-------

This denotes the hand history of the ongoing hand (if any). If it is not empty (i.e. a hand is ongoing), it is of poker hand history (PHH) file format.

Card
----

==== ======== ======================
Key  Key Name JavaScript Native Type
==== ======== ======================
Rank ``rank`` String
Suit ``suit`` String
==== ======== ======================

Each card are represented with a rank and a suit, each of which is a single-character string. The ranks and suits are represented identically as in the `PHH file format <http://phh.readthedocs.io/>`_.

Custom Fields
-------------

In any values of the PFN JSON object that is of JavaScript object type, new key/values can be added to suit the platform's needs provided that the key name is preceded with an underscore character: ``_``.

Discussion
----------

The PFN format has the potential to serve as a transformational solution to various computational poker applications involving the storage of poker hands.

AI Benchmarking Platform
^^^^^^^^^^^^^^^^^^^^^^^^

This format can be used to aid the development of human-computer interface for interacting with poker AI agents, as it is a common practice to pit poker AI agents against professional human players (`DeepStack <https://doi.org/10.1126/science.aam6960>`_, `Libratus <https://doi.org/10.1126/science.aao1733>`_, and `Pluribus <https://doi.org/10.1126/science.aay2400>`_).

Online Casinos
^^^^^^^^^^^^^^

This standard can be used to communicate the shifting table states between servers and clients. In addition, each PFN entry can be treated as a table snapshot and be leveraged when displaying hand histories.

Conclusion
----------

This page introduces the PFN stnadard, designed to concisely describe poker table states. Our solution fills a long-standing gap in the existing literature on the computer poker field. The specification builds on top of JSON, allowing software systems to leverage the rich ecosystem surrounding it. By representing different table state information through key/value pairs, the hand can be described in a consistent, structured manner.

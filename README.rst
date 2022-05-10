==============
igntpview
==============

Used for biblical TEI files from the INTF and the IGNTP.

Installation
============

Clone the repository and install the dependencies::

    git clone https://github.com/rbturnbull/igntpview.git
    cd igntpview
    poetry install

Enter the virtual environment with::

    poetry shell


XML files
====================

To download XML files from https://itseeweb.cal.bham.ac.uk/epistulae/ run this command::

    igntpview download

If you want the Latin texts, use this command::

    igntpview download --latin    


Usage
=====


Then use the program with::

    igntpview list B06K8V17

Here B06K8V17 is the verse ID for Romans 8:17. I will make this more user-friendly if needed.

If you want to not include Latin run this::

    igntpview list B06K8V17 --no-latin

If you want to not include Greek run this::

    igntpview list B06K8V17 --no-greek

Example
=======

.. image:: docs/igntpview-example.png
  :alt: igntpview example

The blue text is original and text for correctors is in red.

NB. Colours will change to be the same as the IGNTP TEI styling.
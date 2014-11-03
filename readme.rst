pytest-growl
------------
 :Author: Anthony Long
 :Date: 20/10/2014
 :Version: 0.1

This plugin sends growl notifications when your test session begins and ends, along with result counts in a short format.

Optionally it also shows individual errors and opens the failed test in your favorite editor when clicking the message.

.. image:: screenshot.png

The theme displayed in the image is included if you wish to use it.


Installation
____________

Install with pip::

  pip install pytest-growl


Usage
_____

Invoke with the ``--growl`` option. Unfortunately py.test will not accept the option without a value::

  py.test --growl=GROWL


Configuration
_____________

Example ``pytest.ini``::

  [pytest]
  quiet_growl = True
  growl_url = txmt://open/?url=file://{path}&line={lineno}&column=1
  addopts = --individual-growl=1

If ``quiet_growl`` is true no Test Start and Test End notifications will be shown.

The value of ``growl_url`` is an URL that will be called when an individual error notification is clicked. In the example `TextMate <http://macromates.com/>`_ is opened with the caret at the error line. Only used if ``--individual-growl`` is also set. That way a notification is shown for each error.

In the ``pytest.ini`` above ``--individual-growl=1`` is added to py.test's ``addopts`` setting, so it doesn't have to be set on the command line each time.

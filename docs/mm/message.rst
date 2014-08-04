.. _message:

Messages
========
The dyn.mm.message module is where you'll find the ability to easily automate the
sending of messages.

send_message
------------
The :func:`~dyn.mm.message.send_message` function allows a user to quickly fire off
an email via the Message Management API

.. autofunction:: dyn.mm.message.send_message

Using send_message
^^^^^^^^^^^^^^^^^^
Below is just a quick example on how to use :func:`~dyn.mm.message.send_message`::

    >>> from dyn.mm.message import send_message
    >>> from_email = 'user@email.com'
    >>> to_email = 'your@email.com'
    >>> subject = 'A Demo Email'
    >>> content = 'Hello User, thank you for registering at http://mysite.com!'
    >>> send_message(from_email, to_email, subject, body=content)


EMail
-----

.. autoclass:: dyn.mm.message.EMail
    :members:
    :undoc-members:

Using the EMail Base class
^^^^^^^^^^^^^^^^^^^^^^^^^^
The ability to be able to customize your messages become far more apparent with
the use of the :class:`~dyn.mm.message.EMail` class as you can see in the example
below it's very easy to use this class for templating, or even subclassing to make
sending emails quick and easy::

    >>> from dyn.mm.message import EMail
    >>> from_email = 'user@email.com'
    >>> to_email = 'your@email.com'
    >>> subject = 'A Demo Email'
    >>> content = 'Hello %s, thank you for registering at http://mysite.com!'
    >>> mailer = EMail(from_email, to_email, subject)
    >>> user_names = ['Jon', 'Ray', 'Carol', 'Margaret']
    >>> for user_name in user_names:
    ...     mailer.body = content % user_name
    ...     mailer.send()


EMail Subclasses
----------------
Below are some :class:`~dyn.mm.message.EMail` subclasses which provide some additional
formatting and, hopefully, helpful features.

.. autoclass:: dyn.mm.message.HTMLEMail
    :members:
    :undoc-members:

.. autoclass:: dyn.mm.message.TemplateEMail
    :members:
    :undoc-members:

.. autoclass:: dyn.mm.message.HTMLTemplateEMail
    :members:
    :undoc-members:

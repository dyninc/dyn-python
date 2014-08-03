# -*- coding: utf-8 -*-
"""The message module allows for quickly and easily sending emails. For quickly
sending messages consider using the send_message function, however, there is
also the :class:`dyn.mm.message.EMail` class which will give you additional
control over the messages you're sending.
"""
from .errors import DynInvalidArgumentError
from .session import session

__author__ = 'jnappi'


def send_message(from_field, to, subject, cc=None, body=None, html=None,
                 replyto=None, xheaders=None):
    """Create and send an email on the fly. For information on the arguments
    accepted by this function see the documentation for
    :class:`dyn.mm.message.EMail`
    """
    EMail(from_field, to, subject, cc, body, html, replyto, xheaders).send()


class EMail(object):
    """Create an and Send it from one of your approved senders"""
    uri = '/send'

    def __init__(self, from_field, to, subject, cc=None, body=None, html=None,
                 replyto=None, xheaders=None):
        """Create a new :class:`EMail` object

        :param from_field: Sender email address - This can either be an email
            address or a properly formatted from header (example: "From Name"
            <example@email.com>). NOTE: The sender must be one of your account's
            Approved Senders
        :param to: A `list` of Address(es) or a single Address that the email
            will be sent to — This/These can either be an email address or a
            properly formatted from header (example: "To Name"
            <example@email.com>). The To field in the email will contain
            all the addresses when it is sent out and will be sent to all the
            addresses.
        :param subject: The subject of the email being sent
        :param cc: Address(es) to copy the email to - This can either be an
            email address or a properly formatted cc header (example: "cc Name"
            <example@email.com>). For multiple addresses, each address must have
            its own 'cc' field. (example: cc = "example1@email.com", cc =
            "example2@email.com").
        :param body: The plain/text version of the email; this field may be
            encoded in Base64 (recommended), quoted-printable, 8-bit, or 7-bit.
        :param html: The text/html version of the email; this field may be
            encoded in 7-bit, 8-bit, quoted-printable, or base64.
        :param replyto: The email address for the recipient to reply to. If left
            blank, defaults to the from address.
        :param xheaders: Any additional custom X-headers to send in the email -
            Pass the X-header's name as the field name and the X-header's value
            as the value (example: x-demonheader=zoom).
        """
        if body is None and html is None:
            raise DynInvalidArgumentError('body and html', (None, None))
        self.from_field = from_field
        self.to = to
        self.subject = subject
        self.cc = cc
        self.body = body
        self.html = html
        self.replyto = replyto
        self.xheaders = xheaders

    def send(self):
        """Send the content of this :class:`Email` object to the provided list
        of recipients.
        """
        d = self.__dict__
        api_args = {x: d[x] for x in d if d[x] is not None and
                    not hasattr(d[x], '__call__')}
        session().execute(self.uri, 'POST', api_args)

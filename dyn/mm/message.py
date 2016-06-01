# -*- coding: utf-8 -*-
"""The message module allows for quickly and easily sending emails. For quickly
sending messages consider using the send_message function, however, there is
also the :class:`~dyn.mm.message.EMail` class which will give you additional
control over the messages you're sending.
"""
from .errors import DynInvalidArgumentError
from .session import MMSession
from ..core import cleared_class_dict

__all__ = ['send_message', 'EMail', 'HTMLEMail', 'TemplateEMail',
           'HTMLTemplateEMail']
__author__ = 'jnappi'


def send_message(from_field, to, subject, cc=None, body=None, html=None,
                 replyto=None, xheaders=None):
    """Create and send an email on the fly. For information on the arguments
    accepted by this function see the documentation for
    :class:`~dyn.mm.message.EMail`
    """
    EMail(from_field, to, subject, cc, body, html, replyto, xheaders).send()


class EMail(object):
    """Create an and Send it from one of your approved senders"""
    uri = '/send'

    def __init__(self, from_field, to, subject, cc=None, body=None, html=None,
                 replyto=None, xheaders=None):
        """Create a new :class:`~dyn.mm.message.EMail` object

        :param from_field: Sender email address - This can either be an email
            address or a properly formatted from header (example: "From Name"
            <example@email.com>). NOTE: The sender must be one of your
            account's Approved Senders
        :param to: A `list` of Address(es) or a single Address that the email
            will be sent to — This/These can either be an email address or a
            properly formatted from header (example: "To Name"
            <example@email.com>). The To field in the email will contain
            all the addresses when it is sent out and will be sent to all the
            addresses.
        :param subject: The subject of the email being sent
        :param cc: Address(es) to copy the email to - This can either be an
            email address or a properly formatted cc header (example: "cc Name"
            <example@email.com>). For multiple addresses, each address must
            have its own 'cc' field. (example: cc = "example1@email.com", cc =
            "example2@email.com").
        :param body: The plain/text version of the email; this field may be
            encoded in Base64 (recommended), quoted-printable, 8-bit, or 7-bit.
        :param html: The text/html version of the email; this field may be
            encoded in 7-bit, 8-bit, quoted-printable, or base64.
        :param replyto: The email address for the recipient to reply to. If
            left blank, defaults to the from address.
        :param xheaders: Any additional custom X-headers to send in the email -
            Pass the X-header's name as the field name and the X-header's value
            as the value (example: x-demonheader=zoom).
        """
        self.from_field = from_field
        self.to = to
        self.subject = subject
        self.cc = cc
        self.bodytext = body
        self.bodyhtml = html
        self.replyto = replyto
        self.xheaders = xheaders

    def send(self, content=None):
        """Send the content of this :class:`~dyn.mm.message.Email` object to
        the provided list of recipients.

        :param content: The optional content field can be used to overrwrite,
            or to specify the actual content of the body of the message. Note:
            If *content*, this instance's body, and this instance's html fields
            are all *None*, then a
            :class:`~dyn.mm.errors.DynInvalidArgumentError` will be raised.
        """
        if content is None and self.bodytext is None and self.bodyhtml is None:
            raise DynInvalidArgumentError('body and html', (None, None))
        api_args = cleared_class_dict(self.__dict__)
        if content is not None:
            api_args['bodytext'] = content
        from_field = api_args.pop('from_field')
        api_args['from'] = from_field
        MMSession.get_session().execute(self.uri, 'POST', api_args)


class HTMLEMail(EMail):
    """:class:`~dyn.mm.message.EMail` subclass with an overridden send method
    for specifying html content on the fly
    """
    def send(self, content=None):
        """Send the content of this :class:`Email` object to the provided list
        of recipients.

        :param content: The optional content field can be used to overrwrite,
            or to specify the actual content of the html of the message. Note:
            If *content*, this instance's body, and this instance's html
            fields are all *None*, then a
            :class:`~dyn.mm.errors.DynInvalidArgumentError` will be raised.
        """
        if content is None and self.bodytext is None and self.bodyhtml is None:
            raise DynInvalidArgumentError('body and html', (None, None))
        api_args = cleared_class_dict(self.__dict__)
        if content is not None:
            api_args['bodyhtml'] = content
        from_field = api_args.pop('from_field')
        api_args['from'] = from_field
        MMSession.get_session().execute(self.uri, 'POST', api_args)


class TemplateEMail(EMail):
    """:class:`~dyn.mm.message.EMail` subclass which treats it's bodytext
    attribute as a template. Allowing you to send out chains of emails by
    only writing the templated email once, and then specifying an iterable with
    the formatting content at send time.
    """
    def send(self, formatters=None):
        """Send the content of this :class:`~dyn.mm.message.Email` object to
        the provided list of recipients.

        :param formatters: Any iterable containing the data you wish inserted
            into your template. Unlike in the :class:`~dyn.mm.message.EMail`
            class this field is not optional and will raise a
            :class:`~dyn.mm.errors.DynInvalidArgumentError` if not provided.
            This exception will also be raised if this instances bodytext
            attribute has not also been set.
        """
        if formatters is None:
            raise DynInvalidArgumentError('send content', None)

        if self.bodytext is None:
            raise DynInvalidArgumentError('body', None)

        for formatter in formatters:
            super(TemplateEMail, self).send(self.bodytext % formatter)


class HTMLTemplateEMail(HTMLEMail):
    """Similar to the :class:`~dyn.mm.message.TemplateEMail` class the
    :class:`~dyn.mm.message.HTMLEMail` subclass which treats it's bodyhtml
    attribute as a template. Allowing you to send out chains of emails by
    only writing the templated html email once, and then specifying an iterable
    with the formatting content at send time.
    """
    def send(self, formatters=None):
        """Send the content of this :class:`~dyn.mm.message.Email` object to
        the provided list of recipients.

        :param formatters: Any iterable containing the data you wish inserted
            into your html template. Unlike in the
            :class:`~dyn.mm.message.HTMLEMail` class this field is not optional
            and will raise a
            :class:`~dyn.mm.errors.DynInvalidArgumentError` if not provided.
            This exception will also be raised if this instances bodyhtml
            attribute has not also been set.
        """
        if formatters is None:
            raise DynInvalidArgumentError('send content', None)

        if self.bodyhtml is None:
            raise DynInvalidArgumentError('html', None)

        for formatter in formatters:
            super(HTMLTemplateEMail, self).send(self.bodyhtml % formatter)

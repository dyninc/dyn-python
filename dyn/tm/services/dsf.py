# -*- coding: utf-8 -*-
"""This module contains wrappers for interfacing with every element of a
Traffic Director (DSF) service.
"""
from collections import Iterable
from dyn.compat import force_unicode, string_types
from dyn.tm.utils import APIList, Active
from dyn.tm.errors import DynectInvalidArgumentError
from dyn.tm.records import (ARecord, AAAARecord, ALIASRecord, CDSRecord,
                            CDNSKEYRecord, CSYNCRecord, CERTRecord,
                            CNAMERecord, DHCIDRecord, DNAMERecord,
                            DNSKEYRecord, DSRecord, KEYRecord, KXRecord,
                            LOCRecord, IPSECKEYRecord, MXRecord, NAPTRRecord,
                            PTRRecord, PXRecord, NSAPRecord, RPRecord,
                            NSRecord, SOARecord, SPFRecord, SRVRecord,
                            TLSARecord, TXTRecord, SSHFPRecord, UNKNOWNRecord)
from dyn.tm.session import DynectSession
from dyn.tm.accounts import Notifier

__author__ = 'jnappi'
__all__ = ['get_all_dsf_services', 'get_all_record_sets',
           'get_all_failover_chains', 'get_all_response_pools',
           'get_all_rulesets', 'get_all_dsf_monitors', 'get_all_records',
           'get_all_notifiers', 'DSFARecord', 'DSFSSHFPRecord', 'get_record',
           'get_record_set', 'get_failover_chain', 'get_response_pool',
           'get_ruleset', 'get_dsf_monitor', 'DSFNotifier', 'DSFAAAARecord',
           'DSFALIASRecord', 'DSFCERTRecord', 'DSFCNAMERecord',
           'DSFDHCIDRecord', 'DSFDNAMERecord', 'DSFDNSKEYRecord',
           'DSFDSRecord', 'DSFKEYRecord', 'DSFKXRecord', 'DSFLOCRecord',
           'DSFIPSECKEYRecord', 'DSFMXRecord', 'DSFNAPTRRecord',
           'DSFPTRRecord', 'DSFPXRecord', 'DSFNSAPRecord', 'DSFRPRecord',
           'DSFNSRecord', 'DSFSPFRecord', 'DSFSRVRecord', 'DSFTXTRecord',
           'DSFRecordSet', 'DSFFailoverChain', 'DSFResponsePool',
           'DSFRuleset', 'DSFMonitorEndpoint', 'DSFMonitor', 'DSFNode',
           'TrafficDirector']


def get_all_dsf_services():
    """:return: A ``list`` of :class:`TrafficDirector` Services"""
    uri = '/DSF/'
    api_args = {'detail': 'Y'}
    response = DynectSession.get_session().execute(uri, 'GET', api_args)
    directors = []
    for dsf in response['data']:
        directors.append(TrafficDirector(None, api=False, **dsf))
    return directors


def get_all_notifiers():
    """:return: A ``list`` of :class:`DSFNotifier` Services"""
    uri = '/Notifier/'
    api_args = {'detail': 'Y'}
    response = DynectSession.get_session().execute(uri, 'GET', api_args)
    notifiers = []
    for notify in response['data']:
        notifiers.append(DSFNotifier(None, api=False, **notify))
    return notifiers


def get_all_records(service):
    """
    :param service: a dsf_id string, or :class:`TrafficDirector`
    :return: A ``list`` of :class:`DSFRecord`s from the passed in `service`
    Warning! This query may take a long time to run with services with many
    records!
    """
    _service_id = _check_type(service)
    uri = '/DSFRecord/{}/'.format(_service_id)
    api_args = {'detail': 'Y'}
    response = DynectSession.get_session().execute(uri, 'GET', api_args)
    record_ids = [record['dsf_record_id'] for record in response['data']]
    records = list()
    for record_id in record_ids:
        uri = '/DSFRecord/{}/{}'.format(_service_id, record_id)
        response = DynectSession.get_session().execute(uri, 'GET', api_args)
        records += _constructor(response['data'])
    return records


def get_all_record_sets(service):
    """:param service: a dsf_id string, or :class:`TrafficDirector`
    :return: A ``list`` of :class:`DSFRecordSets` from the passed in `service`
    """
    _service_id = _check_type(service)
    uri = '/DSFRecordSet/{}/'.format(_service_id)
    api_args = {'detail': 'Y'}
    response = DynectSession.get_session().execute(uri, 'GET', api_args)
    recordSets = list()
    for pool in response['data']:
        recordSets.append(
            DSFRecordSet(pool.pop('rdata_class'), api=False, **pool))
    return recordSets


def get_all_failover_chains(service):
    """:param service: a dsf_id string, or :class:`TrafficDirector`
    :return: A ``list`` of :class:`DSFFailoverChains` from the passed in
    `service`
    """
    _service_id = _check_type(service)
    uri = '/DSFRecordSetFailoverChain/{}/'.format(_service_id)
    api_args = {'detail': 'Y'}
    response = DynectSession.get_session().execute(uri, 'GET', api_args)
    failoverChains = list()
    for pool in response['data']:
        failoverChains.append(
            DSFFailoverChain(pool.pop('label'), api=False, **pool))
    return failoverChains


def get_all_response_pools(service):
    """:param service: a dsf_id string, or :class:`TrafficDirector`
    :return: A ``list`` of :class:`DSFResponsePools` from the passed in
    `service`
    """
    _service_id = _check_type(service)
    uri = '/DSFResponsePool/{}/'.format(_service_id)
    api_args = {'detail': 'Y'}
    response = DynectSession.get_session().execute(uri, 'GET', api_args)
    responsePools = list()
    for pool in response['data']:
        responsePools.append(
            DSFResponsePool(pool.pop('label'), api=False, **pool))
    return responsePools


def get_all_rulesets(service):
    """:param service: a dsf_id string, or :class:`TrafficDirector`
    :return: A ``list`` of :class:`DSFRulesets` from the passed in `service`
    """
    _service_id = _check_type(service)
    uri = '/DSFRuleset/{}/'.format(_service_id)
    api_args = {'detail': 'Y'}
    response = DynectSession.get_session().execute(uri, 'GET', api_args)
    ruleset = list()
    for rule in response['data']:
        ruleset.append(DSFRuleset(rule.pop('label'), api=False, **rule))
    return ruleset


def get_all_dsf_monitors():
    """:return: A ``list`` of :class:`DSFMonitor` Services"""
    uri = '/DSFMonitor/'
    api_args = {'detail': 'Y'}
    response = DynectSession.get_session().execute(uri, 'GET', api_args)
    mons = []
    for dsf in response['data']:
        mons.append(DSFMonitor(api=False, **dsf))
    return mons


def get_record(record_id, service, always_list=False):
    """
    returns :class:`DSFRecord`
    :param record_id: id of record you wish to pull up
    :param service: id of service which this record belongs. Can either be
     the service_id or a :class:`TrafficDirector` Object
    :param always_list: Force the returned record to always be in a list.
    :return returns single record, unless this is a special record type, then
    a list is returned
    """
    _service_id = _check_type(service)
    uri = '/DSFRecord/{}/{}'.format(_service_id, record_id)
    api_args = {'detail': 'Y'}
    response = DynectSession.get_session().execute(uri, 'GET', api_args)
    record = _constructor(response['data'])
    if len(record) > 1 or always_list:
        return record
    else:
        return record[0]


def get_record_set(record_set_id, service):
    """
    returns :class:`DSFRecordSet`
    :param record_set_id: id of record set you wish to pull up
    :param service: id of service which this record belongs. Can either be
     the service_id or a :class:`TrafficDirector` Object
    :return returns :class:`DSFRecordSet` Object
    """
    _service_id = _check_type(service)
    uri = '/DSFRecordSet/{}/{}'.format(_service_id, record_set_id)
    api_args = {'detail': 'Y'}
    response = DynectSession.get_session().execute(uri, 'GET', api_args)
    return DSFRecordSet(response['data'].pop('rdata_class'), api=False,
                        **response['data'])


def get_failover_chain(failover_chain_id, service):
    """
    returns :class:`DSFFailoverChain`
    :param failover_chain_id: id of :class:`DSFFailoverChain` you wish to pull
        up
    :param service: id of service which this record belongs. Can either be
     the service_id or a :class:`TrafficDirector` Object
    :return returns :class:`DSFFailoverChain` Object
    """
    _service_id = _check_type(service)
    uri = '/DSFRecordSetFailoverChain/{}/{}'.format(_service_id,
                                                    failover_chain_id)
    api_args = {'detail': 'Y'}
    response = DynectSession.get_session().execute(uri, 'GET', api_args)
    return DSFFailoverChain(response['data'].pop('label'), api=False,
                            **response['data'])


def get_response_pool(response_pool_id, service):
    """
    returns :class:`DSFResponsePool`
    :param response_pool_id: id of :class:`DSFResponsePool` you wish to pull up
    :param service: id of service which this record belongs. Can either be
     the service_id or a :class:`TrafficDirector` Object
    :return returns :class:`DSFResponsePool` Object
    """
    _service_id = _check_type(service)
    uri = '/DSFResponsePool/{}/{}'.format(_service_id, response_pool_id)
    api_args = {'detail': 'Y'}
    response = DynectSession.get_session().execute(uri, 'GET', api_args)
    return DSFResponsePool(response['data'].pop('label'), api=False,
                           **response['data'])


def get_ruleset(ruleset_id, service):
    """
    returns :class:`DSFRuleset`
    :param ruleset_id: id of :class:`DSFRuleset` you wish to pull up
    :param service: id of service which this record belongs. Can either be
     the service_id or a :class:`TrafficDirector` Object
    :return returns :class:`DSFRuleset` Object
    """
    _service_id = _check_type(service)
    uri = '/DSFRuleset/{}/{}'.format(_service_id, ruleset_id)
    api_args = {'detail': 'Y'}
    response = DynectSession.get_session().execute(uri, 'GET', api_args)
    return DSFRuleset(response['data'].pop('label'), api=False,
                      **response['data'])


def get_dsf_monitor(monitor_id):
    """ A quick :class:`DSFmonitor` getter, for consistency sake.
    :param monitor_id: id of :class:`DSFmonitor` you wish to pull up
    :return returns :class:`DSFmonitor` Object"""
    uri = '/DSFMonitor/{}'.format(monitor_id)
    api_args = {'detail': 'Y'}
    response = DynectSession.get_session().execute(uri, 'GET', api_args)
    return DSFMonitor(api=False, **response['data'])


def _check_type(service):
    if isinstance(service, TrafficDirector):
        _service_id = service.service_id
    elif isinstance(service, string_types):
        _service_id = service
    else:
        raise Exception('Value must be string, or TrafficDirector Object')
    return _service_id


def _constructor(record):
    return_records = []
    constructors = {'a': DSFARecord, 'aaaa': DSFAAAARecord,
                    'alias': DSFALIASRecord, 'cert': DSFCERTRecord,
                    'cname': DSFCNAMERecord, 'dhcid': DSFDHCIDRecord,
                    'dname': DSFDNAMERecord,
                    'dnskey': DSFDNSKEYRecord, 'ds': DSFDSRecord,
                    'key': DSFKEYRecord, 'kx': DSFKXRecord,
                    'loc': DSFLOCRecord,
                    'ipseckey': DSFIPSECKEYRecord,
                    'mx': DSFMXRecord, 'naptr': DSFNAPTRRecord,
                    'ptr': DSFPTRRecord, 'px': DSFPXRecord,
                    'nsap': DSFNSAPRecord, 'rp': DSFRPRecord,
                    'ns': DSFNSRecord, 'spf': DSFSPFRecord,
                    'srv': DSFSRVRecord, 'txt': DSFTXTRecord,
                    'sshfp': DSFSSHFPRecord}
    rec_type = record['rdata_class'].lower()
    constructor = constructors[rec_type]
    rdata_key = 'rdata_{}'.format(rec_type)
    kws = ('ttl', 'label', 'weight', 'automation', 'endpoints',
           'endpoint_up_count', 'eligible', 'dsf_record_id',
           'dsf_record_set_id', 'status', 'torpidity', 'service_id')
    for data in record['rdata']:
        record_data = data['data'][rdata_key]
        for kw in kws:
            record_data[kw] = record[kw]
        if constructor is DSFSRVRecord:
            record_data['rr_weight'] = record_data.pop('weight')

        return_records.append(constructor(**record_data))
    return return_records


class _DSFRecord(object):
    """Super Class for DSF Records."""

    def __init__(self, label=None, weight=1, automation='auto', endpoints=None,
                 endpoint_up_count=None, eligible=True, **kwargs):
        """Create a :class:`_DSFRecord` object.

        :param label: A unique label for this :class:`DSFRecord`
        :param weight: Weight for this :class:`DSFRecord`
        :param automation: Defines how eligible can be changed in response to
            monitoring. Must be one of 'auto', 'auto_down', or 'manual'
        :param endpoints: Endpoints are used to determine status, torpidity,
            and eligible in response to monitor data
        :param endpoint_up_count: Number of endpoints that must be up for the
            Record status to be 'up'
        :param eligible: Indicates whether or not the Record can be served
        """
        self.valid_automation = ('auto', 'auto_down', 'manual')
        self._label = label
        self._weight = weight
        if automation not in self.valid_automation:
            raise DynectInvalidArgumentError('automation', automation,
                                             self.valid_automation)
        self._automation = automation
        self._endpoints = endpoints
        self._endpoint_up_count = endpoint_up_count
        self._eligible = eligible
        self._service_id = self._dsf_record_set_id = self.uri = None
        self._dsf_record_id = self._status = self._note = None
        self._implicitPublish = True
        for key, val in kwargs.items():
            setattr(self, '_' + key, val)

    def _post(self, dsf_id, record_set_id, publish=True, notes=None):
        """Create a new :class:`DSFRecord` on the DynECT System

        :param dsf_id: The unique system id for the DSF service associated with
            this :class:`DSFRecord`
        :param record_set_id: The unique system id for the record set
            associated with this :class:`DSFRecord`
        """
        self._service_id = dsf_id
        self._record_set_id = record_set_id
        self.uri = '/DSFRecord/{}/{}/'.format(self._service_id,
                                              self._record_set_id)
        api_args = {}
        api_args = self.to_json(skip_svc=True)
        if publish:
            api_args['publish'] = 'Y'
        if notes:
            api_args['notes'] = notes
        response = DynectSession.get_session().execute(self.uri, 'POST',
                                                       api_args)
        self._build(response['data'])

    def _get(self, dsf_id, dsf_record_id):
        """Get an existing :class:`DSFRecord` from the DynECT System

        :param dsf_id: The unique system id for the DSF service associated with
            this :class:`DSFRecord`
        :param dsf_record_id: The unique system id for the record set
            associated with this :class:`DSFRecord`
        """
        self._service_id = dsf_id
        self._dsf_record_id = dsf_record_id
        self.uri = '/DSFRecord/{}/{}/'.format(self._service_id,
                                              self._dsf_record_id)
        api_args = {}
        response = DynectSession.get_session().execute(self.uri, 'GET',
                                                       api_args)
        self._build(response['data'])

    def _update_record(self, api_args, publish=True):
        """Make the API call to update the current record type

        :param api_args: arguments to be pased to the API call
        """
        record_rdata = '{}_rdata'.format(
            self._record_type.replace('Record', '').replace('DSF', '').lower())
        new_api_args = {'rdata': {record_rdata: api_args['rdata']}}

        if not self._record_type.endswith('Record'):
            self._record_type += 'Record'
        if publish and self._implicitPublish:
            new_api_args['publish'] = 'Y'
        if self._note:
            new_api_args['notes'] = self._note
        self.uri = 'DSFRecord/{}/{}'.format(self._service_id,
                                            self._dsf_record_id)
        response = DynectSession.get_session().execute(self.uri, 'PUT',
                                                       new_api_args)
        self._build(response['data'])
        # We hose the note if a publish was requested
        if new_api_args.get('publish') == 'Y':
            self._note = None

    def _update(self, api_args, publish=True):
        """API call to update non superclass record type parameters
        :param api_args: arguments to be pased to the API call
        """
        if publish and self._implicitPublish:
            api_args['publish'] = 'Y'
        if self._note:
            api_args['notes'] = self._note
        self.uri = 'DSFRecord/{}/{}'.format(self._service_id,
                                            self._dsf_record_id)
        response = DynectSession.get_session().execute(self.uri, 'PUT',
                                                       api_args)
        self._build(response['data'])
        # We hose the note if a publish was requested
        if api_args.get('publish') == 'Y':
            self._note = None

    def _build(self, data):
        """Private build method

        :param data: API Response data
        """
        for key, val in data.items():
            if key == 'rdata':
                for rdata in val:
                    if isinstance(rdata, dict):
                        for rdatas, rdata_data in rdata.items():
                            # necessary due to unicode!
                            try:
                                for rtype, rdata_v in rdata_data.items():
                                    if rtype == 'rdata_{}'.format(
                                            self._rdata_class.lower()):
                                        for k, v in rdata_v.items():
                                            setattr(self, '_' + k, v)
                            except:
                                pass
            else:
                setattr(self, '_' + key, val)

    def publish(self, notes=None):
        """Publish changes to :class:`TrafficDirector`.
        :param notes: Optional Note that will be added to the
        zone notes of zones attached to this service.
        """
        uri = '/DSF/{}/'.format(self._service_id)
        api_args = {'publish': 'Y'}
        if self._note:
            api_args['notes'] = self._note
            self._note = None
        # if notes are passed in, we override.
        if notes:
            api_args['notes'] = notes
        DynectSession.get_session().execute(uri, 'PUT', api_args)
        self.refresh()

    @property
    def publish_note(self):
        """Returns Current Publish Note, which will be used on the next
        publish action"""
        return self._note

    @publish_note.setter
    def publish_note(self, note):
        """Adds this note to the next action which also performs a publish
        """
        self._note = note

    def refresh(self):
        """Pulls data down from Dynect System and repopulates
        :class:`DSFRecord`
        """
        self._get(self._service_id, self._dsf_record_id)

    def add_to_record_set(self, record_set, service=None,
                          publish=True, notes=None):
        """Creates and links this :class:`DSFRecord` to passed in
        :class:`DSFRecordSet` Object

        :param record_set: Can either be the _dsf_record_set_id or a
            :class:`DSFRecordSet` Object.
        :param service: Only necessary if record_set is passed in as a string.
            This can be a :class:`TrafficDirector` Object. or the _service_id
        :param publish: Publish on execution (Default = True)
        :param notes: Optional Zone publish Notes
        """
        if self._dsf_record_id:
            raise Exception('The record already exists in the system!')

        if isinstance(record_set, DSFRecordSet):
            _record_set_id = record_set._dsf_record_set_id
            _service_id = record_set._service_id
        elif isinstance(record_set, string_types):
            if service is None:
                msg = ('When record_set as a string, you must provide the '
                       'service_id as service=')
                raise Exception(msg)
            _record_set_id = record_set
        else:
            raise Exception('Could not make sense of Record Set Type')
        if service:
            _service_id = _check_type(service)
        self._post(_service_id, _record_set_id, publish=True,
                   notes=notes)

    @property
    def dsf_id(self):
        """The unique system id of the :class:`TrafficDirector` This
        :class:`DSFRecord` is attached to
        """
        return self._service_id

    @property
    def record_id(self):
        """The unique system id for this :class:`DSFRecord`
        """
        return self._dsf_record_id

    @property
    def record_set_id(self):
        """The unique system id of the :class:`DSFRecordSet` This
        :class:`DSFRecord` is attached to
        """
        return self._record_set_id

    @property
    def label(self):
        """A unique label for this :class:`DSFRecord`"""
        return self._label

    @label.setter
    def label(self, value):
        api_args = {'label': value}
        self._update(api_args)
        if self._implicitPublish:
            self._label = value

    @property
    def weight(self):
        """Weight for this :class:`DSFRecord`"""
        return self._weight

    @weight.setter
    def weight(self, value):
        api_args = {'weight': value}
        self._update(api_args)
        if self._implicitPublish:
            self._weight = value

    @property
    def automation(self):
        """Defines how eligiblity can be changed in response to monitoring.
        Must be one of 'auto', 'auto_down', or 'manual'
        """
        return self._automation

    @automation.setter
    def automation(self, value):
        api_args = {'automation': value}
        self._update(api_args)
        if self._implicitPublish:
            self._automation = value

    @property
    def endpoints(self):
        """Endpoints are used to determine status, torpidity, and eligible in
        response to monitor data
        """
        return self._endpoints

    @endpoints.setter
    def endpoints(self, value):
        api_args = {'endpoints': value}
        self._update(api_args)
        if self._implicitPublish:
            self._endpoints = value

    @property
    def endpoint_up_count(self):
        """Number of endpoints that must be up for the Record status to be 'up'
        """
        return self._endpoint_up_count

    @endpoint_up_count.setter
    def endpoint_up_count(self, value):
        api_args = {'endpoint_up_count': value}
        self._update(api_args)
        if self._implicitPublish:
            self._endpoint_up_count = value

    @property
    def eligible(self):
        """Indicates whether or not the Record can be served"""
        return self._eligible

    @eligible.setter
    def eligible(self, value):
        api_args = {'eligible': value}
        self._update(api_args)
        if self._implicitPublish:
            self._eligible = value

    @property
    def status(self):
        """Status of Record"""
        self.refresh()
        return self._status

    def to_json(self, svc_id=None, skip_svc=False):
        """Convert this DSFRecord to a json blob"""

        if self._service_id and not svc_id:
            svc_id = self._service_id

        json = {'label': self._label, 'weight': self._weight,
                'automation': self._automation, 'endpoints': self._endpoints,
                'eligible': self._eligible,
                'endpoint_up_count': self._endpoint_up_count}

        json_blob = {x: json[x] for x in json if json[x] is not None}
        if hasattr(self, '_record_type'):
            rdata = self.rdata()
            outer_key = list(rdata.keys())[0]
            inner_data = rdata[outer_key]
            real_data = {x: inner_data[x] for x in inner_data
                         if x not in json_blob and x not in self.__dict__ and
                         x[1:] not in self.__dict__ and
                         inner_data[x] is not None and x != 'record_set_id' and
                         x != 'service_id' and x != 'implicitPublish'}
            json_blob['rdata'] = {outer_key: real_data}
        if svc_id and not skip_svc:
            json_blob['service_id'] = svc_id

        return json_blob

    @property
    def implicit_publish(self):
        """Toggle for this specific :class:`DSFRecord` for turning on and off
        implicit Publishing for record Updates."""
        return self._implicitPublish

    @implicit_publish.setter
    def implicit_publish(self, value):
        if not isinstance(value, bool):
            raise Exception('Value must be True or False')
        self._implicitPublish = value

    implicitPublish = implicit_publish  # NOQA

    def delete(self, notes=None):
        """Delete this :class:`DSFRecord`
        :param notes: Optional zone publish notes
        """
        api_args = {'publish': 'Y'}
        if notes:
            api_args['notes'] = notes
        uri = '/DSFRecord/{}/{}'.format(self._service_id, self._dsf_record_id)
        DynectSession.get_session().execute(uri, 'DELETE', api_args)


class DSFARecord(_DSFRecord, ARecord):
    """An :class:`ARecord` object which is able to store additional data for
    use by a :class:`TrafficDirector` service.
    """

    def __init__(self, address, ttl=0, label=None, weight=1, automation='auto',
                 endpoints=None, endpoint_up_count=None, eligible=True,
                 **kwargs):
        """Create a :class:`DSFARecord` object

        :param address: IPv4 address for the record
        :param ttl: TTL for this record
        :param label: A unique label for this :class:`DSFARecord`
        :param weight: Weight for this :class:`DSFARecord`
        :param automation: Defines how eligible can be changed in response to
            monitoring. Must be one of 'auto', 'auto_down', or 'manual'
        :param endpoints: Endpoints are used to determine status, torpidity,
            and eligible in response to monitor data
        :param endpoint_up_count: Number of endpoints that must be up for the
            Record status to be 'up'
        :param eligible: Indicates whether or not the Record can be served
        """
        ARecord.__init__(self, None, None, address=address, ttl=ttl,
                         create=False)
        _DSFRecord.__init__(self, label, weight, automation, endpoints,
                            endpoint_up_count, eligible, **kwargs)
        self._record_type = 'DSFARecord'


class DSFAAAARecord(_DSFRecord, AAAARecord):
    """An :class:`AAAARecord` object which is able to store additional data for
    use by a :class:`TrafficDirector` service.
    """

    def __init__(self, address, ttl=0, label=None, weight=1, automation='auto',
                 endpoints=None, endpoint_up_count=None, eligible=True,
                 **kwargs):
        """Create a :class:`DSFAAAARecord` object

        :param address: IPv6 address for the record
        :param ttl: TTL for this record
        :param label: A unique label for this :class:`DSFAAAARecord`
        :param weight: Weight for this :class:`DSFAAAARecord`
        :param automation: Defines how eligible can be changed in response to
            monitoring. Must be one of 'auto', 'auto_down', or 'manual'
        :param endpoints: Endpoints are used to determine status, torpidity,
            and eligible in response to monitor data
        :param endpoint_up_count: Number of endpoints that must be up for the
            Record status to be 'up'
        :param eligible: Indicates whether or not the Record can be served
        """
        AAAARecord.__init__(self, None, None, address=address, ttl=ttl,
                            create=False)
        _DSFRecord.__init__(self, label, weight, automation, endpoints,
                            endpoint_up_count, eligible, **kwargs)
        self._record_type = 'DSFAAAARecord'


class DSFALIASRecord(_DSFRecord, ALIASRecord):
    """An :class:`AliasRecord` object which is able to store additional data
    for use by a :class:`TrafficDirector` service.
    """

    def __init__(self, alias, ttl=0, label=None, weight=1, automation='auto',
                 endpoints=None, endpoint_up_count=None, eligible=True,
                 **kwargs):
        """Create a :class:`DSFALIASRecord` object

        :param alias: alias target name
        :param ttl: TTL for this record
        :param label: A unique label for this :class:`DSFALIASRecord`
        :param weight: Weight for this :class:`DSFALIASRecord`
        :param automation: Defines how eligible can be changed in response to
            monitoring. Must be one of 'auto', 'auto_down', or 'manual'
        :param endpoints: Endpoints are used to determine status, torpidity,
            and eligible in response to monitor data
        :param endpoint_up_count: Number of endpoints that must be up for the
            Record status to be 'up'
        :param eligible: Indicates whether or not the Record can be served
        """
        ALIASRecord.__init__(self, None, None, alias=alias, ttl=ttl,
                             create=False)
        _DSFRecord.__init__(self, label, weight, automation, endpoints,
                            endpoint_up_count, eligible, **kwargs)
        self._record_type = 'DSFALIASRecord'


class DSFCERTRecord(_DSFRecord, CERTRecord):
    """An :class:`CERTRecord` object which is able to store additional data for
    use by a :class:`TrafficDirector` service.
    """

    def __init__(self, format, tag, algorithm, certificate, ttl=0, label=None,
                 weight=1, automation='auto', endpoints=None,
                 endpoint_up_count=None, eligible=True, **kwargs):
        """Create a :class:`DSFCERTRecord` object

        :param format: Numeric value for the certificate type
        :param tag: Numeric value for the public key certificate
        :param algorithm: Public key algorithm number used to generate the
            certificate
        :param certificate: The public key certificate
        :param ttl: TTL for this record
        :param label: A unique label for this :class:`DSFCERTRecord`
        :param weight: Weight for this :class:`DSFCERTRecord`
        :param automation: Defines how eligible can be changed in response to
            monitoring. Must be one of 'auto', 'auto_down', or 'manual'
        :param endpoints: Endpoints are used to determine status, torpidity,
            and eligible in response to monitor data
        :param endpoint_up_count: Number of endpoints that must be up for the
            Record status to be 'up'
        :param eligible: Indicates whether or not the Record can be served
        """
        CERTRecord.__init__(self, None, None, format=format, tag=tag,
                            algorithm=algorithm, certificate=certificate,
                            ttl=ttl, create=False)
        _DSFRecord.__init__(self, label, weight, automation, endpoints,
                            endpoint_up_count, eligible, **kwargs)
        self._record_type = 'DSFCERTRecord'

    def _update_record(self, api_args, publish=True):
        """Make the API call to update the current record type

        :param api_args: arguments to be pased to the API call
        """
        keys = ['format', 'tag', 'algorithm', 'certificate']
        self.refresh()
        for key in keys:
            if key not in api_args:
                api_args['rdata'][key] = getattr(self, key)

        super(DSFCERTRecord, self)._update_record(api_args, publish=publish)


class DSFCNAMERecord(_DSFRecord, CNAMERecord):
    """An :class:`CNAMERecord` object which is able to store additional data
    for use by a :class:`TrafficDirector` service.
    """

    def __init__(self, cname, ttl=0, label=None, weight=1, automation='auto',
                 endpoints=None, endpoint_up_count=None, eligible=True,
                 **kwargs):
        """Create a :class:`DSFCNAMERecord` object

        :param cname: Hostname
        :param ttl: TTL for this record
        :param label: A unique label for this :class:`DSFCNAMERecord`
        :param weight: Weight for this :class:`DSFCNAMERecord`
        :param automation: Defines how eligible can be changed in response to
            monitoring. Must be one of 'auto', 'auto_down', or 'manual'
        :param endpoints: Endpoints are used to determine status, torpidity,
            and eligible in response to monitor data
        :param endpoint_up_count: Number of endpoints that must be up for the
            Record status to be 'up'
        :param eligible: Indicates whether or not the Record can be served
        """
        CNAMERecord.__init__(self, None, None, cname=cname, ttl=ttl,
                             create=False)
        _DSFRecord.__init__(self, label, weight, automation, endpoints,
                            endpoint_up_count, eligible, **kwargs)
        self._record_type = 'DSFCNAMERecord'


class DSFDHCIDRecord(_DSFRecord, DHCIDRecord):
    """An :class:`DHCIDRecord` object which is able to store additional data
    for use by a :class:`TrafficDirector` service.
    """

    def __init__(self, digest, ttl=0, label=None, weight=1, automation='auto',
                 endpoints=None, endpoint_up_count=None, eligible=True,
                 **kwargs):
        """Create a :class:`DSFDHCIDRecord` object

        :param digest: Base-64 encoded digest of DHCP data
        :param ttl: TTL for this record
        :param label: A unique label for this :class:`DSFDHCIDRecord`
        :param weight: Weight for this :class:`DSFDHCIDRecord`
        :param automation: Defines how eligible can be changed in response to
            monitoring. Must be one of 'auto', 'auto_down', or 'manual'
        :param endpoints: Endpoints are used to determine status, torpidity,
            and eligible in response to monitor data
        :param endpoint_up_count: Number of endpoints that must be up for the
            Record status to be 'up'
        :param eligible: Indicates whether or not the Record can be served
        """
        DHCIDRecord.__init__(self, None, None, digest=digest, ttl=ttl,
                             create=False)
        _DSFRecord.__init__(self, label, weight, automation, endpoints,
                            endpoint_up_count, eligible, **kwargs)
        self._record_type = 'DSFDHCIDRecord'


class DSFDNAMERecord(_DSFRecord, DNAMERecord):
    """An :class:`DNAMERecord` object which is able to store additional data
    for use by a :class:`TrafficDirector` service.
    """

    def __init__(self, dname, ttl=0, label=None, weight=1, automation='auto',
                 endpoints=None, endpoint_up_count=None, eligible=True,
                 **kwargs):
        """Create a :class:`DSFDNAMERecord` object

        :param dname: Target Hostname
        :param ttl: TTL for this record
        :param label: A unique label for this :class:`DSFDNAMERecord`
        :param weight: Weight for this :class:`DSFDNAMERecord`
        :param automation: Defines how eligible can be changed in response to
            monitoring. Must be one of 'auto', 'auto_down', or 'manual'
        :param endpoints: Endpoints are used to determine status, torpidity,
            and eligible in response to monitor data
        :param endpoint_up_count: Number of endpoints that must be up for the
            Record status to be 'up'
        :param eligible: Indicates whether or not the Record can be served
        """
        DNAMERecord.__init__(self, None, None, dname=dname, ttl=ttl,
                             create=False)
        _DSFRecord.__init__(self, label, weight, automation, endpoints,
                            endpoint_up_count, eligible, **kwargs)
        self._record_type = 'DSFDNAMERecord'


class DSFDNSKEYRecord(_DSFRecord, DNSKEYRecord):
    """An :class:`DNSKEYRecord` object which is able to store additional data
    for use by a :class:`TrafficDirector` service.
    """

    def __init__(self, protocol, public_key, algorithm=5, flags=256, ttl=0,
                 label=None, weight=1, automation='auto', endpoints=None,
                 endpoint_up_count=None, eligible=True, **kwargs):
        """Create a :class:`DSFDNSKEYRecord` object

        :param protocol: Numeric value for protocol
        :param public_key: The public key for the DNSSEC signed zone
        :param algorithm: Numeric value representing the public key encryption
            algorithm which will sign the zone. Must be one of 1 (RSA-MD5), 2
            (Diffie-Hellman), 3 (DSA/SHA-1), 4 (Elliptic Curve), or
            5 (RSA-SHA-1)
        :param flags: Numeric value confirming this is the zone's DNSKEY
        :param ttl: TTL for this record
        :param label: A unique label for this :class:`DSFDNSKEYRecord`
        :param weight: Weight for this :class:`DSFDNSKEYRecord`
        :param automation: Defines how eligible can be changed in response to
            monitoring. Must be one of 'auto', 'auto_down', or 'manual'
        :param endpoints: Endpoints are used to determine status, torpidity,
            and eligible in response to monitor data
        :param endpoint_up_count: Number of endpoints that must be up for the
            Record status to be 'up'
        :param eligible: Indicates whether or not the Record can be served
        """
        DNSKEYRecord.__init__(self, None, None, protocol=protocol,
                              public_key=public_key, algorithm=algorithm,
                              flags=flags, ttl=ttl, create=False)
        _DSFRecord.__init__(self, label, weight, automation, endpoints,
                            endpoint_up_count, eligible, **kwargs)
        self._record_type = 'DSFDNSKEYRecord'

    def _update_record(self, api_args, publish=True):
        """Make the API call to update the current record type

        :param api_args: arguments to be pased to the API call
        """
        keys = ['flags', 'algorithm', 'protocol', 'public_key']
        self.refresh()
        for key in keys:
            if key not in api_args:
                api_args['rdata'][key] = getattr(self, key)

        super(DSFDNSKEYRecord, self)._update_record(api_args, publish=publish)


class DSFDSRecord(_DSFRecord, DSRecord):
    """An :class:`DSRecord` object which is able to store additional data for
    use by a :class:`TrafficDirector` service.
    """

    def __init__(self, digest, keytag, algorithm=5, digtype=1, ttl=0,
                 label=None, weight=1, automation='auto', endpoints=None,
                 endpoint_up_count=None, eligible=True, **kwargs):
        """Create a :class:`DSFDSRecord` object

        :param digest: The digest in hexadecimal form. 20-byte,
            hexadecimal-encoded, one-way hash of the DNSKEY record surrounded
            by parenthesis characters '(' & ')'
        :param keytag: The digest mechanism to use to verify the digest
        :param algorithm: Numeric value representing the public key encryption
            algorithm which will sign the zone. Must be one of 1 (RSA-MD5), 2
            (Diffie-Hellman), 3 (DSA/SHA-1), 4 (Elliptic Curve), or
            5 (RSA-SHA-1)
        :param digtype: the digest mechanism to use to verify the digest. Valid
            values are SHA1, SHA256
        :param ttl: TTL for this record
        :param label: A unique label for this :class:`DSFDSRecord`
        :param weight: Weight for this :class:`DSFDSRecord`
        :param automation: Defines how eligible can be changed in response to
            monitoring. Must be one of 'auto', 'auto_down', or 'manual'
        :param endpoints: Endpoints are used to determine status, torpidity,
            and eligible in response to monitor data
        :param endpoint_up_count: Number of endpoints that must be up for the
            Record status to be 'up'
        :param eligible: Indicates whether or not the Record can be served
        """
        DSRecord.__init__(self, None, None, digest=digest, keytag=keytag,
                          algorithm=algorithm, digtype=digtype, ttl=ttl,
                          create=False)
        _DSFRecord.__init__(self, label, weight, automation, endpoints,
                            endpoint_up_count, eligible, **kwargs)
        self._record_type = 'DSFDSRecord'

    def _update_record(self, api_args, publish=True):
        """Make the API call to update the current record type

        :param api_args: arguments to be pased to the API call
        """
        keys = ['digest', 'algorithm', 'digtype', 'key_tag']
        self.refresh()
        for key in keys:
            if key not in api_args:
                api_args['rdata'][key] = getattr(self, key)

        super(DSFDSRecord, self)._update_record(api_args, publish=publish)


class DSFKEYRecord(_DSFRecord, KEYRecord):
    """An :class:`KEYRecord` object which is able to store additional data for
    use by a :class:`TrafficDirector` service.
    """

    def __init__(self, algorithm, flags, protocol, public_key, ttl=0,
                 label=None, weight=1, automation='auto', endpoints=None,
                 endpoint_up_count=None, eligible=True, **kwargs):
        """Create a :class:`DSFKEYRecord` object

        :param algorithm: Numeric value representing the public key encryption
            algorithm which will sign the zone. Must be one of 1 (RSA-MD5), 2
            (Diffie-Hellman), 3 (DSA/SHA-1), 4 (Elliptic Curve), or
            5 (RSA-SHA-1)
        :param flags: See RFC 2535 for information on KEY record flags
        :param protocol: Numeric identifier of the protocol for this KEY record
        :param public_key: The public key for this record
        :param ttl: TTL for this record
        :param label: A unique label for this :class:`DSFKEYRecord`
        :param weight: Weight for this :class:`DSFKEYRecord`
        :param automation: Defines how eligible can be changed in response to
            monitoring. Must be one of 'auto', 'auto_down', or 'manual'
        :param endpoints: Endpoints are used to determine status, torpidity,
            and eligible in response to monitor data
        :param endpoint_up_count: Number of endpoints that must be up for the
            Record status to be 'up'
        :param eligible: Indicates whether or not the Record can be served
        """
        KEYRecord.__init__(self, None, None, algorithm=algorithm, flags=flags,
                           protocol=protocol, public_key=public_key, ttl=ttl,
                           create=False)
        _DSFRecord.__init__(self, label, weight, automation, endpoints,
                            endpoint_up_count, eligible, **kwargs)
        self._record_type = 'DSFKEYRecord'

    def _update_record(self, api_args, publish=True):
        """Make the API call to update the current record type

        :param api_args: arguments to be pased to the API call
        """
        keys = ['flags', 'algorithm', 'protocol', 'public_key']
        self.refresh()
        for key in keys:
            if key not in api_args:
                api_args['rdata'][key] = getattr(self, key)

        super(DSFKEYRecord, self)._update_record(api_args, publish=publish)


class DSFKXRecord(_DSFRecord, KXRecord):
    """An :class:`KXRecord` object which is able to store additional data for
    use by a :class:`TrafficDirector` service.
    """

    def __init__(self, exchange, preference, ttl=0, label=None, weight=1,
                 automation='auto', endpoints=None, endpoint_up_count=None,
                 eligible=True, **kwargs):
        """Create a :class:`DSFKXRecord` object

        :param exchange: Hostname that will act as the Key Exchanger. The
            hostname must have a :class:`CNAMERecord`, an :class:`ARecord`
            and/or an :class:`AAAARecord` associated with it
        :param preference: Numeric value for priority usage. Lower value takes
            precedence over higher value where two records of the same type
            exist on the zone/node
        :param ttl: TTL for this record
        :param label: A unique label for this :class:`DSFKXRecord`
        :param weight: Weight for this :class:`DSFKXRecord`
        :param automation: Defines how eligible can be changed in response to
            monitoring. Must be one of 'auto', 'auto_down', or 'manual'
        :param endpoints: Endpoints are used to determine status, torpidity,
            and eligible in response to monitor data
        :param endpoint_up_count: Number of endpoints that must be up for the
            Record status to be 'up'
        :param eligible: Indicates whether or not the Record can be served
        """
        KXRecord.__init__(self, None, None, exchange=exchange,
                          preference=preference, ttl=ttl, create=False)
        _DSFRecord.__init__(self, label, weight, automation, endpoints,
                            endpoint_up_count, eligible, **kwargs)
        self._record_type = 'DSFKXRecord'

    def _update_record(self, api_args, publish=True):
        """Make the API call to update the current record type

        :param api_args: arguments to be pased to the API call
        """
        keys = ['preference', 'exchange', ]
        self.refresh()
        for key in keys:
            if key not in api_args:
                api_args['rdata'][key] = getattr(self, key)

        super(DSFKXRecord, self)._update_record(api_args, publish=publish)


class DSFLOCRecord(_DSFRecord, LOCRecord):
    """An :class:`LOCRecord` object which is able to store additional data for
    use by a :class:`TrafficDirector` service.
    """

    def __init__(self, altitude, latitude, longitude, horiz_pre=10000, size=1,
                 vert_pre=10, ttl=0, label=None, weight=1, automation='auto',
                 endpoints=None, endpoint_up_count=None, eligible=True,
                 **kwargs):
        """Create a :class:`DSFLOCRecord` object

        :param altitude: Measured in meters above sea level
        :param horiz_pre:
        :param latitude: Measured in degrees, minutes, and seconds with N/S
            indicator for North and South
        :param longitude: Measured in degrees, minutes, and seconds with E/W
            indicator for East and West
        :param size:
        :param version:
        :param vert_pre:
        :param ttl: TTL for this record
        :param label: A unique label for this :class:`DSFLOCRecord`
        :param weight: Weight for this :class:`DSFLOCRecord`
        :param automation: Defines how eligible can be changed in response to
            monitoring. Must be one of 'auto', 'auto_down', or 'manual'
        :param endpoints: Endpoints are used to determine status, torpidity,
            and eligible in response to monitor data
        :param endpoint_up_count: Number of endpoints that must be up for the
            Record status to be 'up'
        :param eligible: Indicates whether or not the Record can be served
        """
        LOCRecord.__init__(self, None, None, altitude=altitude,
                           latitude=latitude, longitude=longitude,
                           horiz_pre=horiz_pre, size=size, vert_pre=vert_pre,
                           ttl=ttl, create=False)
        _DSFRecord.__init__(self, label, weight, automation, endpoints,
                            endpoint_up_count, eligible, **kwargs)
        self._record_type = 'DSFLOCRecord'

    def _update_record(self, api_args, publish=True):
        """Make the API call to update the current record type

        :param api_args: arguments to be pased to the API call
        """
        keys = ['altitude', 'horiz_pre', 'latitude', 'longitude', 'size',
                'version', 'vert_pre']
        self.refresh()
        for key in keys:
            if key not in api_args:
                api_args['rdata'][key] = getattr(self, key)

        super(DSFLOCRecord, self)._update_record(api_args, publish=publish)


class DSFIPSECKEYRecord(_DSFRecord, IPSECKEYRecord):
    """An :class:`IPSECKEYRecord` object which is able to store additional data
    for use by a :class:`TrafficDirector` service.
    """

    def __init__(self, precedence, gatetype, algorithm, gateway, public_key,
                 ttl=0, label=None, weight=1, automation='auto',
                 endpoints=None,
                 endpoint_up_count=None, eligible=True, **kwargs):
        """Create a :class:`DSFIPSECKEYRecord` object

        :param precedence: Indicates priority among multiple IPSECKEYS. Lower
            numbers are higher priority
        :param gatetype: Gateway type. Must be one of 0, 1, 2, or 3
        :param algorithm: Public key's cryptographic algorithm and format. Must
            be one of 0, 1, or 2
        :param gateway: Gateway used to create IPsec tunnel. Based on Gateway
            type
        :param public_key: Base64 encoding of the public key. Whitespace is
            allowed
        :param ttl: TTL for this record
        :param label: A unique label for this :class:`DSFIPSECKEYRecord`
        :param weight: Weight for this :class:`DSFIPSECKEYRecord`
        :param automation: Defines how eligible can be changed in response to
            monitoring. Must be one of 'auto', 'auto_down', or 'manual'
        :param endpoints: Endpoints are used to determine status, torpidity,
            and eligible in response to monitor data
        :param endpoint_up_count: Number of endpoints that must be up for the
            Record status to be 'up'
        :param eligible: Indicates whether or not the Record can be served
        """
        IPSECKEYRecord.__init__(self, None, None, precedence=precedence,
                                gatetype=gatetype, algorithm=algorithm,
                                gateway=gateway, public_key=public_key,
                                ttl=ttl,
                                create=False)
        _DSFRecord.__init__(self, label, weight, automation, endpoints,
                            endpoint_up_count, eligible, **kwargs)
        self._record_type = 'DSFIPSECKEYRecord'

    def _update_record(self, api_args, publish=True):
        """Make the API call to update the current record type

        :param api_args: arguments to be pased to the API call
        """
        keys = ['precedence', 'gatetype', 'gateway', 'public_key', ]
        self.refresh()
        for key in keys:
            if key not in api_args:
                api_args['rdata'][key] = getattr(self, key)

        super(DSFIPSECKEYRecord, self)._update_record(api_args,
                                                      publish=publish)


class DSFMXRecord(_DSFRecord, MXRecord):
    """An :class:`MXRecord` object which is able to store additional data
    for use by a :class:`TrafficDirector` service.
    """

    def __init__(self, exchange, preference=10, ttl=0, label=None, weight=1,
                 automation='auto', endpoints=None, endpoint_up_count=None,
                 eligible=True, **kwargs):
        """Create a :class:`DSFMXRecord` object

        :param exchange: Hostname of the server responsible for accepting mail
            messages in the zone
        :param preference: Numeric value for priority usage. Lower value takes
            precedence over higher value where two records of the same type
            exist on the zone/node.
        :param ttl: TTL for this record
        :param label: A unique label for this :class:`DSFMXRecord`
        :param weight: Weight for this :class:`DSFMXRecord`
        :param automation: Defines how eligible can be changed in response to
            monitoring. Must be one of 'auto', 'auto_down', or 'manual'
        :param endpoints: Endpoints are used to determine status, torpidity,
            and eligible in response to monitor data
        :param endpoint_up_count: Number of endpoints that must be up for the
            Record status to be 'up'
        :param eligible: Indicates whether or not the Record can be served
        """
        MXRecord.__init__(self, None, None, exchange=exchange,
                          preference=preference, ttl=ttl, create=False)
        _DSFRecord.__init__(self, label, weight, automation, endpoints,
                            endpoint_up_count, eligible, **kwargs)
        self._record_type = 'DSFMXRecord'

    def _update_record(self, api_args, publish=True):
        """Make the API call to update the current record type

        :param api_args: arguments to be pased to the API call
        """
        keys = ['exchange', 'preference']
        self.refresh()
        for key in keys:
            if key not in api_args:
                api_args['rdata'][key] = getattr(self, key)

        super(DSFMXRecord, self)._update_record(api_args, publish=publish)


class DSFNAPTRRecord(_DSFRecord, NAPTRRecord):
    """An :class:`NAPTRRecord` object which is able to store additional data
    for use by a :class:`TrafficDirector` service.
    """

    def __init__(self, order, preference, services, regexp, replacement,
                 flags='U', ttl=0, label=None, weight=1, automation='auto',
                 endpoints=None, endpoint_up_count=None, eligible=True,
                 **kwargs):
        """Create a :class:`DSFNAPTRRecord` object

        :param order: Indicates the required priority for processing NAPTR
            records. Lowest value is used first.
        :param preference: Indicates priority where two or more NAPTR records
            have identical order values. Lowest value is used first.
        :param services: Always starts with "e2u+" (E.164 to URI). After the
            e2u+ there is a string that defines the type and optionally the
            subtype of the URI where this :class:`NAPTRRecord` points.
        :param regexp: The NAPTR record accepts regular expressions
        :param replacement: The next domain name to find. Only applies if this
            :class:`NAPTRRecord` is non-terminal.
        :param flags: Should be the letter "U". This indicates that this NAPTR
            record terminal
        :param ttl: TTL for this record
        :param label: A unique label for this :class:`DSFNAPTRRecord`
        :param weight: Weight for this :class:`DSFNAPTRRecord`
        :param automation: Defines how eligible can be changed in response to
            monitoring. Must be one of 'auto', 'auto_down', or 'manual'
        :param endpoints: Endpoints are used to determine status, torpidity,
            and eligible in response to monitor data
        :param endpoint_up_count: Number of endpoints that must be up for the
            Record status to be 'up'
        :param eligible: Indicates whether or not the Record can be served
        """
        NAPTRRecord.__init__(self, None, None, order=order,
                             preference=preference, services=services,
                             regexp=regexp, replacement=replacement,
                             flags=flags, ttl=ttl, create=False)
        _DSFRecord.__init__(self, label, weight, automation, endpoints,
                            endpoint_up_count, eligible, **kwargs)
        self._record_type = 'DSFNAPTRRecord'

    def _update_record(self, api_args, publish=True):
        """Make the API call to update the current record type

        :param api_args: arguments to be pased to the API call
        """
        keys = ['order', 'preference', 'flags', 'services', 'regexp',
                'replacement']
        self.refresh()
        for key in keys:
            if key not in api_args:
                api_args['rdata'][key] = getattr(self, key)

        super(DSFNAPTRRecord, self)._update_record(api_args, publish=publish)


class DSFPTRRecord(_DSFRecord, PTRRecord):
    """An :class:`PTRRecord` object which is able to store additional data
    for use by a :class:`TrafficDirector` service.
    """

    def __init__(self, ptrdname, ttl=0, label=None, weight=1,
                 automation='auto',
                 endpoints=None, endpoint_up_count=None, eligible=True,
                 **kwargs):
        """Create a :class:`DSFPTRRecord` object

        :param ptrdname: The hostname where the IP address should be directed
        :param ttl: TTL for this record
        :param label: A unique label for this :class:`DSFPTRRecord`
        :param weight: Weight for this :class:`DSFPTRRecord`
        :param automation: Defines how eligible can be changed in response to
            monitoring. Must be one of 'auto', 'auto_down', or 'manual'
        :param endpoints: Endpoints are used to determine status, torpidity,
            and eligible in response to monitor data
        :param endpoint_up_count: Number of endpoints that must be up for the
            Record status to be 'up'
        :param eligible: Indicates whether or not the Record can be served
        """
        PTRRecord.__init__(self, None, None, ptrdname=ptrdname, ttl=ttl,
                           create=False)
        _DSFRecord.__init__(self, label, weight, automation, endpoints,
                            endpoint_up_count, eligible, **kwargs)
        self._record_type = 'DSFPTRRecord'


class DSFPXRecord(_DSFRecord, PXRecord):
    """An :class:`PXRecord` object which is able to store additional data
    for use by a :class:`TrafficDirector` service.
    """

    def __init__(self, preference, map822, mapx400, ttl=0, label=None,
                 weight=1,
                 automation='auto', endpoints=None, endpoint_up_count=None,
                 eligible=True, **kwargs):
        """Create a :class:`DSFPXRecord` object

        :param preference: Sets priority for processing records of the same
            type. Lowest value is processed first.
        :param map822: mail hostname
        :param mapx400: The domain name derived from the X.400 part of MCGAM
        :param ttl: TTL for this record
        :param label: A unique label for this :class:`DSFPXRecord`
        :param weight: Weight for this :class:`DSFPXRecord`
        :param automation: Defines how eligible can be changed in response to
            monitoring. Must be one of 'auto', 'auto_down', or 'manual'
        :param endpoints: Endpoints are used to determine status, torpidity,
            and eligible in response to monitor data
        :param endpoint_up_count: Number of endpoints that must be up for the
            Record status to be 'up'
        :param eligible: Indicates whether or not the Record can be served
        """
        PXRecord.__init__(self, None, None, preference=preference,
                          map822=map822, mapx400=mapx400, ttl=ttl,
                          create=False)
        _DSFRecord.__init__(self, label, weight, automation, endpoints,
                            endpoint_up_count, eligible, **kwargs)
        self._record_type = 'DSFPXRecord'

    def _update_record(self, api_args, publish=True):
        """Make the API call to update the current record type

        :param api_args: arguments to be pased to the API call
        """
        keys = ['map822', 'preference', 'mapx400']
        self.refresh()
        for key in keys:
            if key not in api_args:
                api_args['rdata'][key] = getattr(self, key)

        super(DSFPXRecord, self)._update_record(api_args, publish=publish)


class DSFNSAPRecord(_DSFRecord, NSAPRecord):
    """An :class:`NSAPRecord` object which is able to store additional data
    for use by a :class:`TrafficDirector` service.
    """

    def __init__(self, nsap, ttl=0, label=None, weight=1, automation='auto',
                 endpoints=None, endpoint_up_count=None, eligible=True,
                 **kwargs):
        """Create a :class:`DSFNSAPRecord` object

        :param nsap: Hex-encoded NSAP identifier
        :param ttl: TTL for this record
        :param label: A unique label for this :class:`DSFNSAPRecord`
        :param weight: Weight for this :class:`DSFNSAPRecord`
        :param automation: Defines how eligible can be changed in response to
            monitoring. Must be one of 'auto', 'auto_down', or 'manual'
        :param endpoints: Endpoints are used to determine status, torpidity,
            and eligible in response to monitor data
        :param endpoint_up_count: Number of endpoints that must be up for the
            Record status to be 'up'
        :param eligible: Indicates whether or not the Record can be served
        """
        NSAPRecord.__init__(self, None, None, nsap=nsap, ttl=ttl, create=False)
        _DSFRecord.__init__(self, label, weight, automation, endpoints,
                            endpoint_up_count, eligible, **kwargs)
        self._record_type = 'DSFNSAPRecord'


class DSFRPRecord(_DSFRecord, RPRecord):
    """An :class:`RPRecord` object which is able to store additional data
    for use by a :class:`TrafficDirector` service.
    """

    def __init__(self, mbox, txtdname, ttl=0, label=None, weight=1,
                 automation='auto', endpoints=None, endpoint_up_count=None,
                 eligible=True, **kwargs):
        """Create a :class:`DSFRPRecord` object

        :param mbox: Email address of the Responsible Person.
        :param txtdname: Hostname where a TXT record exists with more
            information on the responsible person.
        :param ttl: TTL for this record
        :param label: A unique label for this :class:`DSFRPRecord`
        :param weight: Weight for this :class:`DSFRPRecord`
        :param automation: Defines how eligible can be changed in response to
            monitoring. Must be one of 'auto', 'auto_down', or 'manual'
        :param endpoints: Endpoints are used to determine status, torpidity,
            and eligible in response to monitor data
        :param endpoint_up_count: Number of endpoints that must be up for the
            Record status to be 'up'
        :param eligible: Indicates whether or not the Record can be served
        """
        RPRecord.__init__(self, None, None, mbox=mbox, txtdname=txtdname,
                          ttl=ttl, create=False)
        _DSFRecord.__init__(self, label, weight, automation, endpoints,
                            endpoint_up_count, eligible, **kwargs)
        self._record_type = 'DSFRPRecord'

    def _update_record(self, api_args, publish=True):
        """Make the API call to update the current record type

        :param api_args: arguments to be pased to the API call
        """
        keys = ['mbox', 'txtdname']
        self.refresh()
        for key in keys:
            if key not in api_args:
                api_args['rdata'][key] = getattr(self, key)

        super(DSFRPRecord, self)._update_record(api_args, publish=publish)


class DSFNSRecord(_DSFRecord, NSRecord):
    """An :class:`NSRecord` object which is able to store additional data
    for use by a :class:`TrafficDirector` service.
    """

    def __init__(self, nsdname, service_class='', ttl=0, label=None, weight=1,
                 automation='auto', endpoints=None, endpoint_up_count=None,
                 eligible=True, **kwargs):
        """Create a :class:`DSFNSRecord` object

        :param nsdname: Hostname of the authoritative Nameserver for the zone
        :param service_class: Hostname of the authoritative Nameserver for the
            zone
        :param ttl: TTL for this record
        :param label: A unique label for this :class:`DSFNSRecord`
        :param weight: Weight for this :class:`DSFNSRecord`
        :param automation: Defines how eligible can be changed in response to
            monitoring. Must be one of 'auto', 'auto_down', or 'manual'
        :param endpoints: Endpoints are used to determine status, torpidity,
            and eligible in response to monitor data
        :param endpoint_up_count: Number of endpoints that must be up for the
            Record status to be 'up'
        :param eligible: Indicates whether or not the Record can be served
        """
        NSRecord.__init__(self, None, None, nsdname=nsdname,
                          service_class=service_class, ttl=ttl, create=False)
        _DSFRecord.__init__(self, label, weight, automation, endpoints,
                            endpoint_up_count, eligible, **kwargs)
        self._record_type = 'DSFNSRecord'


class DSFSPFRecord(_DSFRecord, SPFRecord):
    """An :class:`SPFRecord` object which is able to store additional data
    for use by a :class:`TrafficDirector` service.
    """

    def __init__(self, txtdata, ttl=0, label=None, weight=1, automation='auto',
                 endpoints=None, endpoint_up_count=None, eligible=True,
                 **kwargs):
        """Create a :class:`DSFSPFRecord` object

        :param txtdata: Free text containing SPF record information
        :param ttl: TTL for this record
        :param label: A unique label for this :class:`DSFSPFRecord`
        :param weight: Weight for this :class:`DSFSPFRecord`
        :param automation: Defines how eligible can be changed in response to
            monitoring. Must be one of 'auto', 'auto_down', or 'manual'
        :param endpoints: Endpoints are used to determine status, torpidity,
            and eligible in response to monitor data
        :param endpoint_up_count: Number of endpoints that must be up for the
            Record status to be 'up'
        :param eligible: Indicates whether or not the Record can be served
        """
        SPFRecord.__init__(self, None, None, txtdata=txtdata, ttl=ttl,
                           create=False)
        _DSFRecord.__init__(self, label, weight, automation, endpoints,
                            endpoint_up_count, eligible, **kwargs)
        self._record_type = 'DSFSPFRecord'


class DSFSRVRecord(_DSFRecord, SRVRecord):
    """An :class:`SRVRecord` object which is able to store additional data
    for use by a :class:`TrafficDirector` service.
    """

    def __init__(self, port, priority, target, rr_weight, ttl=0, label=None,
                 weight=1, automation='auto', endpoints=None,
                 endpoint_up_count=None, eligible=True, **kwargs):
        """Create a :class:`DSFSRVRecord` object

        :param port: Indicates the port where the service is running
        :param priority: Numeric value for priority usage. Lower value takes
            precedence over higher value where two records of the same type
            exist on the zone/node
        :param target: The domain name of a host where the service is running
            on the specified port
        :param rr_weight: Secondary prioritizing of records to serve. Records
            of equal priority should be served based on their weight. Higher
            values are served more often
        :param ttl: TTL for this record
        :param label: A unique label for this :class:`DSFSRVRecord`
        :param weight: Weight for this :class:`DSFSRVRecord`
        :param automation: Defines how eligible can be changed in response to
            monitoring. Must be one of 'auto', 'auto_down', or 'manual'
        :param endpoints: Endpoints are used to determine status, torpidity,
            and eligible in response to monitor data
        :param endpoint_up_count: Number of endpoints that must be up for the
            Record status to be 'up'
        :param eligible: Indicates whether or not the Record can be served
        """
        SRVRecord.__init__(self, None, None, port=port, priority=priority,
                           target=target, weight=rr_weight, ttl=ttl,
                           create=False)
        _DSFRecord.__init__(self, label, weight, automation, endpoints,
                            endpoint_up_count, eligible, **kwargs)
        self._record_type = 'DSFSRVRecord'

    def _update_record(self, api_args, publish=True):
        """Make the API call to update the current record type

        :param api_args: arguments to be pased to the API call
        """
        keys = ['port', 'priority', 'target', 'weight']
        self.refresh()
        for key in keys:
            if key not in api_args:
                api_args['rdata'][key] = getattr(self, key)

        super(DSFSRVRecord, self)._update_record(api_args, publish=publish)


class DSFSSHFPRecord(_DSFRecord, SSHFPRecord):
    """An :class:`SSHFPRecord` object which is able to store additional data
    for use by a :class:`TrafficDirector` service.
    """

    def __init__(self, fptype, algorithm, fingerprint, ttl=0, label=None,
                 weight=1, automation='auto', endpoints=None,
                 endpoint_up_count=None, eligible=True, **kwargs):
        """Create a :class:`DSFSSHFPRecord` object

        :param algorithm: Numeric value representing the public key encryption
            algorithm which will sign the zone.
        :param fptype: FingerPrint Type
        :param fingerprint: fingerprint value
        :param ttl: TTL for this record
        :param label: A unique label for this :class:`DSFSSHFPRecord`
        :param weight: Weight for this :class:`DSFSSHFPRecord`
        :param automation: Defines how eligible can be changed in response to
            monitoring. Must be one of 'auto', 'auto_down', or 'manual'
        :param endpoints: Endpoints are used to determine status, torpidity,
            and eligible in response to monitor data
        :param endpoint_up_count: Number of endpoints that must be up for the
            Record status to be 'up'
        :param eligible: Indicates whether or not the Record can be served
        """
        SSHFPRecord.__init__(self, None, None, algorithm=algorithm,
                             fptype=fptype, fingerprint=fingerprint, ttl=ttl,
                             create=False)
        _DSFRecord.__init__(self, label, weight, automation, endpoints,
                            endpoint_up_count, eligible, **kwargs)
        self._record_type = 'DSFSSHFPRecord'

    def _update_record(self, api_args, publish=True):
        """Make the API call to update the current record type

        :param api_args: arguments to be pased to the API call
        """
        keys = ['fptype', 'fingerprint', 'algorithm']
        self.refresh()
        for key in keys:
            if key not in api_args:
                api_args['rdata'][key] = getattr(self, key)

        super(DSFSSHFPRecord, self)._update_record(api_args, publish=publish)


class DSFTXTRecord(_DSFRecord, TXTRecord):
    """An :class:`TXTRecord` object which is able to store additional data
    for use by a :class:`TrafficDirector` service.
    """

    def __init__(self, txtdata, ttl=0, label=None, weight=1, automation='auto',
                 endpoints=None, endpoint_up_count=None, eligible=True,
                 **kwargs):
        """Create a :class:`DSFTXTRecord` object

        :param txtdata: Plain text data to be served by this
            :class:`DSFTXTRecord`
        :param ttl: TTL for this record
        :param label: A unique label for this :class:`DSFTXTRecord`
        :param weight: Weight for this :class:`DSFTXTRecord`
        :param automation: Defines how eligible can be changed in response to
            monitoring. Must be one of 'auto', 'auto_down', or 'manual'
        :param endpoints: Endpoints are used to determine status, torpidity,
            and eligible in response to monitor data
        :param endpoint_up_count: Number of endpoints that must be up for the
            Record status to be 'up'
        :param eligible: Indicates whether or not the Record can be served
        """
        TXTRecord.__init__(self, None, None, txtdata=txtdata, ttl=ttl,
                           create=False)
        _DSFRecord.__init__(self, label, weight, automation, endpoints,
                            endpoint_up_count, eligible, **kwargs)
        self._record_type = 'DSFTXTRecord'


class DSFRecordSet(object):
    """A Collection of DSFRecord Type objects belonging to a
    :class:`DSFFailoverChain`
    """

    def __init__(self, rdata_class, label=None, ttl=None, automation=None,
                 serve_count=None, fail_count=None, trouble_count=None,
                 eligible=None, dsf_monitor_id=None, records=None, **kwargs):
        """Create a new :class:`DSFRecordSet` object

        :param rdata_class: The type of rdata represented by this
            :class:`DSFRecordSet`
        :param label: A unique label for this :class:`DSFRecordSet`
        :param ttl: Default TTL for :class:`DSFRecord`'s within this
            :class:`DSFRecordSet`
        :param automation: Defines how eligible can be changed in response to
            monitoring
        :param serve_count: How many Records to serve out of this
            :class:`DSFRecordSet`
        :param fail_count: The number of Records that must not be okay before
            this :class:`DSFRecordSet` becomes ineligible.
        :param trouble_count: The number of Records that must not be okay
            before this :class:`DSFRecordSet` becomes in trouble.
        :param eligible: Indicates whether or not this :class:`DSFRecordSet`
            can be served.
        :param dsf_monitor_id: The unique system id of the DSF Monitor attached
            to this :class:`DSFRecordSet`
        :param records: A list of :class:`DSFRecord`'s within this
            :class:`DSFRecordSet`
        :param kwargs: Used for manipulating additional data to be specified
            by the creation of other system objects.
        """
        super(DSFRecordSet, self).__init__()
        self._label = label
        self._rdata_class = rdata_class
        self._ttl = ttl
        self._automation = automation
        self._serve_count = serve_count
        self._fail_count = fail_count
        self._trouble_count = trouble_count
        self._eligible = eligible
        self._dsf_monitor_id = dsf_monitor_id
        self._dsf_record_set_failover_chain_id = self._note = None
        self._implicitPublish = True
        if records is not None and len(records) > 0 and isinstance(records[0],
                                                                   dict):
            self._records = []
            for record in records:
                self._records += _constructor(record)

        else:
            self._records = records or []
        self.uri = self._master_line = self._rdata = self._status = None
        self._service_id = self._dsf_record_set_id = None
        for key, val in kwargs.items():
            if key != 'records':
                setattr(self, '_' + key, val)
        # If dsf_id and dsf_response_pool_id were specified in kwargs
        if (self._service_id is not None and
                self._dsf_record_set_id is not None):
            self.uri = '/DSFRecordSet/{}/{}/'.format(self._service_id,
                                                     self._dsf_record_set_id)

    def _post(self, service_id, publish=True, notes=None):
        """Create a new :class:`DSFRecordSet` on the DynECT System

        :param dsf_id: The unique system id of the DSF service this
            :class:`DSFRecordSet` is attached to
        """

        self._service_id = service_id
        self.uri = '/DSFRecordSet/{}'.format(self._service_id)
        api_args = {}
        api_args = self.to_json(skip_svc=True)
        if self._records:
            api_args['records'] = [record.to_json(skip_svc=True) for record in
                                   self._records]
        if self._dsf_record_set_failover_chain_id:
            api_args[
                'dsf_record_set_failover_chain_id'] = \
                self._dsf_record_set_failover_chain_id
        if publish:
            api_args['publish'] = 'Y'
        if notes:
            api_args['notes'] = notes
        response = DynectSession.get_session().execute(self.uri, 'POST',
                                                       api_args)
        self._build(response['data'])
        self.uri = '/DSFRecordSet/{}/{}/'.format(self._service_id,
                                                 self._dsf_record_set_id)

    def _get(self, dsf_id, dsf_record_set_id):
        """Get an existing :class:`DSFRecordSet` from the DynECT System

        :param dsf_id: The unique system id of the DSF service this
            :class:`DSFRecordSet` is attached to
        :param dsf_record_set_id: The unique system id of the DSF Record Set
            this :class:`DSFRecordSet` is attached to
        """
        self._service_id = dsf_id
        self._dsf_record_set_id = dsf_record_set_id
        self.uri = '/DSFRecordSet/{}/{}/'.format(self._service_id,
                                                 self._dsf_record_set_id)
        api_args = {}
        response = DynectSession.get_session().execute(self.uri, 'GET',
                                                       api_args)
        self._build(response['data'])

    def _update(self, api_args, publish=True):
        """Private update method"""
        if publish and self._implicitPublish:
            api_args['publish'] = 'Y'
        if self._note:
            api_args['notes'] = self._note
        response = DynectSession.get_session().execute(self.uri, 'PUT',
                                                       api_args)
        self._build(response['data'])
        # We hose the note if a publish was requested
        if api_args.get('publish') == 'Y':
            self._note = None

    def _build(self, data):
        """Private build method"""
        if data['records']:
            self._records = []
        for key, val in data.items():
            if key != 'records':
                setattr(self, '_' + key, val)
            if key == 'records':
                for record in val:
                    self._records += _constructor(record)

    def __str__(self):
        str = list()
        str.append('RDClass: {}'.format(self.rdata_class))
        str.append('Label: {}'.format(self.label))
        if self._dsf_record_set_id:
            str.append('ID: {}'.format(self._dsf_record_set_id))
        return '<DSFRecordSet>: {}'.format(', '.join(str))

    __repr__ = __unicode__ = __str__

    def publish(self, notes=None):
        """Publish changes to :class:`TrafficDirector`.
        :param notes: Optional Note that will be added to the zone notes of
                      zones attached to this service.
        """
        uri = '/DSF/{}/'.format(self._service_id)
        api_args = {'publish': 'Y'}
        if self._note:
            api_args['notes'] = self._note
            self._note = None
        # if notes are passed in, we override.
        if notes:
            api_args['notes'] = notes
        DynectSession.get_session().execute(uri, 'PUT', api_args)
        self.refresh()

    @property
    def publish_note(self):
        """Returns Current Publish Note, which will be
        used on the next publish action"""
        return self._note

    @publish_note.setter
    def publish_note(self, note):
        """Adds this note to the next action which also performs a publish
        """
        self._note = note

    def refresh(self):
        """Pulls data down from Dynect System and repopulates
        :class:`DSFRecordSet`
        """
        self._get(self._service_id, self._dsf_record_set_id)

    def add_to_failover_chain(self, failover_chain, service=None,
                              publish=True, notes=None):
        """Creates and links this :class:`DSFRecordSet` to the passed in
        :class:`DSFFailoverChain` Object

        :param failover_chain: Can either be the
            dsf_record_set_failover_chain_id or a
            :class:`DSFFailoverChain` Object.
        :param service: Only necessary is rs_chain is passed in as a string.
            This can be a :class:`TrafficDirector` Object. or the _service_id
        :param publish: Publish on execution (Default = True)
        :param notes: Optional Zone publish Notes
        """
        if isinstance(failover_chain, DSFFailoverChain):
            _dsf_record_set_failover_chain_id = \
                failover_chain._dsf_record_set_failover_chain_id
            _service_id = failover_chain._service_id
        elif isinstance(failover_chain, string_types):
            if service is None:
                msg = ('If passing failover_chain as a string, you must '
                       'provide the service_id as service=')
                raise Exception(msg)
            _dsf_record_set_failover_chain_id = failover_chain
        else:
            raise Exception('Could not make sense of Failover Chain Type')
        if service:
            _service_id = _check_type(service)

        if self._dsf_record_set_failover_chain_id:
            raise Exception(
                'Records Set already attached to Failover Chain: {}.'.format(
                    self._dsf_record_set_failover_chain_id))
        self._dsf_record_set_failover_chain_id = \
            _dsf_record_set_failover_chain_id
        self._post(_service_id, publish=publish, notes=notes)

    @property
    def records(self):
        """The ``list`` of :class:`DSFRecord` types that are stored in this
        :class:`DSFRecordSet`
        """
        return self._records

    @property
    def status(self):
        """The current status of this :class:`DSFRecordSet`"""
        self._get(self._service_id, self._dsf_record_set_id)
        return self._status

    @property
    def label(self):
        """A unique label for this :class:`DSFRecordSet`"""
        return self._label

    @label.setter
    def label(self, value):
        api_args = {'label': value}
        if self._master_line:
            api_args['master_line'] = self._master_line
        else:
            api_args['rdata'] = self._rdata
        self._update(api_args)
        if self._implicitPublish:
            self._label = value

    @property
    def rdata_class(self):
        """The rdata property is a read-only attribute"""
        return self._rdata_class

    @property
    def ttl(self):
        """Default TTL for :class:`DSFRecord`'s within this
            :class:`DSFRecordSet`"""
        return self._ttl

    @ttl.setter
    def ttl(self, value):
        api_args = {'ttl': value}
        if self._master_line:
            api_args['master_line'] = self._master_line
        else:
            api_args['rdata'] = self._rdata
        self._update(api_args)
        if self._implicitPublish:
            self._ttl = value

    @property
    def automation(self):
        """Defines how eligible can be changed in response to monitoring"""
        return self._automation

    @automation.setter
    def automation(self, value):
        api_args = {'automation': value}
        if self._master_line:
            api_args['master_line'] = self._master_line
        else:
            api_args['rdata'] = self._rdata
        self._update(api_args)
        if self._implicitPublish:
            self._automation = value

    @property
    def serve_count(self):
        """How many Records to serve out of this :class:`DSFRecordSet`"""
        return self._serve_count

    @serve_count.setter
    def serve_count(self, value):
        api_args = {'serve_count': value}
        if self._master_line:
            api_args['master_line'] = self._master_line
        else:
            api_args['rdata'] = self._rdata
        self._update(api_args)
        if self._implicitPublish:
            self._serve_count = value

    @property
    def fail_count(self):
        """The number of Records that must not be okay before this
        :class:`DSFRecordSet` becomes ineligible.
        """
        return self._fail_count

    @fail_count.setter
    def fail_count(self, value):
        api_args = {'fail_count': value}
        if self._master_line:
            api_args['master_line'] = self._master_line
        else:
            api_args['rdata'] = self._rdata
        self._update(api_args)
        if self._implicitPublish:
            self._fail_count = value

    @property
    def trouble_count(self):
        """The number of Records that must not be okay before this
        :class:`DSFRecordSet` becomes in trouble.
        """
        return self._trouble_count

    @trouble_count.setter
    def trouble_count(self, value):
        api_args = {'trouble_count': value}
        if self._master_line:
            api_args['master_line'] = self._master_line
        else:
            api_args['rdata'] = self._rdata
        self._update(api_args)
        if self._implicitPublish:
            self._trouble_count = value

    @property
    def eligible(self):
        """Indicates whether or not this :class:`DSFRecordSet` can be served"""
        return self._eligible

    @eligible.setter
    def eligible(self, value):
        api_args = {'eligible': value}
        if self._master_line:
            api_args['master_line'] = self._master_line
        else:
            api_args['rdata'] = self._rdata
        self._update(api_args)
        if self._implicitPublish:
            self._eligible = value

    @property
    def dsf_monitor_id(self):
        """The unique system id of the DSF Monitor attached to this
        :class:`DSFRecordSet`
        """
        return self._dsf_monitor_id

    @dsf_monitor_id.setter
    def dsf_monitor_id(self, value):
        """allows you to manually set the monitor_id, Legacy function for
        backward compatability
        """
        api_args = {'dsf_monitor_id': value}
        self._update(api_args)
        if self._implicitPublish:
            self._dsf_monitor_id = value

    def set_monitor(self, monitor):
        """For attaching a :class:`DSFMonitor` to this record_set
        :param monitor: a :class:`DSFMonitor` or string of the dsf_monitor_id
            to attach to this record_set
        """
        if isinstance(monitor, DSFMonitor):
            _monitor_id = monitor._dsf_monitor_id
        elif isinstance(monitor, string_types):
            _monitor_id = monitor
        else:
            raise Exception('Could not make sense of Monitor Type')
        api_args = {'dsf_monitor_id': _monitor_id}
        self._update(api_args)
        self._dsf_monitor_id = _monitor_id

    @property
    def dsf_id(self):
        """The unique system id of the :class:`TrafficDirector` This
        :class:`DSFRecordSet` is attached to
        """
        return self._service_id

    @property
    def record_set_id(self):
        """The unique system id of this :class:`DSFRecordSet`"""
        return self._dsf_record_set_id

    @property
    def implicit_publish(self):
        """Toggle for this specific :class:`DSFRecordSet` for turning on and
        off implicit Publishing for record Updates.
        """
        return self._implicitPublish

    @implicit_publish.setter
    def implicit_publish(self, value):
        if not isinstance(value, bool):
            raise Exception('Value must be True or False')
        self._implicitPublish = value

    implicitPublish = implicit_publish

    def to_json(self, svc_id=None, skip_svc=False):
        """Convert this :class:`DSFRecordSet` to a JSON blob"""

        if self._service_id and not svc_id:
            svc_id = self._service_id

        json_blob = {'rdata_class': self._rdata_class}
        if svc_id and not skip_svc:
            json_blob['service_id'] = svc_id
        if self._label:
            json_blob['label'] = self._label
        if self._ttl:
            json_blob['ttl'] = self._ttl
        if self._automation:
            json_blob['automation'] = self._automation
        if self._serve_count:
            json_blob['serve_count'] = self._serve_count
        if self._fail_count:
            json_blob['fail_count'] = self._fail_count
        if self._trouble_count:
            json_blob['trouble_count'] = self._trouble_count
        if self._eligible:
            json_blob['eligible'] = self._eligible
        if self._dsf_monitor_id:
            json_blob['dsf_monitor_id'] = self._dsf_monitor_id
        if self._records:
            json_blob['records'] = [rec.to_json(svc_id) for rec in
                                    self._records]
        else:
            json_blob['records'] = []
        return json_blob

    def delete(self, notes=None):
        """Delete this :class:`DSFRecordSet` from the Dynect System
        :param notes: Optional zone publish notes
        """
        api_args = {'publish': 'Y'}
        if notes:
            api_args['notes'] = notes
        DynectSession.get_session().execute(self.uri, 'DELETE', api_args)


class DSFFailoverChain(object):
    """docstring for DSFFailoverChain"""

    def __init__(self, label=None, core=None, record_sets=None, **kwargs):
        """Create a :class:`DSFFailoverChain` object

        :param label: A unique label for this :class:`DSFFailoverChain`
        :param core: Indicates whether or not the contained
            :class:`DSFRecordSets` are core record sets
        :param record_sets: A list of :class:`DSFRecordSet`'s for this
            :class:`DSFFailoverChain`
        """
        super(DSFFailoverChain, self).__init__()
        self._label = label
        self._core = core
        self._note = None
        self._implicitPublish = True
        if isinstance(record_sets, list) and len(record_sets) > 0 and \
                isinstance(record_sets[0], dict):
            # Clear record sets
            self._record_sets = []
            # Create new record set objects
            for record_set in record_sets:
                if 'service_id' in record_set and \
                                record_set['service_id'] == '':
                    record_set['service_id'] = kwargs['service_id']
                self._record_sets.append(DSFRecordSet(**record_set))
        else:
            self._record_sets = record_sets
        self._service_id = self._dsf_response_pool_id = self.uri = None
        self._dsf_record_set_failover_chain_id = None
        for key, val in kwargs.items():
            setattr(self, '_' + key, val)
        # If dsf_id and dsf_response_pool_id were specified in kwargs
        if (self._service_id is not None and
                self._dsf_response_pool_id is not None):
            r_pid = self._dsf_record_set_failover_chain_id
            self.uri = '/DSFRecordSetFailoverChain/{}/{}/'.format(
                self._service_id,
                r_pid)

    def _post(self, dsf_id, dsf_response_pool_id, publish=True, notes=None):
        """Create a new :class:`DSFFailoverChain` on the Dynect System

        :param dsf_id: The unique system id of the DSF service this
            :class:`DSFFailoverChain` is attached to
        :param dsf_response_pool_id: The unique system is of the DSF response
            pool this :class:`DSFFailoverChain` is attached to
        """
        self._service_id = dsf_id
        self._dsf_response_pool_id = dsf_response_pool_id
        self.uri = '/DSFRecordSetFailoverChain/{}/{}/'.format(
            self._service_id, self._dsf_response_pool_id
        )
        api_args = {}
        if self._label:
            api_args['label'] = self._label
        if self._core:
            api_args['core'] = self._core
        if self._record_sets:
            api_args['record_sets'] = [set.to_json(skip_svc=True) for set in
                                       self._record_sets]
        if publish:
            api_args['publish'] = 'Y'
        if notes:
            api_args['notes'] = notes
        response = DynectSession.get_session().execute(self.uri, 'POST',
                                                       api_args)
        self._build(response['data'])

    def _get(self, dsf_id, dsf_record_set_failover_chain_id):
        """Retrieve an existing :class:`DSFFailoverChain` from the Dynect System

        :param dsf_id: The unique system id of the DSF service this
            :class:`DSFFailoverChain` is attached to
        :param dsf_record_set_failover_chain_id: The unique system id of
            this :class:`DSFFailoverChain`.
        """
        self._service_id = dsf_id
        self._dsf_record_set_failover_chain_id = \
            dsf_record_set_failover_chain_id
        self.uri = '/DSFRecordSetFailoverChain/{}/{}/'.format(
            self._service_id, self._dsf_record_set_failover_chain_id
        )
        api_args = {}
        response = DynectSession.get_session().execute(self.uri, 'GET',
                                                       api_args)
        self._build(response['data'])

    def _update(self, api_args, publish=True):
        """API call to update non superclass record type parameters
        :param api_args: arguments to be pased to the API call
        """

        if publish and self._implicitPublish:
            api_args['publish'] = 'Y'
        if self._note:
            api_args['notes'] = self._note
        self.uri = 'DSFRecordSetFailoverChain/{}/{}'.format(
            self._service_id, self._dsf_record_set_failover_chain_id)
        response = DynectSession.get_session().execute(self.uri, 'PUT',
                                                       api_args)
        self._build(response['data'])
        # We hose the note if a publish was requested
        if api_args.get('publish') == 'Y':
            self._note = None

    def _build(self, data):
        """Private build method"""
        if data['record_sets']:
            self._record_sets = []
        for key, val in data.items():
            if key != 'record_sets':
                setattr(self, '_' + key, val)
            if key == 'record_sets':
                for record_set in val:
                    self._record_sets.append(DSFRecordSet(**record_set))

    def __str__(self):
        str = list()
        str.append('Label: {}'.format(self.label))
        if self._dsf_record_set_failover_chain_id:
            str.append('ID: {}'.format(self._dsf_record_set_failover_chain_id))
        return "<DSFFailoverChain>: {}".format(', '.join(str))

    __repr__ = __unicode__ = __str__

    def publish(self, notes=None):
        """Publish changes to :class:`TrafficDirector`.
        :param notes: Optional Note that will be added to the zone
                      notes of zones attached to this service.
        """
        uri = '/DSF/{}/'.format(self._service_id)
        api_args = {'publish': 'Y'}
        if self._note:
            api_args['notes'] = self._note
            self._note = None
        # if notes are passed in, we override.
        if notes:
            api_args['notes'] = notes
        DynectSession.get_session().execute(uri, 'PUT', api_args)
        self.refresh()

    @property
    def publish_note(self):
        """Returns Current Publish Note, which will be
        used on the next publish action"""
        return self._note

    @publish_note.setter
    def publish_note(self, note):
        """Adds this note to the next action which also performs a publish
        """
        self._note = note

    def refresh(self):
        """Pulls data down from Dynect System and repopulates
        :class:`DSFFailoverChain`
        """
        self._get(self._service_id, self._dsf_record_set_failover_chain_id)

    def add_to_response_pool(self, response_pool, service=None,
                             publish=True, notes=None):
        """Creates and Adds this :class:`DSFFailoverChain` to a
        :class:`TrafficDirector` service.

        :param response_pool: Can either be the response_pool_id or a
            :class:`DSFResponsePool` Object.
        :param service: Only necessary when response_pool is passed as a
            string. Can either be the service_id or a :class:`TrafficDirector`
        :param publish: Publish on execution (Default = True)
        :param notes: Optional Zone publish Notes
        """
        if isinstance(response_pool, DSFResponsePool):
            _response_pool_id = response_pool._dsf_response_pool_id
            _service_id = response_pool._service_id
        elif isinstance(response_pool, string_types):
            if service is None:
                msg = ('If passing response_pool as a string, you must '
                       'provide the service_id as service=')
                raise Exception(msg)
            _response_pool_id = response_pool
        else:
            raise Exception('Could not make sense of Response Pool Type')

        if service:
            _service_id = _check_type(service)

        if self._dsf_response_pool_id:
            raise Exception(
                'Records Set already attached to response pool: {}.'.format(
                    self._dsf_response_pool_id))
        self._post(_service_id, _response_pool_id, publish=publish,
                   notes=notes)

    @property
    def label(self):
        """A unique label for this :class:`DSFFailoverChain`"""
        return self._label

    @label.setter
    def label(self, value):
        api_args = {'label': value}
        self._update(api_args)
        if self._implicitPublish:
            self._label = value

    @property
    def core(self):
        """Indicates whether or not the contained :class:`DSFRecordSet`'s are
        core record sets.
        """
        return self._core

    @core.setter
    def core(self, value):
        api_args = {'core': value}
        self._update(api_args)
        if self._implicitPublish:
            self._core = value

    @property
    def record_sets(self):
        """A list of :class:`DSFRecordSet` connected to this
        :class:`DSFFailvoerChain`
        """
        return self._record_sets

    def to_json(self, svc_id=None, skip_svc=False):
        """Convert this :class:`DSFFailoverChain` to a JSON blob"""
        if self._service_id and not svc_id:
            svc_id = self._service_id

        json_blob = {}

        if svc_id and not skip_svc:
            json_blob['service_id'] = svc_id
        if self._label:
            json_blob['label'] = self._label
        if self._dsf_record_set_failover_chain_id:
            json_blob['dsf_record_set_failover_chain_id'] = \
                self._dsf_record_set_failover_chain_id
        if self._core:
            json_blob['core'] = self._core
        if self.record_sets:
            json_blob['record_sets'] = [rs.to_json(svc_id) for rs in
                                        self.record_sets]
        return json_blob

    @property
    def dsf_id(self):
        """The unique system id of the :class:`TrafficDirector` This
        :class:`DSFFailoverChain` is attached to
        """
        return self._service_id

    @property
    def response_pool_id(self):
        """The unique system id of the :class:`DSFResponsePool` this
        :class:`DSFFailoverChain` is attached to
        """
        return self._dsf_response_pool_id

    @property
    def failover_chain_id(self):
        """The unique system id of this :class:`DSFFailoverChain`
        """
        return self._dsf_record_set_failover_chain_id

    @property
    def implicit_publish(self):
        """Toggle for this specific :class:`DSFFailoverChain` for turning on
        and off implicit Publishing for record Updates.
        """
        return self._implicitPublish

    @implicit_publish.setter
    def implicit_publish(self, value):
        if not isinstance(value, bool):
            raise Exception('Value must be True or False')
        self._implicitPublish = value

    implicitPublish = implicit_publish

    def delete(self, notes=None):
        """Delete this :class:`DSFFailoverChain` from the Dynect System
        :param notes: Optional zone publish notes
        """
        api_args = {'publish': 'Y'}
        if notes:
            api_args['notes'] = notes
        DynectSession.get_session().execute(self.uri, 'DELETE', api_args)


class DSFResponsePool(object):
    """docstring for DSFResponsePool"""

    def __init__(self, label, core_set_count=1, eligible=True,
                 automation='auto', dsf_ruleset_id=None, index=None,
                 rs_chains=None, **kwargs):
        """Create a :class:`DSFResponsePool` object

        :param label: A unique label for this :class:`DSFResponsePool`
        :param core_set_count: If fewer than this number of core record sets
            are eligible, status will be set to fail
        :param eligible: Indicates whether or not the :class:`DSFResponsePool`
            can be served
        :param automation: Defines how eligible can be changed in response to
            monitoring
        :param dsf_ruleset_id: Unique system id of the Ruleset this
            :class:`DSFResponsePool` is attached to
        :param index: When specified with dsf_ruleset_id, indicates the
            position of the :class:`DSFResponsePool`
        :param rs_chains: A list of :class:`DSFFailoverChain` that are defined
            for this :class:`DSFResponsePool`
        """
        super(DSFResponsePool, self).__init__()
        self._label = label
        self._core_set_count = core_set_count
        self._eligible = eligible
        self._automation = automation
        self._dsf_ruleset_id = dsf_ruleset_id
        self._dsf_response_pool_id = self._note = None
        self._index = index
        self._implicitPublish = True
        if isinstance(rs_chains, list) and len(rs_chains) > 0 and \
                isinstance(rs_chains[0], dict):
            # Clear Failover Chains
            self._rs_chains = []
            # Create a new FO Chain for each entry returned from API
            for chain in rs_chains:
                self._rs_chains.append(DSFFailoverChain(**chain))
        else:
            self._rs_chains = rs_chains
        self._service_id = self._dsf_response_pool_id = self.uri = None
        for key, val in kwargs.items():
            setattr(self, '_' + key, val)
        # If dsf_id and dsf_response_pool_id were specified in kwargs
        if (self._service_id is not None and
                self._dsf_response_pool_id is not None):
            r_pid = self._dsf_response_pool_id
            self.uri = '/DSFResponsePool/{}/{}/'.format(self._service_id,
                                                        r_pid)

    def _post(self, service_id, publish=True, notes=None):
        """Create a new :class:`DSFResponsePool` on the DynECT System

        :param service_id: the id of the DSF service this
            :class:`DSFResponsePool` is attached to
        """
        self.service_id = service_id
        uri = '/DSFResponsePool/{}/'.format(self.service_id)
        api_args = {'publish': 'N', 'label': self._label,
                    'core_set_count': self._core_set_count,
                    'eligible': self._eligible, 'automation': self._automation}
        if self._dsf_ruleset_id:
            api_args['dsf_ruleset_id'] = self._dsf_ruleset_id
        if self._index:
            api_args['index'] = self._index
        if self._rs_chains:
            api_args['rs_chains'] = [chain.to_json(skip_svc=True) for chain in
                                     self.rs_chains]
        if publish:
            api_args['publish'] = 'Y'
        if notes:
            api_args['notes'] = notes
        response = DynectSession.get_session().execute(uri, 'POST', api_args)
        self._build(response['data'])
        self.uri = '/DSFResponsePool/{}/{}/'.format(self.service_id,
                                                    self._dsf_response_pool_id)

    def _get(self, service_id, dsf_response_pool_id):
        """Get an existing :class:`DSFResponsePool` from the DynECT System
        :param service_id: the id of the DSF service this
            :class:`DSFResponsePool` is attached to
        :param dsf_response_pool_id: the id of this :class:`DSFResponsePool`
        """
        self.service_id = service_id
        self._dsf_response_pool_id = dsf_response_pool_id
        self.uri = '/DSFResponsePool/{}/{}/'.format(self.service_id,
                                                    self._dsf_response_pool_id)
        api_args = {}
        response = DynectSession.get_session().execute(self.uri, 'GET',
                                                       api_args)
        self._build(response['data'])

    def _update(self, api_args, publish=True):
        """Make the API call to update the :class:`DSFResponsePool`
        :param api_args: arguments to be pased to the API call
        """
        if publish and self._implicitPublish:
            api_args['publish'] = 'Y'
        if self._note:
            api_args['notes'] = self._note

        self.uri = 'DSFResponsePool/{}/{}'.format(self._service_id,
                                                  self._dsf_response_pool_id)
        response = DynectSession.get_session().execute(self.uri, 'PUT',
                                                       api_args)
        self._build(response['data'])
        # We hose the note if a publish was requested
        if api_args.get('publish') == 'Y':
            self._note = None

    def _build(self, data):
        """Private build method"""
        if data['rs_chains']:
            self._rs_chains = []
        for key, val in data.items():
            if key != 'rs_chains':
                setattr(self, '_' + key, val)
            if key == 'rs_chains':
                for rs_chain in val:
                    self._rs_chains.append(DSFFailoverChain(**rs_chain))

    def __str__(self):
        str = list()
        str.append('Label: {}'.format(self.label))
        if self._dsf_response_pool_id:
            str.append('ID: {}'.format(self._dsf_response_pool_id))
        return "<DSFResponsePool>: {}".format(', '.join(str))

    __repr__ = __unicode__ = __str__

    def create(self, service, publish=True, notes=None):
        """Adds this :class:`DSFResponsePool` to the passed in
        :class:`TrafficDirector`
        :param service: a :class:`TrafficDirector` or id string for the
            :class:`TrafficDirector` you wish to add this
            :class:`DSFResponsePool` to.
        :param publish: publish at execution time. Default = True
        :param notes: Optional Zone publish Notes
        """
        if self._dsf_response_pool_id:
            raise Exception('Response Pool Already Exists. ID: {}'.format(
                self._dsf_response_pool_id))
        _service_id = _check_type(service)
        self._post(_service_id, publish=publish, notes=notes)

    def publish(self, notes=None):
        """Publish changes to :class:`TrafficDirector`.
        :param notes: Optional Note that will be added to the
        zone notes of zones attached to this service.
        """
        uri = '/DSF/{}/'.format(self._service_id)
        api_args = {'publish': 'Y'}
        if self._note:
            api_args['notes'] = self._note
            self._note = None
        # if notes are passed in, we override.
        if notes:
            api_args['notes'] = notes

        DynectSession.get_session().execute(uri, 'PUT', api_args)
        self.refresh()

    @property
    def publish_note(self):
        """Returns Current Publish Note, which will
        be used on the next publish action"""
        return self._note

    @publish_note.setter
    def publish_note(self, note):
        """Adds this note to the next action which also performs a publish
        """
        self._note = note

    def refresh(self):
        """Pulls data down from Dynect System and repopulates
        :class:`DSFResponsePool`
        """
        self._get(self._service_id, self._dsf_response_pool_id)

    @property
    def label(self):
        """A unique label for this :class:`DSFResponsePool`"""
        return self._label

    @label.setter
    def label(self, value):
        api_args = {'label': value}
        self._update(api_args)
        if self._implicitPublish:
            self._label = value

    @property
    def core_set_count(self):
        """If fewer than this number of core record sets are eligible, status
        will be set to fail
        """
        return self._core_set_count

    @core_set_count.setter
    def core_set_count(self, value):
        api_args = {'core_set_count': value}
        self._update(api_args)
        if self._implicitPublish:
            self._core_set_count = value

    @property
    def eligible(self):
        """Indicates whether or not the :class:`DSFResponsePool` can be served
        """
        return self._eligible

    @eligible.setter
    def eligible(self, value):
        api_args = {'eligible': value}
        self._update(api_args)
        if self._implicitPublish:
            self._eligible = value

    @property
    def automation(self):
        """Defines how eligiblity can be changed in response to monitoring"""
        return self._automation

    @automation.setter
    def automation(self, value):
        api_args = {'automation': value}
        self._update(api_args)
        if self._implicitPublish:
            self._automation = value

    @property
    def ruleset_ids(self):
        """List of Unique system ids of the :class:`DSFRuleset`s this
        :class:`DSFResponsePool` is attached to
        """
        self._get(self._service_id, self._dsf_response_pool_id)
        return [ruleset['dsf_ruleset_id'] for ruleset in self._rulesets]

    @property
    def response_pool_id(self):
        """The Unique system id of this :class:`DSFResponsePool`
        """
        return self._dsf_response_pool_id

    @property
    def dsf_id(self):
        """The unique system id of the :class:`TrafficDirector` This
        :class:`DSFResponsePool` is attached to
        """
        return self._service_id

    @property
    def failover_chains(self):
        """A ``list`` of :class:`DSFFailoverChain` that are defined for this
        :class:`DSFResponsePool`
        """
        return self._rs_chains

    @property
    def rs_chains(self):
        """A ``list`` of :class:`DSFFailoverChain` that are defined for this
        :class:`DSFResponsePool` (legacy call)
        """
        return self._rs_chains

    def to_json(self, svc_id=None, skip_svc=False):
        """Convert this :class:`DSFResponsePool` to a JSON blob"""

        if self._service_id and not svc_id:
            svc_id = self._service_id

        rs_json = [rs.to_json(svc_id) for rs in self._rs_chains]
        json_blob = {'label': self._label, 'eligible': self._eligible,
                     'core_set_count': self._core_set_count,
                     'automation': self._automation, 'rs_chains': rs_json}
        if self._index:
            json_blob['index'] = self._index
        if self._dsf_ruleset_id:
            json_blob['dsf_ruleset_id'] = self._dsf_ruleset_id
        if svc_id and not skip_svc:
            json_blob['service_id'] = svc_id
        return json_blob

    @property
    def implicit_publish(self):
        """Toggle for this specific :class:`DSFResponsePool` for turning on and
        off implicit Publishing for record Updates.
        """
        return self._implicitPublish

    @implicit_publish.setter
    def implicit_publish(self, value):
        if not isinstance(value, bool):
            raise Exception('Value must be True or False')
        self._implicitPublish = value

    implicitPublish = implicit_publish

    def delete(self, notes=None):
        """Delete this :class:`DSFResponsePool` from the DynECT System
        :param notes: Optional zone publish notes
        """
        api_args = {'publish': 'Y'}
        if notes:
            api_args['notes'] = notes
        DynectSession.get_session().execute(self.uri, 'DELETE', api_args)


class DSFRuleset(object):
    """docstring for DSFRuleset"""

    def __init__(self, label, criteria_type, response_pools, criteria=None,
                 failover=None,
                 **kwargs):
        """Create a :class:`DSFRuleset` object

        :param label: A unique label for this :class:`DSFRuleset`
        :param criteria_type: A set of rules describing what traffic is applied
            to the :class:`DSFRuleset`
        :param criteria: Varied depending on the specified criteria_type
        :param failover: IP address or Hostname for a last resort failover.
        :param response_pools: A list of :class:`DSFResponsePool`'s for this
            :class:`DSFRuleset`
        """
        super(DSFRuleset, self).__init__()
        self.valid_criteria_types = ('always', 'geoip')
        self.valid_criteria = {'always': (),
                               'geoip': ()}
        self._label = label
        self._criteria_type = criteria_type
        self._criteria = criteria
        self._failover = failover
        self._ordering = self._note = None
        self._implicitPublish = True

        if isinstance(response_pools, list) and len(response_pools) > 0 and \
                isinstance(response_pools[0], dict):
            self._response_pools = []
            for pool in response_pools:
                pool = {x: pool[x] for x in pool if x != 'rulesets'}
                self._response_pools.append(DSFResponsePool(**pool))
        else:
            self._response_pools = response_pools
        self._service_id = self._dsf_ruleset_id = self.uri = None
        for key, val in kwargs.items():
            setattr(self, '_' + key, val)
        # If dsf_id and dsf_ruleset_id were specified in kwargs
        if self._service_id is not None and self._dsf_ruleset_id is not None:
            self.uri = '/DSFRuleset/{}/{}/'.format(self._service_id,
                                                   self._dsf_ruleset_id)

    def _post(self, dsf_id, publish=True, notes=None):
        """Create a new :class:`DSFRuleset` on the DynECT System

        :param dsf_id: the id of the DSF service this :class:`DSFRuleset` is
            attached to
        :param publish: Publish at run time. Default is True
        """
        self._service_id = dsf_id
        uri = '/DSFRuleset/{}/'.format(self._service_id)
        api_args = {'publish': 'Y', 'label': self._label,
                    'criteria_type': self._criteria_type,
                    'criteria': self._criteria}
        if self._ordering is not None:
            api_args['ordering'] = self._ordering
        if self._response_pools:
            api_args['response_pools'] = [pool.to_json(skip_svc=True) for pool
                                          in self.response_pools]
        if publish:
            api_args['publish'] = 'Y'
        if notes:
            api_args['notes'] = notes
        response = DynectSession.get_session().execute(uri, 'POST', api_args)
        self._build(response['data'])
        self.uri = '/DSFRuleset/{}/{}/'.format(self._service_id,
                                               self._dsf_ruleset_id)

    def _get(self, dsf_id, dsf_ruleset_id):
        """Get an existing :class:`DSFRuleset` from the DynECT System

        :param dsf_id: the id of the DSF service this :class:`DSFRuleset` is
            attached to
        :param dsf_ruleset_id: The unique system id of this :class:`DSFRuleset`
        """
        self._service_id = dsf_id
        self._dsf_ruleset_id = dsf_ruleset_id
        self.uri = '/DSFRuleset/{}/{}/'.format(self._service_id,
                                               self._dsf_ruleset_id)
        api_args = {}
        response = DynectSession.get_session().execute(self.uri, 'GET',
                                                       api_args)
        self._build(response['data'])

    def _update(self, api_args, publish=True):
        """Make the API call to update the current record type
        :param api_args: arguments to be pased to the API call
        """

        if publish and self._implicitPublish:
            api_args['publish'] = 'Y'
        if self._note:
            api_args['notes'] = self._note
        self.uri = 'DSFRuleset/{}/{}'.format(self._service_id,
                                             self._dsf_ruleset_id)
        response = DynectSession.get_session().execute(self.uri, 'PUT',
                                                       api_args)
        self._build(response['data'])
        # We hose the note if a publish was requested
        if api_args.get('publish') == 'Y':
            self._note = None

    def _build(self, data):
        """Private build method"""
        if data['response_pools']:
            self._response_pools = []
        for key, val in data.items():
            if key != 'response_pools':
                setattr(self, '_' + key, val)
            if key == 'response_pools':
                for response_pool in val:
                    self._response_pools.append(
                        DSFResponsePool(**response_pool))

    def __str__(self):
        str = list()
        str.append('Label: {}'.format(self.label))
        if self._dsf_ruleset_id:
            str.append('ID: {}'.format(self._dsf_ruleset_id))
        return "<DSFRuleSet>: {}".format(', '.join(str))

    __repr__ = __unicode__ = __str__

    def add_response_pool(self, response_pool, index=0, publish=True):
        """Adds passed in :class:`DSFResponsePool` to this :class:`DSFRuleSet`.
        By default this adds it to the front of the list.

        :param response_pool: Can either be the response_pool_id or a
            :class:`DSFResponsePool` Object.
        :param index: where in the list of response pools to place this pool.
            0 is the first position, 0 is the default.
        :param publish: Publish on execution (Default = True)
        """
        if isinstance(response_pool, DSFResponsePool):
            _response_pool_id = response_pool._dsf_response_pool_id
        elif isinstance(response_pool, string_types):
            _response_pool_id = response_pool
        else:
            raise Exception('Could not make sense of Response Pool Type')
        self._get(self._service_id, self._dsf_ruleset_id)
        api_args = dict()
        api_args['response_pools'] = list()
        hit = False
        for pIndex, old_pool in enumerate(self._response_pools):
            if pIndex == index:
                api_args['response_pools'].append(
                    {'dsf_response_pool_id': _response_pool_id})
                hit = True
            api_args['response_pools'].append(
                {'dsf_response_pool_id': old_pool._dsf_response_pool_id})
        # If the index was greater than what was available, just append to the
        # end.
        if not hit:
            api_args['response_pools'].append(
                {'dsf_response_pool_id': _response_pool_id})
        self._update(api_args, publish)

    def remove_response_pool(self, response_pool, publish=True):
        """Removes passed in :class:`DSFResponsePool` from this
        :class:`DSFRuleSet`

        :param response_pool: Can either be the response_pool_id or a
            `DSFResponsePool` Object.
        :param publish: Publish on execution (Default = True)
        """
        if isinstance(response_pool, DSFResponsePool):
            _response_pool_id = response_pool._dsf_response_pool_id
        elif isinstance(response_pool, string_types):
            _response_pool_id = response_pool
        else:
            raise Exception('Could not make sense of Response Pool Type')

        self.refresh()
        api_args = dict()
        api_args['response_pools'] = list()
        system_pool_ids = [pool._dsf_response_pool_id for pool in
                           self._response_pools]
        for pool_id in system_pool_ids:
            if pool_id != _response_pool_id:
                api_args['response_pools'].append(
                    {'dsf_response_pool_id': pool_id})
        self._update(api_args, publish)

    def add_failover_ip(self, ip, publish=True):
        """Adds passed in :class:`DSFResponsePool` to the end of this
        :class:`DSFRuleSet`. This effectively creates a special new Record
        chain with a single IP. It can be accessed as a responce pool with
        label equal to the ip passed in.

        :param publish: Publish on execution (Default = True)
        """
        api_args = dict()
        api_args['response_pools'] = list()
        for old_pool in self._response_pools:
            api_args['response_pools'].append(
                {'dsf_response_pool_id': old_pool._dsf_response_pool_id})
        api_args['response_pools'].append({'failover': ip})
        self._update(api_args, publish)

    def order_response_pools(self, pool_list, publish=True):
        """For reordering the ruleset list. simply pass in a ``list`` of
        :class:`DSFResponcePool`s in the order you wish them to failover.

        :param pool_list: ordered ``list`` of :class:`DSFResponcePool`
        :param publish: Publish on execution. default = True
        """

        if not isinstance(pool_list, list):
            msg = ('You must pass in an ordered list of response pool '
                   'objects, or ids.')
            raise Exception(msg)
        _pool_list = list()

        for list_item in pool_list:
            if isinstance(list_item, DSFResponsePool):
                _pool_list.append(list_item._dsf_response_pool_id)
            elif isinstance(list_item, string_types):
                _pool_list.append(list_item)
        api_args = dict()
        api_args['response_pools'] = list()
        for pool_id in _pool_list:
            api_args['response_pools'].append(
                {'dsf_response_pool_id': pool_id})
        self._update(api_args, publish)

    def create(self, service, index=None, publish=True, notes=None):

        """Adds this :class:`DSFRuleset` to the passed in :class:`TrafficDirector`

        :param service: a :class:`TrafficDirector` or id string for the
            :class:`TrafficDirector` you wish to add this :class:`DSFRuleset`
            to.
        :param index: in what position to serve this ruleset. 0 = first.
        :param publish: publish at execution time. Default = True
        :param notes: Optional Zone publish Notes
        """
        if self._dsf_ruleset_id:
            raise Exception(
                'Rule Set Already Exists. ID: {}'.format(self._dsf_ruleset_id))
        _service_id = _check_type(service)
        if index is not None:
            self._ordering = index
        self._post(_service_id, publish=publish, notes=notes)

    def publish(self, notes=None):
        """Publish changes to :class:`TrafficDirector`.
        :param notes: Optional Note that will be added to the zone notes
                      of zones attached to this service.
        """
        uri = '/DSF/{}/'.format(self._service_id)
        api_args = {'publish': 'Y'}
        if self._note:
            api_args['notes'] = self._note
            self._note = None
        # if notes are passed in, we override.
        if notes:
            api_args['notes'] = notes
        DynectSession.get_session().execute(uri, 'PUT', api_args)
        self.refresh()

    @property
    def publish_note(self):
        """Returns Current Publish Note, which will
        be used on the next publish action"""
        return self._note

    @publish_note.setter
    def publish_note(self, note):
        """Adds this note to the next action which also performs a publish
        """
        self._note = note

    def refresh(self):
        """Pulls data down from Dynect System and repopulates
        :class:`DSFRuleset`
        """
        self._get(self._service_id, self._dsf_ruleset_id)

    @property
    def label(self):
        """A unique label for this :class:`DSFRuleset`"""
        return self._label

    @label.setter
    def label(self, value):
        api_args = {'label': value}
        self._update(api_args)
        if self._implicitPublish:
            self._label = value

    @property
    def criteria_type(self):
        """A set of rules describing what traffic is applied to the
        :class:`DSFRuleset`
        """
        return self._criteria_type

    @criteria_type.setter
    def criteria_type(self, value):
        api_args = {'criteria_type': value}
        self._update(api_args)
        if self._implicitPublish:
            self._criteria_type = value

    @property
    def criteria(self):
        """The criteria rules, will be varied depending on the specified
        criteria_type
        """
        return self._criteria

    @criteria.setter
    def criteria(self, value):
        api_args = dict()
        if isinstance(value, dict):
            if value.get('geoip'):
                for key, val in value['geoip'].items():
                    if len(val) != 0:
                        api_args['criteria_type'] = 'geoip'

        api_args['criteria'] = value
        self._update(api_args)
        if self._implicitPublish:
            self._criteria = value

    @property
    def response_pools(self):
        """A list of :class:`DSFResponsePool`'s for this :class:`DSFRuleset`"""
        return self._response_pools

    @property
    def dsf_id(self):
        """The unique system id of the :class:`TrafficDirector` This
        :class:`DSFRuleset` is attached to
        """
        return self._service_id

    @property
    def ruleset_id(self):
        """The unique system id of this :class:`DSFRuleset`
        """
        return self._dsf_ruleset_id

    @property
    def implicit_publish(self):
        """Toggle for this specific :class:`DSFRuleset` for turning on and
        off implicit Publishing for record Updates.
        """
        return self._implicitPublish

    @implicit_publish.setter
    def implicit_publish(self, value):
        if not isinstance(value, bool):
            raise Exception('Value must be True or False')
        self._implicitPublish = value

    implicitPublish = implicit_publish

    @property
    def _json(self, svc_id=None, skip_svc=False):
        """JSON-ified version of this DSFRuleset Object"""

        if self._service_id and not svc_id:
            svc_id = self._service_id

        pool_json = [pool.to_json(svc_id) for pool in self._response_pools]
        if self._failover:
            pool_json.append({'failover': self._failover})
        json_blob = {'label': self._label,
                     'criteria_type': self._criteria_type,
                     'criteria': self._criteria,
                     'response_pools': pool_json}
        if svc_id and not skip_svc:
            json_blob['service_id'] = svc_id

        return json_blob

    def delete(self, notes=None):
        """Remove this :class:`DSFRuleset` from it's associated
        :class:`TrafficDirector` Service
        :param notes: Optional zone publish notes
        """
        api_args = {'publish': 'Y'}
        if notes:
            api_args['notes'] = notes
        DynectSession.get_session().execute(self.uri, 'DELETE', api_args)


class DSFMonitorEndpoint(object):
    """An Endpoint object to be passed to a :class:`DSFMonitor`"""

    def __init__(self, address, label, active='Y', site_prefs=None):
        """Create a :class:`DSFMonitorEndpoint` object

        :param address: The address to monitor.
        :param label: A label to identify this :class:`DSFMonitorEndpoint`.
        :param active: Indicates whether or not this
            :class:`DSFMonitorEndpoint` endpoint is active. Must be one of
            True, False, 'Y', or 'N'
        :param site_prefs: A ``list`` of site codes from which this
            :class:`DSFMonitorEndpoint` will be monitored
        """
        self._address = address
        self._label = label
        self._active = Active(active)
        self._site_prefs = site_prefs
        self._monitor = None

    def _update(self, api_args):
        """Update this :class:`DSFMonitorEndpoint` with the provided api_args

        :param api_args: arguments to pass to the API via PUT
        """
        if self._monitor is not None:
            full_list = self._monitor.endpoints
            args_list = []
            for endpoint in full_list:
                if id(endpoint) == id(self):
                    args_list.append(api_args)
                else:
                    args_list.append(endpoint._json)
            api_args = {'endpoints': args_list}
            self._monitor._update(api_args)

    @property
    def _json(self):
        """Get the JSON representation of this :class:`DSFMonitorEndpoint`
        object
        """
        json_blob = {'address': self._address, 'label': self._label,
                     'active': str(self._active),
                     'site_prefs': self._site_prefs}
        return {x: json_blob[x] for x in json_blob if json_blob[x] is not None}

    @property
    def active(self):
        """Indicates if this :class:`DSFMonitorEndpoint` is active. When
        updating valid arguments are 'Y' or True to activate, or 'N' or False
        to deactivate.

        :returns: An :class:`Active` object representing the current state of
            this :class:`DSFMonitorEndpoint`
        """
        return self._active

    @active.setter
    def active(self, value):
        valid_input = ('Y', 'N', True, False)
        if value not in valid_input:
            raise DynectInvalidArgumentError('active', value, valid_input)
        api_args = self._json
        api_args['active'] = value
        self._update(api_args)

    @property
    def label(self):
        return self._label

    @label.setter
    def label(self, value):
        api_args = self._json
        api_args['label'] = value
        self._update(api_args)

    @property
    def address(self):
        return self._address

    @address.setter
    def address(self, value):
        api_args = self._json
        api_args['address'] = value
        self._update(api_args)

    @property
    def site_prefs(self):
        return self._site_prefs

    @site_prefs.setter
    def site_prefs(self, value):
        api_args = self._json
        api_args['site_prefs'] = value
        self._update(api_args)


class DSFMonitor(object):
    """A Monitor for a :class:`TrafficDirector` Service"""

    def __init__(self, *args, **kwargs):
        """Create a new :class:`DSFMonitor` object

        :param label: A unique label to identify this :class:`DSFMonitor`
        :param protocol: The protocol to monitor. Must be one of 'HTTP',
            'HTTPS', 'PING', 'SMTP', or 'TCP'
        :param response_count: The number of responses to determine whether or
            not the endpoint is 'up' or 'down'
        :param probe_interval: How often to run this :class:`DSFMonitor`
        :param retries: How many retries this :class:`DSFMonitor` should
            attempt on failure before giving up.
        :param active: Indicates if this :class:`DSFMonitor` is active
        :param options: Additional options pertaining to this
            :class:`DSFMonitor`
        :param endpoints: A List of :class:`DSFMonitorEndpoint`'s that are
            associated with this :class:`DSFMonitor`
        """
        super(DSFMonitor, self).__init__()
        self.uri = None
        self._monitor_id = None
        self._label = self._protocol = self._response_count = None
        self._probe_interval = self._retries = self._active = None
        self._options = self._dsf_monitor_id = self._timeout = None
        self._port = self._path = self._host = self._header = None
        self._expected = None
        self._endpoints = []
        if 'api' in kwargs:
            del kwargs['api']
            for key, val in kwargs.items():
                setattr(self, '_' + key, val)
            self.uri = '/DSFMonitor/{}/'.format(self._dsf_monitor_id)
        elif len(args) + len(kwargs) == 1:
            self._get(*args, **kwargs)
        else:
            self._post(*args, **kwargs)

    def _get(self, monitor_id):
        """Get an existing :class:`DSFMonitor` from the DynECT System"""
        self._monitor_id = monitor_id
        self.uri = '/DSFMonitor/{}/'.format(self._monitor_id)
        api_args = {}
        response = DynectSession.get_session().execute(self.uri, 'GET',
                                                       api_args)
        self._build(response['data'])

    def _post(self, label, protocol, response_count, probe_interval, retries,
              active='Y', timeout=None, port=None, path=None, host=None,
              header=None, expected=None, endpoints=None):
        """Create a new :class:`DSFMonitor` on the DynECT System"""
        uri = '/DSFMonitor/'
        self._label = label
        self._protocol = protocol
        self._response_count = response_count
        self._probe_interval = probe_interval
        self._retries = retries
        self._active = Active(active)
        self._options = {}
        if timeout:
            self._timeout = timeout
            self._options['timeout'] = timeout
        if port:
            self._port = port
            self._options['port'] = port
        if path:
            self._path = path
            self._options['path'] = path
        if host:
            self._host = host
            self._options['host'] = host
        if header:
            self._header = header
            self._options['header'] = header
        if expected:
            self._expected = expected
            self._options['expected'] = expected
        self._endpoints = endpoints
        api_args = {'label': self._label,
                    'protocol': self._protocol,
                    'response_count': self._response_count,
                    'probe_interval': self._probe_interval,
                    'retries': self._retries,
                    'active': str(self._active),
                    'options': self._options}
        if self._endpoints is not None:
            api_args['endpoints'] = [x._json for x in self._endpoints]
        response = DynectSession.get_session().execute(uri, 'POST', api_args)
        self._build(response['data'])
        self.uri = '/DSFMonitor/{}/'.format(self._dsf_monitor_id)

    def _update(self, api_args):
        """Private Update method"""
        self.uri = '/DSFMonitor/{}/'.format(self._dsf_monitor_id)
        response = DynectSession.get_session().execute(self.uri, 'PUT',
                                                       api_args)
        self._build(response['data'])

    def _build(self, data):
        """Update this object based on the information passed in via data

        :param data: The ``['data']`` field from an API JSON response
        """
        for key, val in data.items():
            if key == 'endpoints':
                self._endpoints = []
                for endpoint in val:
                    ep = DSFMonitorEndpoint(**endpoint)
                    ep._monitor = self
                    self._endpoints.append(ep)
            elif key == 'active':
                self._active = Active(val)
            else:
                setattr(self, '_' + key, val)

    @property
    def dsf_monitor_id(self):
        """The unique system id of this :class:`DSFMonitor`"""
        return self._dsf_monitor_id

    @dsf_monitor_id.setter
    def dsf_monitor_id(self, value):
        pass

    @property
    def label(self):
        """A unique label to identify this :class:`DSFMonitor`"""
        return self._label

    @label.setter
    def label(self, value):
        self._label = value
        api_args = {'label': self._label}
        self._update(api_args)

    @property
    def protocol(self):
        """The protocol to monitor. Must be one of 'HTTP', 'HTTPS', 'PING',
        'SMTP', or 'TCP'
        """
        return self._protocol

    @protocol.setter
    def protocol(self, value):
        self._protocol = value
        api_args = {'protocol': self._protocol}
        self._update(api_args)

    @property
    def response_count(self):
        """The minimum number of agents reporting the host as up for failover
        not to occur. Must be 0, 1 or 2
        """
        return self._response_count

    @response_count.setter
    def response_count(self, value):
        self._response_count = value
        api_args = {'response_count': self._response_count}
        self._update(api_args)

    @property
    def probe_interval(self):
        """How often to run this :class:`DSFMonitor`"""
        return self._probe_interval

    @probe_interval.setter
    def probe_interval(self, value):
        self._probe_interval = value
        api_args = {'probe_interval': self._probe_interval}
        self._update(api_args)

    @property
    def retries(self):
        """How many retries this :class:`DSFMonitor` should attempt on failure
        before giving up.
        """
        return self._retries

    @retries.setter
    def retries(self, value):
        self._retries = value
        api_args = {'retries': self._retries}
        self._update(api_args)

    @property
    def active(self):
        """Returns whether or not this :class:`DSFMonitor` is active. Will
        return either 'Y' or 'N'
        """
        return self._active

    @active.setter
    def active(self, value):
        self._active = value
        api_args = {'active': self._active}
        self._update(api_args)

    @property
    def endpoints(self):
        """A list of the endpoints (and their statuses) that this
        :class:`DSFMonitor` is currently monitoring.
        """
        self._get(self.dsf_monitor_id)
        return self._endpoints

    @endpoints.setter
    def endpoints(self, value):
        pass

    @property
    def options(self):
        """Additional options pertaining to this :class:`DSFMonitor`"""
        return self._options

    @options.setter
    def options(self, value):
        self._options = value
        api_args = {'options': self._options}
        self._update(api_args)

    def __str__(self):
        """str override"""
        return force_unicode('<DSFMonitor>: {}, ID: {}').format(
            self._label, self._dsf_monitor_id
        )

    __repr__ = __unicode__ = __str__

    def delete(self):
        """Delete an existing :class:`DSFMonitor` from the DynECT System"""
        api_args = {}
        self.uri = '/DSFMonitor/{}/'.format(self._dsf_monitor_id)
        DynectSession.get_session().execute(self.uri, 'DELETE', api_args)


class DSFNotifier(object):
    def __init__(self, *args, **kwargs):
        """ Create a :class:`Notifier` object

        :param label:
        :param recipients: ``list`` of Contact Names
        :param dsf_services:
        :param monitor_services:
        """
        self._label = self._notifier_id = self._recipients = None
        self._services = None
        if 'api' in kwargs:
            del kwargs['api']
            self._build(kwargs)
            return
        if 'td' in kwargs:
            del kwargs['td']
            self._build(kwargs['notifier'], link_id=kwargs['link_id'])
            return
        elif len(args) + len(kwargs) == 1:
            self._get(*args, **kwargs)
        else:
            self._post(*args, **kwargs)
        self.uri = '/Notifier/'

    def _post(self, label, dsf_services=None, monitor_services=None,
              recipients=None):
        """Create a new :class:`TrafficDirector` on the DynECT System"""
        uri = '/Notifier/'
        api_args = {}
        if recipients:
            api_args['recipients'] = list()
            for recipient in recipients:
                api_args['recipients'].append(
                    {'recipient': recipient, 'format': 'email'})

        if dsf_services or monitor_services:
            api_args['services'] = list()

        if dsf_services:
            api_args['services'] += [
                {'service_class': 'DSF', 'service_id': service_id} for
                service_id in dsf_services]
        if monitor_services:
            api_args['services'] += [
                {'service_class': 'Monitor', 'service_id': service_id} for
                service_id in monitor_services]

        self._label = label
        api_args['label'] = label

        response = DynectSession.get_session().execute(uri, 'POST', api_args)
        self.uri = '/Notifier/{}/'.format(response['data']['notifier_id'])
        self._build(response['data'])

    def _get(self, notifier_id):
        self._notifier_id = notifier_id
        self.uri = '/Notifier/{}/'.format(self._notifier_id)
        api_args = {}
        response = DynectSession.get_session().execute(self.uri, 'GET',
                                                       api_args)
        self._build(response['data'])

    def _update(self, api_args):
        """Private update method"""
        self.uri = '/Notifier/{}/'.format(self._notifier_id)
        response = DynectSession.get_session().execute(self.uri, 'PUT',
                                                       api_args)
        self._build(response['data'])

    def _build(self, data, link_id=None):
        for key, val in data.items():
            setattr(self, '_' + key, val)
        self._link_id = link_id

    @property
    def label(self):
        return self._label

    @label.setter
    def label(self, value):
        api_args = {'label': value}
        self._update(api_args)
        self._label = value

    @property
    def link_id(self):
        """ Link ID connecting thie Notifier to TD service """
        return self._link_id

    @property
    def recipients(self):
        return self._recipients

    def add_recipient(self, new_recipient, format='email'):
        recipients = self._recipients
        for recipient in recipients:
            recipient.pop('details', None)
            recipient.pop('features', None)
        recipients.append({'recipient': new_recipient, 'format': format})
        api_args = {'recipients': recipients}
        self._update(api_args)

    def del_recipient(self, recipient):
        recipients = [srecipient for srecipient in self._recipients if
                      srecipient['recipient'] != recipient]
        for recipient in recipients:
            recipient.pop('details', None)
            recipient.pop('features', None)
        api_args = {'recipients': recipients}
        self._update(api_args)

    @property
    def dsf_service_ids(self):
        return [service['service_id'] for service in self._services if
                service['service_class'] == 'DSF']

    @property
    def monitor_service_ids(self):
        return [service['service_id'] for service in self._services if
                service['service_class'] == 'Monitor']

    def to_json(self):
        json_blob = {}
        if self._label:
            json_blob['label'] = self._label
        if self._recipients:
            json_blob['recipients'] = [recipient['recipient'] for recipient in
                                       self._recipients]
        if self._services:
            json_blob['dsf_services'] = [dsf['service_id'] for dsf in
                                         self._services if
                                         dsf['service_class'] == 'DSF']
            json_blob['monitor_services'] = [mon['service_id'] for mon in
                                             self._services if
                                             mon['service_class'] == 'Monitor']
        return json_blob

    def __str__(self):
        """str override"""
        return force_unicode('<DSFNotifier>: {}, ID: {}').format(
            self._label, self._notifier_id
        )

    __repr__ = __unicode__ = __str__

    def delete(self):
        """Delete this :class:`DSFNotifier` from the Dynect
        System
        """
        self.uri = '/Notifier/{}/'.format(self._notifier_id)
        DynectSession.get_session().execute(self.uri, 'DELETE')


class DSFNode(object):
    """DSFNode object. Represents a valid fqdn node within a zone. It should be
    noted that simply creating a :class:`DSFNode` object does not actually
    create anything on the DynECT System. The only way to actively create a
    :class:`DSFNode` on the DynECT System is by attaching either a record or a
    service to it.
    """

    def __init__(self, zone, fqdn=None):
        """Create a :class:`Node` object

        :param zone: name of the zone that this Node belongs to
        :param fqdn: the fully qualified domain name of this zone
        """
        super(DSFNode, self).__init__()
        self.zone = zone
        self.fqdn = fqdn or self.zone + '.'
        self.records = {}

        self.recs = {'A': ARecord, 'AAAA': AAAARecord,
                     'ALIAS': ALIASRecord, 'CDS': CDSRecord,
                     'CDNSKEY': CDNSKEYRecord, 'CSYNC': CSYNCRecord,
                     'CERT': CERTRecord, 'CNAME': CNAMERecord,
                     'DHCID': DHCIDRecord, 'DNAME': DNAMERecord,
                     'DNSKEY': DNSKEYRecord, 'DS': DSRecord,
                     'KEY': KEYRecord, 'KX': KXRecord,
                     'LOC': LOCRecord, 'IPSECKEY': IPSECKEYRecord,
                     'MX': MXRecord, 'NAPTR': NAPTRRecord,
                     'PTR': PTRRecord, 'PX': PXRecord,
                     'NSAP': NSAPRecord, 'RP': RPRecord,
                     'NS': NSRecord, 'SOA': SOARecord,
                     'SPF': SPFRecord, 'SRV': SRVRecord,
                     'TLSA': TLSARecord, 'TXT': TXTRecord,
                     'SSHFP': SSHFPRecord, 'UNKNOWN': UNKNOWNRecord}

    def add_record(self, record_type='A', *args, **kwargs):
        """Adds an a record with the provided data to this :class:`Node`

        :param record_type: The type of record you would like to add.
            Valid record_type arguments are: 'A', 'AAAA', 'CERT', 'CNAME',
            'DHCID', 'DNAME', 'DNSKEY', 'DS', 'KEY', 'KX', 'LOC', 'IPSECKEY',
            'MX', 'NAPTR', 'PTR', 'PX', 'NSAP', 'RP', 'NS', 'SOA', 'SPF',
            'SRV', and 'TXT'.
        :param args: Non-keyword arguments to pass to the Record constructor
        :param kwargs: Keyword arguments to pass to the Record constructor
        """
        # noinspection PyCallingNonCallable
        rec = self.recs[record_type](self.zone, self.fqdn, *args, **kwargs)
        if record_type in self.records:
            self.records[record_type].append(rec)
        else:
            self.records[record_type] = [rec]
        return rec

    def get_all_records(self):
        """Retrieve a list of all record resources for the specified node and
        zone combination as well as all records from any Base_Record below that
        point on the zone hierarchy
        """
        self.records = {}
        uri = '/AllRecord/{}/'.format(self.zone)
        if self.fqdn is not None:
            uri += '{}/'.format(self.fqdn)
        api_args = {'detail': 'Y'}
        response = DynectSession.get_session().execute(uri, 'GET', api_args)
        # Strip out empty record_type lists
        record_lists = {label: rec_list for label, rec_list in
                        response['data'].items() if rec_list != []}
        for key, record_list in record_lists.items():
            search = key.split('_')[0].upper()
            try:
                constructor = self.recs[search]
            except KeyError:
                constructor = self.recs['UNKNOWN']
            list_records = []
            for record in record_list:
                del record['zone']
                fqdn = record['fqdn']
                del record['fqdn']
                # Unpack rdata
                for r_key, r_val in record['rdata'].items():
                    record[r_key] = r_val
                record['create'] = False
                list_records.append(constructor(self.zone, fqdn, **record))
            self.records[key] = list_records
        return self.records

    def get_all_records_by_type(self, record_type):
        """Get a list of all :class:`DNSRecord` of type ``record_type`` which
        are owned by this node.

        :param record_type: The type of :class:`DNSRecord` you wish returned.
            Valid record_type arguments are: 'A', 'AAAA', 'CERT', 'CNAME',
            'DHCID', 'DNAME', 'DNSKEY', 'DS', 'KEY', 'KX', 'LOC', 'IPSECKEY',
            'MX', 'NAPTR', 'PTR', 'PX', 'NSAP', 'RP', 'NS', 'SOA', 'SPF',
            'SRV', and 'TXT'.
        :return: A list of :class:`DNSRecord`'s
        """
        names = {'A': 'ARecord', 'AAAA': 'AAAARecord', 'CERT': 'CERTRecord',
                 'CNAME': 'CNAMERecord', 'DHCID': 'DHCIDRecord',
                 'DNAME': 'DNAMERecord', 'DNSKEY': 'DNSKEYRecord',
                 'DS': 'DSRecord', 'KEY': 'KEYRecord', 'KX': 'KXRecord',
                 'LOC': 'LOCRecord', 'IPSECKEY': 'IPSECKEYRecord',
                 'MX': 'MXRecord', 'NAPTR': 'NAPTRRecord', 'PTR': 'PTRRecord',
                 'PX': 'PXRecord', 'NSAP': 'NSAPRecord', 'RP': 'RPRecord',
                 'NS': 'NSRecord', 'SOA': 'SOARecord', 'SPF': 'SPFRecord',
                 'SRV': 'SRVRecord', 'TLSA': 'TLSARecord', 'TXT': 'TXTRecord',
                 'SSHFP': 'SSHFPRecord', 'ALIAS': 'ALIASRecord'}
        constructor = self.recs[record_type]
        uri = '/{}/{}/{}/'.format(names[record_type], self.zone,
                                  self.fqdn)
        api_args = {'detail': 'Y'}
        response = DynectSession.get_session().execute(uri, 'GET', api_args)
        records = []
        for record in response['data']:
            fqdn = record['fqdn']
            del record['fqdn']
            del record['zone']
            # Unpack rdata
            for key, val in record['rdata'].items():
                record[key] = val
            del record['rdata']
            record['create'] = False
            records.append(constructor(self.zone, fqdn, **record))
        return records

    def get_any_records(self):
        """Retrieve a list of all recs"""
        if self.fqdn is None:
            return
        api_args = {'detail': 'Y'}
        uri = '/ANYRecord/{}/{}/'.format(self.zone, self.fqdn)
        response = DynectSession.get_session().execute(uri, 'GET', api_args)
        # Strip out empty record_type lists
        record_lists = {label: rec_list for label, rec_list in
                        response['data'].items() if rec_list != []}
        for key, record_list in record_lists.items():
            search = key.split('_')[0].upper()
            try:
                constructor = self.recs[search]
            except KeyError:
                constructor = self.recs['UNKNOWN']
            list_records = []
            for record in record_list:
                del record['zone']
                del record['fqdn']
                # Unpack rdata
                for r_key, r_val in record['rdata'].items():
                    record[r_key] = r_val
                record['create'] = False
                list_records.append(
                    constructor(self.zone, self.fqdn, **record))
            self.records[key] = list_records
        return self.records

    def delete(self):
        """Delete this node, any records within this node, and any nodes
        underneath this node
        """
        uri = '/Node/{}/{}'.format(self.zone, self.fqdn)
        DynectSession.get_session().execute(uri, 'DELETE', {})

    def __str__(self):
        """str override"""
        return force_unicode('<DSFNode>: {}').format(self.fqdn)

    __repr__ = __unicode__ = __str__

    def __bytes__(self):
        """bytes override"""
        return bytes(self.__str__())


class TrafficDirector(object):
    """Traffic Director is a DNS based traffic routing and load balancing
    service that is Geolocation aware and can support failover by monitoring
    endpoints.
    """

    def __init__(self, *args, **kwargs):
        """Create a :class:`TrafficDirector` object

        :param label: A unique label for this :class:`TrafficDirector` service
        :param ttl: The default TTL to be used across this service
        :param publish: If Y, service will be published on creation
        :param notes: Optional Publish Zone Notes.
        :param nodes: A Node Object, a zone, FQDN pair in a hash, or a list
            containing those two things (can be mixed) that are to be
            linked to this :class:`TrafficDirector` service:
        :param notifiers: A list of notifier ids associated with this
            :class:`TrafficDirector` service
        :param rulesets: A list of :class:`DSFRulesets` that are defined for
            this :class:`TrafficDirector` service
        """
        super(TrafficDirector, self).__init__()
        self._label = self._ttl = self._publish = self._response_pools = None
        self._record_sets = self.uri = self._service_id = None
        self._notifiers = APIList(DynectSession.get_session, 'notifiers')
        self._nodes = APIList(DynectSession.get_session, 'nodes')
        self._rulesets = APIList(DynectSession.get_session, 'rulesets')
        self._note = None
        self._implicitPublish = True
        if 'api' in kwargs:
            del kwargs['api']
            self._build(kwargs)
        elif len(args) + len(kwargs) == 1:
            self._get(*args, **kwargs)
        else:
            self._post(*args, **kwargs)
        self.uri = '/DSF/{}/'.format(self._service_id)
        self._rulesets.uri = self.uri

    def _post(self, label, ttl=None, publish='Y', nodes=None, notifiers=None,
              rulesets=None, notes=None):
        """Create a new :class:`TrafficDirector` on the DynECT System"""
        uri = '/DSF/'
        self._label = label
        self._ttl = ttl
        self._nodes = nodes
        self._notifiers = notifiers
        self._rulesets = rulesets
        api_args = {'label': self._label,
                    'publish': publish,
                    'notes': notes}
        if ttl:
            api_args['ttl'] = self._ttl
        if nodes:
            _nodeList = []
            if isinstance(nodes, list):
                for node in nodes:
                    if isinstance(node, DSFNode) or\
                                  type(node).__name__ == 'Node':
                        _nodeList.append(
                            {'zone': node.zone, 'fqdn': node.fqdn})
                    elif isinstance(node, dict):
                        _nodeList.append(node)
            elif isinstance(nodes, dict):
                _nodeList.append(nodes)
            elif isinstance(nodes, DSFNode) or type(nodes).__name__ == 'Node':
                _nodeList.append({'zone': nodes.zone, 'fqdn': nodes.fqdn})
            self._nodes = _nodeList
            api_args['nodes'] = self._nodes
        if notifiers:
            api_args['notifiers'] = []
            for notifier in notifiers:
                if isinstance(notifier, DSFNotifier):
                    api_args['notifiers'].append(
                        {'notifier_id': notifier._notifier_id})
                elif isinstance(notifier, Notifier):
                    api_args['notifiers'].append(
                        {'notifier_id': notifier._notifier_id})
                elif isinstance(notifier, string_types):
                    api_args['notifiers'].append({'notifier_id': notifier})
                else:
                    msg = ('notifiers must be a list containing DSFNotifier '
                           'objects, or notifier_id strings.')
                    raise Exception(msg)
        if rulesets:
            api_args['rulesets'] = [rule._json for rule in self._rulesets]
        response = DynectSession.get_session().execute(uri, 'POST', api_args)
        self.uri = '/DSF/{}/'.format(response['data']['service_id'])
        self._build(response['data'])

    def _build(self, data):
        for key, val in data.items():
            if key == 'notifiers':
                self._notifiers = []
                for notifier in val:
                    self._notifiers.append(
                        DSFNotifier(None, td=False, **notifier))
            elif key == 'rulesets':
                # Clear Rulesets
                self._rulesets = APIList(DynectSession.get_session, 'rulesets')
                self._rulesets.uri = None
                # For each Ruleset returned, create a new DSFRuleset object
                for ruleset in val:
                    self._rulesets.append(DSFRuleset(**ruleset))
            elif key == 'nodes':
                # nodes are now returned as Node Objects
                self._nodes = [DSFNode(node['zone'], node['fqdn'])
                               for node in val]
            else:
                setattr(self, '_' + key, val)
        self.uri = '/DSF/{}/'.format(self._service_id)
        self._rulesets.uri = self.uri

    def _get(self, service_id):
        """Get an existing :class:`TrafficDirector` from the DynECT System"""
        self._service_id = service_id
        self.uri = '/DSF/{}/'.format(self._service_id)
        api_args = {'pending_changes': 'Y'}
        response = DynectSession.get_session().execute(self.uri, 'GET',
                                                       api_args)
        self._build(response['data'])

    def _update(self, api_args, publish=True):
        """Private update method"""
        if publish and self._implicitPublish:
            api_args['publish'] = 'Y'
        if self._note:
            api_args['notes'] = self._note
        self.uri = '/DSF/{}/'.format(self._service_id)
        response = DynectSession.get_session().execute(self.uri, 'PUT',
                                                       api_args)
        self._build(response['data'])
        # We hose the note if a publish was requested
        if api_args.get('publish', None):
            if api_args.get('publish') == 'Y':
                self._note = None

    def publish(self, notes=None):
        """Publish changes to :class:`TrafficDirector`.
        :param notes: Optional Note that will be added to
        the zone notes of zones attached to this service.
        """
        uri = '/DSF/{}/'.format(self._service_id)
        api_args = {'publish': 'Y'}
        if self._note:
            api_args['notes'] = self._note
            self._note = None
        # if notes are passed in, we override.
        if notes:
            api_args['notes'] = notes
        DynectSession.get_session().execute(uri, 'PUT', api_args)
        self.refresh()

    @property
    def publish_note(self):
        """Returns Current Publish Note, which will
        be used on the next publish action"""
        return self._note

    @publish_note.setter
    def publish_note(self, note):
        """Adds this note to the next action which also performs a publish
        """
        self._note = note

    def refresh(self):
        """Pulls data down from Dynect System and repopulates
        :class:`TrafficDirector`
        """
        self._get(self._service_id)

    @property
    def all_records(self):
        """Returns All :class:`DSFRecord` in :class:`TrafficDirector`"""
        return get_all_records(self)

    @property
    def all_record_sets(self):
        """Returns All :class:`DSFRecordSet` in :class:`TrafficDirector`"""
        return get_all_record_sets(self)

    @property
    def all_failover_chains(self):
        """Returns All :class:`DSFFailoverChain` in :class:`TrafficDirector`"""
        return get_all_failover_chains(self)

    @property
    def all_response_pools(self):
        """Returns All :class:`DSFResponsePool` in :class:`TrafficDirector`"""
        return get_all_response_pools(self)

    @property
    def all_rulesets(self):
        """Returns All :class:`DSFRuleset` in :class:`TrafficDirector`"""
        return get_all_rulesets(self)

    def revert_changes(self):
        """Clears the changeset for this service and reverts all non-published
        changes to their original state
        """
        api_args = {'revert': True}
        self._update(api_args)

    def add_notifier(self, notifier, notes=None):
        """Links the :class:`DSFNotifier` with the specified id
        to this Traffic Director service, Accepts :class:`DSFNotifier`
        or :class:`Notifier` or the notifier public id.
        """
        if isinstance(notifier, DSFNotifier):
            _notifier_id = notifier._notifier_id
        elif isinstance(notifier, Notifier):
            _notifier_id = notifier._notifier_id
        elif isinstance(notifier, string_types):
            _notifier_id = notifier
        else:
            msg = ('Cannot sensibly determine Notifier type, must be '
                   'DSFNotifier, or notifier_id string')
            raise Exception(msg)
        api_args = {'add_notifier': True, 'notifier_id': _notifier_id}
        if notes:
            api_args['notes'] = notes
        self._update(api_args)

    def del_notifier(self, notifier, notes=None):
        """delinks the :class:`DSFNotifier` with the specified id to
        this Traffic Director service. Accepts :class:`DSFNotifier` or
        :class:`Notifier`.
        """
        if isinstance(notifier, DSFNotifier):
            _link_id = notifier._link_id
        elif isinstance(notifier, Notifier):
            _link_id = notifier._link_id
        else:
            raise Exception("Cannot sensibly determine Notifier type,\
                             must be DSFNotifier, or notifier_id string")
        api_args = {'remove_notifier': True, 'link_id': _link_id}
        if notes:
            api_args['notes'] = notes
        self._update(api_args)

    def remove_orphans(self):
        """Remove Record Set Chains which are no longer referenced by a
        :class:`DSFResponsePool`
        """
        api_args = {'remove_orphans': 'Y'}
        self._update(api_args)

    def replace_all_rulesets(self, rulesets):
        """This request will replace all rulesets with a new list of rulesets.

        :param rulesets: a list of rulesets :class:DSFRuleset to be published
        to the service Warning! This call takes extra time as it is several
        api calls.
        """
        if isinstance(rulesets, Iterable) and isinstance(rulesets[0],
                                                         DSFRuleset):
            old_rulesets = self.all_rulesets
            for old_rule in old_rulesets:
                old_rule.delete()
            for new_rule in rulesets:
                new_rule._dsf_ruleset_id = None
                new_rule.create(self)
        else:
            raise Exception(
                "rulesets parameter must be a list of DSFRuleset objects")

    def replace_one_ruleset(self, ruleset):
        """This request will replace a single ruleset and maintain the order
        of the list.

        Warning! This call takes extra time as it is several api calls.

        :param ruleset: A single object of :class:DSFRuleset` The replacement
        is keyed by the DSFRuleset label value.
        """
        if isinstance(ruleset, DSFRuleset):
            old_rulesets = self.all_rulesets
            old_rule = None
            rule_index = 0
            for rule in old_rulesets:
                if rule.label == ruleset.label:
                    old_rule = rule
                    rule_index += 1
                    break
                rule_index += 1
            if old_rule is not None:
                old_rule.delete()
                ruleset._dsf_ruleset_id = None
                ruleset.create(self, index=rule_index)
            else:
                ruleset.create(self)
        else:
            msg = ('rulesets parameter must be a single object of class '
                   'DSFRuleset')
            raise Exception(msg)

    @property
    def service_id(self):
        """The unique System id of this DSF Service"""
        return self._service_id

    @property
    def records(self):
        """A list of this :class:`TrafficDirector` Services' DSFRecords"""
        self.refresh()
        return [record for ruleset in self._rulesets
                for response_pool in ruleset.response_pools
                for rs_chains in response_pool.rs_chains
                for record_set in rs_chains.record_sets
                for record in record_set.records]

    @records.setter
    def records(self, value):
        pass

    @property
    def record_sets(self):
        """A list of this :class:`TrafficDirector` Services
        :class:`DSFRecordSet`'s
        """
        self.refresh()
        return [record_set for ruleset in self._rulesets
                for response_pool in ruleset.response_pools
                for rs_chains in response_pool.rs_chains
                for record_set in rs_chains.record_sets]

    @record_sets.setter
    def record_sets(self, value):
        pass

    @property
    def response_pools(self):
        """A list of this :class:`TrafficDirector` Services
        :class:`DSFResponsePool`'s
        """
        self.refresh()
        return [response_pool for ruleset in self._rulesets
                for response_pool in ruleset.response_pools]

    @response_pools.setter
    def response_pools(self, value):
        pass

    @property
    def failover_chains(self):
        """A list of this :class:`TrafficDirector` Services
        :class:`DSFFailoverChain`'s
        """
        self.refresh()
        return [rs_chains for ruleset in self._rulesets
                for response_pool in ruleset.response_pools
                for rs_chains in response_pool.rs_chains]

    @failover_chains.setter
    def failover_chains(self, value):
        pass

    @property
    def notifiers(self):
        """A list of names of :class:`DSFNotifier` associated with this
        :class:`TrafficDirector` service
        """
        self.refresh()
        return self._notifiers

    @property
    def rulesets(self):
        """A list of :class:`DSFRulesets` that are defined for this
        :class:`TrafficDirector` service
        """
        self.refresh()
        return self._rulesets

    @rulesets.setter
    def rulesets(self, value):
        if isinstance(value, list) and not isinstance(value, APIList):
            self._rulesets = APIList(DynectSession.get_session, 'rulesets',
                                     None, value)
        elif isinstance(value, APIList):
            self._rulesets = value
        self._rulesets.uri = self.uri

    def order_rulesets(self, ruleset_list, publish=True):
        """For reordering the ruleset list. simply pass in a ``list`` of
        :class:`DSFRulesets`s in the order you wish them to be served.

        :param ruleset_list: ordered ``list`` of :class:`DSFRulesets`
        :param publish: Publish on execution. default = True
        """
        if not isinstance(ruleset_list, list):
            msg = ('You must pass in an ordered list of response pool '
                   'objects, or ids.')
            raise Exception(msg)
        _ruleset_list = list()

        for list_item in ruleset_list:
            if isinstance(list_item, DSFRuleset):
                _ruleset_list.append(list_item._dsf_ruleset_id)
            elif isinstance(list_item, string_types):
                _ruleset_list.append(list_item)
        api_args = dict()
        api_args['rulesets'] = list()
        for ruleset_id in _ruleset_list:
            api_args['rulesets'].append({'dsf_ruleset_id': ruleset_id})
        self._update(api_args, publish)

    @property
    def node_objects(self):
        """A list of :class:`DSFNode` Objects that are linked to this
        :class:`TrafficDirector` service
        """
        uri = '/DSFNode/{}'.format(self._service_id)
        api_args = {}
        response = DynectSession.get_session().execute(uri, 'GET',
                                                       api_args)
        self._nodes = [DSFNode(node['zone'], node['fqdn']) for node
                       in response['data']]
        return self._nodes

    nodeObjects = node_objects

    @property
    def nodes(self):
        """A list of hashes of zones, fqdn for each DSF node that is linked
        to this :class:`TrafficDirector` service"""
        uri = '/DSFNode/{}'.format(self._service_id)
        api_args = {}
        response = DynectSession.get_session().execute(uri, 'GET',
                                                       api_args)
        self._nodes = [DSFNode(node['zone'], node['fqdn']) for node
                       in response['data']]
        return [{'zone': node['zone'], 'fqdn': node['fqdn']} for node in
                response['data']]

    @nodes.setter
    def nodes(self, nodes):
        """A :class:`DSFNode` Object, a Zone & FQDN pair in a hash, or a list
        containing those two things (can be mixed) that are to be
        linked to this :class:`TrafficDirector` service. This overwrites
        whatever nodes are already linked to this :class:`TrafficDirector`
        service
        """
        _nodeList = []
        if isinstance(nodes, list):
            for node in nodes:
                if isinstance(node, DSFNode) or type(node).__name__ == 'Node':
                    _nodeList.append({'zone': node.zone, 'fqdn': node.fqdn})
                elif isinstance(node, dict):
                    _nodeList.append(node)
        elif isinstance(nodes, dict):
            _nodeList.append(nodes)
        elif isinstance(nodes, DSFNode) or type(nodes).__name__ == 'Node':
            _nodeList.append({'zone': nodes.zone, 'fqdn': nodes.fqdn})
        uri = '/DSFNode/{}'.format(self._service_id)
        publish = "Y" if self._implicitPublish else "N"
        api_args = {'nodes': _nodeList, 'publish': publish}
        response = DynectSession.get_session().execute(uri, 'PUT',
                                                       api_args)
        self._nodes = [DSFNode(node['zone'], node['fqdn']) for node
                       in response['data']]

    def add_node(self, node):
        """A :class:`DSFNode` object, or a zone, FQDN pair in a hash to be added
        to this :class:`TrafficDirector` service
        """
        if isinstance(node, DSFNode) or type(node).__name__ == 'Node':
            _node = {'zone': node.zone, 'fqdn': node.fqdn}
        elif isinstance(node, dict):
            _node = node
        uri = '/DSFNode/{}'.format(self._service_id)
        publish = "Y" if self._implicitPublish else "N"
        api_args = {'node': _node, 'publish': publish}
        response = DynectSession.get_session().execute(uri, 'POST',
                                                       api_args)
        self._nodes = [DSFNode(nd['zone'], nd['fqdn']) for nd
                       in response['data']]

    def remove_node(self, node):
        """A :class:`DSFNode` object, or a zone, FQDN pair in a hash to be
        removed to this :class:`TrafficDirector` service
        """
        if isinstance(node, DSFNode) or type(node).__name__ == 'Node':
            _node = {'zone': node.zone, 'fqdn': node.fqdn}
        elif isinstance(node, dict):
            _node = node
        uri = '/DSFNode/{}'.format(self._service_id)
        publish = "Y" if self._implicitPublish else "N"
        api_args = {'node': _node, 'publish': publish}
        response = DynectSession.get_session().execute(uri, 'DELETE',
                                                       api_args)
        self._nodes = [DSFNode(nd['zone'], nd['fqdn']) for nd
                       in response['data']]

    @property
    def label(self):
        """A unique label for this :class:`TrafficDirector` service"""
        return self._label

    @label.setter
    def label(self, value):
        api_args = {'label': value}
        self._update(api_args)
        if self._implicitPublish:
            self._label = value

    @property
    def ttl(self):
        """The default TTL to be used across this service"""
        if not isinstance(self._ttl, int):
            self._ttl = int(self._ttl)
        return self._ttl

    @ttl.setter
    def ttl(self, value):
        api_args = {'ttl': value}
        self._update(api_args)
        if self._implicitPublish:
            self._ttl = value

    @property
    def implicit_publish(self):
        """Toggle for this specific :class:`TrafficDirector` for turning on and
        off implicit Publishing for record Updates.
        """
        return self._implicitPublish

    @implicit_publish.setter
    def implicit_publish(self, value):
        if not isinstance(value, bool):
            raise Exception('Value must be True or False')
        self._implicitPublish = value

    implicitPublish = implicit_publish

    def delete(self):
        """Delete this :class:`TrafficDirector` from the DynECT System
        :param notes: Optional zone publish notes
        """
        api_args = {}
        self.uri = '/DSF/{}/'.format(self._service_id)
        DynectSession.get_session().execute(self.uri, 'DELETE', api_args)

    def __str__(self):
        """str override"""
        return force_unicode('<TrafficDirector>: {}, ID: {}').format(
            self._label, self._service_id)

    __repr__ = __unicode__ = __str__

    def __bytes__(self):
        """bytes override"""
        return bytes(self.__str__())

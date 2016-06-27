# -*- coding: utf-8 -*-
"""This module contains interfaces for all Task management features of the
REST API
"""
from dyn.compat import force_unicode
from dyn.tm.session import DynectSession

__author__ = 'mhowes'


def get_tasks():
    response = DynectSession.get_session().execute('/Task', 'GET',
                                                   {})
    return [Task(task.pop('task_id'), api=False, **task)
            for task in response['data']]


class Task(object):
    """A class representing a DynECT Task"""
    def __init__(self, task_id, *args, **kwargs):
        super(Task, self).__init__()
        self._task_id = task_id
        self._blocking = self._created_ts = None
        self._customer_name = self._debug = None
        self._message = self._modified_ts = None
        self._name = self._status = None
        self._step_count = None
        self._total_steps = self._zone_name = None
        self._args = None

        if 'api' in kwargs:
            del kwargs['api']
            self._build(kwargs)

        self.uri = '/Task/{}'.format(self._task_id)

    def _build(self, data):
        """Build this object from the data returned in an API response"""
        for key, val in data.items():
            if key == 'args':
                self._args = [{varg['name']: varg['value']}
                              for varg in val]
            else:
                setattr(self, '_' + key, val)

    @property
    def args(self):
        """Returns List of args, and their value"""
        return self._args

    @property
    def blocking(self):
        """Returns whether this task is in a blocking state."""
        return self._blocking

    @property
    def created_ts(self):
        """Returns Task Creation timestamp"""
        return self._created_ts

    @property
    def customer_name(self):
        """Returns Customer Name"""
        return self._customer_name

    @property
    def debug(self):
        """Returns Debug Information"""
        return self._debug

    @property
    def message(self):
        """Returns Task Message"""
        return self._message

    @property
    def modified_ts(self):
        """Returns Modified Timestamp"""
        return self._modified_ts

    @property
    def name(self):
        """Returns Task Name"""
        return self._name

    @property
    def status(self):
        """Returns Task Status"""
        return self._status

    @property
    def step_count(self):
        """Returns Task Step Count"""
        return self._step_count

    @property
    def task_id(self):
        """Returns Task_id"""
        return self._task_id

    @property
    def total_steps(self):
        """Returns Total number of steps for this task"""
        return self._total_steps

    @property
    def zone_name(self):
        """Returns Zone name for this task"""
        return self._zone_name

    def refresh(self):
        """Updates :class:'Task' with current data on system. """
        api_args = dict()
        response = DynectSession.get_session().execute(self.uri, 'GET',
                                                       api_args)
        self._build(response['data'])

    def cancel(self):
        """Cancels Task"""
        api_args = dict()
        response = DynectSession.get_session().execute(self.uri, 'DELETE',
                                                       api_args)

        self._build(response['data'])

    def __str__(self):
        return force_unicode('<Task>: {} - {} - {} - {} - {}').format(
                             self._task_id, self._zone_name,
                             self._name, self._message, self._status)

    __repr__ = __unicode__ = __str__

    def __bytes__(self):
        """bytes override"""
        return bytes(self.__str__())

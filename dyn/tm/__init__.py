import sys
__author__ = 'jnappi'
version = sys.version_info[0]


class _APIList(list):
    """Custom API List type. All objects in this list are assumed to have a
    _json property, ensuring that they are JSON serializable
    """
    def __init__(self, session_func, name, uri=None, *args, **kwargs):
        """Create an :class:`_APIList` object

        :param session_func: The singleton generator to get the current API
            Session
        :param name: The kwarg key that this :class:`_APIList` represents
        :param uri: The uri this :class:`_APIList` will make calls to
        :param *args: non-kwargs to pass to the super :class:`list` constructor
        :param **kwargs: kwargs to pass to the super :class:`list` constructor
        """
        super(_APIList, self).__init__(*args, **kwargs)
        self.session_func = session_func
        self.name = name
        self.uri = uri

    def __add__(self, item):
        """Handle the addition of an item to this list via an API Call"""
        response = super(_APIList, self).__add__(item)
        self._update(self.__build_args())
        return response

    def append(self, item):
        """Handle an appending of an item to this list via an API Call"""
        response = super(_APIList, self).append(item)
        self._update(self.__build_args())
        return response

    def extend(self, iterable):
        """Handle an extension to this list via an API Call"""
        response = super(_APIList, self).extend(iterable)
        self._update(self.__build_args())
        return response

    def insert(self, index, item):
        """Handle the insertion of an item into this list via an API Call"""
        response = super(_APIList, self).insert(index, item)
        self._update(self.__build_args())
        return response

    def pop(self, *args, **kwargs):
        """Handle the removal via pop of an item in this list via an API Call"""
        response = super(_APIList, self).pop(*args, **kwargs)
        self._update(self.__build_args())
        return response

    def remove(self, item):
        """Handle the removal of an item in this list via an API Call"""
        response = super(_APIList, self).remove(item)
        self._update(self.__build_args())
        return response

    def __iadd__(self, other):
        """Handle the appending of a new list to this list via an API call"""
        response = super(_APIList, self).__iadd__(other)
        self._update(self.__build_args())
        return response

    def __build_args(self):
        """Convert this list into an API Args dict"""
        my_list = [x._json for x in self if x is not None]
        return {self.name: my_list}

    def _update(self, api_args):
        """Private update (PUT) method"""
        if self.session_func is not None and self.uri is not None:
            response = self.session_func().execute(self.uri, 'PUT', api_args)
            data = response['data'][self.name]
            for new_data, item in zip(data, self):
                item._update(new_data)

    def __delitem__(self, key):
        """Handle the deletion of an entry in this list via an API call"""
        response = super(_APIList, self).__delitem__(key)
        self._update(self.__build_args())
        return response


class Active(object):
    """Object for intercepting the active attribute of most services which
    return a non-pythonic 'Y' or 'N' as the active status. This class aims to
    allow for more pythonic interactions with these attributes by allowing the
    active field to be represented as either it's boolean representation or it's
    string 'Y' or 'N' representation.
    """
    def __init__(self, inp):
        """Accept either a string 'Y' or 'N' or a bool as input

        :param inp: If a string, must be one of 'Y' or 'N'. Otherwise a bool.
        """
        self.value = None
        types = tuple()
        if sys.version_info[0] == 2:
            types = (str, unicode)
        elif sys.version_info[0] == 3:
            types = str
        if isinstance(inp, (str, types)):
            self.value = inp.upper() == 'Y'
        if isinstance(inp, bool):
            self.value = inp

    def __nonzero__(self):
        """Returns the value of this :class:`Active` object. In Python 2.x this
        is the magic method called at boolean expression checking time. ie,
        ``if Active('Y')`` will call this method and return True
        """
        return self.value

    # For forwards compatibility with Python 3.x where __bool__ is called when
    # evaluating boolean expressions
    __bool__ = __nonzero__

    def __str__(self):
        """The string representation of this :class:`Active` will return 'Y' or
        'N' depending on the value of ``self.value``
        """
        if self.value:
            return 'Y'
        return 'N'

    # __repr__ and __str__ return the same data
    __repr__ = __str__

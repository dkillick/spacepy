# -*- coding: utf-8 -*-
"""
The datamodel classes consitute a data model implementation
meant to mirror the functionality of the data model output from pycdf, though
implemented slightlydifferently.

This contains the following classes:
 * dmarray - numpy arrays that support .attrs for information about the data
 * SpaceData - base class that extends dict, to be extended by others
    Currently used in GPScode and other projects

 Example:
 >>> import spacepy.datamodel as datamodel
 >>> position = datamodel.dmarray([1,2,3], attrs={'coord_system':'GSM'})
 >>> position
 dmarray([1, 2, 3])
 >>> position.attrs
 {'coord_system': 'GSM'}
"""

from __future__ import division
import numpy, copy

class dmarray(numpy.ndarray):
    """
    Container for data within a SpaceData object

    @author: Brian Larsen, Steve Morley
    @organization: Los Alamos National Lab
    @contact: balarsen@lanl.gov

    @version: V1: 01-Mar-2011 Based on GPSarray from GPScode codebase

    Example:
    >>> import spacepy.datamodel as datamodel
    >>> position = datamodel.dmarray([1,2,3], attrs={'coord_system':'GSM'})
    >>> position
    dmarray([1, 2, 3])
    >>> position.attrs
    {'coord_system': 'GSM'}
    """
    Allowed_Attributes = ['attrs']

    def __new__(cls, input_array, attrs=None):
       # Input array is an already formed ndarray instance
       # We first cast to be our class type
       obj = numpy.asarray(input_array).view(cls)
       # add the new attribute to the created instance
       if attrs != None:
           obj.attrs = attrs
       else:
           obj.attrs = {}
       # Finally, return the newly created object:
       return obj

    def __array_finalize__(self, obj):
       # see InfoArray.__array_finalize__ for comments
        if obj is None:
            return
        for val in self.Allowed_Attributes:
            self.__setattr__(val, getattr(obj, val, {}))

    def __reduce__(self):
        """This is called when pickling, see:
        http://www.mail-archive.com/numpy-discussion@scipy.org/msg02446.html
        for this particular examnple.
        Only the attributes in Allowed_Attributes can exist,
        they are stored and returned for pickling but the names are lost
        attrs remains attrs all others become extra_attr_X where x goes 1, 2, ...
        """
        object_state = list(numpy.ndarray.__reduce__(self))
        subclass_state = tuple([self.__getattribute__(val) for val in self.Allowed_Attributes])
        object_state[2] = (object_state[2],subclass_state)
        return tuple(object_state)

    def __setstate__(self,state):
        """Used for unpickling after __reduce__ the self.attrs is recoved from
        the way it was saved and reset.  The attribute attrs is restored
        correctly others are restored as extra_attr_X where x goes 1, 2, ...
        """
        nd_state, own_state = state
        numpy.ndarray.__setstate__(self,nd_state)
        for val in range(len(own_state)):
            if val == 0: # this is attrs
                self.__setattr__('attrs', own_state[val])
            else:
                self.Allowed_Attributes = self.Allowed_Attributes + ['extra_attr_' + str(val)]
                self.__setattr__('extra_attr_' + str(val), own_state[val])

    def __setattr__(self, name, value):
        """Make sure that .attrs is the only attribute that we are allowing
        dmarray_ne took 15.324803 s
        dmarray_eq took 15.665865 s
        dmarray_assert took 16.025478 s
        It looks like != is the fastest, but not by much over 10000000 __setattr__
        """
        if name == 'Allowed_Attributes':
            pass
        elif not name in self.Allowed_Attributes:
            raise(TypeError("Only attribute listed in Allowed_Attributes can be set"))
        super(dmarray, self).__setattr__(name, value)

class SpaceData(dict):
    """
    Base datamodel class extending dict

    Currently has just method stubs, no real functionality

    @author: Steve Morley
    @organization: Los Alamos National Lab
    @contact: smorley@lanl.gov

    @version: V1: 01-Mar-2011 Based on GPSarray from GPScode codebase
    """

    def __init__(self, *args, **kwargs):
        """
        Base class for "Data Model" representation data

        Abstract method, reimplement
        """
        #raise(ValueError("Abstract method called, reimplement __init__"))
        self.attrs = {}
        if 'attrs' in kwargs:
            if hasattr(kwargs['attrs'], '__getitem__'):
                self.attrs = kwargs['attrs']
            del kwargs['attrs']

        super(SpaceData, self).__init__(*args, **kwargs)


    #def __repr__(self):
        #"""
        #Abstract method, reimplement
        #"""
        #super(SpaceData, self).__repr__()
        ##raise(ValueError("Abstract method called, reimplement __repr__"))

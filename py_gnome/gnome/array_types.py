'''
Module contains array types that a mover may need based on the data
movers needs

** NOTE: **
    These are global declarations

    For instance: If the WindMover that uses array_types.WindMover updates
    the properties of 'windages' ArrayType, it will change it universally.

    The user/mover should not need to change dtype or shape internally. If
    these need to change, it should be done here.

    The initial_value can be changed by movers since that's only used when
    elements are released. For most arrays, that is currently 0.

    As a convention, when a dict defines these array_types, best to use the
    name of the array_type as the 'key'. When other modules, primarily
    element_type, look for numpy array in data_arrays with associated
    array_types, it will assume the 'key' is the name of the array_types.

'''

from gnome.basic_types import (
    world_point_type,
    windage_type,
    status_code_type,
    oil_status,
    id_type)
import numpy as np


class ArrayType(object):

    """
    Object used to capture attributes of numpy data array for elements

    An ArrayType specifies how data arrays associated with elements
    are defined.
    """

    def __init__(
        self,
        shape,
        dtype,
        initial_value=0,
        ):
        """
        constructor for ArrayType

        :param shape: shape of the numpy array
        :type shape: tuple of integers
        :param dtype: numpy datatype contained in array
        :type dtype: numpy dtype
        """

        self.shape = shape
        self.dtype = dtype
        self.initial_value = initial_value

    def initialize_null(self):
        """
        initialize array with 0 elements. Used so SpillContainer can
        initializes all arrays with 0 elements. Used when the model is rewound.
        The purpose is to show all data_arrays even if model is not yet running
        or no particles have been released
        """
        return self.initialize(0)

    def initialize(self, num_elements):
        """
        Initialize a numpy array with the dtype and shape specified. The length
        of the array is given by num_elements and spill is given as input if
        the initialize function needs information about the spill to initialize

        :param num_elements:
        :param spill:
        """
        arr = np.zeros((num_elements,) + self.shape, dtype=self.dtype)
        if self.initial_value != 0:
            arr[:] = self.initial_value
        return arr

    def __eq__(self, other):
        """" Equality of two ArrayType objects """

        if not isinstance(other, self.__class__):
            return False

        if len(self.__dict__) != len(other.__dict__):
            return False

        for (key, val) in self.__dict__.iteritems():
            if key not in other.__dict__:
                return False
            elif val != other.__dict__[key]:

                return False

        # everything passed, then they must be equal

        return True

    def __ne__(self, other):
        """
        Compare inequality (!=) of two objects
        """

        if self == other:
            return False
        else:
            return True


class IdArrayType(ArrayType):
    """
    The 'id' array assigns a unique int for every particle released.
    """
    def initialize(self, num_elements):
        array = np.arange(self.initial_value,
                          num_elements + self.initial_value, dtype=self.dtype)
        return array


# Required array types - dict defined by SpillContainer
positions = ArrayType((3,), world_point_type)
next_positions = ArrayType((3,), world_point_type)
last_water_positions = ArrayType((3,), world_point_type)
status_codes = ArrayType((), status_code_type, oil_status.in_water)
spill_num = ArrayType((), id_type, -1)
id = IdArrayType((), np.uint32)
mass = ArrayType((), np.float64)

# ArrayTypes required by movers. dict defined by movers
windages = ArrayType((), windage_type)
windage_range = ArrayType((2,), np.float64)
windage_persist = ArrayType((), np.int)
rise_vel = ArrayType((), np.float64)

## TODO: Find out if this is still required?
# water_currents = ArrayType( (3,), basic_types.water_current_type)

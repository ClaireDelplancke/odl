# Copyright 2014, 2015 The ODL development group
#
# This file is part of ODL.
#
# ODL is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# ODL is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with ODL.  If not, see <http://www.gnu.org/licenses/>.

# Imports for common Python 2/3 codebase
from __future__ import print_function, division, absolute_import
from __future__ import unicode_literals
from builtins import super, zip
from future import standard_library
standard_library.install_aliases()

# External imports
import numpy as np

# ODL imports
from odl.space.set import Set, RealNumbers
from odl.utility.utility import errfmt, array1d_repr


class IntervalProd(Set):

    """An n-dimensional rectangular box.

    An IntervalProd is a Cartesian product of `n` intervals, i.e. an
    `n`-dimensional rectangular box aligned with the coordinate axes
    as a subset of :math:`R^n`.

    Attributes
    ----------

    +----------+---------------+--------------------------------------+
    |Name      |Type           |Description                           |
    +==========+===============+======================================+
    |`begin`   |`numpy.ndarray`|(Vector of) leftmost interval point(s)|
    |          |or `float`     |                                      |
    +----------+---------------+--------------------------------------+
    |`end`     |`numpy.ndarray`|(Vector of) rightmost interval        |
    |          |or `float`     |point(s)                              |
    +----------+---------------+--------------------------------------+
    |`dim`     |`int`          |Number of axes                        |
    +----------+---------------+--------------------------------------+
    |`truedim` |`int`          |Number of non-degenerate axes, i.e.   |
    |          |               |where `begin != end`                  |
    +----------+---------------+--------------------------------------+
    |`sizes`   |`numpy.ndarray`|(Vector of) interval length(s)        |
    |          |or `float`     |                                      |
    +----------+---------------+--------------------------------------+
    |`volume`  |`float`        |`dim`-dimensional measure             |
    +----------+---------------+--------------------------------------+
    |`midpoint`|`numpy.ndarray`|Vector of interval midpoint(s)        |
    |          |or `float`     |                                      |
    +----------+---------------+--------------------------------------+

    Methods
    -------

    +--------------------+---------------+----------------------------+
    |Signature           |Return type    |Description                 |
    +====================+===============+============================+
    |`equals(other,      |`boolean`      |Test if `other` is equal to |
    |tol=0.0)`           |               |this interval product.      |
    +--------------------+---------------+----------------------------+
    |`contains(other,    |`boolean`      |Test if `other` is contained|
    |tol=0.0)`           |               |in this interval product.   |
    +--------------------+---------------+----------------------------+
    |`measure(dim=None)` |`float`        |Return the `dim`-dimensional|
    |                    |               |measure of this interval    |
    |                    |               |product.                    |
    +--------------------+---------------+----------------------------+
    |`dist(point,        |`float`        |Return the distance in      |
    |ord=2.0)`           |               |`ord`-norm between `point`  |
    |                    |               |and this interval product.  |
    +--------------------+---------------+----------------------------+
    |`collapse(indcs,    |`IntervalProd` |Return the interval product |
    |vals)`              |               |where the intervals at      |
    |                    |               |`indcs` are collapsed to    |
    |                    |               |single values `vals`.       |
    +--------------------+---------------+----------------------------+
    |`insert(other,      |`IntervalProd` |Return the interval product |
    |index)`             |               |where `other` has been      |
    |                    |               |before `index`.             |
    +--------------------+---------------+----------------------------+
    |`corners(order='C')`|`numpy.ndarray`|Return the corner points    |
    |                    |               |of this interval product    |
    |                    |               |in a single array.          |
    +--------------------+---------------+----------------------------+
    |`uniform_sampling(  |`RegularGrid`  |Create a regular grid by    |
    |num_nodes,          |               |sampling this interval      |
    |as_midp=False)`     |               |product at `num_nodes`      |
    |                    |               |equidistant nodes (per      |
    |                    |               |axis).                      |
    +--------------------+---------------+----------------------------+

    See also
    --------
    `RegularGrid` is defined in `odl.discr.grid`.
    """

    def __init__(self, begin, end):
        """
        Parameters
        ----------
        begin : array-like or float
            The lower ends of the intervals in the product
        end : array-like or float
            The upper ends of the intervals in the product

        Examples
        --------

        >>> b, e = [-1, 2.5, 70], [-0.5, 10, 75]
        >>> rbox = IntervalProd(b, e)
        >>> rbox
        IntervalProd([-1.0, 2.5, 70.0], [-0.5, 10.0, 75.0])
        """
        begin = np.atleast_1d(begin).astype(np.float64)
        end = np.atleast_1d(end).astype(np.float64)

        if len(begin) != len(end):
            raise ValueError(errfmt('''
            Lengths of 'begin' ({}) and 'end' ({}) do not match.
            '''.format(len(begin), len(end))))

        if not np.all(begin <= end):
            i_wrong = np.where(begin > end)
            raise ValueError(errfmt('''
            Entries of 'begin' exceed those of 'end' ({!r} > {!r})
            '''.format(list(begin[i_wrong]), list(end[i_wrong]))))

        self._begin = begin
        self._end = end
        self._ideg = np.where(self._begin == self._end)[0]
        self._inondeg = np.where(self._begin != self._end)[0]
        super().__init__()

    # Basic properties
    @property
    def begin(self):
        """The left interval boundary/boundaries."""
        return self._begin

    @property
    def end(self):
        """The right interval boundary/boundaries."""
        return self._end

    @property
    def dim(self):
        """The number of intervals in the product."""
        return len(self._begin)

    @property
    def truedim(self):
        """The number of non-degenerate (zero-length) intervals."""
        return len(self._inondeg)

    @property
    def size(self):
        """The interval length per axis."""
        return self.end - self.begin

    @property
    def volume(self):
        """The 'dim'-dimensional volume of this IntervalProd."""
        return self.measure(dim=self.dim)

    @property
    def midpoint(self):
        """The midpoint of the interval product.

        If dim == 1, a float is returned, otherwise an array.
        """
        midp = (self._end + self._begin) / 2.
        midp[self._ideg] = self._begin[self._ideg]
        return midp[0] if self.dim == 1 else midp

    def element(self):
        """An arbitrary element, the midpoint."""
        return self.midpoint

    # Overrides of the abstract base class methods
    def equals(self, other, tol=0.0):
        """Test if another set is equal to the current one.

        Parameters
        ----------
        other : object
            The object to be tested.
        tol : float, optional
            The maximum allowed difference in 'inf'-norm between the
            interval endpoints.
            Default: 0.0

        Examples
        --------
        >>> from math import sqrt
        >>> rbox1 = IntervalProd(0, 0.5)
        >>> rbox2 = IntervalProd(0, sqrt(0.5)**2)
        >>> rbox1.equals(rbox2)  # Num error
        False
        >>> rbox1 == rbox2  # Equivalent to rbox1.equals(rbox2)
        False
        >>> rbox1.equals(rbox2, tol=1e-15)
        True
        """
        # pylint: disable=arguments-differ
        if not isinstance(other, IntervalProd):
            return False

        return (np.allclose(self.begin, other.begin, atol=tol, rtol=0.0) and
                np.allclose(self.end, other.end, atol=tol, rtol=0.0))

    def contains(self, point, tol=0.0):
        """Test if a point is contained.

        Parameters
        ----------
        point : array-like or float
            The point to be tested. Its length must be equal
            to the set's dimension. In the 1d case, 'point'
            can be given as a float.
        tol : float, optional
            The maximum allowed distance in 'inf'-norm between the
            point and the set.
            Default: 0.0

        Examples
        --------

        >>> from math import sqrt
        >>> b, e = [-1, 0, 2], [-0.5, 0, 3]
        >>> rbox = IntervalProd(b, e)
        >>> rbox.contains([-1 + sqrt(0.5)**2, 0., 2.9])  # Num error
        False
        >>> rbox.contains([-1 + sqrt(0.5)**2, 0., 2.9], tol=1e-15)
        True
        """
        # pylint: disable=arguments-differ
        point = np.atleast_1d(point)

        if len(point) != self.dim:
            return False

        if not RealNumbers().contains(point[0]):
            return False
        if self.dist(point, ord=np.inf) > tol:
            return False
        return True

    def contains_set(self, other, tol=0.0):
        """Test if another set is contained.

        Parameters
        ----------
        other : `Set`
            The set to be tested. It must implement a `min()` and a
            `max()` method, otherwise a `TypeError` is raised.
        tol : float, optional
            The maximum allowed distance in 'inf'-norm between the
            other set and this interval product.
            Default: 0.0
        """
        if not (hasattr(other, 'min') and hasattr(other, 'max')):
            raise TypeError('cannot test `other` {} without `min` and `max`'
                            'attributes.'.format(other))

        return self.contains(other.min, tol) and self.contains(other.max, tol)

    # Additional property-like methods
    def measure(self, dim=None):
        """The (Lebesgue) measure of the IntervalProd instance.

        Parameters
        ----------
        dim : int, optional
              The dimension of the measure to apply.
              Default: truedim

        Examples
        --------

        >>> b, e = [-1, 2.5, 0], [-0.5, 10, 0]
        >>> rbox = IntervalProd(b, e)
        >>> rbox.measure()
        3.75
        >>> rbox.measure(dim=3)
        0.0
        >>> rbox.measure(dim=3) == rbox.volume
        True
        >>> rbox.measure(dim=1)
        inf
        >>> rbox.measure() == rbox.squeeze().volume
        True
        """
        if self.truedim == 0:
            return 0.0

        if dim is None:
            return self.measure(dim=self.truedim)
        elif dim < self.truedim:
            return np.inf
        elif dim > self.truedim:
            return 0.0
        else:
            return np.prod((self._end - self._begin)[self._inondeg])

    def dist(self, point, ord=2.0):
        """Calculate the distance to a point.

        Parameters
        ----------
        point : array-like or float
                The point. Its length must be equal to the set's
                dimension. In the 1d case, 'point' can be given as a
                float.
        ord : non-zero int or float('inf'), optional
              The order of the norm (see numpy.linalg.norm).
              Default: 2.0

        Examples
        --------

        >>> b, e = [-1, 0, 2], [-0.5, 0, 3]
        >>> rbox = IntervalProd(b, e)
        >>> rbox.dist([-5, 3, 2])
        5.0
        >>> rbox.dist([-5, 3, 2], ord=float('inf'))
        4.0
        """
        point = np.atleast_1d(point)
        if len(point) != self.dim:
            raise ValueError(errfmt('''
            'point' dimension ({}) different from set dimension ({}).
            '''.format(len(point), self.dim)))

        i_larger = np.where(point > self._end)
        i_smaller = np.where(point < self._begin)

        # Access [0] since np.where returns tuple.
        if len(i_larger[0]) == 0 and len(i_smaller[0]) == 0:
            return 0.0
        else:
            proj = np.concatenate((point[i_larger], point[i_smaller]))
            border = np.concatenate((self._end[i_larger],
                                     self._begin[i_smaller]))
            return np.linalg.norm(proj - border, ord=ord)

    # Manipulation
    def collapse(self, indcs, values):
        """Partly collapse the interval product to single values.

        Note that no changes are made in-place.

        Parameters
        ----------
        indcs : int or tuple of ints
            The indices of the dimensions along which to collapse
        values : float or array-like
            The values to which to collapse. Must have the same
            lenght as 'indcs'. Values must lie within the interval
            boundaries.

        Returns
        -------
        The collapsed IntervalProd

        Examples
        --------

        >>> b, e = [-1, 0, 2], [-0.5, 1, 3]
        >>> rbox = IntervalProd(b, e)
        >>> rbox.collapse(1, 0)
        IntervalProd([-1.0, 0.0, 2.0], [-0.5, 0.0, 3.0])
        >>> rbox.collapse([1, 2], [0, 2.5])
        IntervalProd([-1.0, 0.0, 2.5], [-0.5, 0.0, 2.5])
        >>> rbox.collapse([1, 2], [0, 3.5])
        Traceback (most recent call last):
            ...
        ValueError: 'values' not within interval boundaries ([3.5] >
        [3.0])
        """
        indcs = np.atleast_1d(indcs)
        values = np.atleast_1d(values)
        if len(indcs) != len(values):
            raise ValueError(errfmt('''
            lengths of 'indcs' ({}) and 'values' ({}) do not match
            '''.format(len(indcs), len(values))))

        if np.any(indcs < 0) or np.any(indcs >= self.dim):
            raise IndexError(errfmt('''
            'indcs'({!r}) out of range (max {})
            '''.format(list(indcs), self.dim)))

        if np.any(values < self._begin[indcs]):
            i_smaller = np.where(values < self._begin[indcs])
            raise ValueError(errfmt('''
            'values' not within interval boundaries ({!r} < {!r})
            '''.format(list(values[i_smaller]),
                       list((self._begin[indcs])[i_smaller]))))

        if np.any(values > self._end[indcs]):
            i_larger = np.where(values > self._end[indcs])
            raise ValueError(errfmt('''
            'values' not within interval boundaries ({!r} > {!r})
            '''.format(list(values[i_larger]),
                       list((self._end[indcs])[i_larger]))))

        b_new = self._begin.copy()
        b_new[indcs] = values
        e_new = self._end.copy()
        e_new[indcs] = values

        return IntervalProd(b_new, e_new)

    def squeeze(self):
        """Remove the degenerate dimensions.

        Note that no changes are made in-place.

        Returns
        -------
        The squeezed IntervalProd

        Examples
        --------

        >>> b, e = [-1, 0, 2], [-0.5, 1, 3]
        >>> rbox = IntervalProd(b, e)
        >>> rbox.collapse(1, 0).squeeze()
        IntervalProd([-1.0, 2.0], [-0.5, 3.0])
        >>> rbox.collapse([1, 2], [0, 2.5]).squeeze()
        IntervalProd([-1.0], [-0.5])
        >>> rbox.collapse([0, 1, 2], [-1, 0, 2.5]).squeeze()
        IntervalProd([], [])
        """
        b_new = self._begin[self._inondeg]
        e_new = self._end[self._inondeg]
        return IntervalProd(b_new, e_new)

    def insert(self, other, index):
        """Insert another IntervalProd before the given index.

        The given IntervalProd (dim=m) is inserted into the current
        one (dim=n) before the given index, resulting in a new
        IntervalProd of dimension n+m.
        Note that no changes are made in-place.

        Parameters
        ----------
        other : IntervalProd, float or array-like
            The IntervalProd to be inserted. A float or array a is
            treated as an IntervalProd(a, a).
        index : int
            The index of the dimension before which 'other' is to
            be inserted. Must fulfill 0 <= index <= dim.

        Returns
        -------
        The enlarged IntervalProd

        Examples
        --------

        >>> rbox = IntervalProd([-1, 2], [-0.5, 3])
        >>> rbox2 = IntervalProd([0, 0], [1, 0])
        >>> rbox.insert(rbox2, 1)
        IntervalProd([-1.0, 0.0, 0.0, 2.0], [-0.5, 1.0, 0.0, 3.0])
        >>> rbox.insert([-1.0, 0.0], 2)
        IntervalProd([-1.0, 2.0, -1.0, 0.0], [-0.5, 3.0, -1.0, 0.0])
        >>> rbox.insert(0, 1).squeeze().equals(rbox)
        True
        """
        if not 0 <= index <= self.dim:
            raise IndexError('Index ({}) out of range'.format(index))

        if not isinstance(other, IntervalProd):
            other = IntervalProd(other, other)

        new_beg = np.empty(self.dim + other.dim)
        new_end = np.empty(self.dim + other.dim)

        new_beg[: index] = self._begin[: index]
        new_end[: index] = self._end[: index]
        new_beg[index: index+other.dim] = other.begin
        new_end[index: index+other.dim] = other.end
        if index < self.dim:  # Avoid IndexError
            new_beg[index+other.dim:] = self._begin[index:]
            new_end[index+other.dim:] = self._end[index:]

        return IntervalProd(new_beg, new_end)

    def corners(self, order='C'):
        """The corner points in a single array.

        Parameters
        ----------

        order : 'C' or 'F'
            The ordering of the axes in which the corners appear in
            the output.

        Returns
        -------

        out : numpy.ndarray
            The size of the array is 2^m x dim, where m is the number of
            non-degenerate axes, i.e. the corners are stored as rows.

        Examples
        --------

        >>> rbox = IntervalProd([-1, 2, 0], [-0.5, 3, 0.5])
        >>> rbox.corners()
        array([[-1. ,  2. ,  0. ],
               [-1. ,  2. ,  0.5],
               [-1. ,  3. ,  0. ],
               [-1. ,  3. ,  0.5],
               [-0.5,  2. ,  0. ],
               [-0.5,  2. ,  0.5],
               [-0.5,  3. ,  0. ],
               [-0.5,  3. ,  0.5]])
        >>> rbox.corners(order='F')
        array([[-1. ,  2. ,  0. ],
               [-0.5,  2. ,  0. ],
               [-1. ,  3. ,  0. ],
               [-0.5,  3. ,  0. ],
               [-1. ,  2. ,  0.5],
               [-0.5,  2. ,  0.5],
               [-1. ,  3. ,  0.5],
               [-0.5,  3. ,  0.5]])
        """
        from odl.discr.grid import TensorGrid
        if order not in ('C', 'F'):
            raise ValueError(errfmt('''
            Value of 'order' ({}) must be 'C' or 'F'.'''.format(order)))

        minmax_vecs = [0] * self.dim
        for axis in self._ideg:
            minmax_vecs[axis] = self._begin[axis]
        for axis in self._inondeg:
            minmax_vecs[axis] = (self._begin[axis], self._end[axis])

        minmax_grid = TensorGrid(*minmax_vecs)
        return minmax_grid.points(order=order)

    def uniform_sampling(self, num_nodes, as_midp=False):
        """Produce equispaced nodes, a RegularGrid.

        Parameters
        ----------

        num_nodes : int or tuple of int's
            The number of nodes per axis. For dim=1, a single int may
            be given. All entries must be positive. Entries
            corresponding to degenerate axes must be equal to 1.
        as_midp : boolean, optional
            If True, the midpoints of an interval partition will be
            returned, which excludes the endpoints. Otherwise,
            equispaced nodes including the endpoints are generated.
            Note that the resulting strides are different.
            Default: False.

        Returns
        -------

        sampling : grid.RegularGrid

        Examples
        --------

        >>> rbox = IntervalProd([-1, 2], [-0.5, 3])
        >>> grid = rbox.uniform_sampling([2, 5])
        >>> grid.coord_vectors
        (array([-1. , -0.5]), array([ 2.  ,  2.25,  2.5 ,  2.75,  3.  ]))
        >>> grid = rbox.uniform_sampling([2, 5], as_midp=True)
        >>> grid.coord_vectors
        (array([-0.875, -0.625]), array([ 2.1,  2.3,  2.5,  2.7,  2.9]))
        """
        from odl.discr.grid import RegularGrid
        num_nodes = np.atleast_1d(num_nodes).astype(np.int64)

        if np.any(np.isinf(self._begin)) or np.any(np.isinf(self._end)):
            raise ValueError(errfmt('''
            Uniform sampling undefined for infinite domains.'''))

        if num_nodes.shape != (self.dim,):
            raise ValueError(errfmt('''
            'num_nodes' ({}) must have shape ({},).
            '''.format(num_nodes.shape, self.dim)))

        if np.any(num_nodes <= 0):
            raise ValueError(errfmt('''
            All entries of 'num_nodes' must be positive.'''))

        if np.any(num_nodes[self._ideg] > 1):
            raise ValueError(errfmt('''
            Degenerate axes {} cannot be sampled with more than one
            node.'''.format(tuple(self._ideg))))

        center = self.midpoint
        stride = (self.size / num_nodes if as_midp else
                  self.size / (num_nodes - 1))
        return RegularGrid(num_nodes, center, stride)

    # Magic methods
    def __repr__(self):
        return ('IntervalProd({}, {})'.format(
            array1d_repr(self._begin), array1d_repr(self._end)))

    def __str__(self):
        return ' x '.join('[{}, {}]'.format(b, e)
                          for (b, e) in zip(self._begin, self._end))

    def __len__(self):
        return self.dim


class Interval(IntervalProd):
    """ The set of real numbers in the interval [begin, end]
    """
    def __init__(self, begin, end):
        super().__init__(begin, end)
        if self.dim != 1:
            raise ValueError(errfmt('''
            'begin' and 'end' must scalar or have length 1 (got {}).
            '''.format(self.dim)))

    @property
    def length(self):
        """ The length of this interval
        """
        return self.end - self.begin

    def __repr__(self):
        return 'Interval({}, {})'.format(self.begin[0], self.end[0])


class Rectangle(IntervalProd):
    def __init__(self, begin, end):
        super().__init__(begin, end)
        if self.dim != 2:
            raise ValueError(errfmt('''
            Lengths of 'begin' and 'end' must be equal to 2 (got {}).
            '''.format(self.dim)))

    @property
    def area(self):
        """ The area of this triangle
        """
        return self.volume

    def __repr__(self):
        return ('Rectangle({!r}, {!r})'.format(list(self._begin),
                                               list(self._end)))


class Cube(IntervalProd):
    def __init__(self, begin, end):
        super().__init__(begin, end)
        if self.dim != 3:
            raise ValueError(errfmt('''
            Lengths of 'begin' and 'end' must be equal to 3 (got {}).
            '''.format(self.dim)))

    def __repr__(self):
        return ('Cube({!r}, {!r})'.format(list(self._begin),
                                          list(self._end)))
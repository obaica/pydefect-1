# -*- coding: utf-8 -*-
#  Copyright (c) 2020. Distributed under the terms of the MIT License.
import numpy as np
import pytest
from math import sqrt
from pymatgen import Lattice, Structure

from pydefect.input_maker.supercell import (
    Supercell, Supercells, TetragonalSupercells, RhombohedralSupercells,
    CreateSupercell)
from pydefect.util.error_classes import NoSupercellError, NotPrimitiveError


@pytest.fixture
def simple_cubic_supercell():
    lattice = Lattice.orthorhombic(2.0, 1.0, 1.0)
    coords = [[0.0, 0.0, 0.0], [0.5, 0.0, 0.0]]
    results = Structure(lattice=lattice, species=["H", "H"], coords=coords)

    return results


def test_supercell(simple_cubic, simple_cubic_supercell):
    matrix = [[2, 0, 0], [0, 1, 0], [0, 0, 1]]
    supercell = Supercell(input_structure=simple_cubic, matrix=matrix)
    assert supercell.structure == simple_cubic_supercell

    average = (2 + 1 + 1) / 3
    expected = (abs(2 - average) + abs(1 - average) * 2) / 3 / average
    assert supercell.isotropy == expected


def test_supercell_average_angle(monoclinic):
    matrix = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
    supercell = Supercell(input_structure=monoclinic, matrix=matrix)
    assert supercell.average_angle == (90 + 90 + 100) / 3


def test_supercells(simple_cubic):
    supercells = Supercells(input_structure=simple_cubic,
                            min_num_atoms=64,
                            max_num_atoms=100)
    expected = simple_cubic * [[4, 0, 0], [0, 4, 0], [0, 0, 4]]
    assert isinstance(supercells.most_isotropic_supercell, Supercell)
    assert supercells.most_isotropic_supercell.structure == expected


def test_supercells_raise_no_supercell_error(simple_cubic):
    supercells = Supercells(input_structure=simple_cubic,
                            min_num_atoms=10,
                            max_num_atoms=10)
    with pytest.raises(NoSupercellError):
        print(supercells.most_isotropic_supercell)


def test_rhombohedral_supercells(rhombohedral):
    supercells = RhombohedralSupercells(input_structure=rhombohedral,
                                        min_num_atoms=2,
                                        max_num_atoms=4)
    actual = supercells.most_isotropic_supercell.lattice.angles[0]
    assert actual == 74.85849218561553


def test_tetragonal_supercells(elongated_tetragonal):
    supercells = TetragonalSupercells(input_structure=elongated_tetragonal,
                                      min_num_atoms=2,
                                      max_num_atoms=300)
    actual = supercells.most_isotropic_supercell.lattice.lengths
    expected = (4.242640687119285, 4.242640687119285, 4.242640687119286)
    assert actual == expected

    actual = supercells.most_isotropic_supercell.matrix
    expected = np.array([[3, 3, 0], [-3, 3, 0], [0, 0, 1]])
    np.testing.assert_array_equal(actual, expected)


def test_matrix_from_x_y():
    actual = TetragonalSupercells.matrix_from_x_y(2, 0)
    expected = np.array([[2, 0], [0, 2]])
    np.testing.assert_array_equal(actual, expected)

    actual = TetragonalSupercells.matrix_from_x_y(2, 1)
    expected = np.array([[2, 2], [-2, 2]])
    np.testing.assert_array_equal(actual, expected)

    actual = TetragonalSupercells.matrix_from_x_y(1, 2)
    expected = np.array([[0, 2], [-2, 0]])  # rotate the axis
    np.testing.assert_array_equal(actual, expected)


def test_next_x_y_combination():
    assert TetragonalSupercells.next_x_y_combination(24) == (5, 0)
    assert TetragonalSupercells.next_x_y_combination(25) in [(2, 3), (1, 5)]


@pytest.fixture
def tetra_close_to_cubic():
    lattice = Lattice.tetragonal(1.001 * 10 / sqrt(2), 10)
    coords = [[0.0, 0.0, 0.0]]
    results = Structure(lattice=lattice, species=["H"], coords=coords)

    return results


def test_create_supercell_tetragonal(tetra_close_to_cubic):
    cs = CreateSupercell(tetra_close_to_cubic)
    actual = cs.supercell.matrix
    expected =[[ 5,  5,  0],
               [-5,  5,  0],
               [ 0,  0,  5]]
    np.testing.assert_array_equal(actual, expected)


def test_create_supercell(a_centered_orthorhombic):
    cs = CreateSupercell(a_centered_orthorhombic)
    actual_lattice = cs.conv_structure.lattice
    expected = Lattice.orthorhombic(1, 4, 6)
    assert actual_lattice == expected

    actual = cs.supercell.matrix
    expected =[[6,  0,  0],
               [0,  2,  0],
               [0,  0,  1]]
    np.testing.assert_array_equal(actual, expected)


def test_create_supercell_raise_not_primitive_error(bcc):
    with pytest.raises(NotPrimitiveError):
        CreateSupercell(input_structure=bcc)


def test_create_supercell_matrix(a_centered_orthorhombic):
    matrix = [[2, 0, 0], [0, 1, 0], [0, 0, 1]]
    cs = CreateSupercell(a_centered_orthorhombic, matrix=matrix)
    actual = cs.supercell.matrix
    np.testing.assert_array_equal(actual, matrix)


"""
TODO


DONE
- Expand for rhombohedral cell.
- Expand for tetragonal cell.
- Input of structure and trans_mat returns supercell
- Return isotropy
- Return average angle
- Recommend the least isotropic supercell of simple cubic within a given number of atom range.
  When the isotropy is the same, smallest supercell is returned.
- Check max_num_atoms
- Raise NoSupercellError 

REJECT
+ Allow to write the supercell down a file.
    -> Structure already has to, which should be used.
"""
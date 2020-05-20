# -*- coding: utf-8 -*-
#  Copyright (c) 2020. Distributed under the terms of the MIT License.

import pytest

from pydefect.analyzer.defect_energy import (
    SingleDefectEnergy, DefectEnergy, CrossPoints, DefectEnergies)
from pydefect.tests.helpers.assertion import assert_msonable


def test_single_defect_energy():
    assert_msonable(SingleDefectEnergy(name="Va_O1", charge=0, energy=1.0))


@pytest.fixture
def defect_energy():
    return DefectEnergy(name="Va_O1",
                        charges=[0, 1, 2],
                        energies=[6, 3, -4])


def test_defect_energy_cross_points(defect_energy):
    actual = defect_energy.cross_points(1, 6)
    expected = CrossPoints([[5.0, 6.0]], [[1.0, -2.0], [6.0, 6.0]])
    assert actual == expected


@pytest.fixture
def cross_points():
    inner_cross_points = [[2, 20], [3, 30], [4, 40]]
    boundary_points = [[1, 10], [5, 50]]
    return CrossPoints(inner_cross_points, boundary_points)


def test_cross_points(cross_points):
    assert cross_points.all_sorted_points == [[1, 10], [2, 20], [3, 30], [4, 40], [5, 50]]
    assert cross_points.t_all_sorted_points == [[1, 2, 3, 4, 5], [10, 20, 30, 40, 50]]
    assert cross_points.t_inner_cross_points == [[2, 3, 4], [20, 30, 40]]
    assert cross_points.t_boundary_points == [[1, 5], [10, 50]]


def test_defect_energies(defect_energy):
    defect_energies = DefectEnergies([defect_energy],
                                     vbm=1.0,
                                     cbm=6.0,
                                     supercell_vbm=1.5,
                                     supercell_cbm=5.5)
    plt = defect_energies.plot()
    plt.show()


"""
TODO
- Evaluate the crossing points at given Fermi level range.


DONE
- Draw a single defect
- Correction.
"""
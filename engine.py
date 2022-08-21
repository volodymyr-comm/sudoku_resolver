from threading import Thread, Event
from math import floor
import pandas as pd
import numpy as np
import itertools


def resolve(data_array: np.ndarray):
    if (9, 9) != data_array.shape:
        raise Exception('Wrong input data shape')

    found_matrix = data_array.copy()

    # create matrix with preliminary possibilities
    possibility_matrix = np.full((9, 9, 9), np.nan)
    for i in range(9):
        possibility_matrix[i, :, :][np.isnan(data_array)] = i+1

    ret_status, ret_matrix = _resolve_by_possibility_matrix(found_matrix, possibility_matrix)
    return ret_status, ret_matrix


def _resolve_by_possibility_matrix(found_matrix: np.ndarray, possibility_matrix: np.ndarray):
    _found_matrix = found_matrix.copy()
    _possibility_matrix = possibility_matrix.copy()
    while np.isnan(_found_matrix).any():
        possibility_matrix_before_cycle = _possibility_matrix.copy()
        for y in range(9):
            square_y0 = floor(y / 3) * 3
            for x in range(9):
                square_x0 = floor(x / 3) * 3
                if not np.isnan(_found_matrix[y, x]):
                    continue
                square_known_values = _found_matrix[square_y0:square_y0+3, square_x0:square_x0+3]
                column_known_values = _found_matrix[:, x]
                row_known_values = _found_matrix[y, :]
                cell_possibilities = _possibility_matrix[:, y, x]
                # by known values
                cell_possibilities[np.in1d(cell_possibilities, square_known_values)] = np.nan
                cell_possibilities[np.in1d(cell_possibilities, column_known_values)] = np.nan
                cell_possibilities[np.in1d(cell_possibilities, row_known_values)] = np.nan
                cell_possibilities = cell_possibilities[~np.isnan(cell_possibilities)]

                # by possibilities in dependencies
                column_dependency_possibilities = _possibility_matrix[:, :, x].ravel()
                row_dependency_possibilities = _possibility_matrix[:, y, :].ravel()
                square_dependency_possibilities = _possibility_matrix[:, square_x0:square_x0+3, square_y0:square_y0+3].ravel()
                possibilities_in_dependencies = np.concatenate((column_dependency_possibilities,
                                                               row_dependency_possibilities,
                                                               square_dependency_possibilities))
                possibilities_not_in_dependencies = cell_possibilities[~np.in1d(cell_possibilities, possibilities_in_dependencies)]
                possibilities_not_in_dependencies = possibilities_not_in_dependencies[~np.isnan(possibilities_not_in_dependencies)]

                # check if cell solution is found
                # print(x, y, cell_possibilities)

                if len(cell_possibilities) == 1:
                    _found_matrix[y, x] = cell_possibilities[0]
                    # self._set_value(x, y, found_matrix[y, x])
                    continue

                if len(possibilities_not_in_dependencies) == 1:
                    if possibilities_not_in_dependencies[0] not in cell_possibilities:
                        print(f'Oops, cell {x, y}: the only possible value based on possibilities in dependencies does not belong to cell possibilities')
                        return 0, _found_matrix
                        # raise Exception(f'Oops, cell {x, y}: the only possible value based on'
                        #                 f' possibilities in dependencies does not belong to cell possibilities')
                    _found_matrix[y, x] = cell_possibilities[0]
                    # self._set_value(x, y, found_matrix[y, x])

                if len(cell_possibilities) == 0:
                    print(f'Oops, cell {x, y} has no possible values')
                    return 0, _found_matrix
                    # raise Exception(f'Oops, cell {x, y} has no possible values')
        if np.array_equal(possibility_matrix_before_cycle, _possibility_matrix, equal_nan=True):
            # nothing is found in current cycle. It means we must pick one of possible values, and check if
            # might it be a solution

            # sort unknown cells by number of possibilities: {(x,y): len-non-zero} representation
            _xy_combinations = itertools.product(range(9), range(9))
            _possibility_counts_dict = {(y, x): np.count_nonzero(~np.isnan(_possibility_matrix[:, y, x])) for y, x in _xy_combinations}
            _possibility_counts_sorted_dict = dict(sorted(_possibility_counts_dict.items(), key=lambda item: item[1]))
            for (y, x), nof_possibilities in _possibility_counts_sorted_dict.items():
                print(_found_matrix[y, x], _possibility_matrix[:, y, x])
                if not np.isnan(_found_matrix[y, x]):
                    continue
                _cell_possibilities = _possibility_matrix[:, y, x]
                _cell_possibilities = _cell_possibilities[~np.isnan(_cell_possibilities)]
                assert nof_possibilities == len(_cell_possibilities), 'Invalid possibilities count'
                assert not (len(_cell_possibilities) == 1 and np.isnan(_found_matrix[y, x])), 'Something wrong happened in dependency analysis part of code'
                if len(_cell_possibilities) < 2:
                    continue
                for appointed_possibility in _cell_possibilities:
                    _picked_value_matrix = _found_matrix.copy()
                    _picked_value_matrix[y, x] = appointed_possibility
                    ret_status, ret_matrix = _resolve_by_possibility_matrix(_picked_value_matrix, _possibility_matrix)
                    if ret_status:
                        return 1, ret_matrix
            print(f'Oops, solution is not found')
            return 0, _found_matrix
    return 1, _found_matrix

import numpy as np


def ind_to_coord(ind, n_rows, n_cols):
    return np.unravel_index(ind, (n_rows, n_cols))


def coord_to_ind(coord, n_rows, n_cols):
    return np.ravel_multi_index(coord, (n_rows, n_cols))


def neigh_coord_to_ind(coord, n_rows, n_cols):
    ix, iy = coord
    return coord_to_ind([[np.max([ix-1, 0]), np.min([ix+1, n_rows-1]), ix, ix],
                        [iy, iy, np.max([iy-1, 0]), np.min([iy+1, n_cols-1])]],
                        n_rows, n_cols)


def extract_curve(dist_map, end_point):
    n_rows, n_cols = dist_map.shape

    curve = [(end_point[0], end_point[1])]
    u_min = dist_map[curve[-1]]

    while u_min != 0:
        neigh_ind = neigh_coord_to_ind(curve[-1], n_rows, n_cols)
        u = dist_map[ind_to_coord(neigh_ind, n_rows, n_cols)]
        arg_min = np.argmin(u)
        u_min = np.min(u)
        curve.append(ind_to_coord(neigh_ind[arg_min], n_rows, n_cols))

    return np.array(np.flip(curve, 0))

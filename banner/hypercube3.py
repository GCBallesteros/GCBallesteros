from itertools import product

import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d.art3d import Line3DCollection


def rotate_4d(point, axis1, axis2, angle):
    """
    Rotate a 4D point around two specified axes in 4D space.
    """
    cos_a = np.cos(angle)
    sin_a = np.sin(angle)

    rotation_matrix = np.eye(4)
    rotation_matrix[axis1, axis1] = cos_a
    rotation_matrix[axis1, axis2] = -sin_a
    rotation_matrix[axis2, axis1] = sin_a
    rotation_matrix[axis2, axis2] = cos_a

    return np.dot(rotation_matrix, point)


def stereographic_projection(point):
    # Assume the 4D point is represented as a NumPy array
    x, y, z, w = point

    # Stereographic projection formulas
    u = x / (1 - w)
    v = y / (1 - w)
    z_proj = z / (1 - w)

    return u, v, z_proj


def three_d_hypercube(edges_array, angle):
    stereo_coords = np.zeros((32, 3, 2))
    for iii in range(32):
        for jjj in range(2):
            stereo_coords[iii, :, jjj] = np.array(
                stereographic_projection(
                    rotate_4d(edges_array[iii, :, jjj], 2, 3, angle)
                )
            )
    return stereo_coords


n_dims = 4
corner_coords = [f"{{:0{int(n_dims)}b}}".format(i) for i in range(2**n_dims)]


corner_coords_ = np.array([[float(x) for x in corner] for corner in corner_coords])


edges = []
for first, second in product(corner_coords, corner_coords):
    # Filter out:
    # 1. Origin and destiny are the same (first == second)
    # 2. Where we change in more than 1 bit
    if first != second and sum(map(lambda x: x[0] != x[1], zip(first, second))) == 1:
        edges.append((first, second))

# Finally remove duplicates. First we need to sort each edge to be able to use
# the set trick
edges = {tuple(sorted(edge)) for edge in edges}

# dimensions: edge, x,y,z,t..., (start point, end_point)
n_edges = len(edges)
edges_array = np.zeros((n_edges, n_dims, 2))
for idx, edge_ in enumerate(edges):
    # last dimensions correspond to the extremes of the edge.
    # 0 is start points
    # 1 is end points
    for loc in [0, 1]:
        edges_array[idx, :, loc] = tuple(int(x) for x in edge_[loc])

# Center the hypercube around the origin
edges_array -= 0.5

for idx, angle in enumerate(np.linspace(0, np.pi / 2, 60)):
    stereo_coords = three_d_hypercube(edges_array, angle)

    segment_collection = [
        (s, e) for s, e in zip(stereo_coords[:, :, 0], stereo_coords[:, :, 1])
    ]

    lc = Line3DCollection(segment_collection, color="k")
    fig = plt.figure(figsize=(10, 10))
    ax = fig.add_subplot(111, projection="3d")
    ax.auto_scale_xyz([-1.4, 1.4], [-1.4, 1.4], [-1.4, 1.4])
    ax.add_collection(lc)
    plt.axis("equal")

    # Hide axes
    ax.set_axis_off()

    fig.savefig(f"./hypercube_frames/frame_{idx:03}.png")
    plt.close(fig)
# %%

import old_border_solver
import middle_solver
from BorderWrap.border_solver import *

def print_grid1(grid: List[List[Piece]]):
    for y in range(len(grid)):
        s = ''
        for x in range(len(grid[0])):
            piece = grid[x][y]
            if piece is None:
                s += 'N:[N, N, N, N] '
                continue
            s += str(piece.id) + ':' + str(piece.edges) + ' '
        print(s)

def print_grid2(grid: List[List[Piece]]):
    for y in range(len(grid)):
        s = ''
        for x in range(len(grid[0])):
            piece = grid[x][y]
            if piece is None:
                s += 'N:[N, N, N, N] '
                continue
            s += str(piece.id) + ':' + str(piece.get_grid2_edges()) + ' '
        print(s)

def analyze_corner_distribution(ring2):
    """Check where Grid1 corners end up in Grid2"""
    size = int(len(ring2) / 4) + 1
    corner_positions_in_grid2 = []
    for i, piece in enumerate(ring2):
        if piece.id % (size - 1) == 2:
            ring2_pos = int(i / (size - 1))
            ring1_pos = int(piece.id / (size - 1)) - 4
            corner_positions_in_grid2.append((piece.id, ring1_pos, ring2_pos))
    return corner_positions_in_grid2


def analyze_neighbor_distances(ring1, ring2):
        """How far apart are Grid1 neighbors in Grid2?"""
        distances = []
        for i, piece in enumerate(ring1):
                grid2_index = ring2.index(piece)
                right_neighbor = ring1[(i + 1) % len(ring1)]
                right_neighbor_grid2_index = ring2.index(right_neighbor)

                # Distance around the ring
                distance = abs(grid2_index - right_neighbor_grid2_index)
                distance = min(distance, len(ring2) - distance)  # Shorter path around ring
                distances.append(distance)

        return distances


def analyze_move_distances(ring1, ring2):
        """How far apart are Grid1 pieces moved in Grid2?"""
        distances = []
        for i, piece in enumerate(ring1):
                grid2_index = ring2.index(piece)

                # Distance around the ring
                distance = abs(grid2_index - grid2_index)
                distance = min(distance, len(ring2) - distance)  # Shorter path around ring
                distances.append(distance)

        return distances

SIZE = 5

# Solve for borders
border_pieces = old_border_solver.init_pieces(SIZE)
old_border_solver.init_domains(SIZE, border_pieces)
border_solutions = old_border_solver.solve_ring(border_pieces, 1)

grid1_5x5_list = []
grid2_5x5_list = []
for border_solution in border_solutions:
    grid1_5x5_solutions, grid2_5x5_solutions = middle_solver.solve(border_solution, SIZE)
    grid1_5x5_list += grid1_5x5_solutions
    grid2_5x5_list += grid2_5x5_solutions

grid1_7x7_list = []
grid2_7x7_list = []
min_backtracks = float("inf")
max_backtracks = 0
total_backtracks = 0
for i in range(len(grid1_5x5_list)):
    grid1_5x5 = grid1_5x5_list[i]
    grid2_5x5 = grid2_5x5_list[i]

    new_ring1, new_ring2_list, new_grid1_list, new_grid2_list, backtrack_count = solve_new_borders_from_grid(grid1_5x5, grid2_5x5, 1)

    grid1_7x7_list += new_grid1_list
    grid2_7x7_list += new_grid2_list

    min_backtracks = min(min_backtracks, backtrack_count)
    max_backtracks = max(max_backtracks, backtrack_count)
    total_backtracks += backtrack_count

    print_grid1(new_grid1_list[0])
    print()
    print_grid2(new_grid2_list[0])

print(len(grid2_7x7_list))
print("Min backtracks:", min_backtracks)
print("Max backtracks:", max_backtracks)
print("Total backtracks:", total_backtracks)
print("Avg backtracks:", total_backtracks / len(grid2_7x7_list))
print("=================================================================================")
# print(len(solutions))
# print_ring(solutions[0])

# for solution in solutions:
#         corner_distribution = analyze_corner_distribution(solution)
#         neighbor_distances = analyze_neighbor_distances(outer_ring1, solution)
#         move_distances = analyze_move_distances(outer_ring1, solution)

# solutions = solve_new_borders(solutions[0], 1)
# print(len(solutions))
# print_ring(solutions[0])
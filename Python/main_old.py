from typing import List

import BorderWrap.border_solver as border_solver
import middle_solver
from middle_solver import Piece

SIZE = 5

# Solve for borders
border_pieces = border_solver.init_pieces(SIZE)
border_solver.init_domains(SIZE, border_pieces)
border_solutions = border_solver.solve_ring(border_pieces, 10000)

solutions = []

for border_solution in border_solutions:
    grid1, middle_solutions = middle_solver.solve(border_solution, SIZE)
    solutions += middle_solutions
    if len(solutions) > 0:
        break

for y in range(SIZE):
    s = ''
    for x in range(SIZE):
        piece = grid1[x][y]
        if piece is None:
            s += 'N:[N, N, N, N] '
            continue
        s += str(piece.id) + ':' + str(piece.edges) + ' '
    print(s)

print()

solution = solutions[0]
for y in range(SIZE):
    s = ''
    for x in range(SIZE):
        piece = solution[x][y]
        if piece is None:
            s += 'N:[N, N, N, N] '
            continue
        s += str(piece.id) + ':' + str(piece.edges) + ' '
    print(s)

# Use borders to solve for middle
# for border_solution in border_solutions:
#     grid1, middle_solutions = middle_solver.solve(border_solution, SIZE)
#     solutions += middle_solutions
#     len_solutions[len(middle_solutions)] += 1
#     if len(middle_solutions) > 0:
#         border_count += 1
# print(len(solutions))
# print(border_count)
# for i in range(len(len_solutions)):
#     if len_solutions[i] == 0:
#         continue
#     print(len_solutions[i], 'borders with', i, 'solutions')

# for y in range(SIZE):
#     s = ''
#     for x in range(SIZE):
#         piece = grid1[x][y]
#         s += str(piece.id) + ':' + str(piece.edges) + ' '
#     print(s)
# print()
# # for grid2 in solutions:
# #     for y in range(SIZE):
# #         s = ''
# #         for x in range(SIZE):
# #             piece = grid2[x][y]
# #             if piece is None:
# #                 s += 'N:[0, 0, 0, 0] '
# #                 continue
# #             s += str(piece.id) + ':' + str(piece.get_grid2_edges()) + ' '
# #         print(s)
# #     print()
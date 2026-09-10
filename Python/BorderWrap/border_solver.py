from enum import Enum
from time import time
from typing import List, Tuple

import copy

from middle_solver import Piece


DEBUG_LEVEL = 0

UP = 0
RIGHT = 1
DOWN = 2
LEFT = 3

class BorderPiece:
    def __init__(self, id):
        self.id = id
        self.edges = [0] * 4
        self.required_neighbors = [None] * 4
        self.domain = []
        self.ring2_rotation = 0

    def __str__(self):
        return str(self.id)

def get_left_neighbor(ring: List[BorderPiece], piece: BorderPiece) -> BorderPiece:
    idx = (ring.index(piece) + len(ring) - 1) % len(ring)
    return ring[idx]

def get_right_neighbor(ring: List[BorderPiece], piece: BorderPiece) -> BorderPiece:
    idx = (ring.index(piece) + len(ring) + 1) % len(ring)
    return ring[idx]

def print_ring(ring: List[BorderPiece]):
    s = ''
    for piece in ring:
        if piece is None: s += 'N '
        else: s += str(piece) + ' '
    print(s)

def solve_new_borders_from_grid(grid1: List[List[Piece]], grid2: List[List[Piece]], max_solutions: int = 0):
    def unwrap_ring_from_grid() -> List[BorderPiece]:
        ring = []
        size = len(grid2)

        # Top-left corner
        ring.append(BorderPiece(grid2[0][0].id))
        # Top sides
        for x in range(1, size-1):
            ring.append(BorderPiece(grid2[x][0].id))
        # Top-right corner
        ring.append(BorderPiece(grid2[size - 1][0].id))
        # Right sides
        for y in range(1, size-1):
            ring.append(BorderPiece(grid2[size - 1][y].id))
        # Bottom-right corner
        ring.append(BorderPiece(grid2[size - 1][size - 1].id))
        # Bottom sides
        for x in range(size-2, 0, -1):
            ring.append(BorderPiece(grid2[x][size - 1].id))
        # Bottom-left corner
        ring.append(BorderPiece(grid2[0][size - 1].id))
        # Left sides
        for y in range(size-2, 0, -1):
            ring.append(BorderPiece(grid2[0][y].id))

        return ring

    def wrap_ring_around_grid(ring2: List[BorderPiece]) -> Tuple[List[List[Piece]], List[List[Piece]]]:
        old_size = len(grid2)
        size = old_size + 2
        ring1 = sorted(ring2, key=lambda x: x.id)

        new_grid1 = [[None for _ in range(size)] for _ in range(size)]
        new_grid2 = [[None for _ in range(size)] for _ in range(size)]

        def create_corner_piece(border_piece: BorderPiece) -> Piece:
            piece = Piece(border_piece.id, 0, 0)
            rotation1 = int(ring1.index(border_piece) / (size - 1))
            rotation2 = int(ring2.index(border_piece) / (size - 1))

            piece.edges[(DOWN + rotation1) % 4] = border_piece.edges[LEFT]
            piece.edges[(RIGHT + rotation1) % 4] = border_piece.edges[RIGHT]

            piece.grid2_rotation = rotation2 - rotation1
            return piece

        def create_side_piece(border_piece: BorderPiece) -> Piece:
            piece = Piece(border_piece.id, 0, 0)
            rotation1 = int(ring1.index(border_piece) / (size - 1))
            rotation2 = int(ring2.index(border_piece) / (size - 1))

            piece.edges[(LEFT + rotation1) % 4] = border_piece.edges[LEFT]
            piece.edges[(RIGHT + rotation1) % 4] = border_piece.edges[RIGHT]
            piece.edges[(DOWN + rotation1) % 4] = border_piece.edges[DOWN]

            piece.grid2_rotation = rotation2 - rotation1
            return piece

        # Top-left corner
        border_piece = ring1[0]
        piece = create_corner_piece(border_piece)
        new_grid1[0][0] = piece

        border_piece = ring2[0]
        piece = create_corner_piece(border_piece)
        new_grid2[0][0] = piece
        # Top-right corner
        border_piece = ring1[(size - 1)]
        piece = create_corner_piece(border_piece)
        new_grid1[size - 1][0] = piece

        border_piece = ring2[(size-1)]
        piece = create_corner_piece(border_piece)
        new_grid2[size-1][0] = piece
        # Bottom-right corner
        border_piece = ring1[(size-1)*2]
        piece = create_corner_piece(border_piece)
        new_grid1[size - 1][size - 1] = piece

        border_piece = ring2[(size-1)*2]
        piece = create_corner_piece(border_piece)
        new_grid2[size-1][size-1] = piece
        # Bottom-left corner
        border_piece = ring1[(size-1)*3]
        piece = create_corner_piece(border_piece)
        new_grid1[0][size - 1] = piece

        border_piece = ring2[(size-1)*3]
        piece = create_corner_piece(border_piece)
        new_grid2[0][size-1] = piece

        # Top side pieces
        for i in range(1, size-1):
            border_piece = ring1[i]
            piece = create_side_piece(border_piece)
            new_grid1[i][0] = piece

            border_piece = ring2[i]
            piece = create_side_piece(border_piece)
            new_grid2[i][0] = piece
        # Right side pieces
        for i in range(1, size-1):
            border_piece = ring1[i + (size - 1)]
            piece = create_side_piece(border_piece)
            new_grid1[size-1][i] = piece

            border_piece = ring2[i + size-1]
            piece = create_side_piece(border_piece)
            new_grid2[size-1][i] = piece
        # Bottom side pieces
        for i in range(1, size-1):
            border_piece = ring1[i + (size - 1) * 2]
            piece = create_side_piece(border_piece)
            new_grid1[size-1-i][size-1] = piece

            border_piece = ring2[i + (size-1)*2]
            piece = create_side_piece(border_piece)
            new_grid2[size-1-i][size-1] = piece
        # Left side pieces
        for i in range(1, size-1):
            border_piece = ring1[i + (size - 1) * 3]
            piece = create_side_piece(border_piece)
            new_grid1[0][size-1-i] = piece

            border_piece = ring2[i + (size-1)*3]
            piece = create_side_piece(border_piece)
            new_grid2[0][size-1-i] = piece

        # Middle grid
        for x in range(old_size):
            for y in range(old_size):
                piece = grid1[x][y]
                new_grid1[x+1][y+1] = piece
                piece = grid2[x][y]
                new_grid2[x+1][y+1] = piece

        # Inner Top side pieces
        for i in range(1, size - 1):
            outer_piece = new_grid1[i][0]
            inner_piece = new_grid1[i][1]
            inner_piece.edges[UP] = -outer_piece.edges[DOWN]
        # Inner Right side pieces
        for i in range(1, size - 1):
            outer_piece = new_grid1[size-1][i]
            inner_piece = new_grid1[size-2][i]
            inner_piece.edges[RIGHT] = -outer_piece.edges[LEFT]
        # Inner Bottom side pieces
        for i in range(1, size - 1):
            outer_piece = new_grid1[size - 1 - i][size - 1]
            inner_piece = new_grid1[size - 1 - i][size - 2]
            inner_piece.edges[DOWN] = -outer_piece.edges[UP]
        # Inner Left side pieces
        for i in range(1, size - 1):
            outer_piece = new_grid1[0][size - 1 - i]
            inner_piece = new_grid1[1][size - 1 - i]
            inner_piece.edges[LEFT] = -outer_piece.edges[RIGHT]

        return new_grid1, new_grid2

    unwrapped_ring = unwrap_ring_from_grid()
    new_ring1_list, new_ring2_list, backtrack_count = solve_new_borders(unwrapped_ring, max_solutions)
    new_grid1_list = []
    new_grid2_list = []
    for ring2 in new_ring2_list:
        new_grid1, new_grid2 = wrap_ring_around_grid(ring2)
        new_grid1_list.append(new_grid1)
        new_grid2_list.append(new_grid2)

    return new_ring1_list, new_ring2_list, new_grid1_list, new_grid2_list, backtrack_count

def solve_new_borders(previous_ring2: List[BorderPiece], max_solutions: int = 0) -> Tuple[List[BorderPiece], List[List[BorderPiece]], int]:
    previous_ring1 = sorted(previous_ring2, key=lambda x: x.id)
    inner_pieces = {}
    new_ring1_list = []
    new_ring2_list = []

    old_size = int(len(previous_ring2) / 4) + 1
    size = old_size + 2

    next_edge_id = [old_size * (old_size - 1)]
    backtrack_count = [0]

    def get_inner_ring(previous_ring: List[BorderPiece]) -> List[BorderPiece]:
        ring2 = []
        for i in range(len(previous_ring)):
            piece = previous_ring[i]
            if i % (old_size-1) == 0:
                if not inner_pieces.__contains__(-piece.id):
                    inner_pieces[-piece.id] = BorderPiece(-piece.id)
                if not inner_pieces.__contains__(piece.id):
                    inner_pieces[piece.id] = BorderPiece(piece.id)
                ring2.append(inner_pieces[-piece.id])
                ring2.append(None)
                ring2.append(inner_pieces[piece.id])
                continue

            if not inner_pieces.__contains__(piece.id):
                inner_pieces[piece.id] = BorderPiece(piece.id)
            ring2.append(inner_pieces[piece.id])

        ring2 = ring2[1:] + ring2[:1]
        return ring2

    def get_outer_ring1() -> List[BorderPiece]:
        ring1 = []
        next_id = old_size * old_size + 1
        for i in range((size-1) * 4):
            ring1.append(BorderPiece(next_id))
            next_id += 1
        return ring1

    def init_domains():
        for i in range(len(outer_ring1)):
            piece: BorderPiece = outer_ring1[i]

            # Corner pieces can be placed in other corners
            if i % (size - 1) == 0:
                for j in range(4):
                    piece.domain.append(j * (size - 1))
                continue

            # Sides can be placed in non-corners
            for j in range(len(outer_ring1)):
                if j % (size - 1) == 0: continue

                # Also skip side that would connect it to piece it previously connected to
                neighbor = inner_ring1[i]
                if j == inner_ring2.index(neighbor): continue

                piece.domain.append(j)

    def get_inner_neighbor(ring_number: int, piece: BorderPiece) -> BorderPiece:
        if ring_number == 1:
            idx = outer_ring1.index(piece)
            return inner_ring1[idx]
        elif ring_number == 2:
            idx = outer_ring2.index(piece)
            return inner_ring2[idx]
        else:
            raise Exception('Invalid ring number.')

    def get_outer_neighbor(ring_number: int, piece: BorderPiece) -> BorderPiece:
        if ring_number == 1:
            idx = inner_ring1.index(piece)
            return outer_ring1[idx]
        elif ring_number == 2:
            idx = inner_ring2.index(piece)
            return outer_ring2[idx]
        else:
            raise Exception('Invalid ring number.')

    def revert_domains(domains_to_revert: List):
        for piece, domain in reversed(domains_to_revert):
            if DEBUG_LEVEL > 2: print(f" Reverting domain: piece {piece}, domain {domain}")
            piece.domain.append(domain)

    def revert_updates(updates: List):
        for piece, direction, old_val, new_value in reversed(updates):
            piece.edges[direction] = old_val
            piece.required_neighbors[direction] = None
            next_edge_id[0] = min(next_edge_id[0], abs(new_value))

    def validate_solution(solution: List[BorderPiece]):
        """Verify that a solution is actually valid"""
        # Check edge matching
        for i in range(len(solution)):
            piece = solution[i]
            right_neighbor = solution[(i + 1) % len(solution)]
            inner_neighbor = get_inner_neighbor(2, piece)

            if inner_neighbor is None: continue

            if piece.edges[RIGHT] + right_neighbor.edges[LEFT] != 0:
                print(f"Invalid Ring2: piece {piece.id} right edge {piece.edges[RIGHT]} "
                      f"doesn't match {right_neighbor.id} left edge {right_neighbor.edges[LEFT]}")
                return False
            if piece.edges[DOWN] + inner_neighbor.edges[UP] != 0:
                print(f"Invalid Ring2: piece {piece.id} bottom edge {piece.edges[DOWN]} "
                      f"doesn't match {inner_neighbor.id} up edge {inner_neighbor.edges[UP]}")
                return False

        # Check all edges are assigned
        for i in range(len(solution)):
            piece = solution[i]
            if piece.edges[LEFT] == 0:
                print(f"Invalid: piece {piece.id} has undefined left edge")
                return False
            if piece.edges[RIGHT] == 0:
                print(f"Invalid: piece {piece.id} has undefined right edge")
                return False
            if piece.edges[DOWN] == 0 and i % (size-1) != 0:
                print(f"Invalid: piece {piece.id} has undefined bottom edge")
                return False

        # Check edge matching
        for i in range(len(outer_ring1)):
            piece = outer_ring1[i]
            right_neighbor = outer_ring1[(i + 1) % len(outer_ring1)]
            inner_neighbor = get_inner_neighbor(2, piece)

            if inner_neighbor is None: continue

            if piece.edges[RIGHT] + right_neighbor.edges[LEFT] != 0:
                print(f"Invalid Ring1: piece {piece.id} right edge {piece.edges[RIGHT]} "
                      f"doesn't match {right_neighbor.id} left edge {right_neighbor.edges[LEFT]}")
                return False
            if piece.edges[DOWN] + inner_neighbor.edges[UP] != 0:
                print(f"Invalid Ring1: piece {piece.id} bottom edge {piece.edges[DOWN]} "
                      f"doesn't match {inner_neighbor.id} up edge {inner_neighbor.edges[UP]}")
                return False

        # Check all edges are assigned
        for i in range(len(outer_ring1)):
            piece = outer_ring1[i]
            if piece.edges[LEFT] == 0:
                print(f"Invalid: piece {piece.id} has undefined left edge")
                return False
            if piece.edges[RIGHT] == 0:
                print(f"Invalid: piece {piece.id} has undefined right edge")
                return False
            if piece.edges[DOWN] == 0 and i % (size - 1) != 0:
                print(f"Invalid: piece {piece.id} has undefined bottom edge")
                return False

        return True

    def get_neighbor_count(idx: int) -> int:
        right_neighbor = outer_ring2[(idx + 1) % len(outer_ring2)]
        left_neighbor = outer_ring2[(idx - 1) % len(outer_ring2)]
        inner_neighbor = inner_ring2[idx]
        placed_neighbors = 0
        if right_neighbor is not None: placed_neighbors += 1
        if left_neighbor is not None: placed_neighbors += 1
        if inner_neighbor is not None: placed_neighbors += 1
        return placed_neighbors

    def get_heuristic_score(piece: BorderPiece) -> Tuple[int, int, int]:
        domain_size = len(piece.domain)
        if domain_size == 0:
            return -1  # Will be selected first (fail fast)

        # Count max placed neighbors across all domains
        max_placed_neighbors = 0
        for idx in piece.domain:
            placed_neighbors = get_neighbor_count(idx)
            max_placed_neighbors = max(max_placed_neighbors, placed_neighbors)

        # Weighted score: domain size is primary, but neighbor count helps break ties
        # Lower score = higher priority
        score = domain_size - (max_placed_neighbors * 0.5)

        return score

    def try_to_place_piece(piece: BorderPiece, index: int) -> Tuple[bool, List]:
        if DEBUG_LEVEL > 0: print(f"Placing piece {piece} at index {index}")

        updates = []

        if not outer_ring2[index] is None:
            if DEBUG_LEVEL > 1: print(f" Failed: Piece already at index {index}")
            return False, updates

        # Place piece
        outer_ring2[index] = piece

        # Updates edges of pieces, returning false if failed
        def update_edges(left_piece: BorderPiece, right_piece: BorderPiece) -> bool:
            # Get other connections
            other_left_neighbor = get_left_neighbor(outer_ring1, right_piece)
            other_right_neighbor = get_right_neighbor(outer_ring1, left_piece)

            # Update edges
            left_piece.edges[RIGHT] = next_edge_id[0]
            updates.append((left_piece, RIGHT, 0, next_edge_id[0]))
            right_piece.edges[LEFT] = -next_edge_id[0]
            updates.append((right_piece, LEFT, 0, -next_edge_id[0]))
            other_left_neighbor.edges[RIGHT] = next_edge_id[0]
            updates.append((other_left_neighbor, RIGHT, 0, next_edge_id[0]))
            other_right_neighbor.edges[LEFT] = -next_edge_id[0]
            updates.append((other_right_neighbor, LEFT, 0, -next_edge_id[0]))
            next_edge_id[0] += 1

            # If both other pieces are placed, they must connect to each other
            if other_left_neighbor in outer_ring2 and other_right_neighbor in outer_ring2:
                left_index = outer_ring2.index(other_left_neighbor)
                right_index = outer_ring2.index(other_right_neighbor)
                # If other pieces are not connected, invalid
                if (left_index + 1) % len(outer_ring2) != right_index:
                    if DEBUG_LEVEL > 1: print(f" Failed: Other left neighbor {other_left_neighbor} at index {left_index} not next to other right neighbor {other_right_neighbor} at index {right_index}")
                    outer_ring2[index] = None
                    return False
            # Otherwise, mark other piece as required
            else:
                other_left_neighbor.required_neighbors[RIGHT] = other_right_neighbor
                updates.append(
                    (other_left_neighbor, RIGHT, other_left_neighbor.edges[RIGHT], next_edge_id[0]))
                other_right_neighbor.required_neighbors[LEFT] = other_left_neighbor
                updates.append(
                    (other_right_neighbor, LEFT, other_right_neighbor.edges[LEFT], next_edge_id[0]))

            return True

        def update_inner_edges(outer_piece: BorderPiece, inner_piece: BorderPiece) -> bool:
            # Get other connections
            other_outer_neighbor = get_outer_neighbor(1, inner_piece)
            other_inner_neighbor = get_inner_neighbor(1, outer_piece)

            # Update edges
            outer_piece.edges[DOWN] = next_edge_id[0]
            updates.append((outer_piece, DOWN, 0, next_edge_id[0]))
            inner_piece.edges[UP] = -next_edge_id[0]
            updates.append((inner_piece, UP, 0, -next_edge_id[0]))
            other_outer_neighbor.edges[DOWN] = next_edge_id[0]
            updates.append((other_outer_neighbor, DOWN, 0, next_edge_id[0]))
            other_inner_neighbor.edges[UP] = -next_edge_id[0]
            updates.append((other_inner_neighbor, UP, 0, -next_edge_id[0]))
            next_edge_id[0] += 1

            # If both other pieces are placed, they must connect to each other
            if other_outer_neighbor in outer_ring2 and other_inner_neighbor in inner_ring2:
                outer_index = outer_ring2.index(other_outer_neighbor)
                inner_index = inner_ring2.index(other_inner_neighbor)
                # If other pieces are not connected, invalid
                if outer_index != inner_index:
                    if DEBUG_LEVEL > 1: print(
                        f" Failed: Other outer neighbor {other_outer_neighbor} at index {outer_index} not next to other inner neighbor {other_inner_neighbor} at index {inner_index}")
                    outer_ring2[index] = None
                    return False
            # Otherwise, mark other piece as required
            else:
                other_outer_neighbor.required_neighbors[DOWN] = other_inner_neighbor
                updates.append(
                    (other_outer_neighbor, DOWN, other_outer_neighbor.edges[DOWN], next_edge_id[0]))
                other_inner_neighbor.required_neighbors[UP] = other_outer_neighbor
                updates.append(
                    (other_inner_neighbor, UP, other_inner_neighbor.edges[UP], next_edge_id[0]))

            return True

        # Update neighbors edges
        left_neighbor = get_left_neighbor(outer_ring2, piece)
        if not left_neighbor is None:
            # If they don't match, invalid
            if left_neighbor.edges[RIGHT] + piece.edges[LEFT] != 0:
                if DEBUG_LEVEL > 1: print(f" Failed: Piece {piece} left edge {piece.edges[LEFT]} doesn't match left neighbor {left_neighbor} right edge {left_neighbor.edges[RIGHT]}")
                outer_ring2[index] = None
                return False, updates
            if left_neighbor.edges[RIGHT] == 0 and piece.edges[LEFT] == 0:
                success = update_edges(left_neighbor, piece)
                if not success:
                    return False, updates

        right_neighbor = get_right_neighbor(outer_ring2, piece)
        if not right_neighbor is None:
            # If they don't match, invalid
            if piece.edges[RIGHT] + right_neighbor.edges[LEFT] != 0:
                if DEBUG_LEVEL > 1: print(
                    f" Failed: Piece {piece} right edge {piece.edges[RIGHT]} doesn't match right neighbor {right_neighbor} left edge {right_neighbor.edges[LEFT]}")
                outer_ring2[index] = None
                return False, updates
            if piece.edges[RIGHT] == 0 and right_neighbor.edges[LEFT] == 0:
                success = update_edges(piece, right_neighbor)
                if not success:
                    return False, updates

        # Update inner <-> outer edges
        inner_neighbor = get_inner_neighbor(2, piece)
        if not inner_neighbor is None:
            if piece.edges[DOWN] + inner_neighbor.edges[UP] != 0:
                if DEBUG_LEVEL > 1: print(f" Failed: Piece {piece} bottom edge {piece.edges[DOWN]} doesn't match inner neighbor {inner_neighbor} up edge {inner_neighbor.edges[UP]}")
                outer_ring2[index] = None
                return False, updates
            if piece.edges[DOWN] == 0 and inner_neighbor.edges[UP] == 0:
                success = update_inner_edges(piece, inner_neighbor)
                if not success:
                    return False, updates

        return True, updates

    def trim_domains(placed_piece: BorderPiece, index: int, updates: List[Tuple], remaining_pieces: List[BorderPiece]) -> List:
        trimmed_domains = []

        # Remove domains for index just placed
        for piece in remaining_pieces:
            if index in piece.domain:
                if DEBUG_LEVEL > 3: print(f" Trim Domain: Piece {piece}, Domain {index} due to piece placed there")
                trimmed_domains.append((piece, index))
                piece.domain.remove(index)

        # Remove domains based on edges of just placed piece
        left_edge = placed_piece.edges[LEFT]
        if left_edge != 0:
            left_index = (index + len(outer_ring2) - 1) % len(outer_ring2)
            for piece in remaining_pieces:
                right_edge = piece.edges[RIGHT]
                if left_index in piece.domain and right_edge + left_edge != 0:
                    if DEBUG_LEVEL > 3: print(f" Trim Domain: Piece {piece}, Domain {left_index} due to right edge {right_edge} not matching placed piece left edge {left_edge}")
                    trimmed_domains.append((piece, left_index))
                    piece.domain.remove(left_index)
        right_edge = placed_piece.edges[RIGHT]
        if right_edge != 0:
            right_index = (index + 1) % len(outer_ring2)
            for piece in remaining_pieces:
                left_edge = piece.edges[LEFT]
                if right_index in piece.domain and right_edge + left_edge != 0:
                    if DEBUG_LEVEL > 3: print(
                        f" Trim Domain: Piece {piece}, Domain {right_index} due to left edge {left_edge} not matching placed piece right edge {right_edge}")
                    trimmed_domains.append((piece, right_index))
                    piece.domain.remove(right_index)

        # Remove domains based on rule P | Q -X-> P | R | Q, etc.
        right_neighbor = get_right_neighbor(outer_ring1, placed_piece)
        if right_neighbor in remaining_pieces:
            # Trim all domains where P | Q would become P | Q
            domain = (index + 1) % len(outer_ring2)
            if domain in right_neighbor.domain:
                trimmed_domains.append((right_neighbor, domain))
                right_neighbor.domain.remove(domain)
            # Trim all domains where P | Q would become P | R | Q
            domain = (index + 2) % len(outer_ring2)
            if domain in right_neighbor.domain:
                trimmed_domains.append((right_neighbor, domain))
                right_neighbor.domain.remove(domain)

        left_neighbor = get_left_neighbor(outer_ring1, placed_piece)
        if left_neighbor in remaining_pieces:
            # Trim all domains where P | Q would become P | Q
            domain = (index - 1 + len(outer_ring2)) % len(outer_ring2)
            if domain in left_neighbor.domain:
                trimmed_domains.append((left_neighbor, domain))
                left_neighbor.domain.remove(domain)
            # Trim all domains where P | Q would become P | R | Q
            domain = (index - 2 + len(outer_ring2)) % len(outer_ring2)
            if domain in left_neighbor.domain:
                trimmed_domains.append((left_neighbor, domain))
                left_neighbor.domain.remove(domain)

        two_right_neighbor = get_right_neighbor(outer_ring1, get_right_neighbor(outer_ring1, placed_piece))
        if two_right_neighbor in remaining_pieces:
            # Trim all domains where P | R | Q would become P | Q
            domain = (index + 1) % len(outer_ring2)
            if domain in two_right_neighbor.domain:
                trimmed_domains.append((two_right_neighbor, domain))
                two_right_neighbor.domain.remove(domain)

        two_left_neighbor = get_left_neighbor(outer_ring1, get_left_neighbor(outer_ring1, placed_piece))
        if two_left_neighbor in remaining_pieces:
            # Trim all domains where P | R | Q would become P | Q
            domain = (index - 1 + len(outer_ring2)) % len(outer_ring2)
            if domain in two_left_neighbor.domain:
                trimmed_domains.append((two_left_neighbor, domain))
                two_left_neighbor.domain.remove(domain)

        # Remove domains based on updated edges of placed pieces
        def handle_placed_piece(placed_piece: BorderPiece, index: int, direction: int):
            if direction == LEFT:
                neighbor_index = (index + len(outer_ring2) - 1) % len(outer_ring2)
                neighbor = outer_ring2[neighbor_index]

                # Skip neighbor if already placed
                if neighbor is not None: return

                # Check each remaining piece
                for piece in remaining_pieces:
                    removed_domains = []

                    for idx in piece.domain:
                        # Skip domains not at neighbor index
                        if idx != neighbor_index: continue

                        # Remove domain if edges don't match
                        right_edge = piece.edges[RIGHT]
                        if placed_piece.edges[LEFT] + right_edge != 0:
                            if DEBUG_LEVEL > 3: print(
                                f"  Trimmed Domain: Piece {piece}, Domain {idx} due to right edge {right_edge} not matching piece {placed_piece} updated left edge {placed_piece.edges[LEFT]}")
                            removed_domains.append(idx)

                    for domain in removed_domains:
                        if domain in piece.domain:
                            trimmed_domains.append((piece, domain))
                            piece.domain.remove(domain)
            elif direction == RIGHT:
                neighbor_index = (index + 1) % len(outer_ring2)
                neighbor = outer_ring2[neighbor_index]

                # Skip neighbor if already placed
                if neighbor is not None: return

                # Check each remaining piece
                for piece in remaining_pieces:
                    removed_domains = []

                    for idx in piece.domain:
                        # Skip domains not at neighbor index
                        if idx != neighbor_index: continue

                        # Remove domain if edges don't match
                        left_edge = piece.edges[LEFT]
                        if placed_piece.edges[RIGHT] + left_edge != 0:
                            if DEBUG_LEVEL > 3: print(f"  Trimmed Domain: Piece {piece}, Domain {idx} due to left edge {left_edge} not matching piece {placed_piece} updated right edge {placed_piece.edges[RIGHT]}")
                            removed_domains.append(idx)

                    for domain in removed_domains:
                        if domain in piece.domain:
                            trimmed_domains.append((piece, domain))
                            piece.domain.remove(domain)
            elif direction == UP:
                neighbor_index = index
                neighbor = outer_ring2[neighbor_index]

                # Skip neighbor if already placed
                if neighbor is not None: return

                # Check each remaining piece
                for piece in remaining_pieces:
                    removed_domains = []

                    for idx in piece.domain:
                        # Skip domains not at neighbor index
                        if idx != neighbor_index: continue

                        # Remove domain if edges don't match
                        bottom_edge = piece.edges[DOWN]
                        if placed_piece.edges[UP] + bottom_edge != 0:
                            if DEBUG_LEVEL > 3: print(
                                f"  Trimmed Domain: Piece {piece}, Domain {idx} due to bottom edge {bottom_edge} not matching piece {placed_piece} updated top edge {placed_piece.edges[UP]}")
                            removed_domains.append(idx)

                    for domain in removed_domains:
                        if domain in piece.domain:
                            trimmed_domains.append((piece, domain))
                            piece.domain.remove(domain)

            # Don't need to do down since neighbor is guaranteed to be placed already


        # Remove domains of unplaced pieces based on their updated edges
        def handle_unplaced_piece(piece: BorderPiece, direction: int):
            removed_domains = []

            for idx in piece.domain:
                # Check left index
                if direction == LEFT:
                    left_index = (idx + len(outer_ring2) - 1) % len(outer_ring2)
                    left_neighbor = outer_ring2[left_index]

                    # Skip if neighbor space is empty
                    if left_neighbor is None: return

                    if piece.edges[LEFT] + left_neighbor.edges[RIGHT] != 0:
                        if DEBUG_LEVEL > 3: print(
                            f"  Trimmed Domain: Piece {piece}, Domain {idx} due to left edge {piece.edges[LEFT]} not matching piece {left_neighbor} right edge {left_neighbor.edges[RIGHT]}")
                        removed_domains.append(idx)
                # Check right index
                if direction == RIGHT:
                    right_index = (idx + 1) % len(outer_ring2)
                    right_neighbor = outer_ring2[right_index]

                    # Skip if neighbor space is empty
                    if right_neighbor is None: return

                    if piece.edges[RIGHT] + right_neighbor.edges[LEFT] != 0:
                        if DEBUG_LEVEL > 3: print(
                            f"  Trimmed Domain: Piece {piece}, Domain {idx} due to right edge {piece.edges[RIGHT]} not matching piece {right_neighbor} left edge {right_neighbor.edges[LEFT]}")
                        removed_domains.append(idx)
                # Check bottom index
                if direction == DOWN:
                    bottom_neighbor = inner_ring2[idx]

                    # Skip if neighbor space is empty
                    if bottom_neighbor is None: return

                    if piece.edges[DOWN] + bottom_neighbor.edges[UP] != 0:
                        if DEBUG_LEVEL > 3: print(
                            f"  Trimmed Domain: Piece {piece}, Domain {idx} due to bottom edge {piece.edges[DOWN]} not matching piece {bottom_neighbor} top edge {bottom_neighbor.edges[UP]}")
                        removed_domains.append(idx)

            for domain in removed_domains:
                if domain in piece.domain:
                    trimmed_domains.append((piece, domain))
                    piece.domain.remove(domain)

        for piece, direction, old_val, new_val in updates:
            if piece in outer_ring2:
                handle_placed_piece(piece, outer_ring2.index(piece), direction)
            elif piece in inner_ring2:
                handle_placed_piece(piece, inner_ring2.index(piece), direction)
            else:
                handle_unplaced_piece(piece, direction)

        # Print trimmed domains as DEBUG_LEVEL > 2
        # Print reason domain trimed as DEBUG_LEVEL > 3
        if DEBUG_LEVEL > 2:
            print(" Trimmed domains:")
            for piece, domain in trimmed_domains:
                print(f"  Piece: {piece}, Domain: {domain}")

        return trimmed_domains

    def backtrack(remaining_pieces: List[BorderPiece]):
        backtrack_count[0] += 1

        # All pieces placed
        if len(remaining_pieces) == 0:
            solution = outer_ring2.copy()
            # Check that solution is valid
            if validate_solution(solution):
                if DEBUG_LEVEL > 0: print("Solution found.")
                new_ring1_list.append(copy.deepcopy(outer_ring1))
                new_ring2_list.append(copy.deepcopy(outer_ring2))
            else:
                print_ring(new_ring2)
                raise Exception()
            return True

        # FAIL FAST: Check if any piece has empty domain
        for piece in remaining_pieces:
            if len(piece.domain) == 0:
                if DEBUG_LEVEL > 0: print(f"Piece {piece} has no domain.")
                return False

        # Select piece with best heuristic score
        piece_to_place = sorted(remaining_pieces, key=get_heuristic_score)[0]

        if DEBUG_LEVEL > 0: print(f"Piece to place: {piece_to_place}, Domain Length: {len(piece_to_place.domain)}")
        if DEBUG_LEVEL > 3:
            print(f" Edges: {piece_to_place.edges}")
            print(f" Required Neighbors: {piece_to_place.required_neighbors}")
        if DEBUG_LEVEL > 1:
            print(f" Heuristic score: {get_heuristic_score(piece_to_place)}")
            print(f" Domain: {piece_to_place.domain}")

        remaining_pieces.remove(piece_to_place)
        for index in sorted(piece_to_place.domain, key=lambda i: -get_neighbor_count(i)):
            success, updates = try_to_place_piece(piece_to_place, index)
            if success:
                trimmed_domains = trim_domains(piece_to_place, index, updates, remaining_pieces)

                backtrack(remaining_pieces)
                if max_solutions > 0 and len(new_ring2_list) >= max_solutions: return True

                revert_domains(trimmed_domains)

            revert_updates(updates)
            outer_ring2[index] = None

            if DEBUG_LEVEL > 0: print(f"Removed piece {piece_to_place} from index {index}")

        remaining_pieces.append(piece_to_place)
        return False

    inner_ring1 = get_inner_ring(previous_ring1)
    inner_ring2 = get_inner_ring(previous_ring2)

    outer_ring1 = get_outer_ring1()
    outer_ring2 = [None] * len(outer_ring1)

    init_domains()
    backtrack(outer_ring1.copy())
    return new_ring1_list, new_ring2_list, backtrack_count[0]


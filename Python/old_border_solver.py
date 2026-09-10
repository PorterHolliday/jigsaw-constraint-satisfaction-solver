from typing import List, Tuple

import copy


class OldBorderPiece:
    def __init__(self, id):
        self.id = id
        self.left_edge = 0
        self.right_edge = 0
        self.domain = set()
        self.left_piece_required = None
        self.right_piece_required = None

    def __str__(self):
        return str(self.id)

def get_left_neighbor(ring: List, piece: OldBorderPiece) -> OldBorderPiece:
    idx = (ring.index(piece) + len(ring) - 1) % len(ring)
    return ring[idx]

def get_right_neighbor(ring: List, piece: OldBorderPiece) -> OldBorderPiece:
    idx = (ring.index(piece) + 1) % len(ring)
    return ring[idx]

# Initialize pieces (ids are index in ring 1)
def init_pieces(size: int):
    pieces = []
    for i in range((size - 1) * 4):
        pieces.append(OldBorderPiece(i+1))
    return pieces

# Define domains for each location in ring
def init_domains(size:int, pieces):
    for i in range(len(pieces)):
        piece: OldBorderPiece = pieces[i]

        # First corner piece is fixed to remove rotational symmetries
        if i == 0:
            piece.domain.add(0)
            continue

        # Other corner pieces can be placed in other corners
        if i % (size - 1) == 0:
            for j in range(1, 4):
                piece.domain.add(j * (size - 1))
            continue

        # Sides can be placed in non-corners
        for j in range(len(pieces)):
            if j % (size - 1) == 0: continue
            piece.domain.add(j)

def solve_ring(pieces: List[OldBorderPiece], max_solutions: int):
    ring2 = [None] * len(pieces)
    solutions = []
    next_edge_id = [1]

    def try_to_place_piece(piece: OldBorderPiece, index: int) -> Tuple[bool, List]:
        updates = []
        if not ring2[index] is None: return False, updates

        # Place piece
        ring2[index] = piece

        if index == 0: return True, updates

        # Update neighbors edges
        left_neighbor = get_left_neighbor(ring2, piece)
        if not left_neighbor is None:
            # If they don't match, invalid
            if left_neighbor.right_edge + piece.left_edge != 0:
                ring2[index] = None
                return False, updates
            # If both are undefined
            if left_neighbor.right_edge == 0 and piece.left_edge == 0:
                # Get other connections
                other_left_neighbor = get_left_neighbor(pieces, piece)
                other_right_neighbor = get_right_neighbor(pieces, left_neighbor)

                # Update edges
                left_neighbor.right_edge = next_edge_id[0]
                updates.append((left_neighbor, "right", 0, next_edge_id[0]))
                piece.left_edge = -next_edge_id[0]
                updates.append((piece, "left", 0, -next_edge_id[0]))
                other_left_neighbor.right_edge = next_edge_id[0]
                updates.append((other_left_neighbor, "right", 0, next_edge_id[0]))
                other_right_neighbor.left_edge = -next_edge_id[0]
                updates.append((other_right_neighbor, "left", 0, -next_edge_id[0]))
                next_edge_id[0] += 1

                # If both other pieces are placed, they must connect to each other
                if other_left_neighbor in ring2 and other_right_neighbor in ring2:
                    left_index = ring2.index(other_left_neighbor)
                    right_index = ring2.index(other_right_neighbor)
                    # If other pieces are not connected, invalid
                    if (left_index + 1) % len(ring2) != right_index:
                        ring2[index] = None
                        return False, updates
                # Otherwise, mark other piece as required
                else:
                    other_left_neighbor.right_piece_required = other_right_neighbor
                    other_right_neighbor.left_piece_required = other_left_neighbor

        right_neighbor = get_right_neighbor(ring2, piece)
        if not right_neighbor is None:
            # If they don't match, invalid
            if right_neighbor.left_edge + piece.right_edge != 0:
                ring2[index] = None
                return False, updates
            # If both are undefined
            if right_neighbor.left_edge == 0 and piece.right_edge == 0:
                # Get other connections
                other_left_neighbor = get_left_neighbor(pieces, right_neighbor)
                other_right_neighbor = get_right_neighbor(pieces, piece)

                # Update edges
                right_neighbor.left_edge = -next_edge_id[0]
                updates.append((right_neighbor, "left", 0, -next_edge_id[0]))
                piece.right_edge = next_edge_id[0]
                updates.append((piece, "right", 0, next_edge_id[0]))
                other_left_neighbor.right_edge = next_edge_id[0]
                updates.append((other_left_neighbor, "right", 0, next_edge_id[0]))
                other_right_neighbor.left_edge = -next_edge_id[0]
                updates.append((other_right_neighbor, "left", 0, -next_edge_id[0]))
                next_edge_id[0] += 1

                # If both other pieces are placed, they must connect to each other
                if other_left_neighbor in ring2 and other_right_neighbor in ring2:
                    left_index = ring2.index(other_left_neighbor)
                    right_index = ring2.index(other_right_neighbor)
                    # If other pieces are not connected, invalid
                    if (left_index + 1) % len(ring2) != right_index:
                        ring2[index] = None
                        return False, updates
                # Otherwise, mark other piece as required
                else:
                    other_left_neighbor.right_piece_required = other_right_neighbor
                    other_right_neighbor.left_piece_required = other_left_neighbor

        return True, updates

    def trim_domains(placed_piece, index, remaining_pieces):
        trimmed_domains = []
        for piece in remaining_pieces:
            # Trim all domains that match index
            if index in piece.domain:
                trimmed_domains.append((piece, index))
                piece.domain.remove(index)

        # Trim location options of unplaced required neighbors
        for i in range(len(ring2)):
            piece: OldBorderPiece = ring2[i]
            if piece is None: continue
            if not piece.right_piece_required is None:
                required_piece = piece.right_piece_required
                if not required_piece in ring2:
                    removed_domains = []
                    for domain in required_piece.domain:
                        if domain != (i + 1) % len(ring2):
                            removed_domains.append(domain)
                    for domain in removed_domains:
                        trimmed_domains.append((required_piece, domain))
                        required_piece.domain.remove(domain)
            if not piece.left_piece_required is None:
                required_piece = piece.left_piece_required
                if not required_piece in ring2:
                    removed_domains = []
                    for domain in required_piece.domain:
                        if domain != (i - 1 + len(ring2)) % len(ring2):
                            removed_domains.append(domain)
                    for domain in removed_domains:
                        trimmed_domains.append((required_piece, domain))
                        required_piece.domain.remove(domain)


        right_neighbor = get_right_neighbor(pieces, placed_piece)
        if right_neighbor in remaining_pieces:
            # Trim all domains where P | Q would become P | Q
            domain = (index + 1) % len(ring2)
            if domain in right_neighbor.domain:
                trimmed_domains.append((right_neighbor, domain))
                right_neighbor.domain.remove(domain)
            # Trim all domains where P | Q would become P | R | Q
            domain = (index + 2) % len(ring2)
            if domain in right_neighbor.domain:
                trimmed_domains.append((right_neighbor, domain))
                right_neighbor.domain.remove(domain)

        left_neighbor = get_left_neighbor(pieces, placed_piece)
        if left_neighbor in remaining_pieces:
            # Trim all domains where P | Q would become P | Q
            domain = (index - 1 + len(ring2)) % len(ring2)
            if domain in left_neighbor.domain:
                trimmed_domains.append((left_neighbor, domain))
                left_neighbor.domain.remove(domain)
            # Trim all domains where P | Q would become P | R | Q
            domain = (index - 2 + len(ring2)) % len(ring2)
            if domain in left_neighbor.domain:
                trimmed_domains.append((left_neighbor, domain))
                left_neighbor.domain.remove(domain)

        two_right_neighbor = get_right_neighbor(pieces, get_right_neighbor(pieces, placed_piece))
        if two_right_neighbor in remaining_pieces:
            # Trim all domains where P | R | Q would become P | Q
            domain = (index + 1) % len(ring2)
            if domain in two_right_neighbor.domain:
                trimmed_domains.append((two_right_neighbor, domain))
                two_right_neighbor.domain.remove(domain)

        two_left_neighbor = get_left_neighbor(pieces, get_left_neighbor(pieces, placed_piece))
        if two_left_neighbor in remaining_pieces:
            # Trim all domains where P | R | Q would become P | Q
            domain = (index - 1 + len(ring2)) % len(ring2)
            if domain in two_left_neighbor.domain:
                trimmed_domains.append((two_left_neighbor, domain))
                two_left_neighbor.domain.remove(domain)

        return trimmed_domains

    def revert_domains(trimmed_domains):
        for piece, domain in trimmed_domains:
            piece.domain.add(domain)

    def revert_edges(updates):
        for piece, direction, old_val, new_val in updates:
            setattr(piece, direction + '_edge', old_val)
            setattr(piece, direction + '_piece_required', None)
            next_edge_id[0] = min(next_edge_id[0], abs(new_val))

    def validate_solution(ring):
        """Verify that a solution is actually valid"""
        # Check edge matching
        for i in range(len(ring)):
            piece = ring[i]
            right_neighbor = ring[(i + 1) % len(ring)]

            if piece.right_edge + right_neighbor.left_edge != 0:
                print(f"Invalid: piece {piece.id} right edge {piece.right_edge} "
                      f"doesn't match {right_neighbor.id} left edge {right_neighbor.left_edge}")
                return False

        # Check all edges are assigned
        for piece in ring:
            if piece.left_edge == 0:
                print(f"Invalid: piece {piece.id} has undefined left edge")
                return False
            if piece.right_edge == 0:
                print(f"Invalid: piece {piece.id} has undefined right edge")
                return False

        return True

    def backtrack(remaining_pieces: List[OldBorderPiece]):
        # All pieces placed
        if len(remaining_pieces) == 0:
            solution = copy.deepcopy(ring2)
            # Check that solution is valid
            if validate_solution(solution):
                solutions.append(solution)
            else:
                err = ''
                for piece in solution:
                    err += str(piece) + ' '
                raise Exception(err)
            return True

        constrained_piece = sorted(remaining_pieces, key=lambda piece: len(piece.domain))[0]
        # If nowhere to place piece, backtrack
        if len(constrained_piece.domain) == 0: return False

        remaining_pieces.remove(constrained_piece)
        for index in constrained_piece.domain:
            success, edge_updates = try_to_place_piece(constrained_piece, index)
            if success:
                trimmed_domains = trim_domains(constrained_piece, index, remaining_pieces)
                # s = ''
                # for piece in ring2:
                #     s += str(piece) + ' '
                # print(s)
                if (backtrack(remaining_pieces) and len(solutions) >= max_solutions): return True
                #backtrack(remaining_pieces)
                #return True
                revert_domains(trimmed_domains)

            revert_edges(edge_updates)
            ring2[index] = None

        remaining_pieces.append(constrained_piece)
        return False

    backtrack(pieces.copy())
    return solutions

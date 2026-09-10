from typing import List, Tuple

import copy

from old_border_solver import OldBorderPiece

DEBUG_LEVEL = 0

class Piece:
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y
        self.grid2_x = None
        self.grid2_y = None
        self.domain = []
        self.edges = [0] * 4
        self.required_piece = [None] * 4
        self.grid2_rotation = 0

    def __str__(self):
        return str(self.id)

    def get_grid2_edges(self):
        return self.edges[-self.grid2_rotation:] + self.edges[:-self.grid2_rotation]

    def get_grid2_required_pieces(self):
        return self.required_piece[-self.grid2_rotation:] + self.required_piece[:-self.grid2_rotation]

def print_grid1(grid: List[List[Piece]]):
    for y in range(len(grid)):
        s = ''
        for x in range(len(grid[0])):
            piece = grid[x][y]
            if piece == None:
                s += 'N:[N, N, N, N] '
                continue
            s += str(piece) + ':' + str(piece.edges) + ' '
        print(s)

def print_grid2(grid: List[List[Piece]]):
    for y in range(len(grid)):
        s = ''
        for x in range(len(grid[0])):
            piece = grid[x][y]
            if piece == None:
                s += 'N:[N, N, N, N] '
                continue
            s += str(piece) + ':' + str(piece.get_grid2_edges()) + ' '
        print(s)

def get_coords_in_direction(coords: Tuple[int, int], dir: int) -> Tuple[int, int]:
    x, y = coords
    if dir == 0:
        return x, y-1
    if dir == 1:
        return x+1, y
    if dir == 2:
        return x, y+1
    if dir == 3:
        return x-1, y
    return x, y

def solve(border_pieces: List[OldBorderPiece], size: int):
    pieces = []
    grid1 = [[None for _ in range(size)] for _ in range(size)]
    grid2 = [[None for _ in range(size)] for _ in range(size)]
    grid1_list = []
    grid2_list = []
    start_edge_id = int(len(border_pieces) / 2) + 1
    BORDER_ID_MAX = len(border_pieces) - 4 + start_edge_id
    EDGE_ID_MAX = ((size - 2) * (size - 2) * 4 - (BORDER_ID_MAX * 3)) / 4 + start_edge_id
    next_edge_id = [BORDER_ID_MAX + 1]
    edge_dict = {}

    # Add counters
    fc_case1_trims = [0]
    fc_case2_trims = [0]
    total_backtracks = [0]

    backtrack_depths = {}

    def init_pieces():
        def init_border_pieces(start_id: int) -> int:
            id = start_id
            edge_id = start_edge_id
            for x in range(size - 1):
                piece = Piece(id, x, 0)
                grid1[x][0] = piece
                id += 1
                if x > 0:
                    piece.edges[2] = edge_id
                    edge_dict[edge_id] = (piece, 2)
                    edge_id += 1
            for y in range(size - 1):
                piece = Piece(id, size-1, y)
                grid1[size - 1][y] = piece
                id += 1
                if y > 0:
                    piece.edges[3] = edge_id
                    edge_dict[edge_id] = (piece, 3)
                    edge_id += 1
            for x in range(size - 1, 0, -1):
                piece = Piece(id, x, size-1)
                grid1[x][size - 1] = piece
                id += 1
                if x < size - 1:
                    piece.edges[0] = edge_id
                    edge_dict[edge_id] = (piece, 4)
                    edge_id += 1
            for y in range(size - 1, 0, -1):
                piece = Piece(id, 0, y)
                grid1[0][y] = piece
                id += 1
                if y < size - 1:
                    piece.edges[1] = edge_id
                    edge_dict[edge_id] = (piece, 1)
                    edge_id += 1

            return id

        def init_inner_pieces(start_id: int):
            id = start_id
            for y in range(1, size - 1):
                for x in range(1, size - 1):
                    piece = Piece(id, x, y)
                    pieces.append(piece)
                    grid1[x][y] = piece
                    id += 1
                    # Set edges to match border
                    if grid1[x - 1][y] != None:
                        edge_id = -grid1[x - 1][y].edges[1]
                        piece.edges[3] = edge_id
                        edge_dict[edge_id] = (piece, 3)
                    if grid1[x + 1][y] != None:
                        edge_id = -grid1[x + 1][y].edges[3]
                        piece.edges[1] = edge_id
                        edge_dict[edge_id] = (piece, 1)
                    if grid1[x][y - 1] != None:
                        edge_id = -grid1[x][y - 1].edges[2]
                        piece.edges[0] = edge_id
                        edge_dict[edge_id] = (piece, 0)
                    if grid1[x][y + 1] != None:
                        edge_id = -grid1[x][y + 1].edges[0]
                        piece.edges[2] = edge_id
                        edge_dict[edge_id] = (piece, 2)

        id = init_border_pieces(1)
        init_inner_pieces(id)

    def init_domains():
        def add_domains(piece: Piece):
            for x in range(1, size - 1):
                for y in range(1, size - 1):
                    for rotation in range(4):
                        edges = piece.edges.copy()
                        edges = edges[-rotation:] + edges[:-rotation]
                        for dir in range(4):
                            neighbor_x, neighbor_y = get_coords_in_direction((x, y), dir)
                            if grid2[neighbor_x][neighbor_y] != None and edges[dir] != 0:
                                break
                        else:
                            piece.domain.append((x, y, rotation))

        # Go through each middle piece and assign its domains based on position
        for x in range(1, size-1):
            for y in range(1, size-1):
                piece: Piece = grid1[x][y]
                add_domains(piece)

    def get_piece_dict() -> dict:
        piece_dict = {}
        for x in range(size):
            for y in range(size):
                piece = grid1[x][y]
                piece_dict[piece.id] = piece
        return piece_dict

    def get_index_to_coords(size: int) -> dict:
        index_to_coords = {}
        i = 0
        # Top
        for x in range(size-1):
            index_to_coords[i] = (x, 0)
            i += 1
        # Right
        for y in range(size-1):
            index_to_coords[i] = (size - 1, y)
            i += 1
        # Bottom
        for x in range(size-1, 0, -1):
            index_to_coords[i] = (x, size - 1)
            i += 1
        # Left
        for y in range(size-1, 0, -1):
            index_to_coords[i] = (0, y)
            i += 1
        return index_to_coords

    def place_border(border_pieces):
        index_to_coords = get_index_to_coords(size)
        for i in range(len(border_pieces)):
            piece = piece_dict[border_pieces[i].id]
            # Place piece in grid2
            x, y = index_to_coords[i]
            grid2[x][y] = piece
            # Give piece correct rotation
            start_rotation = (piece.id-1) // (size - 1) # Pieces are ascending from 0
            end_rotation = i // (size - 1) # Rotation depends on position (side piece is on)
            rotation_difference = (end_rotation - start_rotation + 4) % 4
            piece.grid2_rotation = rotation_difference
            # Set sides correctly
            piece.edges[(1 + start_rotation) % 4] = border_pieces[i].right_edge
            # Corner
            if i % (size-1) == 0:
                piece.edges[(2 + start_rotation) % 4] = border_pieces[i].left_edge
            # Side
            else:
                piece.edges[(3 + start_rotation) % 4] = border_pieces[i].left_edge

    def get_grid1_piece_in_direction(piece: Piece, dir: int) -> Piece:
        x = piece.x
        y = piece.y
        if dir == 0:
            return grid1[x][y - 1]
        if dir == 1:
            return grid1[x + 1][y]
        if dir == 2:
            return grid1[x][y + 1]
        if dir == 3:
            return grid1[x - 1][y]
        return None

    def get_grid2_piece_in_direction(piece: Piece, dir: int) -> Piece:
        x = piece.grid2_x
        y = piece.grid2_y

        if dir == 0:
            return grid2[x][y - 1]
        if dir == 1:
            return grid2[x + 1][y]
        if dir == 2:
            return grid2[x][y + 1]
        if dir == 3:
            return grid2[x - 1][y]
        return None

    def quick_solvability_check(remaining_pieces: List[Piece], max_backtracks: int = 50000) -> bool:
        """
        Quick test: Can we place at least half the pieces without hitting dead ends?
        If we can't make progress after max_backtracks attempts, border is likely unsolvable.
        """
        backtrack_count = [0]

        def limited_backtrack(pieces_left: List[Piece], placed_count: int) -> bool:
            backtrack_count[0] += 1

            # If we've placed half the pieces, it's probably solvable
            if placed_count >= len(remaining_pieces) // 2:
                return True

            # If we've tried too many times, give up
            if backtrack_count[0] >= max_backtracks:
                return False

            # ... simplified backtracking logic ...
            # (don't need full edge updates, just check basic placement validity)

        return limited_backtrack(remaining_pieces.copy(), 0)

    def get_heuristic_score(piece: Piece) -> Tuple[int, int]:
        domain_size = len(piece.domain)
        if domain_size == 0:
            return (float('inf'), 0)

        max_placed_neighbors = 0
        for domain_x, domain_y, rotation in piece.domain:
            placed_neighbors = sum(
                1 for dir in range(4)
                if grid2[get_coords_in_direction((domain_x, domain_y), dir)[0]]
                [get_coords_in_direction((domain_x, domain_y), dir)[1]] is not None
            )
            max_placed_neighbors = max(max_placed_neighbors, placed_neighbors)

        return domain_size, -max_placed_neighbors

    def try_to_place_piece(piece: Piece, coords: Tuple[int, int], rotation: int) -> Tuple[bool, List, List]:
        updates = []
        new_requirements = []

        x, y = coords
        if grid2[x][y] != None:
            if DEBUG_LEVEL > 1: print(f' Failed due to piece already at ({x}, {y})')
            return False, updates, new_requirements

        # Place piece
        piece.grid2_rotation = rotation
        piece.grid2_x = x
        piece.grid2_y = y
        grid2[x][y] = piece

        # Update undefined | undefined edge
        def undefined_to_undefined(piece1: Piece, piece2: Piece, dir_from_1_to_2: int) -> bool:
            if DEBUG_LEVEL > 4: print(
                f'  Undefined to Undefined | Piece1: {piece1}  Piece2: {piece2}  Dir: {dir_from_1_to_2}')

            # Get other connections
            piece1_dir = (dir_from_1_to_2 - piece1.grid2_rotation + 4) % 4
            piece1_neighbor: Piece = get_grid1_piece_in_direction(piece1, piece1_dir)
            piece1_neighbor_dir = (piece1_dir + 2) % 4
            if DEBUG_LEVEL > 4: print(
                f'   piece1_dir: {piece1_dir}  piece1_neighbor: {piece1_neighbor}  piece1_neighbor_dir: {piece1_neighbor_dir}')

            piece2_dir = (dir_from_1_to_2 + 2 - piece2.grid2_rotation + 4) % 4
            piece2_neighbor: Piece = get_grid1_piece_in_direction(piece2, piece2_dir)
            piece2_neighbor_dir = (piece2_dir + 2) % 4
            if DEBUG_LEVEL > 4: print(
                f'   piece2_dir: {piece2_dir}  piece2_neighbor: {piece2_neighbor}  piece2_neighbor_dir: {piece2_neighbor_dir}')

            # Update edges to next edge id
            piece1.edges[piece1_dir] = next_edge_id[0]
            updates.append((piece1, piece1_dir, 0, next_edge_id[0]))
            piece1_neighbor.edges[piece1_neighbor_dir] = -next_edge_id[0]
            updates.append((piece1_neighbor, piece1_neighbor_dir, 0, next_edge_id[0]))
            piece2.edges[piece2_dir] = next_edge_id[0]
            updates.append((piece2, piece2_dir, 0, next_edge_id[0]))
            piece2_neighbor.edges[piece2_neighbor_dir] = -next_edge_id[0]
            updates.append((piece2_neighbor, piece2_neighbor_dir, 0, next_edge_id[0]))
            next_edge_id[0] += 1

            # If both other pieces are placed, they must connect to each other
            if piece1_neighbor.grid2_x != None and piece2_neighbor.grid2_x != None:
                if DEBUG_LEVEL > 4: print(f'   Both neighbors are placed in grid2')
                # If other pieces are not connected, invalid
                piece1_neighbor_neighbor = get_grid2_piece_in_direction(piece1_neighbor, (piece1_neighbor_dir + piece1_neighbor.grid2_rotation) % 4)
                piece2_neighbor_neighbor = get_grid2_piece_in_direction(piece2_neighbor, (piece2_neighbor_dir + piece2_neighbor.grid2_rotation) % 4)
                if piece1_neighbor_neighbor != piece2_neighbor or piece2_neighbor_neighbor != piece1_neighbor:
                    if DEBUG_LEVEL > 1: print(f'    Failed due to neighbors not connecting. ' +
                                              f'Piece1 neighbor: {piece1_neighbor} - ' +
                                              f'Piece1 neighbor neighbor: {piece1_neighbor_neighbor} | ' +
                                              f'Piece2 neighbor: {piece2_neighbor} - ' +
                                              f'Piece2 neighbor neighbor: {piece2_neighbor_neighbor}')
                    return False
                if DEBUG_LEVEL > 4: print(f'    They are connected to each other in grid2.')
            # Otherwise, mark other piece as required
            else:
                if DEBUG_LEVEL > 3: print(
                    f'   Both neighbors are not placed in grid2. Required neighbors set: Piece {piece1_neighbor} side {piece1_neighbor_dir} - Piece {piece2_neighbor} side {piece2_neighbor_dir}')
                piece1_neighbor.required_piece[piece1_neighbor_dir] = piece2_neighbor
                updates.append(
                    (piece1_neighbor, piece1_neighbor_dir, piece1_neighbor.edges[piece1_neighbor_dir], next_edge_id[0]))
                if piece1_neighbor.grid2_x != None: new_requirements.append((piece1_neighbor, piece1_neighbor_dir))
                piece2_neighbor.required_piece[piece2_neighbor_dir] = piece1_neighbor
                updates.append(
                    (piece2_neighbor, piece2_neighbor_dir, piece2_neighbor.edges[piece2_neighbor_dir], next_edge_id[0]))
                if piece2_neighbor.grid2_x != None: new_requirements.append((piece2_neighbor, piece2_neighbor_dir))

            if DEBUG_LEVEL > 4: print ('    Success')
            return True

        # Update defined | undefined edge, if defined edge is originally facing border
        def defined_to_undefined(piece1: Piece, piece2: Piece, dir_from_1_to_2: int) -> bool:
            if DEBUG_LEVEL > 4: print(f'  Defined to Undefined | Piece1: {piece1}  Piece2: {piece2}  Dir: {dir_from_1_to_2}')

            # Get other connections
            piece1_dir = (dir_from_1_to_2 - piece1.grid2_rotation + 4) % 4
            piece1_neighbor: Piece = get_grid1_piece_in_direction(piece1, piece1_dir)
            piece1_neighbor_dir = (piece1_dir + 2) % 4
            if DEBUG_LEVEL > 4: print(f'   piece1_dir: {piece1_dir}  piece1_neighbor: {piece1_neighbor}  piece1_neighbor_dir: {piece1_neighbor_dir}')

            piece2_dir = (dir_from_1_to_2 + 2 - piece2.grid2_rotation + 4) % 4
            piece2_neighbor: Piece = get_grid1_piece_in_direction(piece2, piece2_dir)
            piece2_neighbor_dir = (piece2_dir + 2) % 4
            if DEBUG_LEVEL > 4: print(f'   piece2_dir: {piece2_dir}  piece2_neighbor: {piece2_neighbor}  piece2_neighbor_dir: {piece2_neighbor_dir}')

            # Update edges
            edge_id = piece1.edges[piece1_dir]
            piece2.edges[piece2_dir] = -edge_id
            updates.append((piece2, piece2_dir, 0, edge_id))
            piece2_neighbor.edges[piece2_neighbor_dir] = edge_id
            updates.append((piece2_neighbor, piece2_neighbor_dir, 0, edge_id))

            # If both other pieces are placed, they must connect to each other
            if piece1_neighbor.grid2_x != None and piece2_neighbor.grid2_x != None:
                if DEBUG_LEVEL > 4: print(f'   Both neighbors are placed in grid2')
                # If other pieces are not connected, invalid
                piece1_neighbor_neighbor = get_grid2_piece_in_direction(piece1_neighbor, (
                            piece1_neighbor_dir + piece1_neighbor.grid2_rotation) % 4)
                piece2_neighbor_neighbor = get_grid2_piece_in_direction(piece2_neighbor, (
                            piece2_neighbor_dir + piece2_neighbor.grid2_rotation) % 4)
                if piece1_neighbor_neighbor != piece2_neighbor or piece2_neighbor_neighbor != piece1_neighbor:
                    if DEBUG_LEVEL > 1: print(f'    Failed due to neighbors not connecting. ' +
                                              f'Piece1 neighbor: {piece1_neighbor} - ' +
                                              f'Piece1 neighbor neighbor: {piece1_neighbor_neighbor} | ' +
                                              f'Piece2 neighbor: {piece2_neighbor} - ' +
                                              f'Piece2 neighbor neighbor: {piece2_neighbor_neighbor}')
                    return False
                if DEBUG_LEVEL > 4: print(f'    They are connected to each other in grid2.')
            # Otherwise, mark other piece as required
            else:
                if DEBUG_LEVEL > 3: print(f'   Both neighbors are not placed in grid2. Required neighbors set: Piece {piece1_neighbor} side {piece1_neighbor_dir} - Piece {piece2_neighbor} side {piece2_neighbor_dir}')
                piece1_neighbor.required_piece[piece1_neighbor_dir] = piece2_neighbor
                updates.append((piece1_neighbor, piece1_neighbor_dir, piece1_neighbor.edges[piece1_neighbor_dir], next_edge_id[0]))
                if piece1_neighbor.grid2_x != None: new_requirements.append((piece1_neighbor, piece1_neighbor_dir))
                piece2_neighbor.required_piece[piece2_neighbor_dir] = piece1_neighbor
                updates.append((piece2_neighbor, piece2_neighbor_dir, piece2_neighbor.edges[piece2_neighbor_dir], next_edge_id[0]))
                if piece2_neighbor.grid2_x != None: new_requirements.append((piece2_neighbor, piece2_neighbor_dir))

            if DEBUG_LEVEL > 4: print('    Success')
            return True

        # Check each neighbor and updates edges if necessary
        for dir in range(4):
            neighbor: Piece = get_grid2_piece_in_direction(piece, dir)

            if neighbor is None: continue

            piece_edge = piece.get_grid2_edges()[dir]
            neighbor_edge = neighbor.get_grid2_edges()[(dir + 2) % 4]

            if DEBUG_LEVEL > 2:
                print(f'  Direction: {dir}')
                print(f'  Piece {piece} grid2 edges {piece.get_grid2_edges()}')
                print(f'  Neighbor piece {neighbor} grid2 edges {neighbor.get_grid2_edges()}')

            success = True
            if piece_edge == 0 and neighbor_edge == 0:
                # Stop if at max edge id
                if next_edge_id[0] == EDGE_ID_MAX:
                    if DEBUG_LEVEL > 1: print(f'  Failed due to trying to place piece {piece} undefined edge next to neighbor {neighbor} undefined past EDGE_ID_MAX')
                    return False, updates, new_requirements
                success = undefined_to_undefined(piece, neighbor, dir)
            elif piece_edge != 0 and abs(piece_edge) <= BORDER_ID_MAX and neighbor_edge == 0:
                success = defined_to_undefined(piece, neighbor, dir)
            elif piece_edge == 0 and neighbor_edge != 0 and abs(neighbor_edge) <= BORDER_ID_MAX:
                success = defined_to_undefined(neighbor, piece, (dir + 2) % 4)
            elif piece_edge + neighbor_edge != 0:
                if DEBUG_LEVEL > 1: print(f'  Failed due to piece {piece} edge {piece_edge} not matching neighbor {neighbor} edge {neighbor_edge}')
                return False, updates, new_requirements

            if not success:
                return False, updates, new_requirements

        return True, updates, new_requirements

    def trim_domains(placed_piece: Piece, coords: Tuple[int, int], rotation: int, new_requirements: List[Tuple],
                     remaining_pieces: List[Piece]) -> List:
        trimmed_domains = []
        x, y = coords

        # Trim position-based domains
        for piece in remaining_pieces:
            for r in range(4):
                if (x, y, r) in piece.domain:
                    if DEBUG_LEVEL > 3: print(
                        f'   Trim piece {piece} domain ({x}, {y}, {r}) due to piece {placed_piece} already there.')
                    trimmed_domains.append((piece, (x, y, r)))
                    piece.domain.remove((x, y, r))

        def trim_for_requirements(piece_with_req: Piece, grid2_dir: int):
            """
            Trim domains for pieces that are required neighbors of piece_with_req.
            piece_with_req: A piece that's already placed in Grid2
            grid2_dir: The Grid2 direction where the requirement exists
            """
            required_piece: Piece = piece_with_req.get_grid2_required_pieces()[grid2_dir]

            if DEBUG_LEVEL > 3:
                print(f'   Required piece: {required_piece}, Grid2 Dir: {grid2_dir}')

            if required_piece is None:
                return

            if required_piece.grid2_x is not None:
                return  # Already placed, no need to trim

            # Get the Grid1 side where this requirement was set
            original_side = required_piece.required_piece.index(piece_with_req)

            # The required piece must be placed adjacent to piece_with_req in Grid2
            piece_with_req_x = piece_with_req.grid2_x
            piece_with_req_y = piece_with_req.grid2_y
            expected_position = get_coords_in_direction((piece_with_req_x, piece_with_req_y), grid2_dir)

            removed_domains = []
            for domain in required_piece.domain:
                domain_x, domain_y, domain_rotation = domain

                # Check if position is correct
                if (domain_x, domain_y) != expected_position:
                    if DEBUG_LEVEL > 3:
                        print(
                            f'   Trim piece {required_piece} domain {domain} - wrong position (need {expected_position})')
                    removed_domains.append(domain)
                    continue

                # Check if rotation is correct
                # The required_piece's original_side must face piece_with_req (opposite of grid2_dir)
                required_rotation = (grid2_dir + 2 - original_side + 4) % 4
                if domain_rotation != required_rotation:
                    if DEBUG_LEVEL > 3:
                        print(
                            f'   Trim piece {required_piece} domain {domain} - wrong rotation (need {required_rotation})')
                    removed_domains.append(domain)

            for domain in removed_domains:
                trimmed_domains.append((required_piece, domain))
                required_piece.domain.remove(domain)

        # Trim for the placed piece's requirements
        for dir in range(4):
            trim_for_requirements(placed_piece, dir)

        # Trim for new requirements (pieces that got requirements during this placement)
        for piece, grid1_dir in new_requirements:
            # Convert Grid1 direction to Grid2 direction
            grid2_dir = (grid1_dir + piece.grid2_rotation) % 4
            trim_for_requirements(piece, grid2_dir)

        return trimmed_domains

    def forward_check_edge_constraints(updates: List[Tuple], remaining_pieces: List[Piece]) -> List:
        """
        After placing a piece and updating edges, check if any remaining piece's domains
        are now invalid due to edge mismatches.

        This handles TWO cases:
        1. Placed pieces with updated edges → check remaining pieces' domains at adjacent positions
        2. Unplaced pieces with updated edges → check their domains against all placed pieces
        """
        trimmed_domains = []

        # CASE 1: Placed pieces with updated edges
        pieces_and_directions = {}  # piece -> set of Grid1 directions that were updated
        for piece, grid1_direction, old_val, new_val in updates:
            if piece.grid2_x is not None:  # Placed piece
                if piece not in pieces_and_directions:
                    pieces_and_directions[piece] = set()
                pieces_and_directions[piece].add(grid1_direction)

        for piece_with_update, updated_grid1_dirs in pieces_and_directions.items():
            if DEBUG_LEVEL > 3:
                print(
                    f'   FC Case 1: Checking placed piece {piece_with_update} at ({piece_with_update.grid2_x}, {piece_with_update.grid2_y})')

            for grid1_dir in updated_grid1_dirs:
                # Convert Grid1 direction to Grid2 direction
                grid2_dir = (grid1_dir + piece_with_update.grid2_rotation) % 4
                piece_edge = piece_with_update.get_grid2_edges()[grid2_dir]

                # Get the position where a neighbor would be
                neighbor_x, neighbor_y = get_coords_in_direction(
                    (piece_with_update.grid2_x, piece_with_update.grid2_y), grid2_dir
                )

                # Skip if neighbor is already placed
                if grid2[neighbor_x][neighbor_y] is not None:
                    continue

                # Check each remaining piece
                for piece in remaining_pieces:
                    removed_domains = []

                    for domain_x, domain_y, domain_rotation in piece.domain:
                        # If this domain would place the piece at the neighbor position
                        if (domain_x, domain_y) == (neighbor_x, neighbor_y):
                            # Get the edge that would face the piece_with_update
                            piece_edges_at_rotation = piece.edges[-domain_rotation:] + piece.edges[:-domain_rotation]
                            facing_edge = piece_edges_at_rotation[(grid2_dir + 2) % 4]

                            # Check if edges match
                            if piece_edge != 0 and facing_edge != 0:
                                if piece_edge + facing_edge != 0:
                                    if DEBUG_LEVEL > 3:
                                        print(
                                            f'   FC Case 1: Trim piece {piece} domain ({domain_x}, {domain_y}, {domain_rotation}) - edge {facing_edge} doesn\'t match {piece_edge}')
                                    removed_domains.append((domain_x, domain_y, domain_rotation))

                    for domain in removed_domains:
                        if domain in piece.domain:
                            fc_case1_trims[0] += 1  # Count trims
                            trimmed_domains.append((piece, domain))
                            piece.domain.remove(domain)

        # CASE 2: Unplaced pieces with updated edges
        unplaced_pieces_with_updates = {}  # piece -> set of Grid1 directions updated
        for piece, grid1_direction, old_val, new_val in updates:
            if piece.grid2_x is None:  # Unplaced piece
                if piece not in unplaced_pieces_with_updates:
                    unplaced_pieces_with_updates[piece] = set()
                unplaced_pieces_with_updates[piece].add(grid1_direction)

        for unplaced_piece, updated_grid1_dirs in unplaced_pieces_with_updates.items():
            if DEBUG_LEVEL > 3:
                print(f'   FC Case 2: Checking unplaced piece {unplaced_piece} with updated edges')

            removed_domains = []

            # Check each domain of this unplaced piece
            for domain_x, domain_y, domain_rotation in unplaced_piece.domain:
                # Get the edges at this rotation
                rotated_edges = unplaced_piece.edges[-domain_rotation:] + unplaced_piece.edges[:-domain_rotation]

                # Check all 4 directions from this position
                conflict_found = False
                for grid2_dir in range(4):
                    # Get the edge in this Grid2 direction
                    # First, convert grid2_dir to grid1_dir for this rotation
                    grid1_dir = (grid2_dir - domain_rotation + 4) % 4

                    # Only check if this direction was updated
                    if grid1_dir not in updated_grid1_dirs:
                        continue

                    edge_in_this_dir = rotated_edges[grid2_dir]

                    # Get neighbor position in Grid2
                    neighbor_x, neighbor_y = get_coords_in_direction((domain_x, domain_y), grid2_dir)

                    # Check if there's already a placed piece at this neighbor position
                    neighbor_piece = grid2[neighbor_x][neighbor_y]
                    if neighbor_piece is not None:
                        # Get the neighbor's edge facing back
                        neighbor_edges = neighbor_piece.get_grid2_edges()
                        neighbor_facing_edge = neighbor_edges[(grid2_dir + 2) % 4]

                        # Check for conflict
                        if edge_in_this_dir != 0 and neighbor_facing_edge != 0:
                            if edge_in_this_dir + neighbor_facing_edge != 0:
                                if DEBUG_LEVEL > 3:
                                    print(
                                        f'   FC Case 2: Trim piece {unplaced_piece} domain ({domain_x}, {domain_y}, {domain_rotation}) - edge {edge_in_this_dir} conflicts with neighbor {neighbor_piece} edge {neighbor_facing_edge}')
                                conflict_found = True
                                break

                if conflict_found:
                    removed_domains.append((domain_x, domain_y, domain_rotation))

            for domain in removed_domains:
                if domain in unplaced_piece.domain:
                    fc_case2_trims[0] += 1  # Count trims
                    trimmed_domains.append((unplaced_piece, domain))
                    unplaced_piece.domain.remove(domain)

        return trimmed_domains

    def propagate_singleton_domains(remaining_pieces: List[Piece]) -> Tuple[bool, List]:
        """
        Aggressively propagate constraints when pieces have singleton domains.
        Returns (success, trimmed_domains)
        """
        trimmed_domains = []
        iteration = 0
        max_iterations = 100  # Prevent infinite loops

        while iteration < max_iterations:
            iteration += 1
            any_changes = False

            # Find pieces with only 1 domain option
            for piece in remaining_pieces:
                if len(piece.domain) == 0:
                    return False, trimmed_domains

                if len(piece.domain) == 1 and piece.grid2_x is None:
                    domain_x, domain_y, domain_rotation = piece.domain[0]

                    if DEBUG_LEVEL > 3:
                        print(
                            f'   Singleton propagation: Piece {piece} must be at ({domain_x}, {domain_y}, {domain_rotation})')

                    # This piece MUST go here - remove this position from all other pieces
                    for other_piece in remaining_pieces:
                        if other_piece == piece:
                            continue

                        removed = []
                        for other_domain in other_piece.domain:
                            other_x, other_y, other_rot = other_domain

                            # Remove if same position
                            if (other_x, other_y) == (domain_x, domain_y):
                                removed.append(other_domain)

                        for domain in removed:
                            if domain in other_piece.domain:
                                trimmed_domains.append((other_piece, domain))
                                other_piece.domain.remove(domain)
                                any_changes = True

                        # Fail fast if we created an empty domain
                        if len(other_piece.domain) == 0:
                            return False, trimmed_domains

            if not any_changes:
                break

        return True, trimmed_domains

    def revert_domains(domains_to_revert: List):
        for piece, domain in reversed(domains_to_revert):
            if DEBUG_LEVEL > 2: print(f'  Adding piece {piece} domain {domain}')
            piece.domain.append(domain)

    def revert_updates(updates: List):
        for piece, direction, old_val, new_value in reversed(updates):
            if DEBUG_LEVEL > 2: print(f'  Reverting update for piece {piece} side {direction}')
            piece.edges[direction] = old_val
            piece.required_piece[direction] = None
            next_edge_id[0] = min(next_edge_id[0], new_value)

    def validate_solution(solution: List[List[Piece]]) -> bool:
        for x in range(1, size-1):
            for y in range(1, size-1):
                piece: Piece = grid2[x][y]
                edges = piece.get_grid2_edges()
                for d in range(4):
                    if edges[d] == 0:
                        print(f'Invalid piece {piece} at ({x},{y}) edge {d} is 0.')
                        return False
                    neighbor: Piece = get_grid2_piece_in_direction(piece, d)
                    neighbor_edges = neighbor.get_grid2_edges()
                    if edges[d] + neighbor_edges[(d + 2) % 4] != 0:
                        print(f'Invalid piece {piece} at ({x},{y}) edge {d} is {edges[d]}, which does not match neighbor of {neighbor_edges[d]}.')
                        return False

            return True

    def backtrack(remaining_pieces: List[Piece], depth: int = 0) -> bool:
        total_backtracks[0] += 1

        # Track depth distribution
        if depth not in backtrack_depths:
            backtrack_depths[depth] = 0
        backtrack_depths[depth] += 1

        if total_backtracks[0] % 10000 == 0:
            print(f"Backtracks: {total_backtracks[0]}")
            print(f"Depth distribution: {sorted(backtrack_depths.items())}")  # First 5 depths

        # All pieces placed
        if len(remaining_pieces) == 0:
            solution = grid2.copy()
            # Check that solution is valid
            if validate_solution(solution):
                grid1_list.append(copy.deepcopy(grid1))
                grid2_list.append(copy.deepcopy(grid2))
            else:
                print_grid2(grid2)
                raise Exception('Invalid solution.')
            return True

        # FAIL FAST: Check if any piece has empty domain
        for piece in remaining_pieces:
            if len(piece.domain) == 0:
                if DEBUG_LEVEL > 0:
                    print(f' Piece {piece} has empty domain - backtracking immediately.')
                return False

        # Select piece with best heuristic score
        piece_to_place = sorted(remaining_pieces, key=get_heuristic_score)[0]

        remaining_pieces.remove(piece_to_place)
        for x, y, rotation in piece_to_place.domain:
            if DEBUG_LEVEL > 0: print(f' Placing piece {piece_to_place} at ({x}, {y}) r: {rotation}')
            success, updates, new_requirements = try_to_place_piece(piece_to_place, (x, y), rotation)

            if DEBUG_LEVEL > 0: print('   Successful:', success)
            if DEBUG_LEVEL > 2:
                print(' Updates:')
                for piece, direction, old_val, new_val in updates:
                    print(f'  Piece: {piece}, Side: {direction}, Old Value: {old_val}, New Value: {new_val}')

            if success:
                trimmed_domains = trim_domains(piece_to_place, (x, y), rotation, new_requirements, remaining_pieces)

                # Forward check based on ALL edge updates (not just the placed piece)
                fc_trimmed = forward_check_edge_constraints(updates, remaining_pieces)
                trimmed_domains.extend(fc_trimmed)

                if DEBUG_LEVEL > 2:
                    print(' Trimmed:')
                    for piece, domain in trimmed_domains:
                        print(f'  Piece {piece}, Domain: {domain}')

                    # NEW: Propagate singleton domains
                success_propagate, singleton_trimmed = propagate_singleton_domains(remaining_pieces)
                trimmed_domains.extend(singleton_trimmed)

                if success_propagate:
                    if backtrack(remaining_pieces, depth + 1):
                        return True
                #backtrack(remaining_pieces)
                #if (len(remaining_pieces) == 0): return True
                # backtrack(remaining_pieces)
                # return True
                if DEBUG_LEVEL > 0: print(' Reverting trimmed domains.')
                revert_domains(trimmed_domains)

            if DEBUG_LEVEL > 0: print(' Reverting updates.')
            revert_updates(updates)
            # Remove piece from grid2
            if DEBUG_LEVEL > 0: print(' Removing piece', piece_to_place)
            grid2[x][y] = None
            piece_to_place.grid2_x = None
            piece_to_place.grid2_y = None
            piece_to_place.grid2_rotation = 0

        remaining_pieces.append(piece_to_place)
        return False

    init_pieces()
    piece_dict = get_piece_dict()
    place_border(border_pieces)
    init_domains()

    backtrack(pieces)
    print(
        f"Final stats - Backtracks: {total_backtracks[0]}, FC Case1: {fc_case1_trims[0]}, FC Case2: {fc_case2_trims[0]}")
    return grid1_list, grid2_list

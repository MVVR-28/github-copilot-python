import copy
import random

SIZE = 9
EMPTY = 0
DEFAULT_DIFFICULTY = "medium"
DIFFICULTY_SETTINGS = {
    "easy": 40,
    "medium": 32,
    "hard": 24,
}


def deep_copy(board):
    return copy.deepcopy(board)


def create_empty_board():
    return [[EMPTY for _ in range(SIZE)] for _ in range(SIZE)]


def is_safe(board, row, col, num):
    for x in range(SIZE):
        if board[row][x] == num or board[x][col] == num:
            return False

    start_row = row - row % 3
    start_col = col - col % 3
    for i in range(3):
        for j in range(3):
            if board[start_row + i][start_col + j] == num:
                return False
    return True


def fill_board(board):
    for row in range(SIZE):
        for col in range(SIZE):
            if board[row][col] == EMPTY:
                possible = list(range(1, SIZE + 1))
                random.shuffle(possible)
                for candidate in possible:
                    if is_safe(board, row, col, candidate):
                        board[row][col] = candidate
                        if fill_board(board):
                            return True
                        board[row][col] = EMPTY
                return False
    return True


def find_empty_cell(board):
    for row in range(SIZE):
        for col in range(SIZE):
            if board[row][col] == EMPTY:
                return row, col
    return None


def is_valid_board(board):
    for index in range(SIZE):
        row_values = [value for value in board[index] if value != EMPTY]
        if len(set(row_values)) != len(row_values):
            return False

        column_values = [
            board[row][index]
            for row in range(SIZE)
            if board[row][index] != EMPTY
        ]
        if len(set(column_values)) != len(column_values):
            return False

    for box_row in range(0, SIZE, 3):
        for box_col in range(0, SIZE, 3):
            values = [
                board[row][col]
                for row in range(box_row, box_row + 3)
                for col in range(box_col, box_col + 3)
                if board[row][col] != EMPTY
            ]
            if len(set(values)) != len(values):
                return False

    return True


def count_solutions(board, limit=2):
    if not is_valid_board(board):
        return 0

    solutions = 0

    def backtrack(current_board):
        nonlocal solutions
        if solutions >= limit:
            return

        empty_cell = find_empty_cell(current_board)
        if empty_cell is None:
            solutions += 1
            return

        row, col = empty_cell
        for candidate in range(1, SIZE + 1):
            if is_safe(current_board, row, col, candidate):
                current_board[row][col] = candidate
                backtrack(current_board)
                current_board[row][col] = EMPTY

    backtrack(deep_copy(board))
    return solutions


def has_unique_solution(board):
    return count_solutions(board, limit=2) == 1


def remove_cells(board, clues):
    target_removed = SIZE * SIZE - clues
    removed = 0
    cells = list(range(SIZE * SIZE))
    random.shuffle(cells)

    for cell_index in cells:
        if removed >= target_removed:
            break

        row, col = divmod(cell_index, SIZE)
        if board[row][col] == EMPTY:
            continue

        original_value = board[row][col]
        board[row][col] = EMPTY
        if not has_unique_solution(board):
            board[row][col] = original_value
            continue

        removed += 1


def get_clue_count(clues=None, difficulty=None):
    if clues is not None:
        return int(clues)

    normalized_difficulty = (difficulty or DEFAULT_DIFFICULTY).lower()
    return DIFFICULTY_SETTINGS.get(
        normalized_difficulty,
        DIFFICULTY_SETTINGS[DEFAULT_DIFFICULTY],
    )


def generate_puzzle(clues=None, difficulty=None):
    clue_count = get_clue_count(clues=clues, difficulty=difficulty)
    board = create_empty_board()
    fill_board(board)
    solution = deep_copy(board)
    remove_cells(board, clue_count)
    puzzle = deep_copy(board)
    return puzzle, solution

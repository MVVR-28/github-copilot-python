import sudoku_logic


def is_valid_board(board):
    for index in range(sudoku_logic.SIZE):
        row_values = [value for value in board[index] if value != sudoku_logic.EMPTY]
        if len(set(row_values)) != len(row_values):
            return False

        column_values = [
            board[row][index]
            for row in range(sudoku_logic.SIZE)
            if board[row][index] != sudoku_logic.EMPTY
        ]
        if len(set(column_values)) != len(column_values):
            return False

    for box_row in range(0, sudoku_logic.SIZE, 3):
        for box_col in range(0, sudoku_logic.SIZE, 3):
            values = [
                board[row][col]
                for row in range(box_row, box_row + 3)
                for col in range(box_col, box_col + 3)
                if board[row][col] != sudoku_logic.EMPTY
            ]
            if len(set(values)) != len(values):
                return False

    return True


def test_generate_puzzle_returns_valid_board_structure():
    puzzle, solution = sudoku_logic.generate_puzzle(35)

    assert len(puzzle) == sudoku_logic.SIZE
    assert all(len(row) == sudoku_logic.SIZE for row in puzzle)
    assert len(solution) == sudoku_logic.SIZE
    assert all(len(row) == sudoku_logic.SIZE for row in solution)

    assert all(value != sudoku_logic.EMPTY for value in sum(solution, []))
    assert any(value == sudoku_logic.EMPTY for value in sum(puzzle, []))
    assert is_valid_board(puzzle)
    assert is_valid_board(solution)


def test_generate_puzzle_supports_difficulty_levels():
    easy_puzzle, _ = sudoku_logic.generate_puzzle(difficulty="easy")
    hard_puzzle, _ = sudoku_logic.generate_puzzle(difficulty="hard")

    easy_clues = sum(cell != sudoku_logic.EMPTY for row in easy_puzzle for cell in row)
    hard_clues = sum(cell != sudoku_logic.EMPTY for row in hard_puzzle for cell in row)

    assert easy_clues > hard_clues


def test_generate_puzzle_has_unique_solution():
    puzzle, _ = sudoku_logic.generate_puzzle(35)

    assert sudoku_logic.has_unique_solution(puzzle)

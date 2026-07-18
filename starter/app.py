from flask import Flask, render_template, jsonify, request
import sudoku_logic
import timer_utils

app = Flask(__name__)

# Shared in-memory game state for the current puzzle, timer, and leaderboard.

# Keep a simple in-memory store for current puzzle and solution
CURRENT = {
    'puzzle': None,
    'solution': None,
    'locked_cells': [],
    'difficulty': None,
    'leaderboard': [],
    'last_completion': None,
}


# Reset the shared game state when a new puzzle is created.
def reset_game_state(puzzle=None, solution=None, difficulty=None):
    CURRENT['puzzle'] = puzzle
    CURRENT['solution'] = solution
    CURRENT['locked_cells'] = []
    CURRENT['difficulty'] = difficulty
    CURRENT['last_completion'] = None
    timer_utils.reset_timer_state(CURRENT)


# Build the completion payload used by the response and leaderboard flow.
def get_completion_details():
    elapsed_seconds = timer_utils.get_elapsed_seconds(CURRENT)
    return {
        'elapsed_seconds': elapsed_seconds,
        'completion_time': timer_utils.format_elapsed_time(elapsed_seconds),
    }


def get_leaderboard(limit=10):
    entries = sorted(
        CURRENT.get('leaderboard', []),
        key=lambda entry: (entry.get('elapsed_seconds', 0), entry.get('submitted_at', '')),
    )
    return entries[:limit]


# Return the positions of all non-empty cells in the current puzzle.
def get_locked_cells(puzzle):
    return [
        [row, col]
        for row in range(sudoku_logic.SIZE)
        for col in range(sudoku_logic.SIZE)
        if puzzle[row][col] != sudoku_logic.EMPTY
    ]


# Find editable cells that are still empty and not already locked by a hint.
def get_available_empty_cells(puzzle):
    locked_cells = {tuple(cell) for cell in CURRENT.get('locked_cells', [])}
    return [
        [row, col]
        for row in range(sudoku_logic.SIZE)
        for col in range(sudoku_logic.SIZE)
        if puzzle[row][col] == sudoku_logic.EMPTY and (row, col) not in locked_cells
    ]


# Compare the submitted board against the solved board and report mismatches.
def get_incorrect_cells(board, solution):
    incorrect = []
    for i in range(sudoku_logic.SIZE):
        for j in range(sudoku_logic.SIZE):
            if board[i][j] != solution[i][j]:
                incorrect.append([i, j])
    return incorrect


# Check whether every cell has been filled in.
def is_board_complete(board):
    return all(cell != sudoku_logic.EMPTY for row in board for cell in row)


@app.route('/')
def index():
    return render_template('index.html')


# Normalize request parameters for puzzle generation.
def get_game_settings(args):
    clues = args.get('clues')
    difficulty = args.get('difficulty', '').strip().lower() or None
    return {
        'clues': int(clues) if clues is not None else None,
        'difficulty': difficulty,
    }


@app.route('/new')
def new_game():
    # Generate a fresh puzzle and reset the current game state for the client.
    settings = get_game_settings(request.args)
    puzzle, solution = sudoku_logic.generate_puzzle(
        clues=settings['clues'],
        difficulty=settings['difficulty'],
    )
    reset_game_state(
        puzzle=sudoku_logic.deep_copy(puzzle),
        solution=sudoku_logic.deep_copy(solution),
        difficulty=settings['difficulty'] or 'medium',
    )
    timer_utils.start_timer(CURRENT)
    return jsonify({'puzzle': sudoku_logic.deep_copy(CURRENT['puzzle'])})


@app.route('/timer')
def get_timer():
    return jsonify(timer_utils.get_timer_payload(CURRENT))


@app.route('/check', methods=['POST'])
def check_solution():
    # Validate the incoming board payload before comparing it to the solution.
    try:
        data = request.get_json(silent=True) or {}
    except Exception:
        data = {}

    board = data.get('board')
    solution = CURRENT.get('solution')
    if solution is None:
        return jsonify({'error': 'No game in progress'}), 400

    if not isinstance(board, list) or len(board) != sudoku_logic.SIZE or not all(isinstance(row, list) for row in board):
        return jsonify({'error': 'Invalid board payload'}), 400

    incorrect = get_incorrect_cells(board, solution)
    is_complete = is_board_complete(board)
    is_solved = not incorrect and is_complete

    completion = None
    if is_solved:
        timer_utils.stop_timer(CURRENT)
        completion = get_completion_details()
        CURRENT['last_completion'] = completion

    return jsonify({
        'incorrect': incorrect,
        'is_complete': is_complete,
        'is_solved': is_solved,
        'completion_time': completion['completion_time'] if completion else None,
        'elapsed_seconds': completion['elapsed_seconds'] if completion else None,
        'leaderboard': get_leaderboard(),
    })


@app.route('/leaderboard', methods=['POST'])
def save_leaderboard_entry():
    # Accept leaderboard submissions and normalize the incoming data.
    try:
        data = request.get_json(silent=True) or {}
    except Exception:
        data = {}

    name = (data.get('name') or '').strip() or 'Anonymous'
    elapsed_seconds = int(data.get('elapsed_seconds', 0) or 0)
    difficulty = (data.get('difficulty') or CURRENT.get('difficulty') or 'medium').strip().lower() or 'medium'

    CURRENT.setdefault('leaderboard', []).append({
        'name': name,
        'elapsed_seconds': elapsed_seconds,
        'difficulty': difficulty,
        'submitted_at': timer_utils.format_elapsed_time(elapsed_seconds),
    })

    return jsonify({'leaderboard': get_leaderboard()})


@app.route('/hint', methods=['POST'])
def give_hint():
    # Fill one available blank cell with the correct value and lock it for the player.
    if CURRENT.get('solution') is None or CURRENT.get('puzzle') is None:
        return jsonify({'error': 'No game in progress'}), 400

    empty_cells = get_available_empty_cells(CURRENT['puzzle'])
    if not empty_cells:
        return jsonify({'error': 'No empty cells left'}), 400

    row, col = empty_cells[0]
    CURRENT['puzzle'][row][col] = CURRENT['solution'][row][col]
    CURRENT['locked_cells'].append([row, col])

    return jsonify({
        'puzzle': sudoku_logic.deep_copy(CURRENT['puzzle']),
        'hinted_cell': [row, col],
        'locked_cells': sudoku_logic.deep_copy(CURRENT['locked_cells']),
    })

if __name__ == '__main__':
    app.run(debug=True)
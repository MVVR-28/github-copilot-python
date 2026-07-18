// Client-side rendering and interaction for the Flask-backed Sudoku
const SIZE = 9;
let puzzle = [];
let lockedCells = new Set();
let lastHintedCellIndex = null;
let timerInterval = null;
let completionData = null;

function getBoxTone(row, col) {
  return (Math.floor(row / 3) + Math.floor(col / 3)) % 2 === 0 ? 'primary' : 'secondary';
}

function handleCellFocus(event) {
  event.target.classList.add('selected');
}

function handleCellBlur(event) {
  event.target.classList.remove('selected');
}

function createBoardElement() {
  // Build the board DOM from the current puzzle size without changing the gameplay logic.
  const boardDiv = document.getElementById('sudoku-board');
  boardDiv.innerHTML = '';
  for (let i = 0; i < SIZE; i++) {
    const rowDiv = document.createElement('div');
    rowDiv.className = 'sudoku-row';
    for (let j = 0; j < SIZE; j++) {
      const input = document.createElement('input');
      input.type = 'text';
      input.maxLength = 1;
      input.className = 'sudoku-cell';
      input.dataset.row = i;
      input.dataset.col = j;
      input.dataset.boxTone = getBoxTone(i, j);
      input.addEventListener('input', handleCellInput);
      input.addEventListener('focus', handleCellFocus);
      input.addEventListener('blur', handleCellBlur);
      rowDiv.appendChild(input);
    }
    boardDiv.appendChild(rowDiv);
  }
}

function getCellIndex(row, col) {
  return row * SIZE + col;
}

function getBoardFromInputs() {
  const boardDiv = document.getElementById('sudoku-board');
  const inputs = boardDiv.getElementsByTagName('input');
  const board = [];
  for (let i = 0; i < SIZE; i++) {
    board[i] = [];
    for (let j = 0; j < SIZE; j++) {
      const idx = getCellIndex(i, j);
      const val = inputs[idx].value;
      board[i][j] = val ? parseInt(val, 10) : 0;
    }
  }
  return { board, inputs };
}

function getConflictSets(board) {
  const invalidCells = new Set();
  const conflictCells = new Set();

  for (let row = 0; row < SIZE; row++) {
    for (let col = 0; col < SIZE; col++) {
      const value = board[row][col];
      if (!value) {
        continue;
      }

      const relatedCells = [];
      for (let idx = 0; idx < SIZE; idx++) {
        if (idx !== col && board[row][idx] === value) {
          relatedCells.push(getCellIndex(row, idx));
        }
        if (idx !== row && board[idx][col] === value) {
          relatedCells.push(getCellIndex(idx, col));
        }
      }

      const boxRow = Math.floor(row / 3) * 3;
      const boxCol = Math.floor(col / 3) * 3;
      for (let boxRowIdx = boxRow; boxRowIdx < boxRow + 3; boxRowIdx++) {
        for (let boxColIdx = boxCol; boxColIdx < boxCol + 3; boxColIdx++) {
          if ((boxRowIdx !== row || boxColIdx !== col) && board[boxRowIdx][boxColIdx] === value) {
            relatedCells.push(getCellIndex(boxRowIdx, boxColIdx));
          }
        }
      }

      if (relatedCells.length > 0) {
        const currentCellIndex = getCellIndex(row, col);
        invalidCells.add(currentCellIndex);
        relatedCells.forEach((cellIndex) => conflictCells.add(cellIndex));
      }
    }
  }

  return { invalidCells, conflictCells };
}

function updateCellClasses(inputs, incorrectIndices = new Set(), board = null, hintedCellIndex = null, options = {}) {
  // Preserve the board styling while adding or removing validation and hint classes.
  const includeValidation = options.includeValidation !== false;
  const preserveExisting = options.preserveExisting === true;
  const validation = includeValidation && board ? getConflictSets(board) : { invalidCells: new Set(), conflictCells: new Set() };

  for (let idx = 0; idx < inputs.length; idx++) {
    const inp = inputs[idx];
    const shouldKeepSelection = inp.className.split(/\s+/).filter(Boolean).includes('selected');
    let classes = preserveExisting
      ? inp.className.split(/\s+/).filter(Boolean)
      : ['sudoku-cell'];

    if (!preserveExisting) {
      classes = ['sudoku-cell'];
    }

    if (shouldKeepSelection) {
      classes.push('selected');
    }

    if (inp.disabled && !classes.includes('prefilled')) {
      classes.push('prefilled');
    }
    if (hintedCellIndex === idx && !classes.includes('hinted')) {
      classes.push('hinted');
    }
    if (includeValidation && validation.invalidCells.has(idx)) {
      if (!classes.includes('invalid')) {
        classes.push('invalid');
      }
      classes = classes.filter((cls) => cls !== 'conflict');
    } else if (includeValidation && validation.conflictCells.has(idx)) {
      if (!classes.includes('conflict')) {
        classes.push('conflict');
      }
      classes = classes.filter((cls) => cls !== 'invalid');
    } else {
      classes = classes.filter((cls) => cls !== 'invalid' && cls !== 'conflict');
    }

    if (incorrectIndices.has(idx)) {
      if (!classes.includes('incorrect')) {
        classes.push('incorrect');
      }
    } else {
      classes = classes.filter((cls) => cls !== 'incorrect');
    }

    inp.className = classes.join(' ');
  }
}

function handleCellInput(e) {
  const cellIndex = getCellIndex(parseInt(e.target.dataset.row, 10), parseInt(e.target.dataset.col, 10));
  if (lockedCells.has(cellIndex)) {
    e.target.value = puzzle[parseInt(e.target.dataset.row, 10)][parseInt(e.target.dataset.col, 10)] || '';
    return;
  }

  const val = e.target.value.replace(/[^1-9]/g, '');
  e.target.value = val;
  const { board, inputs } = getBoardFromInputs();
  updateCellClasses(inputs, new Set(), board, lastHintedCellIndex, { includeValidation: true });
}

function renderPuzzle(puz, serverLockedCells = [], hintedCell = null) {
  // Render the latest puzzle state and keep the visual state in sync with the server data.
  puzzle = puz;
  lockedCells = new Set();
  const boardDiv = document.getElementById('sudoku-board');
  createBoardElement();
  const inputs = boardDiv.getElementsByTagName('input');

  serverLockedCells.forEach((cell) => {
    const idx = getCellIndex(cell[0], cell[1]);
    lockedCells.add(idx);
  });

  for (let i = 0; i < SIZE; i++) {
    for (let j = 0; j < SIZE; j++) {
      const idx = getCellIndex(i, j);
      const val = puzzle[i][j];
      const inp = inputs[idx];
      if (val !== 0 || lockedCells.has(idx)) {
        inp.value = val;
        inp.disabled = true;
      } else {
        inp.value = '';
        inp.disabled = false;
      }
    }
  }

  lastHintedCellIndex = hintedCell ? getCellIndex(hintedCell[0], hintedCell[1]) : null;
  updateCellClasses(inputs, new Set(), puzzle, lastHintedCellIndex);
}

async function refreshTimerDisplay() {
  const timerDisplay = document.getElementById('timer-display');
  const res = await fetch('/timer');
  const data = await res.json();
  timerDisplay.innerText = `Time: ${data.formatted_time}`;
}

function stopTimer() {
  if (timerInterval) {
    clearInterval(timerInterval);
    timerInterval = null;
  }
}

function showCompletionPanel(data) {
  const panel = document.getElementById('completion-panel');
  const message = document.getElementById('completion-message');
  panel.hidden = false;
  message.innerText = `You completed the puzzle in ${data.completion_time || '00:00'}!`;
}

function hideCompletionPanel() {
  document.getElementById('completion-panel').hidden = true;
}

function updateLeaderboard(entries) {
  const list = document.getElementById('leaderboard-list');
  list.innerHTML = '';
  entries.forEach((entry) => {
    const item = document.createElement('li');
    item.innerText = `${entry.name} — ${entry.elapsed_seconds}s (${entry.difficulty})`;
    list.appendChild(item);
  });
}

function startTimer() {
  stopTimer();
  timerInterval = setInterval(async () => {
    try {
      await refreshTimerDisplay();
    } catch (error) {
      stopTimer();
    }
  }, 1000);
}

function updateStatusMessage(message, isError = false) {
  const msg = document.getElementById('message');
  msg.style.color = isError ? '#d32f2f' : '#388e3c';
  msg.innerText = message;
}

async function newGame() {
  try {
    const difficulty = document.getElementById('difficulty-select').value;
    const res = await fetch(`/new?difficulty=${encodeURIComponent(difficulty)}`);
    if (!res.ok) {
      throw new Error('Request failed. Please try again.');
    }
    const data = await res.json();
    renderPuzzle(data.puzzle, [], null);
    completionData = null;
    hideCompletionPanel();
    updateStatusMessage('');
    document.getElementById('player-name').value = '';
    await refreshTimerDisplay();
    startTimer();
  } catch (error) {
    updateStatusMessage(error.message || 'Request failed. Please try again.', true);
  }
}

async function requestHint() {
  try {
    const res = await fetch('/hint', { method: 'POST' });
    if (!res.ok) {
      throw new Error('Request failed. Please try again.');
    }
    const data = await res.json();
    if (data.error) {
      updateStatusMessage(data.error, true);
      return;
    }
    renderPuzzle(data.puzzle, data.locked_cells || [], data.hinted_cell || null);
    updateStatusMessage('Hint used.');
  } catch (error) {
    updateStatusMessage(error.message || 'Request failed. Please try again.', true);
  }
}

async function checkSolution() {
  try {
    const { board, inputs } = getBoardFromInputs();
    const res = await fetch('/check', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ board })
    });
    if (!res.ok) {
      throw new Error('Request failed. Please try again.');
    }
    const data = await res.json();
    if (data.error) {
      updateStatusMessage(data.error, true);
      return;
    }
    const incorrect = new Set(data.incorrect.map((cell) => getCellIndex(cell[0], cell[1])));
    updateCellClasses(inputs, incorrect, board, lastHintedCellIndex, { includeValidation: false, preserveExisting: true });
    if (data.is_solved) {
      stopTimer();
      completionData = {
        completion_time: data.completion_time,
        elapsed_seconds: data.elapsed_seconds,
      };
      showCompletionPanel(completionData);
      await refreshTimerDisplay();
      updateStatusMessage('Congratulations! You solved it!');
      updateLeaderboard(data.leaderboard || []);
    } else if (incorrect.size === 0) {
      updateStatusMessage('No incorrect cells found.');
    } else {
      updateStatusMessage('Some cells are incorrect.', true);
    }
  } catch (error) {
    updateStatusMessage(error.message || 'Request failed. Please try again.', true);
  }
}

async function saveScore() {
  if (!completionData) {
    return;
  }

  try {
    const nameInput = document.getElementById('player-name');
    const difficulty = document.getElementById('difficulty-select').value;
    const res = await fetch('/leaderboard', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        name: nameInput.value,
        elapsed_seconds: completionData.elapsed_seconds,
        difficulty,
      })
    });
    if (!res.ok) {
      throw new Error('Request failed. Please try again.');
    }
    const data = await res.json();
    updateLeaderboard(data.leaderboard || []);
  } catch (error) {
    updateStatusMessage(error.message || 'Request failed. Please try again.', true);
  }
}

// Wire buttons
window.addEventListener('load', () => {
  document.getElementById('new-game').addEventListener('click', newGame);
  document.getElementById('hint-button').addEventListener('click', requestHint);
  document.getElementById('check-solution').addEventListener('click', checkSolution);
  document.getElementById('submit-score').addEventListener('click', saveScore);
  // initialize
  newGame();
});
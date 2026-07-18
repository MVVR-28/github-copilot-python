import app as app_module


def test_index_route_renders_home_page(client):
    response = client.get("/")

    assert response.status_code == 200
    assert b"Sudoku Game" in response.data


def test_index_route_includes_theme_toggle(client):
    response = client.get("/")

    assert response.status_code == 200
    assert b"theme-toggle" in response.data


def test_new_game_route_returns_puzzle(client):
    response = client.get("/new?clues=30")

    assert response.status_code == 200
    payload = response.get_json()
    assert "puzzle" in payload
    assert len(payload["puzzle"]) == 9
    assert all(len(row) == 9 for row in payload["puzzle"])
    assert app_module.CURRENT["solution"] is not None


def test_check_solution_route_reports_incorrect_cells(client):
    client.get("/new?clues=35")

    response = client.post(
        "/check",
        json={"board": app_module.CURRENT["solution"]},
    )
    assert response.status_code == 200
    assert response.get_json()["incorrect"] == []

    wrong_board = [row[:] for row in app_module.CURRENT["solution"]]
    wrong_board[0][0] = 2 if wrong_board[0][0] != 2 else 1

    response = client.post("/check", json={"board": wrong_board})
    assert response.status_code == 200
    assert [0, 0] in response.get_json()["incorrect"]


def test_check_solution_route_reports_completion_state(client):
    client.get("/new?clues=35")

    response = client.post(
        "/check",
        json={"board": app_module.CURRENT["solution"]},
    )

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["incorrect"] == []
    assert payload["is_complete"] is True
    assert payload["is_solved"] is True

    incomplete_board = [row[:] for row in app_module.CURRENT["solution"]]
    incomplete_board[0][0] = 0

    response = client.post("/check", json={"board": incomplete_board})

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["incorrect"] == [[0, 0]]
    assert payload["is_complete"] is False
    assert payload["is_solved"] is False


def test_check_solution_route_returns_error_without_active_game(client):
    response = client.post("/check", json={"board": []})

    assert response.status_code == 400
    assert response.get_json()["error"] == "No game in progress"


def test_check_solution_route_returns_completion_details(client):
    client.get("/new?clues=35")

    response = client.post(
        "/check",
        json={"board": app_module.CURRENT["solution"]},
    )

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["is_solved"] is True
    assert "completion_time" in payload
    assert payload["completion_time"].count(":") == 1
    assert payload["leaderboard"] == []


def test_leaderboard_route_records_and_returns_top_entries(client):
    response = client.post(
        "/leaderboard",
        json={"name": "Ada", "elapsed_seconds": 42, "difficulty": "easy"},
    )

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["leaderboard"][0]["name"] == "Ada"
    assert payload["leaderboard"][0]["elapsed_seconds"] == 42
    assert payload["leaderboard"][0]["difficulty"] == "easy"


def test_new_game_route_accepts_difficulty_parameter(client):
    easy_response = client.get("/new?difficulty=easy")
    hard_response = client.get("/new?difficulty=hard")

    assert easy_response.status_code == 200
    assert hard_response.status_code == 200

    easy_puzzle = easy_response.get_json()["puzzle"]
    hard_puzzle = hard_response.get_json()["puzzle"]
    easy_clues = sum(cell != 0 for row in easy_puzzle for cell in row)
    hard_clues = sum(cell != 0 for row in hard_puzzle for cell in row)

    assert easy_clues > hard_clues


def test_hint_route_fills_one_empty_cell_and_marks_it_locked(client):
    client.get("/new?clues=35")

    response = client.post("/hint")

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["hinted_cell"] is not None
    assert payload["puzzle"][payload["hinted_cell"][0]][payload["hinted_cell"][1]] == app_module.CURRENT["solution"][payload["hinted_cell"][0]][payload["hinted_cell"][1]]
    assert payload["locked_cells"] == [payload["hinted_cell"]]

    second_response = client.post("/hint")
    assert second_response.status_code == 200
    second_payload = second_response.get_json()
    assert len(second_payload["locked_cells"]) == 2
    assert second_payload["hinted_cell"] != payload["hinted_cell"]


def test_hint_route_returns_error_without_active_game(client):
    response = client.post("/hint")

    assert response.status_code == 400
    assert response.get_json()["error"] == "No game in progress"


def test_timer_route_tracks_game_runtime_and_stops_on_solution(client):
    client.get("/new?clues=35")

    timer_response = client.get("/timer")
    assert timer_response.status_code == 200
    timer_payload = timer_response.get_json()
    assert timer_payload["timer_running"] is True
    assert timer_payload["elapsed_seconds"] >= 0

    solved_response = client.post(
        "/check",
        json={"board": app_module.CURRENT["solution"]},
    )

    assert solved_response.status_code == 200
    assert solved_response.get_json()["is_solved"] is True

    stopped_timer_response = client.get("/timer")
    stopped_timer_payload = stopped_timer_response.get_json()
    assert stopped_timer_payload["timer_running"] is False

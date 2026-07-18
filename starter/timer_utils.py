import time


def reset_timer_state(game_state):
    game_state["timer_running"] = False
    game_state["timer_started_at"] = None
    game_state["timer_elapsed_seconds"] = 0
    return game_state


def start_timer(game_state):
    game_state["timer_running"] = True
    game_state["timer_started_at"] = time.time()
    game_state["timer_elapsed_seconds"] = 0
    return game_state


def stop_timer(game_state, now=None):
    elapsed_seconds = get_elapsed_seconds(game_state, now=now)
    game_state["timer_running"] = False
    game_state["timer_started_at"] = None
    game_state["timer_elapsed_seconds"] = elapsed_seconds
    return game_state


def get_elapsed_seconds(game_state, now=None):
    if not game_state.get("timer_running", False):
        return int(game_state.get("timer_elapsed_seconds", 0))

    started_at = game_state.get("timer_started_at")
    if started_at is None:
        return int(game_state.get("timer_elapsed_seconds", 0))

    current_time = now if now is not None else time.time()
    return int(current_time - started_at) + int(game_state.get("timer_elapsed_seconds", 0))


def get_timer_payload(game_state, now=None):
    elapsed_seconds = get_elapsed_seconds(game_state, now=now)
    return {
        "timer_running": game_state.get("timer_running", False),
        "elapsed_seconds": elapsed_seconds,
        "formatted_time": format_elapsed_time(elapsed_seconds),
    }


def format_elapsed_time(total_seconds):
    minutes, seconds = divmod(int(total_seconds), 60)
    return f"{minutes:02d}:{seconds:02d}"

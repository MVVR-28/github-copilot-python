import time


# Reset the timer-related fields when a new game begins.
def reset_timer_state(game_state):
    game_state["timer_running"] = False
    game_state["timer_started_at"] = None
    game_state["timer_elapsed_seconds"] = 0
    return game_state


# Begin timing a new game from the current timestamp.
def start_timer(game_state):
    game_state["timer_running"] = True
    game_state["timer_started_at"] = time.time()
    game_state["timer_elapsed_seconds"] = 0
    return game_state


# Stop the timer and preserve the elapsed time for the completed game.
def stop_timer(game_state, now=None):
    elapsed_seconds = get_elapsed_seconds(game_state, now=now)
    game_state["timer_running"] = False
    game_state["timer_started_at"] = None
    game_state["timer_elapsed_seconds"] = elapsed_seconds
    return game_state


# Return the current elapsed time, whether the timer is still running or already stopped.
def get_elapsed_seconds(game_state, now=None):
    if not game_state.get("timer_running", False):
        return int(game_state.get("timer_elapsed_seconds", 0))

    started_at = game_state.get("timer_started_at")
    if started_at is None:
        return int(game_state.get("timer_elapsed_seconds", 0))

    current_time = now if now is not None else time.time()
    return int(current_time - started_at) + int(game_state.get("timer_elapsed_seconds", 0))


# Build the timer payload used by the frontend for display and updates.
def get_timer_payload(game_state, now=None):
    elapsed_seconds = get_elapsed_seconds(game_state, now=now)
    return {
        "timer_running": game_state.get("timer_running", False),
        "elapsed_seconds": elapsed_seconds,
        "formatted_time": format_elapsed_time(elapsed_seconds),
    }


# Format elapsed seconds as MM:SS for the UI.
def format_elapsed_time(total_seconds):
    minutes, seconds = divmod(int(total_seconds), 60)
    return f"{minutes:02d}:{seconds:02d}"

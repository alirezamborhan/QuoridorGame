#! /usr/bin/python3
"""This module includes functions for the actual playing."""
import requests
import json
import threading
from time import sleep

import Glob
import Urls


def _set_bottom_info(text):
    # Log.
    if len(text) > 100:
        with open("QuoridorLog2.html", "w") as f:
            f.write(text)
    Glob.ui.infoBottomLabel.setText(text)

def _set_info(text):
    Glob.ui.infoLabel.setText(text)

def _check_turn():
    if Glob.turn == Glob.ui.username:
        return True
    return False

def _change_grids(main_grid, wallh_grid, wallv_grid, wallfills_grid, walls):
    """Update the grids on the UI."""
    # Update cells.
    for y in range(9):
        for x in range(9):
            if main_grid[y][x] == 0:
                Glob.ui.cells[y][x].setText("")
            else:
                Glob.ui.cells[y][x].setText(str(main_grid[y][x]))
    # Update horizontal walls.
    for y in range(8):
        for x in range(9):
            if wallh_grid[y][x] == 0:
                Glob.ui.wallsh[y][x].setPalette(Glob.ui.empty_wallh_palette)
            else:
                Glob.ui.wallsh[y][x].setPalette(Glob.ui.wall_palette)
    # Update vertical walls.
    for y in range(9):
        for x in range(8):
            if wallv_grid[y][x] == 0:
                Glob.ui.wallsv[y][x].setPalette(Glob.ui.empty_wallv_palette)
            else:
                Glob.ui.wallsv[y][x].setPalette(Glob.ui.wall_palette)
    # Update wallfills.
    for y in range(8):
        for x in range(8):
            if wallfills_grid[y][x] == 0:
                Glob.ui.wallfills[y][x].setPalette(Glob.ui.empty_wallv_palette)
            else:
                Glob.ui.wallfills[y][x].setPalette(Glob.ui.wall_palette)
    # Update wall numbers for each player.
    remaining_walls = "Remaining walls:\n"
    for user in ("1", "2", "3", "4"):
        if user in walls:
            remaining_walls += ("%s (%s): %d\n" %
                (walls[user][0], user, walls[user][1]))
    Glob.ui.remainingWallsLabel.setText(remaining_walls)

def _wait_for_turn(old_turn, starting=False):
    """Wait for the player's turn.
Works by connecting frequently to check status.
"""
    while True:
        sleep(Glob.wait_time)
        try:
            response = Glob.ui.session.get(Urls.urls["play_and_status"])
            _set_bottom_info("")
        except requests.exceptions.ConnectionError:
            _set_bottom_info("Connection failed.")
            continue
        
        result = response.text.split("\n")
        try:
            result[0] = json.loads(result[0])
        except ValueError:
            _set_bottom_info("Something went wrong: " + response.text)
            continue
        
        if not response.ok:
            _set_bottom_info(result[0]["error"])

        if "new" in result[0] or "waiting" in result[0]:
            _set_info(result[0]["status"])
            _set_bottom_info("")
            if "new" in result[0]:
                Glob.turn = result[0]["turn"]
            if len(result) > 1:
                main_grid = json.loads(result[1])
                wallh_grid = json.loads(result[2])
                wallv_grid = json.loads(result[3])
                wallfills_grid = json.loads(result[4])
                walls = json.loads(result[5])
                _change_grids(main_grid, wallh_grid, wallv_grid,
                              wallfills_grid, walls)
            continue

        if "winner" in result[0]:
            if result[0]["winner"] == Glob.ui.username:
                _set_info("You have won the game!")
            else:
                _set_info(result[0]["status"])
            _set_bottom_info("")
            Glob.ui.won = True

        if "stopped" in result[0]:
            _set_info(result[0]["status"])
            Glob.ui.stopped = True
            Glob.ui.goTo("twoOrFour")
            return

        main_grid = json.loads(result[1])
        wallh_grid = json.loads(result[2])
        wallv_grid = json.loads(result[3])
        wallfills_grid = json.loads(result[4])
        walls = json.loads(result[5])
        _change_grids(main_grid, wallh_grid, wallv_grid,
                      wallfills_grid, walls)

        if Glob.ui.won:
            return

        Glob.turn = result[0]["turn"]

        if result[0]["turn"] == Glob.ui.username:
            _set_info("It's your turn now.")
            _set_bottom_info("")
            break

        if result[0]["turn"] != old_turn:
            _set_info("It's %s's turn now. Waiting..." % result[0]["turn"])
            _set_bottom_info("")

def _wait_for_turn_thread(old_turn, starting=False):
    thread = threading.Thread(target=_wait_for_turn,
                              args=(old_turn,), kwargs={"starting": starting})
    thread.daemon = True
    thread.start()


def _request_move(payload):
    """Sends a request to the server containing the game move."""
    try:
        response = Glob.ui.session.post(Urls.urls["play_and_status"], data=payload)
    except requests.exceptions.ConnectionError:
        _set_bottom_info("Connection failed.")
        return

    result = response.text.split("\n")
    try:
        result[0] = json.loads(result[0])
    except ValueError:
        _set_bottom_info("Something went wrong: " + response.text)
        return

    if "error" in result[0]:
        if response.status_code == 405:
            _set_bottom_info("")
            _set_info(result[0]["error"])
        else:
            _set_bottom_info(result[0]["error"])
            _set_info("")
        return


    # Extract data and update grids.
    status = result[0]["status"]
    if "winner" in result[0]:
        if result[0]["winner"] == Glob.ui.username:
            _set_info("You have won the game!")
        else:
            _set_info(result[0]["status"])
        _set_bottom_info("")
        Glob.ui.won = True
    else:
        turn = result[0]["turn"]
        Glob.turn = result[0]["turn"]
    main_grid = json.loads(result[1])
    wallh_grid = json.loads(result[2])
    wallv_grid = json.loads(result[3])
    wallfills_grid = json.loads(result[4])
    walls = json.loads(result[5])
    _change_grids(main_grid, wallh_grid, wallv_grid, wallfills_grid, walls)

    if Glob.ui.won:
        return

    _set_info("Done. It's %s's turn now. Waiting..." % turn)
    _set_bottom_info("")
    _wait_for_turn_thread(turn)


def clickedCell(x, y):
    """Slot function for a cell being clicked."""
    if not _check_turn() or Glob.ui.won or Glob.ui.stopped:
        return
    payload = {"move": json.dumps({"type": "move", "x": x, "y": y})}
    _request_move(payload)


def clickedWallh(x, y):
    """Slot function for a horizontal wall being clicked."""
    if not _check_turn() or Glob.ui.won or Glob.ui.stopped:
        return
    payload = {"move": json.dumps({"type": "wall", "direction": "h",
                                   "x": x, "y": y})}
    _request_move(payload)


def clickedWallv(x, y):
    """Slot function for a vertical wall being clicked."""
    if not _check_turn() or Glob.ui.won or Glob.ui.stopped:
        return
    payload = {"move": json.dumps({"type": "wall", "direction": "v",
                                   "x": x, "y": y})}
    _request_move(payload)


def clickedWallfill(x, y):
    pass

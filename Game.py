#! /usr/bin/python3

import requests
import json
from time import sleep

import Glob


def _set_bottom_info(text):
    Glob.ui.infoBottomLabel.setText(text)

def _set_info(text):
    Glob.ui.infoLabel.setText(text)

def _check_turn():
    if Glob.turn == Glob.username:
        return True
    return False

def _change_grids(main_grid, wallh_grid, wallv_grid, wallfills_grid):
    """Update the grids on the UI."""
    # Update cells.
    for y in range(9):
        for x in range(9):
            if main_grid[y][x] == 0:
                Glob.ui.cells[y][x].setText("")
            else:
                Glob.ui.cells[y][x].setText(main_grid[y][x])
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

def clickedCell(x, y):
    """Slot function for a cell being clicked.
Sends a request to the server containing the game move.
"""
    if not _check_turn():
        return

    payload = {"type": "move", "x": str(x), "y": str(y)}
    try:
        request = requests.post(Glob.urls["play_and_status"], data=payload)
    except requests.exceptions.ConnectionError:
        _set_bottom_info("Connection failed.")
        return

    result = request.text.split("\n")
    result[0] = json.loads(result[0])

    if not request.ok:
        if request.status_code == 405:
            _set_bottom_info("")
            _set_info(result[0]["error"])
        else:
            _set_bottom_info(result[0]["error"])
            _set_info("")
        return

    if result[0]["turn"] != Glob.username:
        _set_bottom_info("It's not your turn.")

    # Extract data.
    status = result[0]["status"]
    turn = result[0]["turn"]
    Glob.turn = response[0]["turn"]
    main_grid = json.loads(result[1])
    wallh_grid = json.loads(result[2])
    wallv_grid = json.loads(result[3])
    wallfills_grid = json.loads(result[4])

    _change_grids(main_grid, wallh_grid, wallv_grid, wallfills_grid)

    _set_info("Done. It's %s's turn now." % turn)
    _set_bottom_info("")

    # Wait for the player's turn.
    # Connects frequently to check status.
    while True:
        sleep(Glob.wait_time)
        try:
            request = requests.get(Glob.urls["play_and_status"])
            _set_bottom_info("")
        except requests.exceptions.ConnectionError:
            _set_bottom_info("Connection failed.")
            continue
        
        result = request.text.split("\n")
        try:
            result[0] = json.loads(result[0])
        except ValueError:
            _set_bottom_info("Something went wrong.")
            continue
        
        if not request.ok:
            _set_bottom_info(result[0]["error"])

        Glob.turn = response[0]["turn"]

        if response[0]["turn"] == Glob.username:
            _set_info("It's your turn now.")
            _set_bottom_info("")
            break

        if response[0]["turn"] != turn:
            _set_info("It's %s's turn now." % response[0]["turn"])
            _set_bottom_info("")

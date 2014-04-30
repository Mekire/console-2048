from __future__ import print_function

import os
import sys
import copy
import random
import functools

#Python 2/3 compatibility.
if sys.version_info[0] == 2:
    range = xrange
    input = raw_input


def _getch_windows(prompt):
    """
    Windows specific version of getch.  Special keys like arrows actually post
    two key events.  If you want to use these keys you can create a dictionary
    and return the result of looking up the appropriate second key within the
    if block.
    """
    print(prompt, end="")
    key = msvcrt.getch()
    if ord(key) == 224:
        key = msvcrt.getch()
        return key
    print(key.decode())
    return key.decode()


def _getch_linux(prompt):
    """Linux specific version of getch."""
    print(prompt, end="")
    sys.stdout.flush()
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    new = termios.tcgetattr(fd)
    new[3] = new[3] & ~termios.ICANON & ~termios.ECHO
    new[6][termios.VMIN] = 1
    new[6][termios.VTIME] = 0
    termios.tcsetattr(fd, termios.TCSANOW, new)
    char = None
    try:
        char = os.read(fd, 1)
    finally:
        termios.tcsetattr(fd, termios.TCSAFLUSH, old)
    print(char)
    return char


#Set version of getch to use based on operating system.
if sys.platform[:3] == 'win':
    import msvcrt
    getch = _getch_windows
else:
    import termios
    getch = _getch_linux


def push_row(row, left=True):
    """Push all tiles in one row; like tiles will be merged together."""
    row = row[:] if left else row[::-1]
    new_row = [item for item in row if item]
    for i in range(len(new_row)-1):
        if new_row[i] and new_row[i] == new_row[i+1]:
            new_row[i], new_row[i+1:] = new_row[i]*2, new_row[i+2:]+[""]
    new_row += [""]*(len(row)-len(new_row))
    return new_row if left else new_row[::-1]


def get_column(grid, column_index):
    """Return the column from the grid at column_index  as a list."""
    return [row[column_index] for row in grid]


def set_column(grid, column_index, new):
    """
    Replace the values in the grid at column_index with the values in new.
    The grid is changed inplace.
    """
    for i,row in enumerate(grid):
        row[column_index] = new[i]


def push_all_rows(grid, left=True):
    """
    Perform a horizontal shift on all rows.
    Pass left=True for left and left=False for right.
    The grid will be changed inplace.
    """
    for i,row in enumerate(grid):
        grid[i] = push_row(row, left)


def push_all_columns(grid, up=True):
    """
    Perform a vertical shift on all columns.
    Pass up=True for up and up=False for down.
    The grid will be changed inplace.
    """
    for i,val in enumerate(grid[0]):
        column = get_column(grid, i)
        new = push_row(column, up)
        set_column(grid, i, new)


def get_empty_cells(grid):
    """Return a list of coordinate pairs corresponding to empty cells."""
    empty = []
    for j,row in enumerate(grid):
        for i,val in enumerate(row):
            if not val:
                empty.append((j,i))
    return empty


def any_possible_moves(grid):
    """Return True if there are any legal moves, and False otherwise."""
    if get_empty_cells(grid):
        return True
    for row in grid:
        if any(row[i]==row[i+1] for i in range(len(row)-1)):
            return True
    for i,val in enumerate(grid[0]):
        column = get_column(grid, i)
        if any(column[i]==column[i+1] for i in range(len(column)-1)):
            return True
    return False


def get_start_grid(cols=4, rows=4):
    """Create the start grid and seed it with two numbers."""
    grid = [[""]*cols for i in range(rows)]
    for i in range(2):
        empties = get_empty_cells(grid)
        y,x = random.choice(empties)
        grid[y][x] = 2 if random.random() < 0.9 else 4
    return grid


def prepare_next_turn(grid):
    """
    Spawn a new number on the grid; then return the result of
    any_possible_moves after this change has been made.
    """
    empties = get_empty_cells(grid)
    y,x = random.choice(empties)
    grid[y][x] = 2 if random.random() < 0.9 else 4
    return any_possible_moves(grid)


def print_grid(grid):
    """Print a pretty grid to the screen."""
    print("")
    wall = "+------"*len(grid[0])+"+"
    print(wall)
    for row in grid:
        meat = "|".join("{:^6}".format(val) for val in row)
        print("|{}|".format(meat))
        print(wall)


def main():
    """
    Get user input.
    Update game state.
    Display updates to user.
    """
    functions = {"a" : functools.partial(push_all_rows, left=True),
                 "d" : functools.partial(push_all_rows, left=False),
                 "w" : functools.partial(push_all_columns, up=True),
                 "s" : functools.partial(push_all_columns, up=False)}
    grid = get_start_grid(*map(int,sys.argv[1:]))
    print_grid(grid)
    while True:
        grid_copy = copy.deepcopy(grid)
        get_input = getch("Enter direction (w/a/s/d): ")
        if get_input in functions:
            functions[get_input](grid)
        elif get_input == "q":
            break
        else:
            print("\nInvalid choice.")
            continue
        if grid != grid_copy:
            if not prepare_next_turn(grid):
                print_grid(grid)
                print("You Lose!")
                break
        print_grid(grid)
    print("Thanks for playing.")


if __name__ == "__main__":
    main()


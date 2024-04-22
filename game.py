# Import pygame library
import streamlit as st
import pygame 
from pygame import * 
import random

import webbrowser 
from tkinter import Tk 
from tkinter import filedialog as fd 
import os

# Declare base variables
SIZE_X_START = 3  # Initial width of the game board 
SIZE_Y_START = 3  # Initial height of the game board
CUBE_SIZE = 100   # Size of each cube in pixels 
BORDER = 5        # Spacing between cubes 
TILE = 10         # Size of a smaller square unit used in drawing 
SHIFT = 3         # Adds perspective effect to cube drawing
PANEL_SIZE = 30 * 5  # Height of the menu/button panel 
BACKGROUND_COLOR = "#000000"  # Hex code for black background
GRAY_COLOR = "#808080"    
GRAY_COLOR2 = "#A0A0A0"    

CUBE_COLOR = [("W","#ffffea"), ("R","#973aa8"), ("B","#0000ff"), 
              ("Y","#ffff3f"), ("P","#ef476f"), ("G","#70e000")]  # Cube face colors

def init_level(y, x):
    """Creates the initial game board layout.

    Args:
        y: Number of rows on the board.
        x: Number of columns on the board.

    Returns:
        A list of lists representing the board, where each inner list is a row, 
        and each item in a row represents a cube with its top and back face colors.
    """
    level = []
    for ny in range(y):
        str = []  # 'str' might not be the best variable name here (e.g., 'row')
        for nx in range(x):
            str.append(["W", "B"])  # Initialize all cubes as white top, blue back
        level.append(str)

    ny = y // 2   # Find the middle row
    nx = x // 2   # Find the middle column 
    level[ny][nx] = [" ", " "]  # Create an empty space in the center

    return level

def init_level_digit(y, x, level):
    """Assigns tile numbers for tracking the solved state.

    Args:
        y: Number of rows on the board.
        x: Number of columns on the board.
        level: The current layout of the board. 

    Returns:
        A board of the same size, where empty and blocked tiles have "0" and 
        visible cube tiles are numbered to help track if the puzzle is solved.
    """
    level_digit = []
    nn = 1  # Tile number counter
    for ny in range(y):
        stroka = [] 
        for nx in range(x):
            cube = level[ny][nx]
            if cube[0] == " " or cube[0] == "X":  
                stroka.append("0")  
            else:
                stroka.append(str(nn))  
                nn += 1
        level_digit.append(stroka)
    return level_digit

def next_cubes(top, face):
    """Calculates the new orientation of a cube after a roll.

    Args:
        top: The current top face color of the cube (e.g., "W", "R").
        face: The current front face color of the cube.

    Returns:
        A list representing the new colors of the cube's faces in their 
        correct positions after a roll. This is likely used to update the board.
    """

    for face_ind, COLOR_ONE in enumerate(CUBE_COLOR):
        if COLOR_ONE[0] == face: 
            break  # Find the index of the current front face in CUBE_COLOR
    for top_ind, COLOR_ONE in enumerate(CUBE_COLOR):
        if COLOR_ONE[0] == top:
            break  # Find the index of the current top face

    back_ind = (top_ind + 3) % 6  # Calculate the index of the back face

    # 'vek' likely determines roll direction (positive or negative)
    vek = 1 - (top_ind % 2) * 2  

    face_set = CUBE_COLOR.copy()  # Create a copy to work with
    face1 = min(top_ind, back_ind)  # Helps determine order of faces in face_set
    face_set.pop(face1)
    face_set.pop(face1 + 2)  # Remove two faces from the set

    if vek < 0:  # Reverse the order for a roll in a certain direction 
        face_set.reverse()

    # Rotate the face_set until the original 'face' color is at the front
    while face_set[0][0] != face:
        elem = face_set.pop(0)
        face_set.append(elem)

    return face_set 

def check_button(place, y, x):
    """Determines if a mouse click happened within a button's area.

    Args:
        place:  A tuple containing (left, top, right, bottom) coordinates of the button.
        y: Y-coordinate of the mouse click.
        x: X-coordinate of the mouse click.

    Returns:
        True if the click was inside the button's area, False otherwise.
    """

    if (x >= place.left) and (x <= place.right) and (y >= place.top) and (y <= place.bottom):
        return True
    return False

def main():
    # Constants
    SIZE_X = SIZE_X_START  # Initial board width
    SIZE_Y = SIZE_Y_START  # Initial board height
    file_ext = False  # Likely for loading a board from a file (not used yet)
    digit_mode = False  # Likely to display tile numbers

    # Initialise
    random.seed()   
    pygame.init()  # Start PyGame
    font = pygame.font.SysFont('Verdana', 18)  
    fontd = pygame.font.SysFont('Verdana', 24)  
    timer = pygame.time.Clock()  # For controlling the game's framerate
    Tk().withdraw()  # Hide default Tkinter window

    # Restart after changing parameters
    while True:  
        # Additional constants
        WIN_WIDTH = SIZE_X * CUBE_SIZE  
        WIN_HEIGHT = SIZE_Y * CUBE_SIZE + PANEL_SIZE 
        DISPLAY = (WIN_WIDTH, WIN_HEIGHT)  

        if file_ext:
            file_ext = False  # Would reset if loading from a file
        else:
            level = init_level(SIZE_Y, SIZE_X)   # Create starting board
            level_digit = init_level_digit(SIZE_Y, SIZE_X, level)  # Tile numbers
        moves_stack = []    # To store moves (likely for undo functionality)
        moves = 0           
        solved = True       # Whether the puzzle is currently solved
        scramble_move = 0   # Likely for scrambling the board
        edit_mode = False   # Might be a mode to edit the board layout
        square = 0          

        # Window initialization
        screen = pygame.display.set_mode(DISPLAY) 
        pygame.display.set_caption("Rolling Cubes") 
        screen.fill(BACKGROUND_COLOR)  

        # Initialise all buttons
        button_y1 = CUBE_SIZE * SIZE_Y + BORDER + 10
        button_reset = font.render('Reset', True, CUBE_COLOR[2][1], CUBE_COLOR[5][1])
        button_reset_place = button_reset.get_rect(topleft=(10, button_y1))

        # Main program loop 
        while True:
            vek = mouse_x = mouse_y = cube_pos_x = cube_pos_y = 0
            undo = False

            ########################################################################
            # Rendering menu items and buttons
            if scramble_move == 0:

                # Menu
                pf_black = Surface((CUBE_SIZE * SIZE_X, PANEL_SIZE))
                pf_black.fill(Color("#000000"))  # Black panel background
                screen.blit(pf_black, (0, CUBE_SIZE * SIZE_Y))
                pf = Surface((CUBE_SIZE * SIZE_X, 5))
                pf.fill(Color("#B88800"))  # Decorative line
                screen.blit(pf, (0, CUBE_SIZE * SIZE_Y + BORDER))

                # Text
                text_moves = font.render('Moves: ' + str(moves), True, CUBE_COLOR[1][1])  # Moves counter
                text_moves_place = text_moves.get_rect(topleft=(button_reset_place.right + 10, button_y1))
                screen.blit(text_moves, text_moves_place)

                # 'Solved' status
                if solved:
                    text_solved = font.render('Solved', True, CUBE_COLOR[0][1])  # White
                else:
                    text_solved = font.render('Not Solved', True, CUBE_COLOR[5][1])  # Purple?
                text_solved_place = text_solved.get_rect(topleft=(text_moves_place.right + 10, button_y1))
                screen.blit(text_solved, text_solved_place)

                # Reset Button
                screen.blit(button_reset, button_reset_place)

                 # Event handling (continued)
            if scramble_move == 0: 
                timer.tick(10)  # Limit to around 10 updates per second

                for ev in pygame.event.get():  
                    if (ev.type == QUIT) or (ev.type == KEYDOWN and ev.key == K_ESCAPE):
                        return SystemExit, "QUIT"  # Exit the game

                    if ev.type == KEYDOWN and ev.key == K_UP:
                        vek = 1  # Likely sets the roll direction to 'up'
                    if ev.type == KEYDOWN and ev.key == K_LEFT:
                        vek = 2
                    if ev.type == KEYDOWN and ev.key == K_DOWN:
                        vek = 3
                    if ev.type == KEYDOWN and ev.key == K_RIGHT:
                        vek = 4

                    if ev.type == MOUSEBUTTONDOWN and ev.button == 1:
                        mouse_x = ev.pos[0]
                        mouse_y = ev.pos[1]
            else:
                cube_pos_x = random.randint(0,SIZE_X-1)
                cube_pos_y = random.randint(0,SIZE_Y-1)

            # Handle button clicks
            if mouse_x + mouse_y > 0 and scramble_move == 0:
                if mouse_y > CUBE_SIZE * SIZE_Y + BORDER:  
                    if check_button(button_reset_place, mouse_y, mouse_x):  # Reset
                        break  # Exit the inner loop (and likely reset the game)

                # Handling dice clicks
                else:
                    # Determine coordinates of the clicked cube 
                    xx = mouse_x // CUBE_SIZE   # Column index of the cube
                    xx2 = mouse_x % CUBE_SIZE   # X-coordinate within the cube 
                    if xx2 > 0: 
                        xx += 1  # Adjust if the click was on the right half of the cube
                    yy = mouse_y // CUBE_SIZE   # Row index of the cube
                    yy2 = mouse_y % CUBE_SIZE   # Y-coordinate within the cube
                    if yy2 > 0: 
                        yy += 1  # Adjust if the click was on the bottom half of the cube
                    xx -= 1  # Shift coordinates back since arrays start at 0
                    yy -= 1  

                    cube_pos_x = xx  
                    cube_pos_y = yy  

                    # Determine which side was clicked
                    nn1 = xx2 > yy2 
                    nn2 = (CUBE_SIZE - xx2) > yy2
                    if nn1 and nn2:
                        vek2 = 1  # Likely 'up'
                    elif (not nn1) and nn2:
                        vek2 = 2  # Likely 'left'
                    elif (not nn1) and (not nn2):
                        vek2 = 3  # Likely 'down' 
                    elif nn1 and (not nn2):
                        vek2 = 4  # Likely 'right'

                    if not edit_mode:  # Assuming edit_mode allows modifying the board
                        cube = level[yy][xx]
                        if cube[0] != " " and cube[0] != "X":  # Ignore empty and blocked cubes
                            num = 0  # Initialize a counter for empty cells

                            # Check for an empty cell above 
                            if yy != 0:  # Ensure the cube is not already on the top row
                                cube_test = level[yy - 1][xx]  # Get the cube directly above the clicked one
                                if cube_test[0] == " ":  # Check if this upper cube is empty
                                    vek = 1  # Set the tentative roll direction to 'up'
                                    num += 1  # Found an empty cell, increment the counter

                            # Check for an empty cell to the left
                            if xx != 0:  # Ensure the cube is not already on the leftmost column
                                cube_test = level[yy][xx - 1]  # Get the cube to the left 
                                if cube_test[0] == " ":  
                                    vek = 2  # Set the tentative roll direction to 'left'
                                    num += 1 

                            # Check for an empty cell below 
                            if yy != SIZE_Y - 1:  # Ensure the cube is not on the bottom row
                                cube_test = level[yy + 1][xx]  # Get the cube directly below 
                                if cube_test[0] == " ":  
                                    vek = 3  # Set the tentative roll direction to 'down'
                                    num += 1 

                            # Check for an empty cell to the right
                            if xx != SIZE_X - 1:  # Ensure the cube is not on the rightmost column
                                cube_test = level[yy][xx + 1]  # Get the cube to the right 
                                if cube_test[0] == " ": 
                                    vek = 4  # Set the tentative roll direction to 'right'
                                    num += 1  
            if vek != 0:  # A roll direction has been indicated
                if mouse_x + mouse_y == 0:  # Input is from the keyboard 
                    # Search for an empty cell 
                    fl = False
                    for ny in range(SIZE_Y):
                        for nx in range(SIZE_X):
                            cube = level[ny][nx]
                            if cube[0] == " ": 
                                fl = True 
                                break  # Found an empty cell, stop searching
                        if fl: 
                            break  # Stop outer loop as well
                    # Empty cell coordinates are now in 'nyp' and 'nxp'
                    # found the position of an empty cell
                    nyp = ny
                    nxp = nx

                    # Find the position of the cube that will be rolled
                    fl = True  # Initialize a flag to signal if a valid roll is possible 
                    if vek == 1:  # Check if the roll direction is 'up'
                        if ny == SIZE_Y - 1:  # Check if the cube is already at the top edge
                            fl = False  # If at the edge, the cube can't roll up
                        ny += 1  # Look at the cube above for rolling (since we're rolling up)
                    elif vek == 3:  # Check if the roll direction is 'down'
                        if ny == 0:  # Check if the cube is already at the bottom edge 
                            fl = False  # If at the edge, the cube can't roll down
                        ny -= 1  # Look at the cube below for rolling 
                    elif vek == 2:  # Check if the roll direction is 'left'
                        if nx == SIZE_X - 1:  # Check if the cube is already at the rightmost edge
                            fl = False  # If at the edge, the cube can't roll left
                        nx += 1  # Look at the cube to the right for rolling
                    elif vek == 4:  # Check if the roll direction is 'right'
                        if nx == 0:  # Check if the cube is already at the leftmost edge
                            fl = False  # If at the edge, the cube can't roll right
                        nx -= 1  # Look at the cube to the left for rolling 
                else:  # Assuming mouse click 
                    # Coordinates of clicked cube calculated earlier
                    nxp = nx = cube_pos_x
                    nyp = ny = cube_pos_y

                    # Ensure a valid empty cell exists for the roll
                    fl = True   # Reset the 'fl' flag
                    if vek == 1:  # Check if rolling 'up'
                        if nyp == 0:  # Check if we're trying to roll off the top 
                            fl = False 
                        nyp -= 1  # Check the cell above the cube for emptiness
                    elif vek == 3:  # Check if rolling 'down'
                        if nyp == SIZE_Y - 1:  # Check if we're trying to roll off the bottom
                            fl = False 
                        nyp += 1  # Check the cell below the cube for emptiness
                    elif vek == 2:  # Check if rolling 'left'
                        if nxp == 0:  # Check if we're trying to roll off the left edge
                            fl = False 
                        nxp -= 1  # Check the cell to the left of the cube for emptiness
                    elif vek == 4:  # Check if rolling 'right'
                        if nxp == SIZE_X - 1:  # Check if we're trying to roll off the right edge
                            fl = False 
                        nxp += 1  # Check the cell to the right of the cube for emptiness 

                # The rotation of the cube itself
                if fl:  # Check if a valid roll was determined earlier
                    cube = level[ny][nx]  # Store the cube to be rolled 
                    cube0 = level[nyp][nxp]  # Store the contents of the empty cell

                    if cube[0] != "X" and cube0[0] == " ":  # Can only roll non-blocked cubes into empty spaces
                        face_set = next_cubes(cube[0], cube[1])  # Calculate new face arrangement (1st rotation)
                        face_set2 = next_cubes(face_set[4 - vek][0], cube[0])  # Adjust based on roll direction (2nd rotation)

                        # Update the cube's faces based on the roll direction ('vek')
                        if vek == 1:  # UP
                            cube = [face_set2[3][0], face_set2[2][0]] 
                        elif vek == 3:  # DOWN
                            cube = [face_set2[3][0], face_set2[0][0]] 
                        elif vek == 2:  # LEFT
                            cube = [face_set2[3][0], cube[1]]  
                        elif vek == 4:  # RIGHT
                            cube = [face_set2[3][0], cube[1]]  

                        level[ny][nx] = [" ", " "]  # Clear the cube's old position in the board data 
                        level[nyp][nxp] = cube  # Place the rotated cube in the new position

                        if digit_mode:  # If tile numbers are enabled
                            # Swap tile numbers to reflect the roll 
                            level_digit[ny][nx], level_digit[nyp][nxp] = level_digit[nyp][nxp], level_digit[ny][nx]

                        if not undo:  # Assuming 'undo' relates to undoing moves
                            moves += 1  # Increment the move counter
                            moves_stack.append([vek, nyp, nxp])  # Likely store the move for undo functionality

            if scramble_move != 0:  # Assuming 'scramble_move' is for scrambling the board
                scramble_move -= 1  # Decrement a scramble counter
                moves_stack = []  # Potentially clear the undo history during a scramble
                moves = 0  # Reset the move count during a scramble
                continue  # Likely skips to the next iteration of a loop (not shown) 
            
            # Drawing cubes on the playing field
            x = y = 0  # Initialize coordinates for drawing
            for ny, row in enumerate(level):  # Iterate over each row in the board ('level')
                for nx, cube in enumerate(row):  # Iterate over each cube within a row
                    if cube[0] == " ":  #  Check for an empty space
                        # Empty cell
                        pf = Surface((CUBE_SIZE, CUBE_SIZE))  # Create a surface the size of a cube
                        pf.fill(Color(BACKGROUND_COLOR))  # Fill with the background color
                        screen.blit(pf, (x, y))  # Draw the empty cell on the screen 

                    elif cube[0] == "X":  # Check for a blocked cube
                        # Blocked cube
                        pf = Surface((CUBE_SIZE - BORDER * 2 + 2, CUBE_SIZE - BORDER * 2 + 2))  # Smaller surface for the block
                        pf.fill(Color(GRAY_COLOR))  # Fill with a gray color
                        screen.blit(pf, (x + BORDER, y + BORDER))  # Draw with an offset (the border)

                        # Draw diagonal 'X' lines
                        draw.line(screen, GRAY_COLOR2, (x + BORDER + TILE, y + BORDER + TILE), 
                                (x + BORDER + CUBE_SIZE - BORDER * 2 - TILE, y + BORDER + CUBE_SIZE - BORDER * 2 - TILE), 10) 
                        draw.line(screen, GRAY_COLOR2, (x + BORDER + CUBE_SIZE - BORDER * 2 - TILE, y + BORDER + TILE), 
                                (x + BORDER + TILE, y + BORDER + CUBE_SIZE - BORDER * 2 - TILE), 10)

                    else:  # Cube with visible faces

                        # Top face
                        pf = Surface((CUBE_SIZE - BORDER * 2 - TILE * 2, CUBE_SIZE - BORDER * 2 - TILE * 2)) 
                        for up, COLOR_ONE in enumerate(CUBE_COLOR):  # Find the matching color 
                            if COLOR_ONE[0] == cube[0]: 
                                pf.fill(Color(COLOR_ONE[1]))  # Fill the surface with the color
                                break  # Stop searching once the color is found
                        screen.blit(pf, (x + BORDER + TILE, y + BORDER + TILE))  # Draw the top face
                        face_set = next_cubes(cube[0],cube[1])

                        # Front face
                        for nn, COLOR_ONE in enumerate(CUBE_COLOR):  # Iterate through color options
                            if COLOR_ONE[0] == face_set[0][0]:  # Find matching color for the front face
                                # Draw the front face polygon using coordinates
                                draw.polygon(screen, COLOR_ONE[1], [
                                    [x + BORDER + TILE, y + CUBE_SIZE - BORDER - TILE],  # Top left corner
                                    [x + BORDER + TILE + CUBE_SIZE - BORDER * 2 - TILE * 2, y + CUBE_SIZE - BORDER - TILE],  # Top right corner
                                    [x + BORDER + TILE + CUBE_SIZE - BORDER * 2 - TILE * 2 - SHIFT, y + CUBE_SIZE - BORDER - TILE + TILE],  # Bottom right corner (shifted inwards)
                                    [x + BORDER + TILE + SHIFT, y + CUBE_SIZE - BORDER - TILE + TILE]  # Bottom left corner (shifted inwards)
                                ])
                                break  # Stop searching once the color is found

                        # Left face
                        for nn, COLOR_ONE in enumerate(CUBE_COLOR):  # Iterate through color options
                            if COLOR_ONE[0] == face_set[1][0]:  # Find matching color for the left face
                                # Draw the left face polygon using coordinates (similar to front face)
                                draw.polygon(screen, COLOR_ONE[1], [
                                    [x + BORDER, y + BORDER + TILE + SHIFT],  # Top left corner (shifted upwards)
                                    [x + BORDER + TILE, y + BORDER + TILE],  # Top right corner
                                    [x + BORDER + TILE, y + BORDER + TILE + CUBE_SIZE - BORDER * 2 - TILE * 2],  # Bottom right corner
                                    [x + BORDER, y + BORDER + TILE + CUBE_SIZE - BORDER * 2 - TILE * 2 - SHIFT]  # Bottom left corner (shifted downwards)
                                ])
                                break  # Stop searching once the color is found

                        # Back face
                        for nn, COLOR_ONE in enumerate(CUBE_COLOR):  # Iterate through color options
                            if COLOR_ONE[0] == face_set[2][0]:  # Find matching color for the back face
                                # Draw the back face polygon using coordinates (similar to front face)
                                draw.polygon(screen, COLOR_ONE[1], [
                                    [x + BORDER + TILE + SHIFT, y + BORDER],  # Top left corner (shifted upwards)
                                    [x + BORDER + TILE + CUBE_SIZE - BORDER * 2 - TILE * 2 - SHIFT, y + BORDER],  # Top right corner (shifted upwards)
                                    [x + BORDER + TILE + CUBE_SIZE - BORDER * 2 - TILE * 2, y + BORDER + TILE],  # Bottom right corner
                                    [x + BORDER + TILE, y + BORDER + TILE]  # Bottom left corner
                                ])
                                break  # Stop searching once the color is found

                        # Right face
                        for nn, COLOR_ONE in enumerate(CUBE_COLOR):  # Iterate through color options
                            if COLOR_ONE[0] == face_set[3][0]:  # Find matching color for the right face
                                # Draw the right face polygon using coordinates (similar to front face)
                                draw.polygon(screen, COLOR_ONE[1], [
                                    [x + CUBE_SIZE - BORDER - TILE, y + BORDER + TILE],  # Top left corner
                                    [x + CUBE_SIZE - BORDER - TILE + TILE, y + BORDER + TILE + SHIFT],  # Top right corner (shifted upwards)
                                    [x + CUBE_SIZE - BORDER - TILE + TILE, y + BORDER + TILE + CUBE_SIZE - BORDER * 2 - TILE * 2 - SHIFT],  # Bottom right corner (shifted downwards)
                                    [x + CUBE_SIZE - BORDER - TILE, y + BORDER + TILE + CUBE_SIZE - BORDER * 2 - TILE * 2]  # Bottom left corner
                                ])
                                break  # Stop searching once the color is found
                        # Numbers
                        if digit_mode: 
                            if level_digit[ny][nx] != "0":  # Check if a tile number should be displayed
                                digit = fontd.render(level_digit[ny][nx], True, BACKGROUND_COLOR)  # Create the number text
                                digit_place = digit.get_rect(center=(x + CUBE_SIZE / 2, y + CUBE_SIZE / 2))  # Center the text
                                screen.blit(digit, digit_place)  # Draw the number

                    x += CUBE_SIZE  # Move drawing position to the right
                y += CUBE_SIZE  # Move drawing position down
                x = 0  # Reset 'x' for the next row

            # Check for solved state
            solved = True  # Assume the puzzle is solved initially 
            for ny, row in enumerate(level):  # Iterate over each row in the board ('level')
                if not solved: break  # Stop checking if already determined not solved
                for nx, cube in enumerate(row):  # Iterate over each cube in the row
                    if cube[0] == " " or cube[0] == "X": 
                        continue  # Ignore empty or blocked cubes
                    if cube[0] == "W" or cube[1] == "Y":  # Check if cube's color matches the solution
                        solved = False
                        break  # Stop checking this row if a mismatch is found 

            if digit_mode and solved:  # If tile number mode is on and the puzzle is solved
                num = 1  # Initialize the tile number counter
                for row in level_digit:  # Iterate over each row in 'level_digit'
                    if not solved: break  # Stop checking if already determined not solved
                    for dig in row:  # Iterate over each digit in the row
                        if dig == "0": continue  # Ignore empty tiles
                        if dig != str(num):  # Check if the tile number is correct
                            solved = False
                            break  # Stop checking the row if a mismatch is found
                        num += 1  # Increment the expected tile number

            pygame.display.update()  # Update the entire display to reflect any changes
st.title("Rolling Cubes Game") # Likely restarts the game or level
if st.button("Play"):
    pygame.init()  # Start PyGame
    main()  # Run the game when the button is clicked
    pygame.quit()  # Quit PyGame after the game finishes
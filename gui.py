# gui.py

import pygame
import copy
from engine import (
    create_board, is_valid_move, make_move,
    get_available_captures, count_pieces,
    calculate_score, promote_to_king, handle_multi_capture
)

# Constants
ROWS, COLS = 8, 8
MARGIN = 40  # Margin around the board
BUTTON_HEIGHT = 40
BUTTON_MARGIN = 20
BUTTON_AREA = BUTTON_HEIGHT + BUTTON_MARGIN * 2

# Colors
LIGHT_BROWN = (245, 222, 179)
DARK_BROWN = (139, 69, 19)
GREEN = (50, 205, 50)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (70, 130, 180)

# Load sounds and images
pygame.init()
move_sound = pygame.mixer.Sound("assets/move.wav")
king_image_red = pygame.image.load("assets/red_king.png")
king_image_black = pygame.image.load("assets/black_king.png")

# Responsive layout
info = pygame.display.Info()
SCREEN_WIDTH = min(info.current_w - 100, 720)
max_board_height = info.current_h - 180
SQUARE_SIZE = min((SCREEN_WIDTH - MARGIN * 2) // COLS, (max_board_height - MARGIN * 2 - BUTTON_AREA) // ROWS)
BOARD_SIZE = SQUARE_SIZE * ROWS
SCREEN_HEIGHT = BOARD_SIZE + BUTTON_AREA + MARGIN * 2

# Resize images
king_image_red = pygame.transform.scale(king_image_red, (SQUARE_SIZE - 10, SQUARE_SIZE - 10))
king_image_black = pygame.transform.scale(king_image_black, (SQUARE_SIZE - 10, SQUARE_SIZE - 10))

WIN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Checkers GUI")

# Button dimensions responsive to width
button_width = SCREEN_WIDTH // 4
undo_button = pygame.Rect(SCREEN_WIDTH // 8, SCREEN_HEIGHT - BUTTON_AREA + BUTTON_MARGIN, button_width, BUTTON_HEIGHT)
redo_button = pygame.Rect(SCREEN_WIDTH * 5 // 8, SCREEN_HEIGHT - BUTTON_AREA + BUTTON_MARGIN, button_width, BUTTON_HEIGHT)

# Drawing functions
def draw_board(win, board, valid_moves):
    win.fill(WHITE)
    for row in range(ROWS):
        for col in range(COLS):
            x = MARGIN + col * SQUARE_SIZE
            y = MARGIN + row * SQUARE_SIZE
            color = DARK_BROWN if (row + col) % 2 else LIGHT_BROWN
            pygame.draw.rect(win, color, (x, y, SQUARE_SIZE, SQUARE_SIZE))
            if (row, col) in valid_moves:
                pygame.draw.rect(win, GREEN, (x, y, SQUARE_SIZE, SQUARE_SIZE))

    for row in range(ROWS):
        for col in range(COLS):
            piece = board[row][col]
            if piece != ' ':
                center = (MARGIN + col * SQUARE_SIZE + SQUARE_SIZE // 2, MARGIN + row * SQUARE_SIZE + SQUARE_SIZE // 2)
                if piece == 'B':
                    pygame.draw.circle(win, BLACK, center, SQUARE_SIZE // 2 - 10)
                elif piece == 'R':
                    pygame.draw.circle(win, RED, center, SQUARE_SIZE // 2 - 10)
                elif piece == 'BK':
                    win.blit(king_image_black, (center[0] - king_image_black.get_width() // 2, center[1] - king_image_black.get_height() // 2))
                elif piece == 'RK':
                    win.blit(king_image_red, (center[0] - king_image_red.get_width() // 2, center[1] - king_image_red.get_height() // 2))

    draw_buttons(win)
    pygame.display.update()

def draw_buttons(win):
    pygame.draw.rect(win, BLUE, undo_button, border_radius=8)
    pygame.draw.rect(win, BLUE, redo_button, border_radius=8)
    font = pygame.font.SysFont(None, 28)
    undo_text = font.render("Undo", True, WHITE)
    redo_text = font.render("Redo", True, WHITE)
    win.blit(undo_text, (undo_button.centerx - undo_text.get_width() // 2, undo_button.centery - undo_text.get_height() // 2))
    win.blit(redo_text, (redo_button.centerx - redo_text.get_width() // 2, redo_button.centery - redo_text.get_height() // 2))

def get_row_col_from_mouse(pos):
    x, y = pos
    x -= MARGIN
    y -= MARGIN
    return y // SQUARE_SIZE, x // SQUARE_SIZE

def main():
    board = create_board()
    clock = pygame.time.Clock()
    run = True
    selected = None
    current_player = 'B'
    valid_moves = []
    move_log = []
    undo_stack = []
    redo_stack = []

    while run:
        clock.tick(60)
        draw_board(WIN, board, valid_moves)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()

                if undo_button.collidepoint(mouse_pos) and move_log:
                    redo_stack.append((copy.deepcopy(board), current_player))
                    board = undo_stack.pop()
                    current_player = 'R' if current_player == 'B' else 'B'
                    selected = None
                    valid_moves = []
                    continue
                elif redo_button.collidepoint(mouse_pos) and redo_stack:
                    undo_stack.append(copy.deepcopy(board))
                    board, current_player = redo_stack.pop()
                    selected = None
                    valid_moves = []
                    continue

                row, col = get_row_col_from_mouse(mouse_pos)
                if not (0 <= row < ROWS and 0 <= col < COLS):
                    continue

                if selected:
                    if is_valid_move(board, *selected, row, col, current_player):
                        undo_stack.append(copy.deepcopy(board))
                        redo_stack.clear()
                        new_r, new_c = make_move(board, *selected, row, col, current_player, move_log)
                        promote_to_king(board, new_r, new_c, current_player)
                        move_sound.play()

                        before_switch = (new_r, new_c)
                        after_r, after_c = handle_multi_capture(board, new_r, new_c, current_player, move_log)
                        if (after_r, after_c) == before_switch:
                            current_player = 'R' if current_player == 'B' else 'B'
                    selected = None
                    valid_moves = []
                elif board[row][col].startswith(current_player):
                    selected = (row, col)
                    valid_moves = get_available_captures(board, row, col, current_player)

        pygame.display.set_caption(f"Checkers - {current_player}'s Turn")

    pygame.quit()

if __name__ == "__main__":
    main()

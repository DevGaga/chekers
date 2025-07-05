# gui.py

import pygame
import copy
from engine import (
    create_board, is_valid_move, make_move,
    get_available_captures, count_pieces,
    calculate_score, promote_to_king, handle_multi_capture,
    player_has_captures
)

# Constants
ROWS, COLS = 8, 8
BUTTON_HEIGHT = 40
BUTTON_MARGIN = 10
BUTTON_AREA = BUTTON_HEIGHT + BUTTON_MARGIN * 2

# Margins and layout
LEFT_MARGIN = 120
RIGHT_MARGIN = 10
TOP_MARGIN = 10
BOTTOM_MARGIN = 10 + BUTTON_AREA

# Colors
LIGHT_BROWN = (245, 222, 179)
DARK_BROWN = (139, 69, 19)
GREEN = (50, 205, 50)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (70, 130, 180)

# Initialize pygame and load resources
pygame.init()

move_sound = pygame.mixer.Sound("assets/move.wav")
king_image_red = pygame.image.load("assets/red_king.png")
king_image_black = pygame.image.load("assets/black_king.png")
logo = pygame.image.load("assets/ireens_logo.png")

info = pygame.display.Info()
SCREEN_WIDTH = min(info.current_w - 50, 800)
max_board_height = info.current_h - 120

available_width = SCREEN_WIDTH - LEFT_MARGIN - RIGHT_MARGIN
SQUARE_SIZE = min(
    available_width // COLS,
    (max_board_height - TOP_MARGIN - BOTTOM_MARGIN) // ROWS
)
BOARD_SIZE = SQUARE_SIZE * ROWS
SCREEN_HEIGHT = BOARD_SIZE + TOP_MARGIN + BOTTOM_MARGIN

king_image_red = pygame.transform.scale(king_image_red, (SQUARE_SIZE - 10, SQUARE_SIZE - 10))
king_image_black = pygame.transform.scale(king_image_black, (SQUARE_SIZE - 10, SQUARE_SIZE - 10))
logo = pygame.transform.scale(logo, (LEFT_MARGIN - 20, LEFT_MARGIN - 20))

WIN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Checkers GUI")

button_width = SCREEN_WIDTH // 4
undo_button = pygame.Rect(SCREEN_WIDTH // 8, SCREEN_HEIGHT - BUTTON_AREA + BUTTON_MARGIN, button_width, BUTTON_HEIGHT)
redo_button = pygame.Rect(SCREEN_WIDTH * 5 // 8, SCREEN_HEIGHT - BUTTON_AREA + BUTTON_MARGIN, button_width, BUTTON_HEIGHT)

def draw_board(win, board, valid_moves):
    win.fill(WHITE)
    win.blit(logo, (10, TOP_MARGIN))

    for row in range(ROWS):
        for col in range(COLS):
            x = LEFT_MARGIN + col * SQUARE_SIZE
            y = TOP_MARGIN + row * SQUARE_SIZE
            color = DARK_BROWN if (row + col) % 2 else LIGHT_BROWN
            pygame.draw.rect(win, color, (x, y, SQUARE_SIZE, SQUARE_SIZE))
            if (row, col) in valid_moves:
                pygame.draw.rect(win, GREEN, (x, y, SQUARE_SIZE, SQUARE_SIZE))

    for row in range(ROWS):
        for col in range(COLS):
            piece = board[row][col]
            if piece != ' ':
                center = (LEFT_MARGIN + col * SQUARE_SIZE + SQUARE_SIZE // 2, TOP_MARGIN + row * SQUARE_SIZE + SQUARE_SIZE // 2)
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

def draw_alert(win, message):
    if message:
        font = pygame.font.SysFont(None, 32)
        text = font.render(message, True, RED)
        win.blit(text, (LEFT_MARGIN + 10, SCREEN_HEIGHT - BUTTON_AREA - 30))

def get_row_col_from_mouse(pos):
    x, y = pos
    x -= LEFT_MARGIN
    y -= TOP_MARGIN
    return y // SQUARE_SIZE, x // SQUARE_SIZE

def get_all_capture_positions(board, player):
    positions = []
    for r in range(ROWS):
        for c in range(COLS):
            if board[r][c].startswith(player):
                if get_available_captures(board, r, c, player):
                    positions.append((r, c))
    return positions

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
    alert_message = ""

    while run:
        clock.tick(60)
        draw_board(WIN, board, get_all_capture_positions(board, current_player) if alert_message else valid_moves)
        draw_alert(WIN, alert_message)
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()

                if undo_button.collidepoint(mouse_pos) and undo_stack:
                    redo_stack.append((copy.deepcopy(board), current_player))
                    board = undo_stack.pop()
                    current_player = 'R' if current_player == 'B' else 'B'
                    selected = None
                    valid_moves = []
                    alert_message = ""
                    continue
                elif redo_button.collidepoint(mouse_pos) and redo_stack:
                    undo_stack.append(copy.deepcopy(board))
                    board, current_player = redo_stack.pop()
                    selected = None
                    valid_moves = []
                    alert_message = ""
                    continue

                row, col = get_row_col_from_mouse(mouse_pos)
                if not (0 <= row < ROWS and 0 <= col < COLS):
                    continue

                if selected:
                    if player_has_captures(board, current_player):
                        if is_valid_move(board, *selected, row, col, current_player, is_capture=True):
                            undo_stack.append(copy.deepcopy(board))
                            redo_stack.clear()
                            new_r, new_c = make_move(board, *selected, row, col, current_player, move_log)
                            promote_to_king(board, new_r, new_c, current_player)
                            move_sound.play()
                            selected = None
                            valid_moves = []
                            alert_message = ""
                            before_switch = (new_r, new_c)
                            after_r, after_c = handle_multi_capture(board, new_r, new_c, current_player, move_log)
                            if (after_r, after_c) == before_switch:
                                current_player = 'R' if current_player == 'B' else 'B'
                        else:
                            alert_message = "⚠️ You must capture!"
                            selected = None
                            valid_moves = []
                    else:
                        if is_valid_move(board, *selected, row, col, current_player):
                            undo_stack.append(copy.deepcopy(board))
                            redo_stack.clear()
                            new_r, new_c = make_move(board, *selected, row, col, current_player, move_log)
                            promote_to_king(board, new_r, new_c, current_player)
                            move_sound.play()
                            selected = None
                            valid_moves = []
                            alert_message = ""
                            before_switch = (new_r, new_c)
                            after_r, after_c = handle_multi_capture(board, new_r, new_c, current_player, move_log)
                            if (after_r, after_c) == before_switch:
                                current_player = 'R' if current_player == 'B' else 'B'
                        else:
                            alert_message = "Invalid move."
                            selected = None
                            valid_moves = []
                elif board[row][col].startswith(current_player):
                    selected = (row, col)
                    valid_moves = get_available_captures(board, row, col, current_player) if player_has_captures(board, current_player) else []
                    alert_message = ""

        pygame.display.set_caption(f"Checkers - {current_player}'s Turn")

    pygame.quit()

if __name__ == "__main__":
    main()

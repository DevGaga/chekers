# gui.py
import pygame
from engine import create_board, is_valid_move, make_move, get_available_captures, count_pieces, calculate_score, promote_to_king

# Constants
WIDTH, HEIGHT = 640, 640
ROWS, COLS = 8, 8
SQUARE_SIZE = WIDTH // COLS

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
move_sound = pygame.mixer.Sound("assets\move.wav")
king_image_red = pygame.image.load("assets\red_king.png")
king_image_black = pygame.image.load("black_king.png")
king_image_red = pygame.transform.scale(king_image_red, (SQUARE_SIZE - 10, SQUARE_SIZE - 10))
king_image_black = pygame.transform.scale(king_image_black, (SQUARE_SIZE - 10, SQUARE_SIZE - 10))

WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Checkers GUI")

# Drawing functions
def draw_board(win, board, valid_moves):
    for row in range(ROWS):
        for col in range(COLS):
            color = DARK_BROWN if (row + col) % 2 else LIGHT_BROWN
            pygame.draw.rect(win, color, (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
            if (row, col) in valid_moves:
                pygame.draw.rect(win, GREEN, (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

    for row in range(ROWS):
        for col in range(COLS):
            piece = board[row][col]
            if piece != ' ':
                center = (col * SQUARE_SIZE + SQUARE_SIZE // 2, row * SQUARE_SIZE + SQUARE_SIZE // 2)
                if piece == 'B':
                    pygame.draw.circle(win, BLACK, center, SQUARE_SIZE // 2 - 10)
                elif piece == 'R':
                    pygame.draw.circle(win, RED, center, SQUARE_SIZE // 2 - 10)
                elif piece == 'BK':
                    win.blit(king_image_black, (col * SQUARE_SIZE + 5, row * SQUARE_SIZE + 5))
                elif piece == 'RK':
                    win.blit(king_image_red, (col * SQUARE_SIZE + 5, row * SQUARE_SIZE + 5))

    pygame.display.update()

def get_row_col_from_mouse(pos):
    x, y = pos
    return y // SQUARE_SIZE, x // SQUARE_SIZE

def main():
    board = create_board()
    clock = pygame.time.Clock()
    run = True
    selected = None
    current_player = 'B'
    valid_moves = []
    move_log = []

    while run:
        clock.tick(60)
        draw_board(WIN, board, valid_moves)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                row, col = get_row_col_from_mouse(pygame.mouse.get_pos())
                if selected:
                    if is_valid_move(board, *selected, row, col, current_player):
                        make_move(board, *selected, row, col, current_player, move_log)
                        promote_to_king(board, row, col, current_player)
                        move_sound.play()
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

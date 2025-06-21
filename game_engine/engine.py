# Initialize the board
def create_board():
    board = []
    for row in range(8):
        board_row = []
        for column in range(8):
            if (row + column) % 2 == 1:  # Dark squares
                if row < 3:
                    board_row.append('B')  # Black pieces
                elif row > 4:
                    board_row.append('R')  # Red pieces
                else:
                    board_row.append(' ')  # Empty square
            else:
                board_row.append(' ')  # Light squares
        board.append(board_row)
    return board

# Print the board for visualization
def print_board(board):
    for row in board:
        print(' '.join(row))

# --- CALLING THE FUNCTIONS ---
board = create_board()
print_board(board)

def is_valid_move(board, start_row, start_col, end_row, end_col, player):
    # Ensure move is inside the board
    if not all(0 <= n < 8 for n in [start_row, start_col, end_row, end_col]):
        return False

    piece = board[start_row][start_col]
    dest = board[end_row][end_col]

    # Move must be to an empty dark square
    if dest != ' ' or (start_row + start_col) % 2 != 1 or (end_row + end_col) % 2 != 1:
        return False

    # Direction of movement
    direction = -1 if player == 'B' else 1  # Black moves down, Red moves up

    # Normal move (one diagonal step)
    if (end_row == start_row + direction and abs(end_col - start_col) == 1):
        return True

    # Capture move (two diagonal steps over opponent)
    if (end_row == start_row + 2 * direction and abs(end_col - start_col) == 2):
        mid_row = (start_row + end_row) // 2
        mid_col = (start_col + end_col) // 2
        mid_piece = board[mid_row][mid_col]
        if mid_piece != ' ' and mid_piece != player:
            return True

    return False


def make_move(board, start_row, start_col, end_row, end_col, player):
    # Handle captures
    if abs(end_row - start_row) == 2:
        mid_row = (start_row + end_row) // 2
        mid_col = (start_col + end_col) // 2
        board[mid_row][mid_col] = ' '  # Remove captured piece

    board[end_row][end_col] = player
    board[start_row][start_col] = ' '


# Main game loop (simplified for testing)
board = create_board()
current_player = 'B'

while True:
    print_board(board)
    print(f"\n{current_player}'s turn")
    try:
        move = input("Enter move (start_row start_col end_row end_col): ")
        sr, sc, er, ec = map(int, move.strip().split())

        if board[sr][sc] != current_player:
            print("You can only move your own piece.")
            continue

        if is_valid_move(board, sr, sc, er, ec, current_player):
            make_move(board, sr, sc, er, ec, current_player)
            current_player = 'R' if current_player == 'B' else 'B'
        else:
            print("Invalid move. Try again.")
    except Exception as e:
        print("Error:", e)
        print("Invalid input format. Use: start_row start_col end_row end_col")

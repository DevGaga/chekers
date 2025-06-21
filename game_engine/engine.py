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
    print("  " + " ".join(map(str, range(8))))  # Column numbers
    for idx, row in enumerate(board):
        print(str(idx) + ' ' + ' '.join(row))  # Row numbers

# Check if move is valid
def is_valid_move(board, start_row, start_col, end_row, end_col, player, is_capture=False):
    if not all(0 <= n < 8 for n in [start_row, start_col, end_row, end_col]):
        return False

    if board[start_row][start_col] != player:
        return False

    if board[end_row][end_col] != ' ':
        return False

    d_row = end_row - start_row
    d_col = end_col - start_col

    # Normal move (only forward allowed)
    if abs(d_row) == 1 and abs(d_col) == 1 and not is_capture:
        if (player == 'B' and d_row == 1) or (player == 'R' and d_row == -1):
            return True
        return False

    # Capture move (allow all directions)
    if abs(d_row) == 2 and abs(d_col) == 2:
        mid_row = (start_row + end_row) // 2
        mid_col = (start_col + end_col) // 2
        middle_piece = board[mid_row][mid_col]
        if middle_piece != ' ' and middle_piece != player:
            return True

    return False

# Make a move (and handle capture)
def make_move(board, start_row, start_col, end_row, end_col, player):
    if abs(end_row - start_row) == 2:
        mid_row = (start_row + end_row) // 2
        mid_col = (start_col + end_col) // 2
        board[mid_row][mid_col] = ' '
    board[end_row][end_col] = player
    board[start_row][start_col] = ' '
    return end_row, end_col

# Get all possible captures from a position
def get_available_captures(board, row, col, player):
    directions = [(-2, -2), (-2, 2), (2, -2), (2, 2)]
    captures = []
    for dr, dc in directions:
        new_r, new_c = row + dr, col + dc
        if is_valid_move(board, row, col, new_r, new_c, player, is_capture=True):
            captures.append((new_r, new_c))
    return captures

# --- GAME STARTS HERE ---
board = create_board()
current_player = 'B'

while True:
    print_board(board)
    print(f"\n{current_player}'s turn")
    try:
        move = input("Enter move (start_row start_col end_row end_col): ")
        sr, sc, er, ec = map(int, move.strip().split())

        if not is_valid_move(board, sr, sc, er, ec, current_player):
            print("Invalid move.")
            continue

        sr, sc = make_move(board, sr, sc, er, ec, current_player)

        # Multi-capture loop
        while True:
            captures = get_available_captures(board, sr, sc, current_player)
            if not captures:
                break
            print_board(board)
            print(f"{current_player}, you have another capture from ({sr}, {sc})!")
            print("Available jumps:", captures)
            next_input = input("Enter next jump (end_row end_col): ")
            try:
                new_er, new_ec = map(int, next_input.strip().split())
                if (new_er, new_ec) not in captures:
                    print("Invalid jump. Turn ends.")
                    break
                sr, sc = make_move(board, sr, sc, new_er, new_ec, current_player)
            except:
                print("Invalid input. Turn ends.")
                break

        # Switch turn
        current_player = 'R' if current_player == 'B' else 'B'

    except Exception as e:
        print("Error:", e)
        print("Invalid input format. Use: start_row start_col end_row end_col")

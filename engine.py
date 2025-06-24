# engine.py

def create_board():
    board = []
    for row in range(8):
        board_row = []
        for col in range(8):
            if (row + col) % 2 == 1:
                if row < 3:
                    board_row.append('B')
                elif row > 4:
                    board_row.append('R')
                else:
                    board_row.append(' ')
            else:
                board_row.append(' ')
        board.append(board_row)
    return board

def print_board(board):
    print("  " + " ".join(map(str, range(8))))
    for idx, row in enumerate(board):
        print(str(idx) + ' ' + ' '.join(p if len(p) == 2 else ' ' + p for p in row))

def is_king(piece):
    return piece in ['BK', 'RK']

def promote_to_king(board, row, col, player):
    if player == 'B' and row == 7:
        board[row][col] = 'BK'
    elif player == 'R' and row == 0:
        board[row][col] = 'RK'

def is_valid_move(board, sr, sc, er, ec, player, is_capture=False):
    if not all(0 <= n < 8 for n in [sr, sc, er, ec]):
        return False

    piece = board[sr][sc]
    if piece not in [player, player + 'K']:
        return False

    if board[er][ec] != ' ':
        return False

    dr = er - sr
    dc = ec - sc
    abs_dr = abs(dr)
    abs_dc = abs(dc)

    if abs_dr == 1 and abs_dc == 1 and not is_capture:
        if is_king(piece):
            return True
        elif (player == 'B' and dr == 1) or (player == 'R' and dr == -1):
            return True
        return False

    if abs_dr == 2 and abs_dc == 2:
        mid_row = (sr + er) // 2
        mid_col = (sc + ec) // 2
        middle = board[mid_row][mid_col]
        if middle != ' ' and middle[0] != player:
            return True
        return False

    if is_king(piece) and abs_dr == abs_dc:
        enemies = 0
        step_r = 1 if dr > 0 else -1
        step_c = 1 if dc > 0 else -1
        r, c = sr + step_r, sc + step_c
        enemy_pos = None
        while r != er and c != ec:
            if board[r][c] != ' ':
                if board[r][c][0] != player:
                    enemies += 1
                    if enemies > 1:
                        return False
                    enemy_pos = (r, c)
                else:
                    return False
            r += step_r
            c += step_c
        return enemies == 1

    return False

def make_move(board, sr, sc, er, ec, player, move_log):
    piece = board[sr][sc]
    move_log.append((sr, sc, er, ec, piece))

    if abs(er - sr) > 1:
        step_r = 1 if er > sr else -1
        step_c = 1 if ec > sc else -1
        r, c = sr + step_r, sc + step_c
        while r != er and c != ec:
            if board[r][c] != ' ' and board[r][c][0] != player:
                board[r][c] = ' '
                break
            r += step_r
            c += step_c

    board[er][ec] = piece
    board[sr][sc] = ' '
    promote_to_king(board, er, ec, player)
    return er, ec

def get_available_captures(board, r, c, player):
    piece = board[r][c]
    captures = []
    if is_king(piece):
        for d in range(1, 8):
            for dr, dc in [(-d, -d), (-d, d), (d, -d), (d, d)]:
                er, ec = r + dr, c + dc
                if 0 <= er < 8 and 0 <= ec < 8 and is_valid_move(board, r, c, er, ec, player, is_capture=True):
                    captures.append((er, ec))
    else:
        for dr, dc in [(-2, -2), (-2, 2), (2, -2), (2, 2)]:
            er, ec = r + dr, c + dc
            if 0 <= er < 8 and 0 <= ec < 8 and is_valid_move(board, r, c, er, ec, player, is_capture=True):
                captures.append((er, ec))
    return captures

def has_any_moves(board, player):
    for r in range(8):
        for c in range(8):
            if board[r][c] in [player, player + 'K']:
                for dr in [-1, 1]:
                    for dc in [-1, 1]:
                        nr, nc = r + dr, c + dc
                        if 0 <= nr < 8 and 0 <= nc < 8 and is_valid_move(board, r, c, nr, nc, player):
                            return True
                if get_available_captures(board, r, c, player):
                    return True
    return False

def count_pieces(board):
    flat = sum(board, [])
    return {
        'B': sum(p.startswith('B') and not is_king(p) for p in flat),
        'BK': sum(p == 'BK' for p in flat),
        'R': sum(p.startswith('R') and not is_king(p) for p in flat),
        'RK': sum(p == 'RK' for p in flat)
    }

def calculate_score(piece_counts):
    return {
        'B': piece_counts['B'] * 1 + piece_counts['BK'] * 3,
        'R': piece_counts['R'] * 1 + piece_counts['RK'] * 3
    }

def detect_draw(piece_counts):
    kings = piece_counts['BK'] + piece_counts['RK']
    total = piece_counts['B'] + piece_counts['R']
    return kings >= 2 and total <= 2

def replay_game(move_log):
    board = create_board()
    print("\n📽️ Replaying game:")
    for move in move_log:
        sr, sc, er, ec, piece = move
        board[er][ec] = piece
        board[sr][sc] = ' '
        print_board(board)
        input("Press Enter for next move...")

if __name__ == "__main__":
    board = create_board()
    current_player = 'B'
    move_log = []

    while True:
        print_board(board)
        print(f"\n{current_player}'s turn")
        piece_counts = count_pieces(board)

        if not has_any_moves(board, current_player):
            print(f"🛑 {current_player} has no valid moves. Game over!")
            winner = 'R' if current_player == 'B' else 'B'
            print(f"🎉 {winner} wins!")
            break

        if detect_draw(piece_counts):
            print("🤝 It's a draw! Only kings or 1 piece left each.")
            break

        try:
            move = input("Enter move (start_row start_col end_row end_col): ")
            sr, sc, er, ec = map(int, move.strip().split())

            if not is_valid_move(board, sr, sc, er, ec, current_player):
                print("❌ Invalid move.")
                continue

            sr, sc = make_move(board, sr, sc, er, ec, current_player, move_log)

            # Multi-capture loop
            while True:
                captures = get_available_captures(board, sr, sc, current_player)
                if not captures:
                    break
                print_board(board)
                print(f"{current_player}, you have another capture from ({sr}, {sc})!")
                print("Available jumps:", captures)
                next_jump = input("Next jump (end_row end_col): ")
                try:
                    new_er, new_ec = map(int, next_jump.strip().split())
                    if (new_er, new_ec) not in captures:
                        print("Invalid capture. Ending turn.")
                        break
                    sr, sc = make_move(board, sr, sc, new_er, new_ec, current_player, move_log)
                except:
                    print("Invalid input. Ending chain.")
                    break

            current_player = 'R' if current_player == 'B' else 'B'
        except Exception as e:
            print("⚠️ Error:", e)
            print("Use format: start_row start_col end_row end_col")

    ans = input("🔁 Replay game? (y/n): ").lower()
    if ans == 'y':
        replay_game(move_log)

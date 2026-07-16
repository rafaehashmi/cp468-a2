//CONSTANTS
ROWS = 6
COLUMNS = 7
CONNECT_ALL = 4

EMPTY = 0
ONE = 1
TWO = 2


class ConnectFour:
    """
    Connect Four game state

    Board values:
        0 = empty
        1 = Player 1
        2 = Player 2

    Row 0 top
    Row 5 bottom
    """

    def __init__(self, board, current_player=ONE):
        """
        Initialize a Connect Four object.

        Since @dataclass is no longer being used, the constructor must
        be written manually.
        """
        self.board = board
        self.current_player = current_player

    @classmethod
    def new_game(cls):
        """Create and return an empty Connect Four board."""
        board = [
            [EMPTY for column in range(COLUMNS)]
            for row in range(ROWS)
        ]

        return cls(
            board=board,
            current_player=ONE
        )

    def copy(self):
        """Return a deep copy of the current game state."""
        copied_board = [row[:] for row in self.board]

        return ConnectFour(
            board=copied_board,
            current_player=self.current_player
        )

    def legal_moves(self):
        """
        Return all columns into which a disc can legally be dropped.

        A column is legal when its top cell is empty.
        """
        legal_columns = []

        for column in range(COLUMNS):
            if self.board[0][column] == EMPTY:
                legal_columns.append(column)

        return legal_columns

    def apply_move(self, column):
        """
        Return a new game state after the current player drops a disc
        into the selected column.

        Gravity is applied by placing the disc in the lowest available
        cell of the column.

        The original state is not modified.
        """
        if not isinstance(column, int):
            raise TypeError("The column must be an integer.")

        if column < 0 or column >= COLUMNS:
            raise ValueError(
                f"Column must be between 0 and {COLUMNS - 1}."
            )

        if self.board[0][column] != EMPTY:
            raise ValueError(f"Column {column} is full.")

        new_state = self.copy()

        # Start at the bottom row and search upward.
        for row in range(ROWS - 1, -1, -1):
            if new_state.board[row][column] == EMPTY:
                new_state.board[row][column] = self.current_player
                break

        # Change to the other player.
        if self.current_player == ONE:
            new_state.current_player = TWO
        else:
            new_state.current_player = ONE

        return new_state

    def winner(self):
        """
        Return the winning player number.

        Returns:
            1 if Player 1 has won
            2 if Player 2 has won
            None if there is currently no winner
        """

        # Each tuple contains:
        # (change in row, change in column)
        directions = [
            (0, 1),    # Horizontal
            (1, 0),    # Vertical
            (1, 1),    # Down-right diagonal
            (1, -1)    # Down-left diagonal
        ]

        for row in range(ROWS):
            for column in range(COLUMNS):
                player = self.board[row][column]

                if player == EMPTY:
                    continue

                for row_change, column_change in directions:
                    end_row = (
                        row
                        + (CONNECT_ALL - 1) * row_change
                    )

                    end_column = (
                        column
                        + (CONNECT_ALL - 1) * column_change
                    )

                    # Skip this direction if the sequence would leave
                    # the board.
                    if not (
                        0 <= end_row < ROWS
                        and 0 <= end_column < COLUMNS
                    ):
                        continue

                    four_connected = True

                    for step in range(1, CONNECT_ALL):
                        check_row = row + step * row_change

                        check_column = (
                            column + step * column_change
                        )

                        if (
                            self.board[check_row][check_column]
                            != player
                        ):
                            four_connected = False
                            break

                    if four_connected:
                        return player

        return None

    def is_draw(self):
        """
        Return True when the board is full and neither player has won.
        """
        return (
            self.winner() is None
            and len(self.legal_moves()) == 0
        )

    def is_terminal(self):
        """
        Return True when the game has ended through either a win
        or a draw.
        """
        return (
            self.winner() is not None
            or len(self.legal_moves()) == 0
        )

    def result(self):
        """
        Return the result of a terminal state.

        Returns:
            1 = Player 1 wins
            2 = Player 2 wins
            0 = draw
            None = game is not finished
        """
        winning_player = self.winner()

        if winning_player is not None:
            return winning_player

        if self.is_draw():
            return 0

        return None

    def display(self):
        """Print the board as a text-based interface."""
        symbols = {
            EMPTY: ".",
            ONE: "X",
            TWO: "O"
        }

        print()
        print("  0 1 2 3 4 5 6")

        for row in self.board:
            displayed_row = " ".join(
                symbols[cell] for cell in row
            )

            print(f"| {displayed_row} |")

        print("+---------------+")
        print()

import math
import random

from connect_four import (
    COLUMNS,
    CONNECT_ALL,
    EMPTY,
    ONE,
    ROWS,
    TWO,
)


WIN_SCORE = 1_000_000


def otherPlayer(player):
    """Return the other player."""
    if player == ONE:
        return TWO

    if player == TWO:
        return ONE

    raise ValueError("Player must be ONE (1) or TWO (2).")


def boardWindows(board):
    """Yield every horizontal, vertical, and diagonal group of four."""

    # Horizontal
    for row in range(ROWS):
        for column in range(COLUMNS - CONNECT_ALL + 1):
            yield [
                board[row][column + offset]
                for offset in range(CONNECT_ALL)
            ]

    # Vertical
    for row in range(ROWS - CONNECT_ALL + 1):
        for column in range(COLUMNS):
            yield [
                board[row + offset][column]
                for offset in range(CONNECT_ALL)
            ]

    # Down-right diagonal
    for row in range(ROWS - CONNECT_ALL + 1):
        for column in range(COLUMNS - CONNECT_ALL + 1):
            yield [
                board[row + offset][column + offset]
                for offset in range(CONNECT_ALL)
            ]

    # Down-left diagonal
    for row in range(ROWS - CONNECT_ALL + 1):
        for column in range(CONNECT_ALL - 1, COLUMNS):
            yield [
                board[row + offset][column - offset]
                for offset in range(CONNECT_ALL)
            ]


class RandomAgent:
    """Choose a random legal move."""

    def __init__(self, seed=None):
        self.seed = seed
        self.random = random.Random(seed)

    def chooseMove(self, state):
        """Return a random legal column."""
        if state.is_terminal():
            raise ValueError("Cannot choose a move from a terminal state.")

        legalMoves = state.legal_moves()
        return self.random.choice(legalMoves)


class RuleBasedAgent:
    """Choose moves using win, block, centre, and threat rules."""

    def __init__(self, seed=None):
        self.seed = seed
        self.random = random.Random(seed)

    def chooseMove(self, state):
        """Return the best move under the rule order."""
        if state.is_terminal():
            raise ValueError("Cannot choose a move from a terminal state.")

        legalMoves = state.legal_moves()
        player = state.current_player
        opponent = otherPlayer(player)

        # Take a winning move.
        winningMoves = [
            move
            for move in legalMoves
            if state.apply_move(move).winner() == player
        ]

        if winningMoves:
            return self.random.choice(winningMoves)

        # Block an immediate loss.
        opponentState = state.copy()
        opponentState.current_player = opponent

        blockingMoves = [
            move
            for move in legalMoves
            if opponentState.apply_move(move).winner() == opponent
        ]

        if blockingMoves:
            return self.random.choice(blockingMoves)

        # Prefer columns near the centre.
        centrality = {
            move: (COLUMNS // 2) - abs(move - (COLUMNS // 2))
            for move in legalMoves
        }
        bestCentrality = max(centrality.values())
        centralMoves = [
            move
            for move in legalMoves
            if centrality[move] == bestCentrality
        ]

        # Break central ties using threat strength.
        moveScores = {}

        for move in centralMoves:
            child = state.apply_move(move)
            moveScores[move] = self._extensionScore(child, player)

        bestScore = max(moveScores.values())
        bestMoves = [
            move
            for move, score in moveScores.items()
            if score == bestScore
        ]

        return self.random.choice(bestMoves)

    @staticmethod
    def _extensionScore(state, player):
        """Score threats, connected lines, and two-disc windows."""
        threats = 0
        buildingWindows = 0

        for window in boardWindows(state.board):
            playerCount = window.count(player)
            emptyCount = window.count(EMPTY)

            if playerCount == 3 and emptyCount == 1:
                threats += 1
            elif playerCount == 2 and emptyCount == 2:
                buildingWindows += 1

        longestLine = RuleBasedAgent._longestLine(state.board, player)
        return threats, longestLine, buildingWindows

    @staticmethod
    def _longestLine(board, player):
        """Return the player's longest connected line."""
        directions = [
            (0, 1),
            (1, 0),
            (1, 1),
            (1, -1),
        ]
        longest = 0

        for row in range(ROWS):
            for column in range(COLUMNS):
                if board[row][column] != player:
                    continue

                for rowChange, columnChange in directions:
                    length = 1
                    nextRow = row + rowChange
                    nextColumn = column + columnChange

                    while (
                        0 <= nextRow < ROWS
                        and 0 <= nextColumn < COLUMNS
                        and board[nextRow][nextColumn] == player
                    ):
                        length += 1
                        nextRow += rowChange
                        nextColumn += columnChange

                    longest = max(longest, length)

        return longest


class MinimaxAgent:
    """Choose moves with depth-limited Minimax and alpha-beta pruning."""

    def __init__(self, depth=4, seed=None):
        if not isinstance(depth, int):
            raise TypeError("Search depth must be an integer.")

        if depth < 1:
            raise ValueError("Search depth must be at least 1.")

        self.depth = depth
        self.seed = seed
        self.random = random.Random(seed)

    def chooseMove(self, state):
        """Return the highest-scoring legal move."""
        if state.is_terminal():
            raise ValueError("Cannot choose a move from a terminal state.")

        legalMoves = state.legal_moves()
        rootPlayer = state.current_player
        moveScores = {}

        for move in legalMoves:
            child = state.apply_move(move)
            score = self._minimax(
                child,
                self.depth - 1,
                -math.inf,
                math.inf,
                rootPlayer,
            )
            moveScores[move] = score

        bestScore = max(moveScores.values())
        bestMoves = [
            move
            for move, score in moveScores.items()
            if score == bestScore
        ]

        return self.random.choice(bestMoves)

    def _minimax(self, state, depth, alpha, beta, rootPlayer):
        """Return the Minimax value of a state."""
        winner = state.winner()

        if winner == rootPlayer:
            return WIN_SCORE + depth

        if winner == otherPlayer(rootPlayer):
            return -WIN_SCORE - depth

        if not state.legal_moves():
            return 0

        if depth == 0:
            return self.heuristic(state, rootPlayer)

        legalMoves = state.legal_moves()

        # Maximize for the starting player.
        if state.current_player == rootPlayer:
            value = -math.inf

            for move in legalMoves:
                child = state.apply_move(move)
                value = max(
                    value,
                    self._minimax(
                        child,
                        depth - 1,
                        alpha,
                        beta,
                        rootPlayer,
                    ),
                )
                alpha = max(alpha, value)

                if alpha >= beta:
                    break

            return value

        # Minimize for the opponent.
        value = math.inf

        for move in legalMoves:
            child = state.apply_move(move)
            value = min(
                value,
                self._minimax(
                    child,
                    depth - 1,
                    alpha,
                    beta,
                    rootPlayer,
                ),
            )
            beta = min(beta, value)

            if alpha >= beta:
                break

        return value

    @staticmethod
    def heuristic(state, player):
        """Score open windows and centre-column control."""
        opponent = otherPlayer(player)
        score = 0
        centreColumn = COLUMNS // 2

        for row in range(ROWS):
            if state.board[row][centreColumn] == player:
                score += 3
            elif state.board[row][centreColumn] == opponent:
                score -= 3

        for window in boardWindows(state.board):
            score += MinimaxAgent._scoreWindow(window, player, opponent)

        return score

    @staticmethod
    def _scoreWindow(window, player, opponent):
        """Score one group of four cells."""
        playerCount = window.count(player)
        opponentCount = window.count(opponent)
        emptyCount = window.count(EMPTY)

        # Mixed windows cannot form a connect four.
        if playerCount > 0 and opponentCount > 0:
            return 0

        weights = {
            1: 1,
            2: 10,
            3: 100,
        }

        if opponentCount == 0 and emptyCount > 0:
            return weights.get(playerCount, 0)

        if playerCount == 0 and emptyCount > 0:
            return -weights.get(opponentCount, 0)

        return 0


# Keep the original names available for existing drivers and tests.
globals()["other_player"] = otherPlayer
globals()["board_windows"] = boardWindows

for agentClass in (RandomAgent, RuleBasedAgent, MinimaxAgent):
    setattr(agentClass, "choose_move", agentClass.chooseMove)

setattr(RuleBasedAgent, "_extension_score", RuleBasedAgent._extensionScore)
setattr(RuleBasedAgent, "_longest_line", RuleBasedAgent._longestLine)
setattr(MinimaxAgent, "_score_window", MinimaxAgent._scoreWindow)
import csv
import random
import time

from connect_four import ConnectFour, ONE, TWO
from agents import RandomAgent, RuleBasedAgent, MinimaxAgent


# =====================================================
# Configuration
# =====================================================

MASTER_SEED = 42
GAMES_PER_PAIRING = 30

SHOW_BOARD = True


# =====================================================
# Helper Functions
# =====================================================

def average(total, count):
    if count == 0:
        return 0
    return total / count



def save_game_result(data):

    try:
        with open("game_results.csv", "r"):
            exists = True

    except FileNotFoundError:
        exists = False


    with open(
        "game_results.csv",
        "a",
        newline=""
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=data.keys()
        )

        if not exists:
            writer.writeheader()

        writer.writerow(data)



# =====================================================
# Play One Game
# =====================================================

def play_game(agent1, agent2, display=False):

    state = ConnectFour.new_game()

    time_agent1 = 0
    time_agent2 = 0

    moves_agent1 = 0
    moves_agent2 = 0


    while not state.is_terminal():


        if display:
            state.display()


        if state.current_player == ONE:

            start = time.perf_counter()

            move = agent1.chooseMove(state)

            end = time.perf_counter()

            time_agent1 += end - start
            moves_agent1 += 1


        else:

            start = time.perf_counter()

            move = agent2.chooseMove(state)

            end = time.perf_counter()

            time_agent2 += end - start
            moves_agent2 += 1



        state = state.apply_move(move)



    if display:
        state.display()



    return (
        state.result(),
        time_agent1,
        time_agent2,
        moves_agent1,
        moves_agent2
    )



# =====================================================
# Run Experiments
# =====================================================

def run_experiment(
        agentA_class,
        agentB_class,
        nameA,
        nameB,
        games,
        seed
):

    print("\n" + "=" * 60)
    print(f"{nameA} vs {nameB}")
    print("=" * 60)


    winsA = 0
    winsB = 0
    draws = 0


    totalTimeA = 0
    totalTimeB = 0

    totalMovesA = 0
    totalMovesB = 0


    rng = random.Random(seed)


    for game in range(games):

        print(f"Game {game+1}/{games}")


        # alternate first player
        swap = game % 2 == 1


        seedA = rng.randint(
            0,
            1000000
        )

        seedB = rng.randint(
            0,
            1000000
        )


        agentA = agentA_class(seed=seedA)
        agentB = agentB_class(seed=seedB)



        # -----------------------------------------
        # Normal order
        # -----------------------------------------

        if not swap:


            winner, timeA, timeB, movesA, movesB = play_game(
                agentA,
                agentB,
                SHOW_BOARD
            )


            first_player = nameA



            if winner == ONE:
                winner_name = nameA

            elif winner == TWO:
                winner_name = nameB

            else:
                winner_name = "Draw"



        # -----------------------------------------
        # Swapped order
        # -----------------------------------------

        else:


            winner, timeB, timeA, movesB, movesA = play_game(
                agentB,
                agentA,
                SHOW_BOARD
            )


            first_player = nameB



            if winner == ONE:
                winner_name = nameB

            elif winner == TWO:
                winner_name = nameA

            else:
                winner_name = "Draw"



        # Update statistics

        if winner_name == nameA:
            winsA += 1

        elif winner_name == nameB:
            winsB += 1

        else:
            draws += 1



        totalTimeA += timeA
        totalTimeB += timeB

        totalMovesA += movesA
        totalMovesB += movesB



        # Save individual game

        save_game_result({

            "Pairing":
                f"{nameA} vs {nameB}",

            "Game Number":
                game + 1,

            "First Player":
                first_player,

            "Agent 1":
                nameA,

            "Agent 2":
                nameB,

            "Winner":
                winner_name,

            "Agent 1 Wins":
                "YES" if winner_name == nameA
                else "NO",

            "Agent 2 Wins":
                "YES" if winner_name == nameB
                else "NO",

            "Draw":
                "YES" if winner_name == "Draw"
                else "NO",


            "Agent 1 Decision Time":
                timeA,

            "Agent 2 Decision Time":
                timeB,


            "Agent 1 Moves":
                movesA,

            "Agent 2 Moves":
                movesB,


            "Agent A Seed":
                seedA,

            "Agent B Seed":
                seedB

        })



    # Summary

    avgA = average(
        totalTimeA,
        totalMovesA
    )

    avgB = average(
        totalTimeB,
        totalMovesB
    )


    print("\nResults")
    print("----------------------")

    print(nameA, "wins:", winsA)
    print(nameB, "wins:", winsB)
    print("Draws:", draws)

    print()

    print(nameA,
          "win rate:",
          f"{winsA/games:.2%}")

    print(nameB,
          "win rate:",
          f"{winsB/games:.2%}")

    print(
        "Draw rate:",
        f"{draws/games:.2%}"
    )


    print()

    print(
        nameA,
        "avg decision time:",
        avgA
    )

    print(
        nameB,
        "avg decision time:",
        avgB
    )



    return {


        "Pairing":
            f"{nameA} vs {nameB}",


        "Games":
            games,


        "Seed":
            seed,


        "Agent 1":
            nameA,


        "Agent 2":
            nameB,


        "Agent 1 Wins":
            winsA,


        "Agent 2 Wins":
            winsB,


        "Draws":
            draws,


        "Agent 1 Win Rate":
            winsA/games,


        "Agent 2 Win Rate":
            winsB/games,


        "Draw Rate":
            draws/games,


        "Agent 1 Avg Decision Time":
            avgA,


        "Agent 2 Avg Decision Time":
            avgB

    }



# =====================================================
# Main
# =====================================================

def main():


    print("Connect Four AI Experiments")
    print(
        "Master Seed:",
        MASTER_SEED
    )


    results = []



    results.append(
        run_experiment(
            RandomAgent,
            RuleBasedAgent,
            "Random",
            "Rule-Based",
            GAMES_PER_PAIRING,
            MASTER_SEED
        )
    )



    results.append(
        run_experiment(
            RuleBasedAgent,
            lambda seed=None:
                MinimaxAgent(
                    depth=4,
                    seed=seed
                ),

            "Rule-Based",
            "Minimax",

            GAMES_PER_PAIRING,

            MASTER_SEED + 1
        )
    )



    results.append(
        run_experiment(
            lambda seed=None:
                MinimaxAgent(
                    depth=4,
                    seed=seed
                ),

            RandomAgent,

            "Minimax",

            "Random",

            GAMES_PER_PAIRING,

            MASTER_SEED + 2
        )
    )



    # Save summary CSV

    with open(
        "experiment_summary.csv",
        "w",
        newline=""
    ) as file:


        writer = csv.DictWriter(
            file,
            fieldnames=results[0].keys()
        )


        writer.writeheader()

        writer.writerows(results)



    print("\nFinished!")
    print(
        "Created:"
    )

    print(
        "- game_results.csv"
    )

    print(
        "- experiment_summary.csv"
    )




if __name__ == "__main__":
    main()

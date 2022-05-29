from time import sleep
import queue
import chess
import chess.engine
import multiprocessing
import json

from sympy import per
from lichess import lichessApiConnection

#Haurem de passar la classe del robot com argument
def start_lichess_game():
    try:
        board = chess.Board()

        game_manager = multiprocessing.Manager()

        # Queues for each players moves
        lichess_move_queue = game_manager.Queue()
        chesser_move_queue = game_manager.Queue()

        #Start listening for games
        start_process = multiprocessing.Process(target=lichessApiConnection.start, args=[lichess_move_queue, chesser_move_queue]).start()


        TEMP_MOVES = ['e2e4', 'd1h5', 'f1c4', 'h5f7']
        i = 0

        while board.outcome() is None:
            #Consumir queues i ficar a la board els moviments, tambe fer moviments
            #
            #board.push_uci(move)
            sleep(1)
            #chesser_move_queue.put('eee')

        
            if board.turn == chess.WHITE:
                try:
                    '''
                    aqui cal agafar el moviment amb la IA
                    chesser_move_queue.put(move)
                    board.push_uci(chesser_move_queue.get(block=False))
                    '''
                    print("New white move:", TEMP_MOVES[i])
                    chesser_move_queue.put(TEMP_MOVES[i])
                    board.push_uci(TEMP_MOVES[i])
                    print("\nNew white move on board:\n", board)
                    
                    i += 1
                except queue.Empty:
                    pass

            if board.turn == chess.BLACK:
                try:
                    lichess_move = lichess_move_queue.get(block=False)
                    board.push_uci(lichess_move)
                    print("\nNew black move on board:\n", board)
                except queue.Empty:
                    pass
        print("Match finished, winner:", board.outcome().winner if "White" else "Black")
        sleep(1)
    except KeyboardInterrupt:
        print("Keyboard interrupt")
        return


def start_local_game(engine_path, player, players):

    board = chess.Board()
    engine = chess.engine.SimpleEngine.popen_uci(engine_path)

    TEMP_MOVES = ['f2f3', 'g2g4']
    i = 0

    difficulty, percentage = get_difficulty(player, players)

    print(f'Dificulty for player {player} is {difficulty} seconds. Winrate {percentage}')

    while board.outcome() is None:
        if board.turn == chess.WHITE:
            print("\nNew white move:", TEMP_MOVES[i])
            board.push_uci(TEMP_MOVES[i])
            print(board)
            i += 1
            
        if board.turn == chess.BLACK:
            engine_play = engine.play(board, chess.engine.Limit(time=difficulty))
            board.push_uci(engine_play.move.uci())
            print("\nNew black move:", engine_play.move.uci())
            print(board)
            pass
        
        sleep(1)

    print("Match finished, winner:", "White" if board.outcome().winner else "Black")
    save_game("win" if board.outcome().winner else "lose", player, players)
    engine.quit()

def get_difficulty(player, players):
    wins, loses = 0, 0
    if player in players:
        if "win" in players[player]:
            wins = players[player]["win"]
        if "lose" in players[player]:
            loses = players[player]["lose"]
    
    if wins + loses != 0:
        percentage = (wins / (wins + loses)) * 100
        if percentage <= 50 or (wins == 0 and loses != 0):
            return (0.1, percentage)
        elif percentage > 50 and percentage < 60:
            return (1, percentage)
        elif percentage >= 60:
            return (3, percentage)
    else:
        return (0.1, "N/A")
    


def save_game(result, player, players):
    if player in players:
        if result not in players[player]:
            players[player][result] = 1
        else:
            players[player][result] += 1
    else:
        players[player] = {}
        players[player][result] = 1
    
    with open("players/players.json", 'w') as f:
        json.dump(players, f)
        return

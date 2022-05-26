import chess
import multiprocessing
from lichess.lichessApiConnection import start

#Haurem de passar la classe del robot com argument
def start_lichess_game():

    board = chess.Board()

    game_manager = multiprocessing.Manager()

    # Queues for each players moves
    lichess_move_queue = game_manager.Queue()
    chesser_move_queue = game_manager.Queue()

    #Start listening for games
    multiprocessing.Process(target=start, args=[lichess_move_queue, chesser_move_queue]).start()

    while True:
        #Consumir queues i ficar a la board els moviments, tambe fer moviments
        pass
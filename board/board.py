from time import sleep
import queue
import chess
import multiprocessing
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
                    print(i)
                    print("New white move:", TEMP_MOVES[i])
                    chesser_move_queue.put(TEMP_MOVES[i])
                    board.push_uci(TEMP_MOVES[i])
                    print("New white move on board:", board)
                    
                    i += 1
                except queue.Empty:
                    pass

            if board.turn == chess.BLACK:
                try:
                    lichess_move = lichess_move_queue.get(block=False)
                    print("New black move on board:", board)
                    board.push_uci(lichess_move)
                except queue.Empty:
                    pass
        print("Match finished, winner:", board.outcome().winner)
        sleep(5)
    except KeyboardInterrupt:
        print("Keyboard interrupt")
        return


def start_local_game():
    try:
        board = chess.Board()

        while board.outcome() is None:
            #Consumir queues i ficar a la board els moviments, tambe fer moviments
            #
            #board.push_uci(move)
            sleep(4)
            #chesser_move_queue.put('eee')
            print("here")

            #board.outcome()
            
            pass
    except KeyboardInterrupt:
        print("Keyboard interrupt")
        return

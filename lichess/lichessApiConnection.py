import json
from lib2to3.pytree import Base
from collections import defaultdict
import multiprocessing
from multiprocessing.managers import BaseManager
from multiprocessing.managers import SyncManager
import queue
import time
import requests
from dotenv import dotenv_values
from pprint import pprint

class LichessApi:
    def __init__(self):
        self.API_KEY = dotenv_values(".env")["API_KEY"]
        self.base_url = "https://lichess.org"
        self.headers = {
            "Authorization": f"Bearer {self.API_KEY}",
            "Content-Type": "application/x-ndjson"
        }
        self.event_queue = []
        self.stop = False

        self.n_move = 0

    def get_events(self):
        return requests.get(self.base_url + "/api/stream/event", headers=self.headers, stream=True)

    def stream_events(self, control_queue):
        #The API returns a stream, so we need a dedicated process
        #to receive new events
        while not self.get_stop():
            try:
                response = self.get_events()
                ndjson = response.iter_lines()

                for line in ndjson:
                    if line:
                        control_queue.put_nowait(json.loads(line.decode("utf-8")))
            except:
                pass
            time.sleep(1)
        print('Stopping stream: events')

    def abort_match(self, challenge_id):
        requests.post(self.base_url + f'/api/board/game/{challenge_id}/abort', headers={"Authorization": f"Bearer {self.API_KEY}"})

    def accept_challenge(self, challenge_id):
        requests.post(self.base_url + f'/api/challenge/{challenge_id}/accept', headers={"Authorization": f"Bearer {self.API_KEY}"})

    def get_match(self, challenge_id):
        return requests.get(self.base_url + f'/api/bot/game/stream/{challenge_id}', headers=self.headers, stream=True)

    def stream_match(self, challenge_id, match_queue):
        #The API returns a stream, so we need a dedicated process
        #to receive new match events
        while not self.get_stop():
            try:
                response = self.get_match(challenge_id)
                ndjson = response.iter_lines()

                for line in ndjson:
                    if line:
                        match_queue.put_nowait(json.loads(line.decode("utf-8")))
            except:
                pass
            time.sleep(1)
        print('Stopping stream: match')
    
    def get_stop(self):
        return self.stop

    def set_stop(self):
        self.stop = True

    def get_n_move(self):
        return self.n_move

    def next_turn(self):
        self.n_move += 1


class lichessApiManager(BaseManager): #Custom Manager https://docs.python.org/3/library/multiprocessing.html#customized-managers
    pass


def start(lichess_move_queue, chesser_move_queue):
    lichessApiManager.register('lichess_api', LichessApi)
    lichessApiManager.register('Queue', multiprocessing.Queue)

    with lichessApiManager() as lichess_api_manager:

        print("Started listening for events")

        lichess_api = lichess_api_manager.lichess_api()


        control_queue = lichess_api_manager.Queue()
        match_queue = lichess_api_manager.Queue()

        #Start process to receive events
        control_stream = multiprocessing.Process(target=lichess_api.stream_events, args=[control_queue]).start()


        challenge_id = ''
        in_match = False

        while not lichess_api.get_stop():
            try:
                event = control_queue.get(block=False)
                pprint(event)
            except queue.Empty:
                pass

            try:
                match event['type']:
                    case "challenge":  # challenge requested
                        if not in_match:
                            print("Received challenge request\n")
                            challenge_id = event["challenge"]["id"]
                            lichess_api.accept_challenge(challenge_id)
                    case "challengeCanceled":
                        pass
                    case "challengeDeclined":
                        pass
                    case "gameStart":
                        if not in_match:
                            print("Game Started\n")
                            multiprocessing.Process(target=lichess_api.stream_match, args=[challenge_id, match_queue]).start()
                            in_match = True
                            event.clear()
                        pass
                    case "gameFinish":
                        #Game finished
                        pass
            except:
                pass
            
            try:
                match = match_queue.get(block=False)
                pprint(match)
            except queue.Empty:
                pass
            
            try:
                match match['type']:
                    case "gameFull":
                        #Game started
                        pass
                    case "gameState":
                        print("Received game state\n")
                        #For each move
                        #Aqui hem de respondre amb el moviment del jugador fisic
                        pprint(match)

                        #Lichess player always second
                        if lichess_api.get_n_move() % 2 == 1:
                            lichess_move_queue.put(match['moves'])
                            print("Lichess user turn")
                        
                        lichess_api.next_turn()


                        #aixo para tot el bot, tambe processos fills
                        #lichess_api.set_stop()

                        #Una vegada consumim el moviment resetejar 
                        match.clear()
                        pass
                    case "chatLine":
                        pass
            except:
                pass

            if lichess_api.get_n_move() % 2 == 0:
                #Consumir moviment del usuari fisic i enviar a lichess
                pass

            time.sleep(1)


if __name__ == '__main__':

    lichess_move_queue = multiprocessing.Queue() #Queue on rebrem els nous moviments
    try:
        #A main 2 queues o 1 queue amb tuplas, una llista de moviments per cada jugador
        start(lichess_move_queue)
    except KeyboardInterrupt:
        print("Keyboard interrupt")
    finally:
        print(lichess_move_queue.get())


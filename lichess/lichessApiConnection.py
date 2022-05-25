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

    def get_events(self):
        return requests.get(self.base_url + "/api/stream/event", headers=self.headers, stream=True)

    def stream_events(self, control_queue):
        #La api retorna un stream, pel que necessitem un thread
        #dedicat a rebre nous events
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
        # La api retorna un stream, pel que necessitem un thread
        # dedicat a rebre nous events del match
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


class lichessApiManager(BaseManager): #Custom Manager https://docs.python.org/3/library/multiprocessing.html#customized-managers
    pass

def start():
    #Registrem la classe lichess_api i Queue al manager
    lichessApiManager.register('lichess_api', LichessApi)
    lichessApiManager.register('Queue', multiprocessing.Queue)

    with lichessApiManager() as lichess_api_manager:

        lichess_api = lichess_api_manager.lichess_api()
        print("Started listening for events")

        # Igual totes les queues van tambe al objecte
        control_queue = lichess_api_manager.Queue()
        match_queue = lichess_api_manager.Queue()
        control_stream = multiprocessing.Process(target=lichess_api.stream_events, args=[control_queue])
        control_stream.start()

        challenge_id = ''
        in_match = False # Ficar en classe

        while not lichess_api.get_stop():
            try:
                event = control_queue.get(block=False)
                print(event)
            except queue.Empty:
                pass

            print(lichess_api.get_stop())
            try:
                match event['type']:
                    case "challenge":  # challenge requested
                        if not in_match:
                            challenge_id = event["challenge"]["id"]
                            lichess_api.accept_challenge(challenge_id)
                    case "challengeCanceled":
                        pass
                    case "challengeDeclined":
                        pass
                    case "gameStart":
                        if not in_match:
                            multiprocessing.Process(target=lichess_api.stream_match, args=[challenge_id, match_queue]).start()
                            print("entramo")
                            in_match = True
                        pass
                    case "gameFinish":
                        pass
            except:
                pass
            
            try:
                match = match_queue.get(block=False)
                print(match)
            except queue.Empty:
                pass
            
            try:
                match match['type']:
                    case "gameFull":
                        #Inici partida
                        pass
                    case "gameState":
                        #Per cada moviment
                        #Aqui hem de respondre amb el moviment del jugador fisic
                        print(match)

                        #aixo para tot el bot, tambe processos fills
                        lichess_api.set_stop()

                        pass
                    case "chatLine":
                        pass
            except:
                pass
            time.sleep(1)


if __name__ == '__main__':
    start()

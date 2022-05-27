import json
import multiprocessing
from multiprocessing.managers import BaseManager
import queue
import time
import requests
from dotenv import dotenv_values

class LichessApi:
    def __init__(self):
        self.API_KEY = dotenv_values("lichess/.env")["API_KEY"]
        self.base_url = "https://lichess.org"
        self.headers = {
            "Authorization": f"Bearer {self.API_KEY}",
            "Content-Type": "application/x-ndjson"
        }

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
        return

    def abort_match(self, challenge_id):
        requests.post(self.base_url + f'/api/board/game/{challenge_id}/abort', headers={"Authorization": f"Bearer {self.API_KEY}"})

    def accept_challenge(self, challenge_id):
        requests.post(self.base_url + f'/api/challenge/{challenge_id}/accept', headers={"Authorization": f"Bearer {self.API_KEY}"})

    def make_move(self, challenge_id, move):
        return requests.post(self.base_url + f'/api/bot/game/{challenge_id}/move/{move}', headers={"Authorization": f"Bearer {self.API_KEY}"})

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
        return
    
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
        try:
        
            print("Started listening for events")

            #Init LichessApi proxy instance
            lichess_api = lichess_api_manager.lichess_api()

            control_queue = lichess_api_manager.Queue()
            match_queue = lichess_api_manager.Queue()

            #Start process to receive events
            control_stream = multiprocessing.Process(target=lichess_api.stream_events, args=[control_queue])
            control_stream.start()

            match_stream = None
            challenge_id = ''
            in_match = False
            game_state = {}
            match = {}

            while not lichess_api.get_stop():
                try:
                    event = control_queue.get(block=False)
                except queue.Empty:
                    pass

                try:
                    match event['type']:
                        case "challenge":  
                            # challenge requested
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
                                match_stream = multiprocessing.Process(target=lichess_api.stream_match, args=[challenge_id, match_queue]).start()
                                in_match = True
                                event.clear()
                            pass
                        case "gameFinish":
                            # Game finished
                            print("Game finished")
                            lichess_api.set_stop()
                            control_stream.join()
                            match_stream.join()
                            return
                except:
                    pass
                
                try:
                    game_state = match
                    match = match_queue.get(block=False)
                except queue.Empty:
                    pass
                
                try:
                    match match['type']:
                        case "gameFull":
                            # Game started
                            pass
                        case "gameState":
                            # Lichess player always second
                            print("Game state:", game_state, "Match:", match)
                            if len(match['moves']) % 2 == 1 and game_state != match:
                                print("Received game state\n")
                                lichess_move_queue.put(match['moves'].split()[-1])
                                print("Lichess user move: ", match['moves'].split()[-1])
                                lichess_api.next_turn()
                            
                            match.clear()
                            pass
                        case "chatLine":
                            pass
                except:
                    pass
                
                if 'moves' in match or lichess_api.get_n_move() == 0 or not chesser_move_queue.empty():
                    if lichess_api.get_n_move() % 2 == 0 and in_match:
                        # Consume chesser movement and send to lichess
                        try:
                            chesser_move = chesser_move_queue.get(block=False)
                            print("Chesserbot user move: ", chesser_move)
                            lichess_api.make_move(challenge_id, chesser_move)
                            lichess_api.next_turn()
                            chesser_move.clear()
                        except:
                            pass 

                time.sleep(2)

        except KeyboardInterrupt:
            if in_match:
                lichess_api.abort_match(challenge_id)
            return
    


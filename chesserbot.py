import argparse
import board.board as board
import argparse
import json

def start(args, players):

    match args.mode[0]:
        case "local":
            board.start_local_game(args.engine_path, args.player, players)
        case "lichess":
            board.start_lichess_game()

def load_players():
    try:
        with open('players/players.json', 'r') as f:
            return json.load(f)
    except:
        with open('players/players.json', 'w') as f:
            json.dump({}, f)
            return {}


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", nargs=1, help="Select mode: local or lichess")
    parser.add_argument("--engine", dest='engine_path', type=str, help="Full path to the engine")
    parser.add_argument("-player", dest='player', type=str, help="Which player is playing the local game")
    return parser.parse_args()

if __name__ == '__main__':
    
    args = parse_args()
    players = load_players()

    if args.mode[0] == "local" and args.engine_path is None:
        print("You need to supply an engine with --engine to play locally")
        quit()

    start(args, players)
# Chesserbot
# What is this?
Chesserbot is a SCARA robot that plays chess. It works by digitalizing a chess board with the camera and making a move according to the board state. It can move the pieces automatically with a chess engine, or it can play moves it receives via the Internet from remote opponents on the platform [Lichess](https://lichess.org/).
# Requirements
### Software
- [Python 3.10.x](https://www.python.org/)
- [RPi.GPIO](https://pypi.org/project/RPi.GPIO/)
- [Python-chess](https://python-chess.readthedocs.io/)
- [Python-dotenv](https://pypi.org/project/python-dotenv/)
### Hardware
- Raspberry Pi
- 3 28BYJ-48 stepper motor
- 3 ULN2003 Stepper driver
- Electromagnet
- Camera
- Limit switches
# How to Use
1. Clone this repo.
2. If you want to integrate chesserbot with Lichess, you will need a bot account and [API key](https://lichess.org/api#operation/apiBotOnline). You will need to create a .env on the lichess folder, and save your API key as such, **API_KEY**=YOUR_KEY.
3. Install the required libraries.
> pip install -r requirements.txt
4. Execute chessboard.py
# Authors
Pol Monedero - Forgenn
Saúl Adserias - saul44203
Pol Carulla - PolCarulla

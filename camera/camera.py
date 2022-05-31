import cv2
import numpy as np
import matplotlib.pyplot as plt

class Camera:
    def __init__(self, res=1024, brd_points=None):
        self.cam = cv2.VideoCapture(0)
        self.res = res
        if brd_points:
            self.brd_points = brd_points
        else
            self.calibrate()

    def calibrate(self):
        try:
            self.brd_points = np.load("brd_points.npy")
        except OSError:
            frame = slef.get_frame()
            plt.imshow(frame)
            self.brd_points = np.array(plt.ginput(n=4, timeout=0))
            np.save("brd_points.npy", self.brd_points)

    def segment_board(self):
        dst_points = np.array([
            [0,0],
            [self.res,0],
            [self.res,self.res],
            [0,self.res]
        ])
        
        frame = self.get_frame()
        H, _ = cv2.findHomography(self.brd_points, dst_points)
        board = cv2.wrapPerspective(frame, H, (self.res, self.res))
       
        sz = self.res//8
        squares = self.zeros((8, 8, sz, sz, 3))

        for i in range(8):
            for j in range(8):
                squares[i,j] = board[i*sz:(i+1)*sz, j*sz:(j+1)*sz]
        
        return squares

    def detect_move(self, threshold=0.2):
        from time import sleep
        sq_bf= self.segment()
        means_bf = np.mean(squares_bf, axis=(2,3,4))

        n = 0
        sq_detected = ([], [])

        while n < 2:
            sleep(2)

            sq_af = self.segment()
            means_af = np.mean(sq_af, axis=(2,3,4))
            
            diff = np.abs(means_bf-means_af)
            moves = diff > (means_bf*threshold)

            sq_detected = np.where(moves)
            n = np.sum(moves)
        
        return sq_detected

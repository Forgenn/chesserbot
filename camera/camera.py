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

    def segment(self):
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
        squares = self.zeros((8, 8, sz, sz))

        for i in range(8):
            for j in range(8):
                squares[i,j] = board[i*sz:(i+1)*sz, j*sz:(j+1)*sz]
        
        return squares

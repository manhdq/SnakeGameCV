import cvzone
import cv2
import math
import time
import numpy as np
import random
import argparse
from cvzone.HandTrackingModule import HandDetector


class SnakeGameClass:
    def __init__(self, opt):
        self.opt = opt
        self.imgFood = cv2.imread(opt.pathSFood, cv2.IMREAD_UNCHANGED)
        self.imgFood = cv2.resize(self.imgFood, tuple(opt.SFoodSize))
        self.reset()

        self.gameOver = False
        self.menuScreen = True
        self.inGame = False
        self.level = 0
        self.levelDict = {0: 'Easy', 1: 'Medium', 2: 'Hard'}
        self.inClick = False

    def reset(self):
        self.points = []  # all points of the snake
        self.lengths = []  # distance between each point
        self.currentLength = 0  # total length of the snake
        self.allowedLength = 150  # total allowed length
        self.previousHead = 0, 0  # previous head point
        self.distanceThresh = 300  # maximum distance between each point
        self.score = 0  # Initial score
        self.startTime = time.time()

        self.randomSFoodLocation()

        self.lengthPerSFood = 50
        self.scorePerSFood = 100

    def getScreen(self):
        if self.opt.pathScreen is not None:
            imgInitial = cv2.imread(self.opt.pathScreen)[..., ::-1]
            imgInitial = cv2.resize(imgInitial, (self.opt.imgWidth, self.opt.imgHeight))
        else:
            imgInitial = np.zeros((self.opt.imgHeight, self.opt.imgWidth, 3))

        ## Game Name
        font = cv2.FONT_HERSHEY_COMPLEX
        text = self.opt.name
        textsize = cv2.getTextSize(text, font, 3, 9)[0]
        imgInitial = cv2.putText(imgInitial, text, (int((imgInitial.shape[1] - textsize[0]) / 2), 200), font, 3, (0, 0, 0), 9)
        textsize = cv2.getTextSize(text, font, 3, 5)[0]
        imgInitial = cv2.putText(imgInitial, text, (int((imgInitial.shape[1] - textsize[0]) / 2), 200), font, 3, (0, 200, 0), 5)

        img = imgInitial.copy()

        ## Game Option  (0-640)
        # Start game
        img = cv2.rectangle(img, (100, 300), (540, 400), (0, 200, 0), -1)
        font = cv2.FONT_HERSHEY_COMPLEX
        text = "Start Game"
        textsize = cv2.getTextSize(text, font, 1, 3)[0]
        img = cv2.putText(img, text, (int((img.shape[1] - 640 - textsize[0]) / 2), 360), font, 1, (0, 0, 0), 3)
        # Level
        img = cv2.rectangle(img, (100, 420), (540, 520), (0, 200, 0), -1)
        font = cv2.FONT_HERSHEY_COMPLEX
        text = f"Select Level: {self.levelDict[self.level]}"
        textsize = cv2.getTextSize(text, font, 1, 3)[0]
        img = cv2.putText(img, text, (int((img.shape[1] - 640 - textsize[0]) / 2), 480), font, 1, (0, 0, 0), 3)


        # Combine
        img = cv2.addWeighted(img, 0.7, imgInitial, 0.3, 1.0)

        return img

    def updateScreen(self, img, points):
        c1x, c1y = points[0]
        c2x, c2y = points[1]
        distance = math.hypot(c1x-c2x, c1y-c2y)
        print(distance)

        if distance < 45 and self.inClick == False:  # in-click
            self.inClick = True
        if distance > 60 and self.inClick == True:
            self.inClick = False
            cx, cy = (c1x + c2x) // 2, (c1y + c2y) // 2

            ## Click start game
            if 100 < cx < 540 and 300 < cy < 400:
                self.menuScreen = False
                self.inGame = True

            elif 100 < cx < 540 and 420 < cy < 520:
                self.level = (self.level + 1) % len(self.levelDict)

    def randomSFoodLocation(self):
        self.foodSPoint = random.randint(150,1130), random.randint(150,570)

    def randomLFoodLocation(self):
        self.foodLPoint = random.randint(150,1130), random.randint(150,570)

    def updateInGameScreen(self, imgMain):
        # Draw Food
        rx, ry = self.foodSPoint
        
        imgMain = cvzone.overlayPNG(imgMain, self.imgFood, (rx-self.opt.SFoodSize[0]//2, ry-self.opt.SFoodSize[1]//2))

        imgMain = cv2.rectangle(imgMain, (0,0), (800, 120), (0, 180, 0), -1)
        imgMain = cv2.putText(imgMain, self.opt.name, (20, 60), cv2.FONT_HERSHEY_COMPLEX,
                            2, (255, 255, 255), 3, cv2.LINE_AA)
        imgMain = cv2.putText(imgMain, f"Score: {self.score}", (20, 110), cv2.FONT_HERSHEY_SIMPLEX,
                            1, (255, 255, 255), 2, cv2.LINE_AA)
        imgMain = cv2.putText(imgMain, f"Time: {time.time() - self.startTime:.2f}s", (500, 110), cv2.FONT_HERSHEY_SIMPLEX,
                            1, (255, 255, 255), 2, cv2.LINE_AA)

        imgMain = cv2.rectangle(imgMain, (5, 685), (600, 715), (0, 220, 0), 1)

        return imgMain

    def update(self, imgMain, currentHead):
        px, py = self.previousHead
        cx, cy = currentHead
        
        self.points.append([cx, cy])
        distance = math.hypot(cx-px, cy-py)
        if distance > self.distanceThresh:
            pass  ##TODO

        self.lengths.append(distance)
        self.currentLength += distance
        self.previousHead = cx, cy

        # Length Reduction
        if self.currentLength > self.allowedLength:
            for i, length in enumerate(self.lengths):
                self.currentLength -= length
                self.lengths.pop(i)
                self.points.pop(i)

                if self.currentLength <= self.allowedLength:
                    break

        # Check if snake ate the food
        rx, ry = self.foodSPoint
        if rx - self.opt.SFoodSize[0]//2 < cx < rx + self.opt.SFoodSize[0]//2 and \
                ry - self.opt.SFoodSize[1]//2 < cy < ry + self.opt.SFoodSize[1]//2:
            self.randomSFoodLocation()
            self.allowedLength += self.lengthPerSFood
            self.score += self.scorePerSFood


        # Draw snake
        if self.points:
            for i, point in enumerate(self.points):
                if i != 0:
                    cv2.line(imgMain, self.points[i-1], self.points[i], (0,0,255), 20)
            cv2.circle(imgMain, self.points[-1], 20, (200,0,200), cv2.FILLED)

        # Check for Collision
        pts = np.array(self.points[:-2], np.int32)
        pts = pts.reshape((-1, 1, 2))
        cv2.polylines(imgMain, [pts], False, (0, 255, 0), 3)
        minDist = cv2.pointPolygonTest(pts, (cx, cy), True)

        if -1 <= minDist <= 1:
            self.gameOver = True
            self.reset()

        return imgMain


def main(opt):
    game = SnakeGameClass(opt)

    cap = cv2.VideoCapture(0)
    cap.set(3,opt.imgWidth)
    cap.set(4,opt.imgHeight)
    cv2.namedWindow(opt.name, cv2.WND_PROP_FULLSCREEN)
    cv2.setWindowProperty(opt.name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    detector = HandDetector(detectionCon=0.6, maxHands=1)

    while True:
        success, img = cap.read()

        img = cv2.flip(img, 1)
        hands, img = detector.findHands(img, flipType=False)

        if game.menuScreen:
            img = game.getScreen()
            if hands:
                lmList = hands[0]['lmList']
                points = []
                points.append(lmList[8][0:2])
                points.append(lmList[12][0:2])
                cv2.circle(img, points[0], 20, (200,0,200), cv2.FILLED)
                cv2.circle(img, points[1], 20, (200,0,200))
                game.updateScreen(img, points)
        elif game.inGame:
            if hands:
                lmList = hands[0]['lmList']
                pointIndex = lmList[8][0:2]
                cv2.circle(img, pointIndex, 20, (200,0,200), cv2.FILLED)
                img = game.update(img, pointIndex)
            img = game.updateInGameScreen(img)
        elif game.gameOver:
            pass
        cv2.imshow(opt.name, img)
        
        k = cv2.waitKey(1) & 0xFF
        if k == ord('q'):
            break


if __name__ == '__main__':
    parser = argparse.ArgumentParser("Args parser for game options")
    parser.add_argument("--name", default="Super Snake XYZ3000", help="game name")
    parser.add_argument("--pathSFood", default="GreenApple.png", help="path for small food")
    parser.add_argument("--SFoodSize", default=[50,50], type=int, nargs="+", help="size of small food")
    parser.add_argument("--pathLFood", default="RedApple.png", help="path for large food")
    parser.add_argument("--LFoodSize", default=[150,150], type=int, nargs="+", help="size of small food")

    parser.add_argument("--imgHeight", default=720, type=int, help="image height")
    parser.add_argument("--imgWidth", default=1280, type=int, help="image width")

    ## Menu Screen options
    parser.add_argument("--pathScreen", default="screen.jpg", help="path for screen")

    opt = parser.parse_args()
    main(opt)
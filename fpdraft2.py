
from turtle import heading, width
from imutils.perspective import four_point_transform
from imutils import contours
import numpy as np
import PySimpleGUI as sg
import argparse
import imutils
import cv2


def showResults(correctAnswer, answer, secW, secH, imgResult):
    for x in range(0, questions):
        correctAnswer = correctAnswers[x]
        answer = answers[x]
        aX = (answer * secW) + secW//2
        aY = (x*secH) + int(secH/1.5)

        cX = (correctAnswer * secW) + secW//2
        cY = (x * secH) + int(secH/1.5)
        print(aX, aY)
        if answer == correctAnswer:
            cv2.circle(imgResult, (aX, aY), 15, (0, 255, 0), 4)
        else:
            cv2.circle(imgResult, (aX, aY), 15, (0, 0, 255), 4)
            cv2.circle(imgResult, (cX, cY), 15, (255, 0, 0), 4)
    return imgResult


def findCorners(i):
    perimeter = cv2.arcLength(i, closed=True)
    sides = cv2.approxPolyDP(i, 0.02*perimeter, True)
    return(sides)


# load the image, convert it to grayscale, blur it
# slightly, then find edges

width = 720
height = 903
questions = 15
choices = 4
correctAnswers = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]

image = cv2.imread("testcase/testcase2.jpg")
image = cv2.resize(image, (width, height))
imgContour = image.copy()
imgFinal = image.copy()
imgGray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
imgBlur = cv2.GaussianBlur(imgGray, (5, 5), 1)
edged = cv2.Canny(imgBlur, 10, 50)


contours, hierarchy = cv2.findContours(
    edged, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

# draw contours  (-1 : all contours ) color, thickness
cv2.drawContours(imgContour, contours, -1, (0, 255, 0), 5)


rectContours = []

for i in contours:
    area = cv2.contourArea(i)
    if area > 50:
        # Look for possible rectangles
        perimeter = cv2.arcLength(i, closed=True)
        sides = cv2.approxPolyDP(i, 0.02*perimeter, True)
        if len(sides) == 4:
            rectContours.append(i)

# Sort rectangle Contours descending
rectContours = sorted(rectContours, key=cv2.contourArea, reverse=True)

# Finding and reshaping corner points
bigContour = findCorners(rectContours[0])
bigContour = bigContour.reshape((4, 2))
newbigContour = np.zeros((4, 1, 2), np.int32)
# Adding of x axis bigContour [1: x axis]
add = bigContour.sum(1)
# Re-ordering bigContour
newbigContour[0] = bigContour[np.argmin(add)]  # [0,0]
newbigContour[3] = bigContour[np.argmax(add)]  # [w, h]
diff = np.diff(bigContour, axis=1)
newbigContour[1] = bigContour[np.argmin(diff)]  # [w,0]
newbigContour[2] = bigContour[np.argmax(diff)]  # [0,h]
# Viewing the rectangle with the choices only


# Size for the choices
width2 = 180
height2 = 810
pt1 = np.float32(newbigContour)
pt2 = np.float32([[0, 0], [width2, 0], [0, height2], [width2, height2]])
mat = cv2.getPerspectiveTransform(pt1, pt2)
imgWarped = cv2.warpPerspective(image, mat, (width2, height2))

imgWarpedGray = cv2.cvtColor(imgWarped, cv2.COLOR_BGR2GRAY)
# THRESHOLDIMG
thresh = cv2.threshold(imgWarpedGray, 220, 250, cv2.THRESH_BINARY_INV)[1]


# SplitBoxes

rows = np.vsplit(thresh, 15)

boxes = []
for r in rows:
    cols = np.hsplit(r, 4)
    for box in cols:
        boxes.append(box)


# Marking answer: getting pixel of each choice/box
pixelVal = np.zeros((questions, choices))
countCol = 0
countRow = 0
for img in boxes:
    totalPixels = cv2.countNonZero(img)
    pixelVal[countRow][countCol] = totalPixels
    countCol += 1
    # if the value choiices is = 4 go down
    if (countCol == choices):
        countRow += 1
        countCol = 0


answers = []
for x in range(0, questions):
    tmp_array = pixelVal[x]
    # getting and storing the max pixels in the array
    answer = np.where(tmp_array == np.amax(tmp_array))
    answers.append(answer[0][0])

finalAnswers = np.array(answers)
correctAnswers = np.array(correctAnswers)
checks = np.equal(finalAnswers, correctAnswers)

correctScore = 0
for check in checks:
    if check == True:
        correctScore += 1


# SHOW ANSWERS:

imgResult = imgWarped.copy()
secW = int(imgResult.shape[1]/choices)
secH = int(imgResult.shape[0]/questions)

print(secW, secH)
for x in range(0, questions):
    correctAnswer = correctAnswers[x]
    answer = answers[x]
    aX = (answer * secW) + secW//2
    aY = (x*secH) + int(secH/1.5)

    cX = (correctAnswer * secW) + secW//2
    cY = (x * secH) + int(secH/1.5)
    print(aX, aY)
    if answer == correctAnswer:
        cv2.circle(imgResult, (aX, aY), 15, (0, 255, 0), 5)
    else:
        cv2.circle(imgResult, (aX, aY), 15, (0, 0, 255), 5)
        cv2.circle(imgResult, (cX, cY), 15, (255, 0, 0), 5)

test = np.zeros_like(imgWarped)
test = showResults(correctAnswer, answer, secW, secH, test)
invMat = cv2.getPerspectiveTransform(pt2, pt1)
sefinal = cv2.warpPerspective(test, invMat, (width, height))

imgFinal = cv2.addWeighted(imgFinal, 1, sefinal, 1, 0)

cv2.imshow("",  imgFinal)
cv2.waitKey(0)

import numpy as np
import cv2
# Show results , correct asnswers, your answers


# Show results of the answer sheet: multiple choice
def showResults(correctAnswer, answer, secW, secH, imgResult):
    # aX aY : x and y coord of the user answers
    # cX cY : x and y coord of the correct answers
    for x in range(0, questions):
        #  index 1 -> to the choices ; index 0 -> numbers
        checkX = 25
        correctAnswer = correctAnswers[x] + 1
        answer = answers[x] + 1
        aX = (answer * secW) + secW//2
        aY = (x*secH) + int(secH/1.5)
        cX = (correctAnswer * secW) + secW//2
        cY = (x * secH) + int(secH/1.5)
        if answer == correctAnswer:
            cv2.circle(imgResult, (aX, aY), 15, (0, 255, 0), 4)
            # Draw check mark on the number with correct answer
            cv2.line(imgResult, (checkX+5, aY+10),
                     (checkX+15, aY-10), (0, 255, 0), 3)
        else:
            # For wrong shaded answers (with one shade only)
            if answer != 0:
                cv2.circle(imgResult, (aX, aY), 15, (0, 0, 255), 4)
            # Draw x mark on the number with wrong answer
            cv2.line(imgResult, (checkX+5, aY+10),
                     (checkX+15, aY-10), (0, 0, 255), 3)
            cv2.line(imgResult, (checkX, aY-10),
                     (checkX+20, aY+5), (0, 0, 255), 3)
            # Shows correct answer
            cv2.circle(imgResult, (cX, cY), 15, (255, 0, 0), 4)
    return imgResult

# Find the corners of the contour rectangle/square


def findCorners(i):
    perimeter = cv2.arcLength(i, closed=True)
    sides = cv2.approxPolyDP(i, 0.02*perimeter, True)
    return(sides)

# Furnishing the points and appearance of the poly


def reOrderContour(rectContour):
    rectContour = rectContour.reshape((4, 2))
    add = rectContour.sum(1)
    newbigContour = np.zeros((4, 1, 2), np.int32)
    # Re-ordering points
    newbigContour[0] = rectContour[np.argmin(add)]  # [0,0]
    newbigContour[3] = rectContour[np.argmax(add)]  # [w, h]
    diff = np.diff(rectContour, axis=1)
    newbigContour[1] = rectContour[np.argmin(diff)]  # [w,0]\
    newbigContour[2] = rectContour[np.argmax(diff)]  # [0,h]
    return newbigContour


# File attributes
width = 400
height = 911
questions = 15
choices = 4

# List of correct answers
choice = {'a': 0, 'b': 1, 'c': 2, 'd': 3}
f = open("answer_keys/answer_keys.txt", "r")
correctAnswers = [choice.get(x.strip()) for x in f.readlines()]

# Reading of file
image = cv2.imread("testcase/t6.png")
image = cv2.resize(image, (width, height))
imgContour = image.copy()
imgFinal = image.copy()
imgGray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
imgBlur = cv2.GaussianBlur(imgGray, (5, 5), 1)
edged = cv2.Canny(imgBlur, 10, 50)
contours, hierarchy = cv2.findContours(
    edged, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

# Looking for rectangular contours
rectContours = []
for i in contours:
    area = cv2.contourArea(i)
    # Threshold
    if area > 50:
        # Look for possible rectangles
        perimeter = cv2.arcLength(i, closed=True)
        sides = cv2.approxPolyDP(i, 0.02*perimeter, True)
        if len(sides) == 4:
            rectContours.append(i)

# Sort rectangle Contours descending
rectContours = sorted(rectContours, key=cv2.contourArea, reverse=True)

# Finding and reshaping corner points
mcContour = findCorners(rectContours[0])

newMCContour = reOrderContour(mcContour)


# ========= MULTIPLE CHOICE SHEET ===========
# Size for multiple choice sheet
width2 = 255
height2 = 825
# Viewing the rectangle of multiple choice sheet and score using perspective
pt1 = np.float32(newMCContour)
pt2 = np.float32([[0, 0], [width2, 0], [0, height2], [width2, height2]])
mat = cv2.getPerspectiveTransform(pt1, pt2)
imgWarped = cv2.warpPerspective(image, mat, (width2, height2))
imgWarpedGray = cv2.cvtColor(imgWarped, cv2.COLOR_BGR2GRAY)
# THRESHOLDIMG
thresh = cv2.threshold(imgWarpedGray, 220, 250, cv2.THRESH_BINARY_INV)[1]

# SplitBoxes
rows = np.vsplit(thresh, 15)
boxes = []
numbers = []
count = 0
for r in rows:
    cols = np.hsplit(r, 5)
    for box in cols:
        if(count % 5 == 0):
            numbers.append(box)
        else:
            boxes.append(box)
        count += 1

# Marking answer: getting pixel of each choice/box
pixelVal = np.zeros((questions, choices))
countCol = 0
countRow = 0
for img in boxes:

    cv2.waitKey(0)
    totalPixels = cv2.countNonZero(img)
    pixelVal[countRow][countCol] = totalPixels
    countCol += 1
    # if the value choiices is = 4 go down
    if (countCol == 4):
        countRow += 1
        countCol = 0

# Compiling answers
print(pixelVal)
answers = []
for x in range(0, questions):
    numberShades = 0
    tmp_array = pixelVal[x]
    # getting and storing the max pixels in the array
    answer = np.where(tmp_array == np.amax(tmp_array))

    # Thresholds
    if int(np.amax(tmp_array)) > 800:
        # checks if there are 2 or more shades
        for choice in tmp_array:
            if choice > 800:
                numberShades += 1

        if numberShades > 1:
            answers.append(-1)
        else:
            answers.append(answer[0][0])
    # If there is no answer or shade
    else:
        answers.append(-1)
        # compare finalAsnswer to the correct answers

finalAnswers = np.array(answers)
correctAnswers = np.array(correctAnswers)
checks = np.equal(finalAnswers, correctAnswers)

correctScore = 0
for check in checks:
    if check == True:
        correctScore += 1

# ========= SCORE SHEET ===========
scoreContour = findCorners(rectContours[1])
newScoreContour = reOrderContour(scoreContour)
# Size for multiple choice sheet
width3 = 600
height3 = 300
# Viewing the rectangle of multiple choice sheet and score using perspective
pt1_1 = np.float32(newScoreContour)
pt1_2 = np.float32([[0, 0], [width3, 0], [0, height3], [width3, height3]])
imgWarpedScore = cv2.warpPerspective(image, mat, (width3, height3))

# # SHOW SCORE
imgRawScore = np.zeros_like(imgWarpedScore)
font = cv2.FONT_HERSHEY_SIMPLEX
cv2.putText(imgRawScore, str(int(correctScore)) + "/15",
            (width3//2, height3//2), font, 3,
            (0, 255, 0) if correctScore >= 8 else (0, 255, 255), 3)
invMat2 = cv2.getPerspectiveTransform(pt1_2, pt1_1)
imgInvScore = cv2.warpPerspective(imgRawScore, invMat2, (width, height))

# SHOW ANSWERS /Checking Answers
imgResult = imgWarped.copy()
# First Phase
secW = int(imgResult.shape[1]/5)
secH = int(imgResult.shape[0]/questions)
correctAnswer = correctAnswers[x] + 1
# imgResult = showResults(correctAnswer, answer, secW, secH, imgResult)

# Second Phase: Reverting back
revertImg = np.zeros_like(imgWarped)
revertImg = showResults(correctAnswer, answer, secW, secH, revertImg)
invMat = cv2.getPerspectiveTransform(pt2, pt1)
sefinal = cv2.warpPerspective(revertImg, invMat, (width, height))
imgFinal = cv2.addWeighted(sefinal, 1.3, imgFinal, .7, 0)
imgFinal = cv2.addWeighted(imgInvScore, 1.3, imgFinal, .7, 0)

# cv2.imwrite("output/test.png", imgFinal)
cv2.imshow("",  imgFinal)
cv2.waitKey(0)

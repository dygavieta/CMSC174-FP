import numpy as np
import cv2


def scan(filename, output_name):
   # def scan(filename, output_name):
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

    # List of correct answers
    questions = 15
    choices = 4
    choice = {'a': 0, 'b': 1, 'c': 2, 'd': 3}
    test = filename.split('.')
    f = open("answer_keys/" + test[0] + ".txt", "r")
    correctAnswers = [choice.get(x.strip()) for x in f.readlines()]

    # Reading Files
    image = cv2.imread("testcase/" + test[0] + ".png")
    imgFinal = image.copy()
    # File attributes
    width, height = image.shape[::-1][1::]

    imgGray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    imgBlur = cv2.GaussianBlur(imgGray, (3, 3), 1)
    edged = cv2.Canny(imgBlur, 1, 50)
    contours, hierarchy = cv2.findContours(
        edged, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    # Looking for rectangular contours
    rectangles = []
    for i in contours:

        area = cv2.contourArea(i)
        # Threshold
        if area > 50:
            # Look for possible rectangles
            perimeter = cv2.arcLength(i, closed=True)
            sides = cv2.approxPolyDP(i, 0.02*perimeter, True)
            if len(sides) == 4:
                rectangles.append(i)

    # Sort rectangle Contours descending
    rectangles = sorted(rectangles, key=cv2.contourArea, reverse=True)

    # Finding and reshaping corner points
    mcContour = findCorners(rectangles[0])
    newMCContour = reOrderContour(mcContour)

    # ========= BUBBLE ANSWER SHEET ===========
    # Sizing
    width2 = 255
    height2 = 825
    # Viewing the rectangle of multiple choice sheet and score using perspective
    pt1 = np.float32(newMCContour)
    pt2 = np.float32([[0, 0], [width2, 0], [0, height2], [width2, height2]])
    mat = cv2.getPerspectiveTransform(pt1, pt2)
    imgWarped = cv2.warpPerspective(image, mat, (width2, height2))
    imgWarpedGray = cv2.cvtColor(imgWarped, cv2.COLOR_BGR2GRAY)
    # THRESHOLDING
    thresh = cv2.threshold(imgWarpedGray, 220, 250, cv2.THRESH_BINARY_INV)[1]

    # SplitBoxes
    rows = np.vsplit(thresh, 15)
    boxes = []
    numbers = []
    count = 0
    for r in rows:
        cols = np.hsplit(r, 5)
        for box in cols:
            # cropping choice img for focus
            box = box[15:box.shape[0], 5: box.shape[1]]
            if(count % 5 == 0):
                numbers.append(box)
            else:
                boxes.append(box)
            count += 1

    # ==================== CHECKING ANSWERS =====================
    # Getting pixel of each choice/box
    pixelVal = np.zeros((questions, choices))
    countCol = 0
    countRow = 0
    for img in boxes:
        totalPixels = cv2.countNonZero(img)
        pixelVal[countRow][countCol] = totalPixels
        countCol += 1
        # if the value choiices is = 4 go down
        if (countCol == 4):
            countRow += 1
            countCol = 0

    # Compiling answers
    answers = []
    for x in range(0, questions):
        numberShades = 0
        tmp_array = pixelVal[x]
        # getting and storing the max pixels in the array
        answer = np.where(tmp_array == np.amax(tmp_array))
        maxPixel = int(np.amax(tmp_array))

        # Thresholds
        # Accepted If > 1000 overshaded < 750 partially shaded
        if (maxPixel > 700 and maxPixel < 1000):
            # checks if there are 2 or more shades
            for choice in tmp_array:
                # double shaded (partially and fully considered)
                if choice > 470:
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

    totalScore = 0
    for check in checks:
        if check == True:
            totalScore += 1

    # ========= SCORE SHEET ===========
    scoreContour = findCorners(rectangles[1])
    newScoreContour = reOrderContour(scoreContour)
    # Size for multiple choice sheet
    width3 = 600
    height3 = 300
    # Viewing the rectangle of multiple choice sheet and score using perspective
    pt1_1 = np.float32(newScoreContour)
    pt1_2 = np.float32([[0, 0], [width3, 0], [0, height3], [width3, height3]])
    imgWarpedScore = cv2.warpPerspective(image, mat, (width3, height3))

    #  SHOW SCORE
    imgRawScore = np.zeros_like(imgWarpedScore)
    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(imgRawScore, str(int(totalScore)) + "/15",
                (width3//2, height3//2), font, 3,
                (0, 255, 0) if totalScore >= 10 else (0, 255, 255) if totalScore >= 6 else (0, 0, 255), 10)
    invMat2 = cv2.getPerspectiveTransform(pt1_2, pt1_1)
    imgInvScore = cv2.warpPerspective(imgRawScore, invMat2, (width, height))

    # ================================

    # SHOW ANSWERS
    # Checking Answers
    imgResult = imgWarped.copy()
    # First Phase
    secW = int(imgResult.shape[1]/5)
    secH = int(imgResult.shape[0]/questions)
    correctAnswer = correctAnswers[x] + 1

    # Second Phase: Reverting back
    revertImg = np.zeros_like(imgWarped)
    revertImg = showResults(correctAnswer, answer, secW, secH, revertImg)

    invMat = cv2.getPerspectiveTransform(pt2, pt1)
    sefinal = cv2.warpPerspective(revertImg, invMat, (width, height))

    imgFinal = cv2.addWeighted(sefinal, 1.3, imgFinal, .7, 0)
    imgFinal = cv2.addWeighted(imgInvScore, 1.3, imgFinal, .7, 0)
    # output_dir = "output/"+output_name
    # cv2.imwrite(output_dir, imgFinal)
    # # return totalScore, output_dir

    output_dir = "output/"+output_name
    cv2.imwrite(output_dir, cv2.resize(imgFinal, (600, 900)))
    return totalScore, output_dir

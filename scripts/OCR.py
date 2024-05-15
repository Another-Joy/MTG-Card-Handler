
import cv2
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract'
import string
import re
import numpy as np
import DB



def parseRead(input):
    input = re.sub(r'[^a-zA-Z0-9]', ' ', input)
    input = input.split()
    
    
    print(input)
    if len(input[0]) == 1:
        num = str(int(input[1]))
        set = input[2]
    else:
        input[0] = re.sub('o', '0', input[0])
        if sum(l in string.ascii_lowercase for l in input[0]):
            input.pop(0)
            input[0] = re.sub('o', '0', input[0])
        num = str(int(input[0]))
        if len(input[1]) == 3:
            set = input[3]
        else:
            set = input[2]
            
            
    return (num, set)


def get_angle(point):
    x, y = point
    return np.arctan2(y, x)

def getCardImage(buffer):
    buffer = cv2.imread(buffer)
    buffer = cv2.rotate(buffer, cv2.ROTATE_90_COUNTERCLOCKWISE)
    grayscale = cv2.cvtColor(buffer, cv2.COLOR_RGB2GRAY)
    blurred = cv2.GaussianBlur(grayscale, (5, 5), 0)
    _, threshold = cv2.threshold(
        blurred,
        110,
        255,
        cv2.THRESH_BINARY_INV
    )

    contours, _ = cv2.findContours(
        threshold,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    cardContours = sorted([
        contour
        for contour in contours
        if len(
            cv2.approxPolyDP(
                contour,
                0.04 * cv2.arcLength(contour, True),
                True
            )
        ) == 4
    ], key=cv2.contourArea, reverse=True)

    # No card was found, bail
    if not cardContours:
        return

    largestCard, *_ = cardContours

    rectangle = cv2.minAreaRect(largestCard)
    center, size, angle = rectangle
    width, height = size

    box = sorted([
        point
        for point in cv2.boxPoints(rectangle)
    ], key=lambda p: get_angle(center - p))

    # # if the image isn't close enough in aspect ratio to our reference ratio
    # # then stop processing
    # if abs((width / height) - MTG_CARD_ASPECT_RATIO) > 0.05:
    #     return

    # Perspective warping probably isn't necessary here
    # since we are just transforming a box with no perspective on it at all
    # but this code is a bit more readable than doing an affine transform imo
    # and in the future I'd like to do some magic with hough lines and kmeans
    # to get the cards perspective and warp from that.
    
    # I can't just get the cards perspective from the contour, since
    # approxPolyDP will cut of edge of the card, due to the rounded corners

    transform = cv2.getPerspectiveTransform(
        np.float32(box),
        np.array([
            [1000, 1000],
            [0, 1000],
            [0, 0],
            [1000, 0],
        ], dtype=np.float32)
    )
    result = cv2.warpPerspective(
        buffer,
        transform,
        (1000, 1000)
    )
    cv2.imshow('ROI', result)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    cv2.imwrite('temp.png', result)
    return 'temp.png'

def recognizeCardText(path):
    img = cv2.imread(path)
    
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)    
    
    # Apply histogram equalization to improve contrast
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)
    height, width = img.shape[:2]
    


    roi = enhanced[(46*height//50):(49*height//50), width//18:(width//4)]
    # Use Tesseract OCR to extract text    # Display the ROI for verification
    cv2.imshow('ROI', roi)
    cv2.waitKey(0)
    cv2.destroyAllWindows()   
    return (pytesseract.image_to_string(roi, config='--psm 6')).strip().lower()



def getCardId(path):
    return DB.getCardNumber(parseRead(recognizeCardText(getCardImage(path))))
    
    
    
id = getCardId("C:\\Users\\tiago\\Documents\\COde\\esper2.png")
print(DB.getNameFromId(id))
print(DB.getSetFromId(id))
print(DB.getRarityFromId(id))
print(DB.getPriceFromId(id))
print(DB.divideByPrice(id))


import cv2
from collections import deque
import argparse
import pyautogui

#работаем с двумя камерами
camera = cv2.VideoCapture(0)
camera1 = cv2.VideoCapture(1)

ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video",
	help="path to the (optional) video file")
ap.add_argument("-b", "--buffer", type=int, default=64,
	help="max buffer size")
args = vars(ap.parse_args())


colorLower = (4, 100, 100)
colorUpper = (24, 255, 255)
pts = deque(maxlen=args["buffer"])


while True:

  (grabbed, frame) = camera.read()
  (grabbed, frame1) = camera1.read()
  hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

  hsv1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2HSV)
  mask1 = cv2.inRange(hsv1, colorLower, colorUpper)
  mask1 = cv2.erode(mask1, None, iterations=2)
  mask1 = cv2.dilate(mask1, None, iterations=2)
  cnts = cv2.findContours(mask1.copy(), cv2.RETR_EXTERNAL,
                          cv2.CHAIN_APPROX_SIMPLE)[-2]

  hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
  mask = cv2.inRange(hsv, colorLower, colorUpper)
  mask = cv2.erode(mask, None, iterations=2)
  mask = cv2.dilate(mask, None, iterations=2)
  cnts1 = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
                          cv2.CHAIN_APPROX_SIMPLE)[-2]

  center = None

  # only proceed if at least one contour was found
  if len(cnts) > 0:
    # find the largest contour in the mask, then use
    # it to compute the minimum enclosing circle and
    # centroid
    c = max(cnts, key=cv2.contourArea)
    ((x, y), radius) = cv2.minEnclosingCircle(c)
    M = cv2.moments(c)
    center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
    #КРУГ-РАДИУС
    # only proceed if the radius meets a minimum size
    if radius > 10:
      # draw the circle and centroid on the frame,
      # then update the list of tracked points
      cv2.circle(frame1, (int(x), int(y)), int(radius),
                 (0, 255, 255), 2)
      cv2.circle(frame1, center, 5, (0, 0, 255), -1)
      #дублируем движение объекта, курсором мыши
      pyautogui.moveTo(int(x)*2, int(y)*2)

  if len(cnts1) > 0:
    # find the largest contour in the mask, then use
    # it to compute the minimum enclosing circle and
    # centroid
    c = max(cnts1, key=cv2.contourArea)
    ((x, y), radius) = cv2.minEnclosingCircle(c)
    M = cv2.moments(c)
    center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
    #КРУГ-РАДИУС
    # only proceed if the radius meets a minimum size
    if radius > 10:
      # draw the circle and centroid on the frame,
      # then update the list of tracked points
      cv2.circle(frame, (int(x), int(y)), int(radius),
                 (0, 255, 255), 2)
      cv2.circle(frame, center, 5, (0, 0, 255), -1)
      #клик, когда шарик попадает в зону "клика" второй камеры
      if int(x)>290:
        pyautogui.click()
	#задержка чтобы наш поросенок отлетел от стены, иначе накрутит много очков
        cv2.waitKey(700)





  # update the points queue
  pts.appendleft(center)
  #линия настройки, на картинке получаемой с камеры контроля "клика"
  cv2.line(frame, (320, 0), (320, 512), (0, 255, 0), thickness=2)
  cv2.line(frame, (295, 0), (295, 512), (0, 255, 0), thickness=2)

  #cv2.imshow("Frame", frame)
  #cv2.imshow("Frame1", frame1)

  key = cv2.waitKey(1) & 0xFF

  # if the 'q' key is pressed, stop the loop
  if key == ord("q"):
    break

# cleanup the camera and close any open windows
camera.release()
cv2.destroyAllWindows()

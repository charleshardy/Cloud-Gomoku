#!/usr/bin/python

# -*- coding: utf-8 -*-

import sys
import time
import cv2
import cv2.cv as cv
from optparse import OptionParser
import numpy as np

DEBUG_VERBOSE = 1
DEBUG_BENCHMARK = 2
DEBUG_DETECT_CIRCLE = 4
DEBUG_DETECT_OBJECT = 8
DEBUG_LOW_LEVEL = 0x10

def get_put_chess():
	global currReportIndex
	# TODO: use mutex
	if len(boardCoodinates) == currReportIndex:
		return ()

	ret = tuple(boardCoodinates[currReportIndex])
	currReportIndex += 1

	return ret

def calcChessCoodinate(i, color):
	name = "Black chess" if color == 0 else "White chess"
	if debug & DEBUG_DETECT_OBJECT:
		print("calcChessCoodinate(" + name + "): (%d, %d)" % (i[0], i[1]))

	x_delta = (i[0] - leftTopStarPosition[0] + gridInterval / 2.0) / gridInterval
	y_delta = (i[1] - leftTopStarPosition[1] + gridInterval / 2.0) / gridInterval

	cood = (leftTopStarCoodinate[0] + int(x_delta), leftTopStarCoodinate[1] + int(y_delta))
	if cood[0] >= maxChessBoardGrid or cood[1] >= maxChessBoardGrid:
		if debug & (DEBUG_VERBOSE | DEBUG_DETECT_OBJECT) == DEBUG_VERBOSE | DEBUG_DETECT_OBJECT:
			print(name + " (%d, %d) recongnized but out of chess board (%d)" % (cood[0], cood[1], maxChessBoardGrid))
		return

	if debug:
		print(name + " (%d, %d) recongnized" % (cood[0], cood[1]))

	# FIXME: use mutex
	boardCoodinates.append((cood[0], cood[1], color))

def putVirtualBoard(x, y, color):
	if debug & DEBUG_DETECT_OBJECT:
		print("putVirtualBoard(): (%d, %d, color = %d) added" % (x, y, color))

	if color == 0:
		blackChessPositions.append([x, y, False])
	else:
		whiteChessPositions.append([x, y, False])

	# 检查是否可以开始计算每个棋子的坐标了
	if leftTopStarPosition == ():
		return

	for i in blackChessPositions:
		if i[2] == True:
			continue

		# 表示还没有经过坐标计算
		calcChessCoodinate(i, color = 0)
		# 标记为已经计算过
		i[2] = True

	for i in whiteChessPositions:
		if i[2] == True:
			continue

		calcChessCoodinate(i, color = 1)
		i[2] = True

	if debug:
		print("boardCoodinates: ", boardCoodinates)

def inKnownPosition(x, y, positions):
	# 单个方向上的误差是正负2
	delta_threshold = 4
	# 遍历所有已经记录的位置，如果新的位置距离所有已经记录的位置超过阈值，
	# 则表示这是一个新的合法的位置。
	for i in positions:
		x_delta = abs(i[0] - x)
		y_delta = abs(i[1] - y)
		if x_delta < delta_threshold and y_delta < delta_threshold:
			return True

	return False

def inKnownStarPosition(x, y):
	# 单个方向上的误差是正负2
	delta_threshold = 4
	# 遍历所有已经记录的位置，如果新的位置距离所有已经记录的位置超过阈值，
	# 则表示这是一个新的合法的位置。
	for i in starPositions:
		x_delta = abs(i[0] - x)
		y_delta = abs(i[1] - y)
		if x_delta < delta_threshold and y_delta < delta_threshold:
			return True

	return False

def inKnownChessPosition(x, y, positions):
	# 单个方向上的误差是正负2
	delta_threshold = 4
	# 遍历所有已经记录的位置，如果新的位置距离所有已经记录的位置超过阈值，
	# 则表示这是一个新的合法的位置。
	for i in positions:
		x_delta = abs(i[0] - x)
		y_delta = abs(i[1] - y)
		if x_delta < delta_threshold and y_delta < delta_threshold:
			# 如果已经被计算过棋盘坐标，那么就算作已知的棋子
			return i[2] == True

	return False

def inKnownBlackChessPosition(x, y):
	return inKnownChessPosition(x, y, blackChessPositions)

def inKnownWhiteChessPosition(x, y):
	return inKnownChessPosition(x, y, whiteChessPositions)

def calcStarPosition(x, y):
	# If 4 stars are available on the chess board,
	# there is no need to recalculate the positions.
	if len(starPositions) == 4:
		return

	if debug & DEBUG_DETECT_OBJECT:
		print("calcStarPosition(): (%d, %d) added to %s" % (x, y, repr(starPositions)))

	# we have a new coordinate of star
	starPositions.append((x, y))

	if len(starPositions) != 4:
		return

	# 当统计出了4个坐标以后，找出左上角的坐标
	# TODO: 找出4个星的坐标
	min = 0
	leftTopIndex = 0
	for n, i in enumerate(starPositions):
		# 左上角的星的x、y坐标和一定是最小的
		if min and i[0] + i[1] >= min:
			continue

		min = i[0] + i[1]
		leftTopIndex = n

	global leftTopStarPosition
	leftTopStarPosition = (starPositions[leftTopIndex][0], starPositions[leftTopIndex][1])

	if debug:
		print("Left top star @ (%d, %d)" % \
			(leftTopStarPosition[0], leftTopStarPosition[1]))

def __showHist(img, color, desc):
	hist = cv2.calcHist([img], [0], None, histSize = [256], ranges = [0, 256])
	minVal, maxVal, minLoc, maxLoc = cv2.minMaxLoc(hist)
	maxLimit = img.shape[0] * img.shape[1]
	if debug & (DEBUG_VERBOSE | DEBUG_LOW_LEVEL) == DEBUG_VERBOSE | DEBUG_LOW_LEVEL:
		print("%s statistics:" % desc)
		print("  min intensity: %d" % minLoc[1])
		print("  numbers of min intensity: %d (%f%%)" % (minVal, minVal * 100 / maxLimit))
		print("  max intensity %d" % maxLoc[1])
		print("  numbers of max intensity: %d (%f%%)" % (maxVal, maxVal * 100 / maxLimit))

	hist_img = np.zeros([256,512,3], np.uint8)
	for h in range(256):
		tmp = hist[h] * (256 * 0.9) / maxVal
		cv2.line(hist_img, (h*2+0, 256), (h*2+0, 256 - tmp), color)
		cv2.line(hist_img, (h*2+1, 256), (h*2+1, 256 - tmp), color)
	cv2.imshow(desc + " hist image", hist_img)

def showHist(img, title):
	if img.ndim == 3:
		b, g, r = cv2.split(img)
		print b.shape, b.ndim
		__showHist(b, (255, 0, 0), title + ": blue")
		__showHist(g, (0, 255, 0), title + ": green")
		__showHist(r, (0, 0, 255), title + ": red")
		gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
	elif img.ndim == 2:
		gray = img.reshape((img.shape[0], img.shape[1], 1))
	else:
		print("Unsupport dim %d" % img.ndim)

	__showHist(gray, (127, 127, 127), title + ": gray")

def drawCircle(frame, x, y, r, color):
    # draw the outer circle
	cv2.circle(frame, (x, y), r, color, 1)
	# draw the center of the circle
	cv2.circle(frame, (x, y), 1, (0, 0, 255), 1)

def detectCircles(screen, **p):
	if debug & DEBUG_BENCHMARK:
		e1 = cv2.getTickCount()

	img = cv2.cvtColor(screen, cv2.COLOR_BGR2GRAY)

	if debug & (DEBUG_LOW_LEVEL | DEBUG_VERBOSE) == DEBUG_LOW_LEVEL | DEBUG_VERBOSE:
		cv2.imshow("Gray screen", img)

	if False:
		img = cv2.equalizeHist(img)
		if debug & (DEBUG_LOW_LEVEL | DEBUG_VERBOSE) == DEBUG_LOW_LEVEL | DEBUG_VERBOSE:
			showHist(img, "equalizeHist")

	if p["lKernelSize"]:
		l = cv2.Laplacian(img, cv2.CV_8U, ksize = p["lKernelSize"], borderType = cv2.BORDER_CONSTANT)
		ret, l = cv2.threshold(l, 0, 255, p["thresholdType"] + cv2.THRESH_OTSU)
		img -= l

	if p["gKernelSize"]:
		img = cv2.GaussianBlur(img, ksize = (p["gKernelSize"], p["gKernelSize"]), sigmaX = p["sigma"], sigmaY = p["sigma"])

	if p["kernelSize"]:
		kernel = np.ones((p["kernelSize"], p["kernelSize"]), np.uint8)
		img = cv2.dilate(img, kernel, iterations = p["iter"])
		img = cv2.erode(img, kernel, iterations = p["iter"])

	circles = cv2.HoughCircles(img, cv.CV_HOUGH_GRADIENT, 1, p["minDist"], param1= p["cannyThreshold"], \
		param2 = p["accThreshold"], minRadius = p["minRadius"], maxRadius = p["maxRadius"])

	if debug & DEBUG_BENCHMARK:
		e2 = cv2.getTickCount()
		print("detectCircles() takes %f sec" % ((e2 - e1) / cv2.getTickFrequency()))

	if debug & DEBUG_LOW_LEVEL:
		cv2.imshow("Circles detected screen", img)

	if circles is not None:
		if debug & DEBUG_DETECT_CIRCLE:
			print("%d circles detected" % circles.shape[1])

		return np.uint16(np.around(circles[0]))

	if debug & DEBUG_DETECT_CIRCLE:
		print("No circle detected")

	return None

def filterCircles(gray, targetGray, grayDelta, r, radius, radiusDelta):
	if abs(gray - targetGray) <= grayDelta and abs(r - radius) <= radiusDelta:
		return True

	return False

def detectWhiteChesses(gray, r):
	if debug & (DEBUG_DETECT_OBJECT | DEBUG_VERBOSE) == DEBUG_DETECT_OBJECT | DEBUG_VERBOSE:
		print("detectWhiteChesses(): gray %f vs %f +- %f, radius %f vs %f +- %f" \
			% (gray, whiteChessGray, whiteChessGrayDelta, \
			r, (minChessRadius + maxChessRadius) / 2.0, \
			chessRadiusDelta))
	return filterCircles(gray, whiteChessGray, whiteChessGrayDelta, \
		r, (minChessRadius + maxChessRadius) / 2.0, chessRadiusDelta)

def detectBlackChesses(gray, r):
	if debug & (DEBUG_DETECT_OBJECT | DEBUG_VERBOSE) == DEBUG_DETECT_OBJECT | DEBUG_VERBOSE:
		print("detectBlackChesses(): gray %f vs %f +- %f, radius %f vs %f +- %f" \
			% (gray, blackChessGray, blackChessGrayDelta, \
			r, (minChessRadius + maxChessRadius) / 2.0, \
			chessRadiusDelta))
	return filterCircles(gray, blackChessGray, blackChessGrayDelta, \
		r, (minChessRadius + maxChessRadius) / 2.0, chessRadiusDelta)

def detectStars(gray, r):
	if debug & (DEBUG_DETECT_OBJECT | DEBUG_VERBOSE) == DEBUG_DETECT_OBJECT | DEBUG_VERBOSE:
		print("detectStars(): gray %f vs %f +- %f, radius %f vs %f +- %f" \
			% (gray, starGray, starGrayDelta, r, \
			(minStarRadius + maxStarRadius) / 2.0, starRadiusDelta))
	return filterCircles(gray, starGray, starGrayDelta, \
		r, (minStarRadius + maxStarRadius) / 2.0, starRadiusDelta)

def processFrame(prev_frame, curr_frame, **param):
#	if prev_frame is not None:
#		frame = cv2.absdiff(curr_frame, prev_frame)
#	else:
	frame = curr_frame

	circles = detectCircles(frame, **param)

	if circles is not None:
		for i in circles:
			x = int(i[0])
			y = int(i[1])
			r = int(i[2])
			gray = float(frame[y, x].mean())

			if debug & DEBUG_DETECT_CIRCLE:
				print("Detected circle: gray %f @(%d, %d, %d)" % (gray, x, y, r))
				drawCircle(curr_frame, x, y, r, (127, 127, 127))

			if x + r >= screen_width or x - r < 0 or \
				y + r >= screen_height or y - r < 0:
				continue

			if inKnownBlackChessPosition(x, y) == True:
				if debug & DEBUG_DETECT_OBJECT:
					drawCircle(curr_frame, x, y, r, (255, 255, 255))
				continue

			if inKnownWhiteChessPosition(x, y) == True:
				if debug & DEBUG_DETECT_OBJECT:
					drawCircle(curr_frame, x, y, r, (0, 0, 0))
				continue

			# 当棋子放在了星号上的时候，应该优先显示棋子的轮廓
			if inKnownStarPosition(x, y) == True:
				if debug & DEBUG_DETECT_OBJECT:
					drawCircle(curr_frame, x, y, r, (0, 255, 0))
				continue

			if detectStars(gray, r) == True:
				# TODO: creating matching block for speeding up in futures
				if debug & DEBUG_DETECT_OBJECT:
					drawCircle(curr_frame, x, y, r, (0, 255, 0))

				calcStarPosition(x, y)
				continue

			if detectBlackChesses(gray, r) == True:
				if debug & DEBUG_DETECT_OBJECT:
					drawCircle(curr_frame, x, y, r, (255, 255, 255))

				putVirtualBoard(x, y, color = 0)
				continue

			if detectWhiteChesses(gray, r) == True:
				if debug & DEBUG_DETECT_OBJECT:
					drawCircle(curr_frame, x, y, r, (0, 0, 0))

				putVirtualBoard(x, y, color = 1)
				continue

			# The remaining are unment circles
			if debug & DEBUG_DETECT_OBJECT:
				print("Unmet circle: gray %f @(%d, %d, %d)" % (gray, x, y, r))
				#log.write(err.join("\n"))
				drawCircle(curr_frame, x, y, r, (0, 0, 255))

	if debug:
		cv2.imshow(screen_title, curr_frame)

def nothing(x):
	pass

# Place holders. See the details in main()
debug = 0
startDelay = 0
frameDelay = 0
minChessRadius = 0.0
maxChessRadius = 0.0
chessRadiusDelta = 0.0
minStarRadius = 0.0
maxStarRadius = 0.0
starRadiusDelta = 0.0
whiteChessGray = 0
whiteChessGrayDelta = 0
blackChessGray = 0
blackChessGrayDelta = 0
starGray = 0
starGrayDelta = 0
screen_title = "Chess Board"
screen_width = 0
screen_height = 0
whiteChessRadius = 0
whiteChessX = 0
whiteChessY = 0
maxChessBoardGrid = 0
leftTopStarCoodinate = (2, 2)
boardCoodinates = []
gridInterval = 41
blackChessPositions = []
whiteChessPositions = []
starPositions = []
leftTopStarPosition = ()
currReportIndex = 0
	
def main(camera_id = 0, debug_level = DEBUG_DETECT_OBJECT, frame_delay = 300, image_test = False):
	print("Carmera ID %d, debug level 0x%x" % (camera_id, debug_level))

	# Global settings
	global debug, startDelay, frameDelay, minChessRadius, maxChessRadius, chessRadiusDelta, \
	minStarRadius, maxStarRadius, starRadiusDelta, whiteChessGray, whiteChessGrayDelta, \
	blackChessGray, blackChessGrayDelta, starGray, starGrayDelta, screen_title, \
	screen_width, screen_height, whiteChessRadius, whiteChessX, whiteChessY, \
	leftTopStarCoodinate, boardCoodinates, gridInterval, chessPositions, starPositions, \
	leftTopStarPosition, currReportIndex, maxChessBoardGrid

	# 0 - disabled
	# 1 - enabled
	# 2 - benchmark
	# 3 - verbose message
	# 4 - low level debugging for circle detection
	# 5 - lowest level debugging for image recognition
	debug = debug_level

	# 摄像头读取第一帧前的延迟（秒）
	startDelay = 2

	# 读取每一帧的延迟（豪秒）
	frameDelay = frame_delay

	# 用于检测棋子的半径
	minChessRadius = 10.0
	maxChessRadius = 12.0
	chessRadiusDelta = 1.0

	# 用于检测星号的半径
	minStarRadius = 5.0
	maxStarRadius = 7.0
	starRadiusDelta = 1.5

	# 黑白棋子的亮度和最大误差
	whiteChessGray = 213
	whiteChessGrayDelta = 15
	blackChessGray = 20
	blackChessGrayDelta = 15
	starGray = 20
	starGrayDelta = 15

	screen_title = "Chess Board"
	screen_width = 0
	screen_height = 0

	whiteChessRadius = 0
	whiteChessX = 0
	whiteChessY = 0

	# 棋盘最大的格子数
	maxChessBoardGrid = 10
	leftTopStarCoodinate = (2, 2)
	# 保存已经下了的棋子所在的坐标
	boardCoodinates = []
	# 格子间隔
	gridInterval = 41
	# 保存棋子的位置
	chessPositions = []
	# 保存所有星的位置
	starPositions = []
	# 保存左上角星的位置
	leftTopStarPosition = ()

	currReportIndex = 0

	log = open("log", "w")

	if image_test == False:
		# Start video capture from camera
		cap = cv2.VideoCapture(camera_id)

		if not cap.isOpened():
			print("Camera cannot be opened")
			sys.exit(-1)

		screen_width = int(cap.get(3))
		screen_height = int(cap.get(4))
	else:
		test_img = cv2.imread("sample.bmp")
		screen_width = int(test_img.shape[1])
		screen_height = int(test_img.shape[0])

	print("Screen width %d, height %d" % (screen_width, screen_height))

	# Default settings for low level parameters
	minDist = 2 * int(maxChessRadius)
	minRadius = int(minStarRadius)
	maxRadius = int(maxChessRadius)
	kernelSize = 3
	iter = 2
	gKernelSize = 3
	sigma = 3
	thresholdType = 1
	cannyThreshold = 50
	lKernelSize = 27
	accThreshold = 18

	if debug:
		cv2.namedWindow(screen_title)
		if debug & DEBUG_DETECT_CIRCLE:
			cv2.createTrackbar('Minimum circle radius', screen_title, minRadius, 15, nothing)
			cv2.createTrackbar('Maximum circle radius', screen_title, int(maxChessRadius), 15, nothing)
			cv2.createTrackbar('Minimum distance', screen_title, minDist, screen_width, nothing)
			cv2.createTrackbar('Accumulator threshold', screen_title, accThreshold, 50, nothing)
		if debug & DEBUG_LOW_LEVEL:
			cv2.createTrackbar('Kernel size for element', screen_title, kernelSize, 255, nothing)
			cv2.createTrackbar('Iterations', screen_title, iter, 255, nothing)
			cv2.createTrackbar('Gaussian kernel size', screen_title, gKernelSize, 255, nothing)
			cv2.createTrackbar('Sigma for Gaussian', screen_title, sigma, 255, nothing)
			cv2.createTrackbar('Threshold type', screen_title, thresholdType, 4, nothing)
			cv2.createTrackbar('Canny threshold', screen_title, cannyThreshold, 1024, nothing)
			cv2.createTrackbar('Laplacian kernel size', screen_title, lKernelSize, 31, nothing)
			#cv2.createTrackbar('Scale factor for Laplacian', screen_title, 1, 255, nothing)
			#cv2.createTrackbar('Delta for Laplacian', screen_title, 0, 255, nothing)
			#cv2.createTrackbar('Border Type for Laplacian', screen_title, 0, 4, nothing)
		if debug & DEBUG_DETECT_OBJECT:
			cv2.createTrackbar('White gray', screen_title, whiteChessGray, 255, nothing)
			cv2.createTrackbar('Black gray', screen_title, blackChessGray, 255, nothing)
			cv2.createTrackbar('Star gray', screen_title, starGray, 255, nothing)
			cv2.createTrackbar('White gray delta', screen_title, whiteChessGrayDelta, 50, nothing)
			cv2.createTrackbar('Black gray delta', screen_title, blackChessGrayDelta, 50, nothing)
			cv2.createTrackbar('Star gray delta', screen_title, starGrayDelta, 50, nothing)

	if image_test == False:
		# 适当的延迟可以忽略掉在摄像头刚刚打开时包含的不稳定的前几帧数据
		time.sleep(startDelay)

	prev_frame = None
	while True:
		if image_test == False:
			ret, curr_frame = cap.read()

			if ret is None:
				print("Camera video EOF")
				break

			if debug:
				cv2.imwrite("current_frame.bmp", curr_frame)
		else:
			curr_frame = test_img

		if debug:
			# get current positions of all trackbars
			if debug & DEBUG_DETECT_CIRCLE:
				minDist = cv2.getTrackbarPos('Minimum distance', screen_title)
				minRadius = cv2.getTrackbarPos('Minimum circle radius', screen_title)
				maxRadius = cv2.getTrackbarPos('Maximum circle radius', screen_title)
				accThreshold = cv2.getTrackbarPos('Accumulator threshold', screen_title)
				if accThreshold == 0:
					accThreshold = 1
			if debug & DEBUG_LOW_LEVEL:
				kernelSize = cv2.getTrackbarPos('Kernel size for element', screen_title)
				iter = cv2.getTrackbarPos('Iterations', screen_title)
				gKernelSize = cv2.getTrackbarPos('Gaussian kernel size', screen_title)
				if gKernelSize:
					gKernelSize = gKernelSize if gKernelSize & 1 else gKernelSize + 1
				sigma = cv2.getTrackbarPos('Sigma for Gaussian', screen_title)
				thresholdType = cv2.getTrackbarPos('Threshold type', screen_title)
				cannyThreshold = cv2.getTrackbarPos('Canny threshold', screen_title)
				if cannyThreshold == 0:
					cannyThreshold = 1
				lKernelSize = cv2.getTrackbarPos('Laplacian kernel size', screen_title)
				if lKernelSize:
					lKernelSize = lKernelSize if lKernelSize & 1 else lKernelSize + 1
				#scale = cv2.getTrackbarPos('Scale factor for Laplacian', screen_title)
				#delta = cv2.getTrackbarPos('Delta for Laplacian', screen_title)
				#borderType = cv2.getTrackbarPos('Border Type for Laplacian', screen_title)
				#if borderType == 3:
				#	borderType = 4
			if debug & DEBUG_DETECT_OBJECT:
				whiteChessGray = cv2.getTrackbarPos('White gray', screen_title)
				blackChessGray = cv2.getTrackbarPos('Black gray', screen_title)
				starGray = cv2.getTrackbarPos('Star gray', screen_title)
				whiteChessGrayDelta = cv2.getTrackbarPos('White gray delta', screen_title)
				blackChessGrayDelta = cv2.getTrackbarPos('Black gray delta', screen_title)
				starGrayDelta = cv2.getTrackbarPos('Star gray delta', screen_title)

		if debug:
			frame = curr_frame.copy()
		else:
			frame = curr_frame

		params = {
			"whiteChessGray": whiteChessGray,
			"blackChessGray": blackChessGray,
			"starGray": starGray,
			"whiteChessGrayDelta": whiteChessGrayDelta,
			"blackChessGrayDelta": blackChessGrayDelta,
			"starGrayDelta": starGrayDelta,
			"minDist": minDist,
			"minRadius": minRadius,
			"maxRadius": maxRadius,
			"kernelSize": kernelSize,
			"iter": iter,
			"gKernelSize": gKernelSize,
			"sigma": sigma,
			"thresholdType": thresholdType,
			"cannyThreshold": cannyThreshold,
			"lKernelSize": lKernelSize,
			#"scale": scale,
			#"delta": delta,
			#"borderType": borderType,
			"accThreshold": accThreshold,
		}
		processFrame(prev_frame, frame, **params)
		prev_frame = curr_frame

		if frameDelay:
			cmd = cv2.waitKey(frameDelay) & 0xFF
			if cmd == ord('q'):
				break
			elif cmd == ord('s'):
				cv2.waitKey()

	if image_test == False:
		cap.release()

	if debug:
		cv2.destroyAllWindows()

	log.close()

VERSION = '0.3'

def parse_args():
	parser = OptionParser(usage='%prog [-h] [--version] [-D debug] [-d camera_id]',
						  version='%prog ' + VERSION)
	parser.add_option('-D', '--debug-level', dest='debug', action='store',
					  default=DEBUG_DETECT_OBJECT, help='Specify the debug level [%default]')
	parser.add_option('-d', '--camera-id', dest='camera_id', action='store',
					  default=0, help='Specify the camera id [%default]')
	parser.add_option('-f', '--frame-delay', dest='frame_delay', action='store',
					  default=300, help='Specify the delay per frame in ms [%default]')

	opts, args = parser.parse_args()

	if len(args):
		parser.print_help()
		sys.exit(-1)

	return opts

if __name__ == "__main__":
	opts = parse_args()

	main(int(opts.camera_id), int(opts.debug), int(opts.frame_delay))

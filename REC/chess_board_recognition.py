#!/usr/bin/python

# -*- coding: utf-8 -*-

import sys
import time
import cv2
import cv2.cv as cv
from optparse import OptionParser
import numpy as np

def get_put_chess():
	global currReportIndex
	try:
		ret = tuple(boardCoodinates[currReportIndex])
		currReportIndex += 1
	except IndexError:
		return ()

	return ret

def calcChessCoodinate(i):
	name = "Black chess" if i[2] == 0 else "White chess"
	if debug >= 1:
		print("calcChessCoodinate(" + name + "): (%d, %d)" % (i[0], i[1]))

	x_delta = (i[0] - leftTopStarPosition[0] + gridInterval / 2.0) / gridInterval
	y_delta = (i[1] - leftTopStarPosition[1] + gridInterval / 2.0) / gridInterval

	cood = (leftTopStarCoodinate[0] + int(x_delta), leftTopStarCoodinate[1] + int(y_delta))
	if cood[0] >= maxChessBoardGrid or cood[1] >= maxChessBoardGrid:
		if debug >= 1:
			print(name + " (%d, %d) recongnized but out of chess board" % (cood[0], cood[1]))
		return

	if debug >= 1:
		print(name + " (%d, %d) recongnized" % (cood[0], cood[1]))

	boardCoodinates.append((cood[0], cood[1], i[2]))

def calcChessPosition(x, y, type):
	if len(chessPositions) > 0:
		min_x_delta = screen_width
		min_y_delta = screen_height
		# 单个方向上的误差是正负2
		delta_threshold = 4
		# 遍历所有已经记录的位置，如果新的位置距离所有已经记录的位置超过阈值，
		# 则表示这是一个新的合法的棋子。
		for i in chessPositions:
			x_delta = abs(i[0] - x)
			y_delta = abs(i[1] - y)
			if x_delta <= delta_threshold and y_delta <= delta_threshold:
				return

		# we have a new coordinate of chess
		chessPositions.append([x, y, type, False])
	else:
		chessPositions.append([x, y, type, False])

def putVirtualBoard(x, y, type):
	calcChessPosition(x, y, type)

	# 检查是否可以开始计算每个棋子的坐标了
	if leftTopStarPosition == ():
		return

	for i in chessPositions:
		# 表示还没有经过坐标计算
		if i[3] == False:
			calcChessCoodinate(i)
			# 标记为已经计算过
			i[3] = True

	if debug >= 1:
		print("boardCoodinates: ", boardCoodinates)

def calcStarPosition(x, y):
	if debug >= 3:
		print("calcStarPosition(): checking (%d, %d) against %d" % (x, y, len(starPositions)))

	# 4 stars available on the chess board
	if len(starPositions) == 4:
		return
	elif len(starPositions) > 0:
		min_x_delta = screen_width
		min_y_delta = screen_height
		# 单个方向上的误差是正负2
		delta_threshold = 4
		# 遍历所有已经记录的位置，如果新的位置距离所有已经记录的位置超过阈值，
		# 则表示这是一个新的合法的星。
		for i in starPositions:
			x_delta = abs(i[0] - x)
			y_delta = abs(i[1] - y)
			if x_delta <= delta_threshold and y_delta <= delta_threshold:
				return

		# we have a new coordinate of star
		starPositions.append((x, y))
	else:
		starPositions.append((x, y))
		return

	if debug >= 3:
		print("calcStarPosition(): (%d, %d) added to %s" % (x, y, repr(starPositions)))

	# 当统计出了4个坐标以后，找出左上角的坐标
	min = 0
	leftTopIndex = 0
	if len(starPositions) == 4:
		for n, i in enumerate(starPositions):
			if min and i[0] + i[1] >= min:
				continue

			min = i[0] + i[1]
			leftTopIndex = n

		global leftTopStarPosition
		leftTopStarPosition = (starPositions[leftTopIndex][0], starPositions[leftTopIndex][1])

		if debug >= 1:
			print("Left top star @ (%d, %d)" % (leftTopStarPosition[0], leftTopStarPosition[1]))

def __showHist(img, color, desc):
	hist = cv2.calcHist([img], [0], None, histSize = [256], ranges = [0, 256])
	minVal, maxVal, minLoc, maxLoc = cv2.minMaxLoc(hist)
	maxLimit = img.shape[0] * img.shape[1]
	if debug >= 3:
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

def drawCircle(frame, c, color):
	if debug >= 1:
	    # draw the outer circle
		cv2.circle(frame, (c[0], c[1]), c[2], color, 1)
		# draw the center of the circle
		cv2.circle(frame, (c[0], c[1]), 1, (0, 0, 255), 1)

def detectCircles(screen, **p):
	if debug >= 2:
		e1 = cv2.getTickCount()

	img = cv2.cvtColor(screen, cv2.COLOR_BGR2GRAY)
	if debug >= 3:
		showHist(img, "Screen gray")
		cv2.imshow("Screen gray", img)

	if False:
		img = cv2.equalizeHist(img)
		if debug >= 1:
			showHist(img, "equalizeHist")

	if True:
		#l = cv2.Laplacian(img, cv2.CV_8U, ksize = 1, scale = 1, delta = 0)
		#l = cv2.Laplacian(img, cv2.CV_8U, ksize = p["kernelSize"], borderType = cv2.BORDER_REFLECT)
		l = cv2.Laplacian(img, cv2.CV_8U, ksize = 5, borderType = cv2.BORDER_CONSTANT)
		ret, l = cv2.threshold(l, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
		#ret, l = cv2.threshold(l, 0, 255, p["threshold"] + cv2.THRESH_OTSU)
		img -= l

	if p["gKernelSize"]:
		img = cv2.GaussianBlur(img, ksize = (p["gKernelSize"], p["gKernelSize"]), sigmaX = p["sigma"], sigmaY = p["sigma"])

	if p["kernelSize"]:
		kernel = np.ones((p["kernelSize"], p["kernelSize"]), np.uint8)
		img = cv2.dilate(img, kernel, iterations = p["iter"])
		img = cv2.erode(img, kernel, iterations = p["iter"])

	if True:
		circles = cv2.HoughCircles(img, cv.CV_HOUGH_GRADIENT, 1, p["minDist"], \
			param2 = p["accThreshold"], minRadius = p["minRadius"], maxRadius = p["maxRadius"])
	else:
		circles = cv2.HoughCircles(img, cv.CV_HOUGH_GRADIENT, 1, p["minDist"], param1= p["cannyThreshold"], \
			param2 = p["accThreshold"], minRadius = p["minRadius"], maxRadius = p["maxRadius"])

	if debug >= 2:
		e2 = cv2.getTickCount()
		print("detectCircles() takes %f sec" % ((e2 - e1) / cv2.getTickFrequency()))

	if debug >= 3:
		cv2.imshow("Circles detected ...", img)

	if circles is not None:
		if debug >= 3:
			print("%d circles detected" % circles.shape[1])

		return np.uint16(np.around(circles))

	if debug >= 3:
		print("No circle detected")

	return None

def filterCircles(frame, circles, targetGray, grayDelta, radius, radiusDelta, desc):
	chesses = []

	for i in circles[0, :]:
		if i.mean() == 0:
			continue

		x = i[0]
		y = i[1]
		r = int(i[2])

		if x >= screen_width or y >= screen_height:
			continue

		gray = int(frame[y, x].mean())
		if debug >= 3:
			print("filterCircles(" + desc + "): gray %d vs %d ? %d, radius %d vs %d ? %d" % (gray, targetGray, grayDelta, r, radius, radiusDelta))
		if abs(gray - targetGray) <= grayDelta and abs(r - radius) <= radiusDelta:
			chesses.append((x, y, r))
			i[:] = 0
			# TODO: 制作模板

	return chesses

def averageChessRadius():
	return (minChessRadius + maxChessRadius) / 2.0

def averageStarRadius():
	return (minStarRadius + maxStarRadius) / 2.0

def detectWhiteChesses(frame, circles):
	return filterCircles(frame, circles, whiteChessGray, whiteChessGrayDelta, \
		averageChessRadius(), chessRadiusDelta, "White Chess")

def detectBlackChesses(frame, circles):
	return filterCircles(frame, circles, blackChessGray, blackChessGrayDelta, \
		averageChessRadius(), chessRadiusDelta, "Black Chess")

def detectStars(frame, circles):
	return filterCircles(frame, circles, starGray, starGrayDelta, \
		averageStarRadius(), starRadiusDelta, "Star")

def processFrame(prev_frame, curr_frame, **param):
#	if prev_frame is not None:
#		frame = cv2.absdiff(curr_frame, prev_frame)
#	else:
	frame = curr_frame

	circles = detectCircles(frame, **param)

	if circles is not None:
		for i in circles[0, :]:
			if i.mean() == 0:
				continue

			# TODO: filter out invalid circles
			if i[0] >= screen_width or i[1] >= screen_height:
				continue

			if debug >= 3:
				x = i[0]
				y = i[1]
				r = i[2]
				print("Detected circle: gray %d @(%d, %d, %d)" % (frame[y, x].mean(), x, y, r))

		Stars = detectStars(frame, circles)
		for n in Stars:
			if debug >= 1:
				drawCircle(curr_frame, n, (0, 255, 0))
			calcStarPosition(int(n[0]), int(n[1]))

		BlackChesses = detectBlackChesses(frame, circles)
		for n in BlackChesses:
			if debug >= 1:
				drawCircle(curr_frame, n, (255, 255, 255))
			putVirtualBoard(int(n[0]), int(n[1]), type = 0)

		whiteChesses = detectWhiteChesses(frame, circles)
		for n in whiteChesses:
			if debug >= 1:
				drawCircle(curr_frame, n, (0, 0, 0))
			putVirtualBoard(int(n[0]), int(n[1]), type = 1)

		# 剩下的是不符合要求的采样
		for i in circles[0, :]:
			if i.mean() == 0:
				continue

			if debug >= 3:
				print("Unmet circle: gray %f @(%d, %d, %d)" % (frame[i[1], i[0]].mean(), i[0], i[1], i[2]))
				#print(err)
				#log.write(err.join("\n"))
				drawCircle(curr_frame, i, (0, 0, 255))

	if debug >= 1:
		cv2.imshow(screen_title, curr_frame)

def nothing(x):
	pass

VERSION = '0.1'

def parse_args():
	parser = OptionParser(usage='%prog [-h] [--version] [-D debug] [-d camera_id]',
						  version='%prog ' + VERSION)
	parser.add_option('-D', '--debug-level', dest='debug', action='store',
					  default=1, help='Specify the debug level [%default]')
	parser.add_option('-d', '--camera-id', dest='camera_id', action='store',
					  default=0, help='Specify the camera id [%default]')

	opts, args = parser.parse_args()

	if len(args):
		parser.print_help()
		sys.exit(-1)

	return opts

# 占位符。真正的设置见main()
debug = 1
startDelay = 2
frameDelay = 300
minChessRadius = 9.0
maxChessRadius = 12.0
chessRadiusDelta = 2.0
minStarRadius = 5.0
maxStarRadius = 7.0
starRadiusDelta = 1.5
whiteChessGray = 226
whiteChessGrayDelta = 12
blackChessGray = 31
blackChessGrayDelta = 6
starGray = 29
starGrayDelta = 7
screen_title = "Chess Board"
screen_width = 0
screen_height = 0
whiteChessRadius = 0
whiteChessX = 0
whiteChessY = 0
maxChessBoardGrid = 10
leftTopStarCoodinate = (2, 2)
boardCoodinates = []
gridInterval = 41
chessPositions = []
starPositions = []
leftTopStarPosition = ()
currReportIndex = 0
	
def main(camera_id = 0, debug_level = 3):
	print("Carmera ID %d, debug level %d" % (camera_id, debug_level))

	# Global settings
	global debug, startDelay, frameDelay, minChessRadius, maxChessRadius, chessRadiusDelta, \
	minStarRadius, maxStarRadius, starRadiusDelta, whiteChessGray, whiteChessGrayDelta, \
	blackChessGray, blackChessGrayDelta, starGray, starGrayDelta, screen_title, \
	screen_width, screen_height, whiteChessRadius, whiteChessX, whiteChessY, \
	leftTopStarCoodinate, boardCoodinates, gridInterval, chessPositions, starPositions, \
	leftTopStarPosition, currReportIndex

	# 0 - disabled
	# 1 - enabled
	# 2 - benchmark
	# 3 - verbose message
	# 4 - reserved
	# 5 - show images
	debug = debug_level

	# 摄像头读取第一帧前的延迟（秒）
	startDelay = 2

	# 读取每一帧的延迟（豪秒）
	frameDelay = 300

	# 用于检测棋子的半径
	minChessRadius = 9.0
	maxChessRadius = 12.0
	chessRadiusDelta = 2.0

	# 用于检测星号的半径
	minStarRadius = 5.0
	maxStarRadius = 7.0
	starRadiusDelta = 1.5

	# 黑白棋子的亮度和最大误差
	whiteChessGray = 226
	whiteChessGrayDelta = 12
	blackChessGray = 31
	blackChessGrayDelta = 6
	starGray = 29
	starGrayDelta = 7

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

	# Start videp capture from camera
	cap = cv2.VideoCapture(camera_id)

	if not cap.isOpened():
		print("Camera cannot be opened ...")
		sys.exit(-1)

	screen_width = cap.get(3)
	screen_height = cap.get(4)
	print("Screen width %d, height %d" % (screen_width, screen_height))

	if debug >= 1:
		cv2.namedWindow(screen_title)
		whiteChessGray = cv2.createTrackbar('White gray', screen_title, whiteChessGray, 255, nothing)
		blackChessGray = cv2.createTrackbar('Black gray', screen_title, blackChessGray, 255, nothing)
		starGray = cv2.createTrackbar('Star gray', screen_title, starGray, 255, nothing)
		#cv2.createTrackbar('Kernel size for element', screen_title, 3, 255, nothing)
		#cv2.createTrackbar('Iterations', screen_title, 2, 255, nothing)
		#cv2.createTrackbar('Gaussian kernel size', screen_title, 5, 255, nothing)
		#cv2.createTrackbar('Sigma for Gaussian', screen_title, 4, 255, nothing)
		#cv2.createTrackbar('Threshold', screen_title, 0, 4, nothing)
		cv2.createTrackbar('Accumulator threshold', screen_title, 14, 255, nothing)
		cv2.createTrackbar('Minimum distance', screen_title, 2 * int(minChessRadius), 1024, nothing)
		#cv2.createTrackbar('Threshold for Canny', screen_title, 200, 4096, nothing)
		cv2.createTrackbar('Minimum circle radius', screen_title, int(minStarRadius), 20, nothing)
		cv2.createTrackbar('Maximum circle radius', screen_title, int(maxChessRadius), 20, nothing)
		#cv2.createTrackbar('Kernel size for Laplacian', screen_title, 5, 255, nothing)
		#cv2.createTrackbar('Scale factor for Laplacian', screen_title, 1, 255, nothing)
		#cv2.createTrackbar('Delta for Laplacian', screen_title, 0, 255, nothing)
		#cv2.createTrackbar('Border Type for Laplacian', screen_title, 0, 4, nothing)
	else:
		kernelSize = 3
		iter = 2
		gKernelSize = 5
		sigma = 4
		accThreshold = 14
		minDist = 2 * int(minChessRadius)
		minRadius = int(minStarRadius)
		maxRadius = int(maxChessRadius)

	# FIXME
	if True:
		kernelSize = 3
		iter = 2
		gKernelSize = 5
		sigma = 4
		accThreshold = 20
		minDist = 2 * int(minChessRadius)
		minRadius = int(minStarRadius)
		maxRadius = int(maxChessRadius)

	# 适当的延迟可以忽略掉在摄像头刚刚打开时包含的不稳定的前几帧数据
	time.sleep(startDelay)

	prev_frame = None
	while True:
		ret, curr_frame = cap.read()

		if ret is None:
			print("Camera video EOF")
			break

		if debug >= 1:
			cv2.imwrite("current_frame.bmp", curr_frame)

			# get current positions of all trackbars
			whiteChessGray = cv2.getTrackbarPos('White gray', screen_title)
			blackChessGray = cv2.getTrackbarPos('Black gray', screen_title)
			starGray = cv2.getTrackbarPos('Star gray', screen_title)
			#kernelSize = cv2.getTrackbarPos('Kernel size for element', screen_title)
			#iter = cv2.getTrackbarPos('Iterations', screen_title)
			#gKernelSize = cv2.getTrackbarPos('Gaussian kernel size', screen_title)
			#if gKernelSize:
			#	gKernelSize = gKernelSize if gKernelSize & 1 else gKernelSize + 1
			#sigma = cv2.getTrackbarPos('Sigma for Gaussian', screen_title)
			#thresholdType = cv2.getTrackbarPos('Threshold', screen_title)
			minDist = cv2.getTrackbarPos('Minimum distance', screen_title)
			#cannyThreshold = cv2.getTrackbarPos('Threshold for Canny', screen_title)
			#if cannyThreshold == 0:
			#	cannyThreshold = 1
			accThreshold = cv2.getTrackbarPos('Accumulator threshold', screen_title)
			if accThreshold == 0:
				accThreshold = 1
			minRadius = cv2.getTrackbarPos('Minimum circle radius', screen_title)
			maxRadius = cv2.getTrackbarPos('Maximum circle radius', screen_title)
			#kernelSize = cv2.getTrackbarPos('Kernel size for Laplacian', screen_title)
			#kernelSize = kernelSize if kernelSize & 1 else kernelSize + 1
			#scale = cv2.getTrackbarPos('Scale factor for Laplacian', screen_title)
			#delta = cv2.getTrackbarPos('Delta for Laplacian', screen_title)
			#borderType = cv2.getTrackbarPos('Border Type for Laplacian', screen_title)
			#if borderType == 3:
			#	borderType = 4

		if debug >= 1:
			frame = curr_frame.copy()
		else:
			frame = curr_frame

		params = {
			"whiteChessGray": whiteChessGray,
			"blackChessGray": blackChessGray,
			"starGray": starGray,
			"gKernelSize": gKernelSize,
			"sigma": sigma,
			#"thresholdType": thresholdType,
			"minDist": minDist,
			#"cannyThreshold": cannyThreshold,
			"accThreshold": accThreshold,
			"minRadius": minRadius,
			"maxRadius": maxRadius,
			"kernelSize": kernelSize,
			"iter": iter,
			#"scale": scale,
			#"delta": delta,
			#"borderType": borderType,
		}
		processFrame(prev_frame, frame, **params)
		prev_frame = curr_frame

		if cv2.waitKey(frameDelay) & 0xFF == ord('q'):
			break

	cap.release()
	log.close()

if __name__ == "__main__":
	opts = parse_args()

	main(int(opts.camera_id), int(opts.debug))
import cv2
import numpy
import datetime

def fit(img, templates, threshold):
	print(img.shape)
	# img_width, img_height = img.shape[1::-1]

	location = []
	for template in templates:
		result = cv2.matchTemplate(img, template, cv2.TM_CCOEFF_NORMED)
		# result = np.where(result >= threshold)
		cv2.imshow(result)
		location += result

source = cv2.imread("source.png", cv2.IMREAD_GRAYSCALE)
template = cv2.imread("template.png")

fit(source, template, 0.7)
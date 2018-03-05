import cv2
import numpy as np
from datetime import datetime

def fit(img, templates, threshold):
    img_width, img_height = img.shape[1::-1]
    best_location_count = -1
    best_locations = []

    locations = []
    location_count = 0
    for template in templates:
        result = cv2.matchTemplate(img, template, cv2.TM_CCOEFF_NORMED)
        # print(result)
        result = np.where(result >= threshold)
        location_count += len(result[0])
        locations += [result]
        # print(result)

    if (location_count > best_location_count):
        best_location_count = location_count
        best_locations = locations
    elif (location_count < best_location_count):
        pass

    return best_locations
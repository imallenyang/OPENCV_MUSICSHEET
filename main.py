import sys
import subprocess
import cv2
import time
import numpy as np
from best_fit import fit
from rectangle import Rectangle
from note import Note
from random import randint
from midiutil import MIDIFile

staff_files = ["resources/template/staff4.png", "resources/template/staff3.png", "resources/template/staff2.png", "resources/template/staff1.png"]
quarter_files = ["resources/template/quarter1.png", "resources/template/quarter2.png", "resources/template/quarter3.png"]
sharp_files = ["resources/template/sharp.png", "resources/template/f-sharp.png"]
flat_files = ["resources/template/flat-line.png", "resources/template/flat-space.png" ]
half_files = ["resources/template/half-space.png", "resources/template/half-note-line.png", "resources/template/half-line.png", "resources/template/half-note-space.png"]
whole_files = ["resources/template/whole-space.png", "resources/template/whole-note-line.png", "resources/template/whole-line.png", "resources/template/whole-note-space.png"]

staff_imgs = [cv2.imread(staff_file, 0) for staff_file in staff_files]
quarter_imgs = [cv2.imread(quarter_file, 0) for quarter_file in quarter_files]
sharp_imgs = [cv2.imread(sharp_files, 0) for sharp_files in sharp_files]
flat_imgs = [cv2.imread(flat_file, 0) for flat_file in flat_files]
half_imgs = [cv2.imread(half_file, 0) for half_file in half_files]
whole_imgs = [cv2.imread(whole_file, 0) for whole_file in whole_files]

staff_lower, staff_upper, staff_thresh = 50, 150, 0.70
sharp_lower, sharp_upper, sharp_thresh = 50, 150, 0.70
flat_lower, flat_upper, flat_thresh = 50, 150, 0.77
quarter_lower, quarter_upper, quarter_thresh = 50, 150, 0.70
half_lower, half_upper, half_thresh = 50, 150, 0.70
whole_lower, whole_upper, whole_thresh = 50, 150, 0.70

# Transforming the locations returned to a rectangle
def locate_rectangles(img, templates, start, stop, threshold):
    locations = fit(img, templates, start, stop, threshold)
    img_locations = []
    for i in range(len(templates)):
        w, h = templates[i].shape[::-1]
        for pt in zip(*locations[i][::-1]):
            img_locations.append(Rectangle(pt[0], pt[1], w, h))
    return img_locations

#Merge the raectangles that mostly overlap
def merge_rectangles(recs, threshold):
    merged_recs = []
    while len(recs) > 0:
        r = recs.pop(0)
        recs.sort(key=lambda rec: rec.distance(r))
        merged = True
        while(merged):
            merged = False
            i = 0
            for _ in range(len(recs)):
                if r.overlap(recs[i]) > threshold or recs[i].overlap(r) > threshold:
                    r = r.merge(recs.pop(i))
                    merged = True
                elif recs[i].distance(r) > r.w/2 + recs[i].w/2:
                    break
                else:
                    i += 1
        merged_recs.append(r)
    return merged_recs

#Draw the rectangle on the given image
def draw_rectangles(recs, img):
    rectangle_img = img.copy()
    for r in recs:
        r.draw(rectangle_img, (0, 0, 255), 2)
    return rectangle_img

def open_file(path):
    cmd = {'linux':'eog', 'win32':'explorer', 'darwin':'open'}[sys.platform]
    subprocess.run([cmd, path])

# img_file = sys.argv[1]
img_file = 'resources/samples/lost.jpg'

img_gray = cv2.imread(img_file, 0)
img = cv2.cvtColor(img_gray,cv2.COLOR_GRAY2RGB)
ret,img_gray = cv2.threshold(img_gray,127,255,cv2.THRESH_BINARY)
img_width, img_height = img_gray.shape[::-1]

print("Matching staff image...")
staff_recs = locate_rectangles(img_gray, staff_imgs, staff_lower, staff_upper, staff_thresh)

if staff_recs != []:
    print("{} different matches found".format(len(staff_recs)))
    print("Drawing staff image results...")
    cv2.imwrite("staff_recs_img.png", draw_rectangles(staff_recs, img))
    open_file("staff_recs_img.png")
else:
    print("No staff matches found")

print("Filtering weak staff matches...")
heights = [r.y for r in staff_recs] + [0]
histo = [heights.count(i) for i in range(0, max(heights) + 1)]
avg = np.mean(list(set(histo)))
staff_recs = [r for r in staff_recs if histo[r.y] > avg]

print("Merging staff image results...")
staff_recs = merge_rectangles(staff_recs, 0.01)

if staff_recs != []:
    print("{} different matches found".format(len(staff_recs)))
    print("Drawing staff image results...")
    cv2.imwrite("staff_recs_img_1.png", draw_rectangles(staff_recs, img))
    open_file("staff_recs_img_1.png")
else:
    print("No staff matches found")

# print("Discovering staff locations...")
# staff_boxes = merge_rectangles([Rectangle(0, r.y, img_width, r.h) for r in staff_recs], 0.01)
# staff_boxes_img = img.copy()
# for r in staff_boxes:
#     r.draw(staff_boxes_img, (0, 0, 255), 2)
# cv2.imwrite('staff_boxes_img.png', staff_boxes_img)
# open_file('staff_boxes_img.png')

# print("Matching sharp image...")
# sharp_recs = locate_rectangles(img_gray, sharp_imgs, sharp_lower, sharp_upper, sharp_thresh)
# print("Merging sharp image results...")
# sharp_recs = merge_rectangles(sharp_recs, 0.5)
# if sharp_recs != []:
#     print("{} different matches found".format(len(sharp_recs)))
#     print("Drawing sharp image results...")
#     cv2.imwrite('sharp_recs_img.png', draw_rectangles(sharp_recs, img))
#     open_file('sharp_recs_img.png')
# else:
#     print("No sharp signs found")

# print("Matching flat image...")
# flat_recs = locate_rectangles(img_gray, flat_imgs, flat_lower, flat_upper, flat_thresh)
# print("Merging flat image results...")
# flat_recs = merge_rectangles(flat_recs, 0.5)
# if flat_recs != []:
#     print("{} different matches found".format(len(flat_recs)))
#     print("Drawing flat image results...")
#     cv2.imwrite("flat_recs_img.png", draw_rectangles(flat_recs, img))
#     open_file("flat_recs_img.png")
# else:
#     print("No flat signs found")

# print("Matching quarter image...")
# quarter_recs = locate_rectangles(img_gray, quarter_imgs, quarter_lower, quarter_upper, quarter_thresh)
# print("Merging quarter image results...")
# quarter_recs = merge_rectangles(quarter_recs, 0.5)
# if quarter_recs != []:
#     print("{} different matches found".format(len(quarter_recs)))
#     print("Drawing quarter image results...")
#     cv2.imwrite("quarter_recs_img.png", draw_rectangles(quarter_recs, img))
#     open_file("quarter_recs_img.png")
# else:
#     print("No quarter notes found")

# print("Matching half image...")
# half_recs = locate_rectangles(img_gray, half_imgs, half_lower, half_upper, half_thresh)
# print("Merging half image results...")
# half_recs = merge_rectangles(half_recs, 0.5)
# if half_recs != []:
#     print("{} different matches found".format(len(half_recs)))
#     print("Drawing half image results...")
#     cv2.imwrite("half_recs_img.png", draw_rectangles(half_recs, img))
#     open_file("half_recs_img.png")
# else:
#     print("No half notes found")

# print("Matching whole image...")
# whole_recs = locate_rectangles(img_gray, whole_imgs, whole_lower, whole_upper, whole_thresh)
# print("Merging whole image results...")
# whole_recs = merge_rectangles(whole_recs, 0.5)
# if whole_recs != []:
#     print("{} different matches found".format(len(whole_recs)))
#     print("Drawing whole image results...")
#     cv2.imwrite("whole_recs_img.png", draw_rectangles(whole_recs, img))
#     open_file("whole_recs_img.png")
# else:
#     print("No whole notes found")

# note_groups = []
# for box in staff_boxes:
#     staff_sharps = [Note(r, "sharp", box) 
#         for r in sharp_recs if abs(r.middle[1] - box.middle[1]) < box.h*5.0/8.0]
#     staff_flats = [Note(r, "flat", box) 
#         for r in flat_recs if abs(r.middle[1] - box.middle[1]) < box.h*5.0/8.0]
#     quarter_notes = [Note(r, "4,8", box, staff_sharps, staff_flats) 
#         for r in quarter_recs if abs(r.middle[1] - box.middle[1]) < box.h*5.0/8.0]
#     half_notes = [Note(r, "2", box, staff_sharps, staff_flats) 
#         for r in half_recs if abs(r.middle[1] - box.middle[1]) < box.h*5.0/8.0]
#     whole_notes = [Note(r, "1", box, staff_sharps, staff_flats) 
#         for r in whole_recs if abs(r.middle[1] - box.middle[1]) < box.h*5.0/8.0]
#     staff_notes = quarter_notes + half_notes + whole_notes
#     staff_notes.sort(key=lambda n: n.rec.x)
#     staffs = [r for r in staff_recs if r.overlap(box) > 0]
#     staffs.sort(key=lambda r: r.x)
#     note_color = (randint(0, 255), randint(0, 255), randint(0, 255))
#     note_group = []
#     i = 0; j = 0;
#     while(i < len(staff_notes)):
#         if (staff_notes[i].rec.x > staffs[j].x and j < len(staffs)):
#             r = staffs[j]
#             j += 1;
#             if len(note_group) > 0:
#                 note_groups.append(note_group)
#                 note_group = []
#             note_color = (randint(0, 255), randint(0, 255), randint(0, 255))
#         else:
#             note_group.append(staff_notes[i])
#             staff_notes[i].rec.draw(img, note_color, 2)
#             i += 1
#     note_groups.append(note_group)

# for r in staff_boxes:
#     r.draw(img, (0, 0, 255), 2)
# for r in sharp_recs:
#     r.draw(img, (0, 0, 255), 2)
# flat_recs_img = img.copy()
# for r in flat_recs:
#     r.draw(img, (0, 0, 255), 2)

# midi = MIDIFile(1, adjust_origin = -1)
 
# track = 0   
# time = 0
# channel = 0
# volume = 100

# midi.addTrackName(track, time, "Track")
# midi.addTempo(track, time, 140)

# if note_groups != [[]]:
#     for note_group in note_groups:
#         duration = None
#         for note in note_group:
#             note_type = note.sym
#             if note_type == "1":
#                 duration = 4
#             elif note_type == "2":
#                 duration = 2
#             elif note_type == "4,8":
#                 duration = 1 if len(note_group) == 1 else 0.5
#             pitch = note.pitch
#             midi.addNote(track,channel,pitch,time,duration,volume)
#             time += duration

#     midi.addNote(track,channel,pitch,time,4,0)
#     # And write it to disk.
#     binfile = open("output.mid", 'wb')
#     midi.writeFile(binfile)
#     binfile.close()
#     open_file('output.mid')
# else:
#     print("Failed to detect any note")

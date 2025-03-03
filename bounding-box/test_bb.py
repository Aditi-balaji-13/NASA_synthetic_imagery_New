import cv2

image_path = "output/trial_0/image_00.png"
image = cv2.imread(image_path)

xmin, ymin, xmax, ymax =0,0,0,0

xmin = int(xmin)
ymin = int(ymin)
xmax = int(xmax)
ymax = int(ymax)

color = (0,0,255)
thickness = 2
image = cv2.rectangle(image, (xmin, ymin), (xmax, ymax), color, thickness)
output_path = "image1.png"
cv2.imwrite(output_path, image)

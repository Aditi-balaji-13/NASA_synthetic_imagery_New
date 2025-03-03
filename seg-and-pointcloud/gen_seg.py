import cv2

image_path = "output/trial_01/image_03.png"
image = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)

background_path = "../data/background/sky.jpg"
background = cv2.imread(background_path, cv2.IMREAD_UNCHANGED)

dimx, dimy, dimz = image.shape
for i in range(0,dimx):
    for j in range(0,dimy):
        if(image[i][j][3] == 0):
            image[i][j] = [0,0,0,255]
        else:
            image[i][j] = [255, 255, 255,255]


# xmin = int(xmin)
# ymin = int(ymin)
# xmax = int(xmax)
# ymax = int(ymax)

# color = (0,0,255)
# thickness = 2
# image = cv2.rectangle(image, (xmin, ymin), (xmax, ymax), color, thickness)
output_path = "image1.png"
cv2.imwrite(output_path, image)
image = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)

output_path = "image2.png"
for i in range(0, dimx):
    for j in range(0,dimy):
        if image[i][j][3] == 0:
            image[i][j][0] = background[(int) (i/3)][(int) (j/3)][0]
            image[i][j][1] = background[(int) (i/3)][(int) (j/3)][1]
            image[i][j][2] = background[(int) (i/3)][(int) (j/3)][2]
            image[i][j][3] = 255

cv2.imwrite(output_path, image)
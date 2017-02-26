# importing some useful packages
import matplotlib.image as mpimg
import numpy as np
import cv2


image_height = 0
image_width = 0
blur_ksize = 5  # Gaussian blur kernel size
canny_lthreshold = 50  # Canny edge detection low threshold
canny_hthreshold = 150  # Canny edge detection high threshold

# Hough transform parameters
rho = 1
theta = np.pi / 180
threshold = 15
min_line_length = 20
max_line_gap = 20

#history data is for smooth function
history=[]
SMOOTH_ENABLE=False


def grayscale(img):
    """Applies the Grayscale transform
    This will return an image with only one color channel
    but NOTE: to see the returned image as grayscale
    (assuming your grayscaled image is called 'gray')
    you should call plt.imshow(gray, cmap='gray')"""
    return cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    # Or use BGR2GRAY if you read an image with cv2.imread()
    # return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)


def canny(img, low_threshold, high_threshold):
    """Applies the Canny transform"""
    return cv2.Canny(img, low_threshold, high_threshold)


def gaussian_blur(img, kernel_size):
    """Applies a Gaussian Noise kernel"""
    return cv2.GaussianBlur(img, (kernel_size, kernel_size), 0)


def region_of_interest(img, vertices):
    """
    Applies an image mask.

    Only keeps the region of the image defined by the polygon
    formed from `vertices`. The rest of the image is set to black.
    """
    # defining a blank mask to start with
    mask = np.zeros_like(img)

    # defining a 3 channel or 1 channel color to fill the mask with depending on the input image
    if len(img.shape) > 2:
        channel_count = img.shape[2]  # i.e. 3 or 4 depending on your image
        ignore_mask_color = (255,) * channel_count
    else:
        ignore_mask_color = 255

    # filling pixels inside the polygon defined by "vertices" with the fill color
    cv2.fillPoly(mask, vertices, ignore_mask_color)

    # returning the image only where mask pixels are nonzero
    masked_image = cv2.bitwise_and(img, mask)
    return masked_image


def draw_lines(img, lines, color=[255, 0, 0], thickness=10):
    """
    NOTE: this is the function you might want to use as a starting point once you want to
    average/extrapolate the line segments you detect to map out the full
    extent of the lane (going from the result shown in raw-lines-example.mp4
    to that shown in P1_example.mp4).

    Think about things like separating line segments by their
    slope ((y2-y1)/(x2-x1)) to decide which segments are part of the left
    line vs. the right line.  Then, you can average the position of each of
    the lines and extrapolate to the top and bottom of the lane.

    This function draws `lines` with `color` and `thickness`.
    Lines are drawn on the image inplace (mutates the image).
    If you want to make the lines semi-transparent, think about combining
    this function with the weighted_img() function below
    """
    for line in lines:
        for x1, y1, x2, y2 in line:
            cv2.line(img, (x1, y1), (x2, y2), color, thickness)


def weighted_img(img, initial_img, α=0.8, β=1., λ=0.):
    """
    `img` is the output of the hough_lines(), An image with lines drawn on it.
    Should be a blank image (all black) with lines drawn on it.

    `initial_img` should be the image before any processing.

    The result image is computed as follows:

    initial_img * α + img * β + λ
    NOTE: initial_img and img must be the same shape!
    """
    return cv2.addWeighted(initial_img, α, img, β, λ)


def filterAbnormalLines(lines_ori):
    lines_des = []
    for line in lines_ori:
        for x1, y1, x2, y2 in line:
            if(not (x1 - x2)==0):
                slop = (y1 - y2) / (x1 - x2)
                if (0.4 < slop < 0.7 or -0.85 < slop < -0.65):
                    lines_des.append([[x1, y1, x2, y2]])
    return np.array(lines_des)


def getLeftAndRightLaneLines(lines):
    left_slop_sum = 0
    right_slop_sum = 0
    left_start_x_sum = 0
    right_start_x_sum = 0
    left_num = 0
    right_num = 0

    # solve x2
    #    (SP_x,image_height)
    solve_x2 = lambda x1, y1, y2, k: (y2 - y1) / k + x1

    for line in lines:
        for x1, y1, x2, y2 in line:
            slop = (y1 - y2) / (x1 - x2)
            if (slop < 0):
                left_slop_sum += slop
                left_start_x_sum += solve_x2(x1, y1, image_height, slop)
                left_num += 1
            else:
                right_slop_sum += slop
                right_start_x_sum += solve_x2(x1, y1, image_height, slop)
                right_num += 1

    if(left_num<3 or right_num<3):
        return history

    left_slop_ave = left_slop_sum / left_num
    right_slop_ave = right_slop_sum / right_num
    left_start_x_ave = left_start_x_sum / left_num
    right_start_x_ave = right_start_x_sum / right_num

    left_and_right_y2 = 300.0/500*image_height
    # left_and_right_y2 = 330

    left_end_x2 = solve_x2(left_start_x_ave, image_height, left_and_right_y2, left_slop_ave)
    right_end_x2 = solve_x2(right_start_x_ave, image_height, left_and_right_y2, right_slop_ave)

    left_line = [left_start_x_ave, image_height, left_end_x2, left_and_right_y2]
    right_line = [right_start_x_ave, image_height, right_end_x2, left_and_right_y2]
    left_line = list(map(lambda x: int(round(x)), left_line))
    right_line = list(map(lambda x: int(round(x)), right_line))
    return np.array([[left_line], [right_line]])


def hough_lines(img, rho, theta, threshold, min_line_len, max_line_gap):
    global history
    """
    `img` should be the output of a Canny transform.

    Returns an image with hough lines drawn.
    """
    lines = cv2.HoughLinesP(img, rho, theta, threshold, np.array([]), minLineLength=min_line_len,
                            maxLineGap=max_line_gap)
    # filter abnormal line
    lines_des = filterAbnormalLines(lines)
    # print(lines_des)
    # print('---------')

    lines_des = getLeftAndRightLaneLines(lines_des)

    if (SMOOTH_ENABLE==True and not (history ==[])):
        for i in range(0,2):
            error=np.linalg.norm(lines_des[i]-history[i])
            if(error>20):
                lines_des[i] = np.average(np.array([lines_des[i], history[i]]), axis=0, weights=[0,1])
            else:
                lines_des[i]=np.average(np.array([lines_des[i],history[i]]),axis=0,weights=[0.4,0.6])

    history=lines_des

    # print(lines_des)
    # print('-----------')

    # # print slop
    # for line in lines_des:
    #     for x1, y1, x2, y2 in line:
    #         print((y1 - y2) / (x1 - x2))
    #
    # print('------')
    # print slop
    # for line in lines:
    #     for x1, y1, x2, y2 in line:
    #         print((y1 - y2) / (x1 - x2))
    line_img = np.zeros((img.shape[0], img.shape[1], 3), dtype=np.uint8)
    draw_lines(line_img, lines_des)
    return line_img


def clearHistory():
    global history
    history=[]


def detect(image_origin,smooth_enable=False):
    try:
        global SMOOTH_ENABLE
        global image_height, image_width

        SMOOTH_ENABLE=smooth_enable

        # reading in an image
        gaussian_blur(image_origin, 5)
        # plt.figure()
        # plt.imshow(grayscale(image_origin), cmap='gray')
        edges = canny(image_origin, 50, 150)
        # plt.figure()
        # plt.imshow(edges, cmap='Greys_r')

        # This time we are defining a four sided polygon to mask
        imshape = image_origin.shape
        image_height, image_width = imshape[0], imshape[1]
        vertices = np.array([[(0, imshape[0]), (400, 350), (600, 350), (imshape[1], imshape[0])]], dtype=np.int32)
        edges = region_of_interest(edges, vertices)
        # plt.figure()
        # plt.imshow(edges, cmap='Greys_r')

        line_img = hough_lines(edges, rho, theta, threshold, 30, 10)
        output_img = cv2.addWeighted(image_origin, 0.8, line_img, 1, 0)
        return output_img
    except :
        return image_origin

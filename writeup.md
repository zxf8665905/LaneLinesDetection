# **Finding Lane Lines on the Road** 

## Writeup

---

#### Finding Lane Lines on the Road

The goals / steps of this project are the following:
* Make a pipeline that finds lane lines on the road
* Reflect on your work in a written report

---

### Reflection

### 1. Describe my pipeline. 

1. Image conversion to *grayscale*
2. Apply Gaussian blur to image
3. Used Canny edges detection
4. Croped region of interest
5. Hough line detection
6. Filter out the straight line with an irregular slope
7. Calculate the average slope of the two lane lines and the average intercept（Approximate straight line of lane）
8. Filter out some straight lines with sudden changes in position
9. Bleinding original image and image with lines


### 2. Identify potential shortcomings with your current pipeline

- The result is easily affected by the debris on the ground


### 3. Suggest possible improvements to your pipeline

- Add a filter for example: Kalman filter

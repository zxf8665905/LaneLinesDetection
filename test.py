import processImage
import matplotlib.pyplot as mpl
import matplotlib.image as mpimg
image_path='/Users/zengxuefeng/Development/LaneLinesDetection/test_images/whiteCarLaneSwitch.jpg'
img=processImage.detect(mpimg.imread(image_path))
mpl.imshow(img)
print('end test')
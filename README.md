## Prokudin-Gorsky
The first color photographer of Russia is Mikhail Sergeyevich Prokudin-Gorsky, who made the only color port of Leo Tolstoy. Each of his shots consists of three images in grayscale, corresponding to the blue, green and red color channels. Now
a collection of his photographs is in the American Library of Congress, a scan of the photographic plates available online. There is a program that combine images obtained from Prokudin-Gorsky photographic plates.

![PG_train](https://github.com/sibsonya/Computer-vision/blob/master/PG_train.png)

## Task description
# Basic alignment
The implementation of the basic part of the program consists of several stages:
1. Loading image and dividing it into three channels. It is enough to divide the image into three equal parts in height.
2. Removing frames. Each of the image channels needs to be cut off by 5% from each side.
3. Finding the best offset for channel alignment. In order to combine two images, we will shift one image relative to the other within certain limits, for example, from −15 to 15 pixels. Next, for the overlapping areas of the images, we calculate the metric. Optimal will be the shift at which the metric takes the largest or smallest value (depending on the metric). Two suitable metrics include Mean Square Error (MSE) and the Normalized Cross Correlation (NCC). To find the optimal shift using first metric, you need to take a minimum of all the shifts, using second metric - maximum of all the shifts.

# Pyramid Alignment
Combining large images with the basic approach will be very slow. For acceleration of alignment we can realize a pyramid of images. In the pyramid of images the original image is consistently reduced by 2 times to a certain size (for example, both sides were no more than 500 pixels in length). The search for the optimal shift begins with small image, and then on the way to the original image is refined at reduced copies of the image. Thus, the original image is not aligned in the range
−15...15 pixels, it is aligned in a smaller range, refined with the help of reduced copies of the image.

# Program interface, data and script for testing
It is necessary to implement the **align** function, which receives the image obtained by scanning the photographic plate as an input and returns the combined image. Data for testing - 10 images in two resolutions for testing a regular implementation and an implementation with a pyramid, respectively. Three dots are marked on each picture, one on each channel. The alignment function **align** must be on the point (g_row, g_col) of the green channel determine the coordinates of the corresponding points of the blue and red channels: (b_row, b_col), (r_row, r_col). For points returned by the function of coordinates and marking coordinates, it is calculated metric **l1**, which then collides with the threshold. If the metric does not exceed the threshold, then the image considered to be qualitatively combined. For small images, the threshold is 5, for large - 10.

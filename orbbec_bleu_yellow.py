import cv2
import numpy as np
from pyorbbecsdk import Context

# Initialize Orbbec SDK
ctx = Context()
ctx.init()

# Get the first connected device
device_list = ctx.query_devices()
if len(device_list) == 0:
    raise RuntimeError("No Orbbec device found!")
device = device_list[0]

# Create color stream
color_stream = device.create_color_stream()
color_stream.start()

# Define HSV ranges for blue and yellow
blue_lower = np.array([100, 150, 50])
blue_upper = np.array([140, 255, 255])
yellow_lower = np.array([20, 100, 100])
yellow_upper = np.array([30, 255, 255])

while True:
    # Get color frame
    frame = color_stream.wait_for_frame(1000)  # timeout in ms
    if frame is None:
        continue

    # Convert frame to numpy array
    img = np.frombuffer(frame.data(), dtype=np.uint8).reshape((frame.height(), frame.width(), 3))
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

    # Convert to HSV
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # Masks for blue and yellow
    mask_blue = cv2.inRange(hsv, blue_lower, blue_upper)
    mask_yellow = cv2.inRange(hsv, yellow_lower, yellow_upper)

    # Find contours
    contours_blue, _ = cv2.findContours(mask_blue, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours_yellow, _ = cv2.findContours(mask_yellow, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Draw contours on separate images
    blue_contour_img = np.zeros_like(img)
    yellow_contour_img = np.zeros_like(img)
    cv2.drawContours(blue_contour_img, contours_blue, -1, (255, 0, 0), 2)
    cv2.drawContours(yellow_contour_img, contours_yellow, -1, (0, 255, 255), 2)

    def get_center(contours):
        if contours:
            largest = max(contours, key=cv2.contourArea)
            M = cv2.moments(largest)
            if M["m00"] != 0:
                return int(M["m10"]/M["m00"]), int(M["m01"]/M["m00"])
        return None

    blue_center = get_center(contours_blue)
    yellow_center = get_center(contours_yellow)

    if blue_center and yellow_center:
        path_center_x = (blue_center[0] + yellow_center[0]) // 2
        path_center_y = (blue_center[1] + yellow_center[1]) // 2
        cv2.circle(img, (path_center_x, path_center_y), 10, (0, 0, 255), -1)

        # Compute steering offset
        img_center_x = img.shape[1] // 2
        offset = path_center_x - img_center_x
        print(f"Steering offset: {offset}")

    # Show main image and contour windows
    cv2.imshow("Path Detection", img)
    cv2.imshow("Blue Contours", blue_contour_img)
    cv2.imshow("Yellow Contours", yellow_contour_img)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

color_stream.stop()
ctx.close()
cv2.destroyAllWindows()

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Simulate a depth image (480x640)
h, w = 480, 640
depth_data = np.random.randint(500, 3000, size=(h, w))  # random depth values

# Define ROI
roi_top = h // 3
roi_bottom = 2 * h // 3
roi_left = w // 4
roi_right = 3 * w // 4

# Plot depth image
plt.figure(figsize=(8, 6))
plt.imshow(depth_data, cmap='jet')
plt.colorbar(label='Depth (mm)')
plt.title("Depth Frame with ROI Highlighted")

# Add ROI rectangle
rect = patches.Rectangle((roi_left, roi_top), roi_right - roi_left, roi_bottom - roi_top,
                         linewidth=2, edgecolor='yellow', facecolor='none')
plt.gca().add_patch(rect)

plt.show()

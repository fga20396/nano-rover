import pyorbbecsdk as ob
import numpy as np
import cv2
import math

# Initialize pipeline and config
pipeline = ob.Pipeline()
config = ob.Config()

# Enable depth stream
profiles = pipeline.get_stream_profile_list(ob.SensorType.DEPTH)
depth_profile = profiles.get_video_stream_profile(640, 480, ob.Format.Y16, 30)
config.enable_stream(depth_profile)

# Start pipeline
pipeline.start(config)
print("Streaming depth frames... Press ESC to exit.")

try:
    while True:
        frame_set = pipeline.wait_for_frameset(1000)
        depth_frame = frame_set.depth_frame()

        # Convert depth frame to numpy array
        depth_data = np.frombuffer(depth_frame.data(), dtype=np.uint16).reshape((depth_frame.height(), depth_frame.width()))

        # Define ROI (center area)
        h, w = depth_data.shape
        roi = depth_data[h//3:2*h//3, w//4:3*w//4]

        # Split ROI into left and right halves
        left_roi = roi[:, :roi.shape[1]//2]
        right_roi = roi[:, roi.shape[1]//2:]

        # Compute average depth (ignore zeros)
        left_depth = np.mean(left_roi[left_roi > 0])
        right_depth = np.mean(right_roi[right_roi > 0])
        center_depth = np.mean(roi[roi > 0])

        # Steering logic
        angle = 0.0
        if left_depth < right_depth:
            angle = 30  # steer right
        elif right_depth < left_depth:
            angle = -30  # steer left

        # Speed logic (closer obstacles = slower)
        speed = max(0.1, min(1.0, center_depth / 2000.0))  # normalize speed (0.1 to 1.0)

        print(f"Steering Angle: {angle}°, Speed: {speed:.2f}, Center Depth: {center_depth:.1f} mm")

        # Visualization
        depth_vis = cv2.convertScaleAbs(depth_data, alpha=0.03)
        depth_vis = cv2.applyColorMap(depth_vis, cv2.COLORMAP_JET)
        cv2.imshow("Depth", depth_vis)

        if cv2.waitKey(1) == 27:  # ESC to exit
            break

except KeyboardInterrupt:
    print("Stopping...")
finally:
    pipeline.stop()

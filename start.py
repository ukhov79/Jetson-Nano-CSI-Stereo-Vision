# This script calibrate IMX219-83 Stereo camera and show results (disparity map)
# Video starts from two Cameras connected to Jetson Nano B01
# When you see the recognized chessboard on the screen,
# press 'c' to add points into Calibration info
# You need to save about 30 shots of the chessboard, then press 's' to save calibration results.
# To view the calibration results press 'v'.
# Tap Esc to exit program.
# All Calibration data will be saved into /camera directory using pickle format

import cv2
import numpy as np
import pickle
from camera.camera import Camera

# Size of chessboard to Calibration
nx, ny = 9, 6

# termination criteria
criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

# prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
objp = np.zeros((ny * nx, 3), np.float32)
objp[:, :2] = np.mgrid[0:nx, 0:ny].T.reshape(-1, 2)

# Arrays to store object points and image points from all screens.
objpointsl = []  # 3d point in real world space
imgpointsl = []  # 2d points in image plane.
objpointsr = []
imgpointsr = []


def main():
    # Start Left Camera
    left_camera = Camera()
    left_camera.open(0)
    left_camera.start()

    # Start Right Camera
    right_camera = Camera()
    right_camera.open(1)
    right_camera.start()

    # Iteration ratio
    i = 1

    cv2.namedWindow("IMX219-83 Stereo camera", cv2.WINDOW_AUTOSIZE)

    while cv2.getWindowProperty("IMX219-83 Stereo camera", 0) >= 0:

        # Read Images
        _, left_image = left_camera.read()
        _, right_image = right_camera.read()

        # Find the chessboard corners
        retl, cornersl = cv2.findChessboardCorners(left_image, (nx, ny), None)
        retr, cornersr = cv2.findChessboardCorners(right_image, (nx, ny), None)

        # This also acts as
        keycode = cv2.waitKey(30) & 0xFF
        # Stop the program on the ESC key
        if keycode == 27:
            break

        # If found corners, draw corners and check to add Calibration info
        if retl is True & retr is True:
            # Draw and display the corners
            cv2.drawChessboardCorners(left_image, (nx, ny), cornersl, retl)
            cv2.drawChessboardCorners(right_image, (nx, ny), cornersr, retr)

            # Add points into Calibration info when user press 'c'
            if keycode == ord('c'):
                print("Add points from video capture (%d)" % i)

                # Convert to grayscale
                grayl = cv2.cvtColor(left_image, cv2.COLOR_RGB2GRAY)
                grayr = cv2.cvtColor(right_image, cv2.COLOR_RGB2GRAY)

                # Add left points
                objpointsl.append(objp)
                cv2.cornerSubPix(grayl, cornersl, (11, 11), (-1, -1), criteria)
                imgpointsl.append(cornersl)

                # Add right points
                objpointsr.append(objp)
                cv2.cornerSubPix(grayr, cornersr, (11, 11), (-1, -1), criteria)
                imgpointsr.append(cornersr)

                i += 1

        # Save all calibration data into pickle format
        if keycode == ord('s') and i > 1:
            retval, cm1, dc1, cm2, dc2, r, t, e, f = cv2.stereoCalibrate(objpointsl, imgpointsl, imgpointsr,
                                                                         (1280, 720), None, None, None, None)
            # Save the camera calibration results.
            calib_result_pickle = {
                "retval": retval,
                "cm1": cm1, "dc1": dc1,
                "cm2": cm2, "dc2": dc2,
                "r": r, "t": t, "e": e, "f": f
            }

            try:
                pickle.dump(calib_result_pickle, open("./camera/stereo_calib.p", "wb"))
                print("Calibration results saved\n")
            except RuntimeError:
                print("Unable to save Calibration results\n")

        # View calibration result
        if keycode == ord('v'):
            print("Unable to show Calibration results")

        camera_images = np.hstack((left_image, right_image))
        cv2.imshow("IMX219-83 Stereo camera", camera_images)

    # Stop Cameras and close all windows
    left_camera.stop()
    left_camera.release()
    right_camera.stop()
    right_camera.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()

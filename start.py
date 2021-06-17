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
# We use chessboard with 25mm square_size
objp = np.zeros((ny * nx, 3), np.float32)
objp[:, :2] = np.mgrid[0:ny, 0:nx].T.reshape(-1, 2)
objp = objp * 0.025

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
            height, width, channel = left_image.shape
            retval, cm1, dc1, cm2, dc2, r, t, e, f = cv2.stereoCalibrate(objpointsl, imgpointsl, imgpointsr,
                                                                         (width, height), None, None, None, None)
            print("Stereo calibration rms: ", retval)
            r1, r2, p1, p2, q, roi_left, roi_right = cv2.stereoRectify(
                cm1, dc1, cm2, dc2, (width, height), r, t,
                flags=cv2.CALIB_ZERO_DISPARITY, alpha=0.9
            )

            # Save the camera calibration results.
            calib_result_pickle = {
                "retval": retval,
                "cm1": cm1, "dc1": dc1,
                "cm2": cm2, "dc2": dc2,
                "r": r, "t": t, "e": e, "f": f,
                "r1": r1, "r2": r2, "p1": p1, "p2": p2, "q": q
            }

            try:
                pickle.dump(calib_result_pickle, open("./camera/stereo_calib.p", "wb"))
                print("Calibration results saved\n")
            except RuntimeError:
                print("Unable to save Calibration results\n")

        # View calibration result
        if keycode == ord('v'):
            try:
                calib_result_pickle = pickle.load(open("./camera/stereo_calib.p", "rb"))
                cm1 = calib_result_pickle["cm1"]
                cm2 = calib_result_pickle["cm2"]
                dc1 = calib_result_pickle["dc1"]
                dc2 = calib_result_pickle["dc2"]
                r = calib_result_pickle["r"]
                t = calib_result_pickle["t"]
                r1 = calib_result_pickle["r1"]
                p1 = calib_result_pickle["p1"]
                r2 = calib_result_pickle["r2"]
                p2 = calib_result_pickle["p2"]
                q = calib_result_pickle["q"]
            except RuntimeError:
                print("Unable to load Calibration coefficients")
                break

            # We use the shape for remap
            height, width, channel = left_image.shape

            # Undistortion and Rectification part!
            cv2.stereoRectify(cm1, dc1, cm2, dc2, (width, height), r, t, r1, r2, p1,
                              p2, q, alpha=-1, newImageSize=(0, 0))
            leftMapX, leftMapY = cv2.initUndistortRectifyMap(cm1, dc1, r1, p1, (width, height), cv2.CV_32FC1)
            left_image = cv2.remap(left_image, leftMapX, leftMapY, cv2.INTER_LINEAR, cv2.BORDER_CONSTANT)
            rightMapX, rightMapY = cv2.initUndistortRectifyMap(cm2, dc2, r2, p2, (width, height), cv2.CV_32FC1)
            right_image = cv2.remap(right_image, rightMapX, rightMapY, cv2.INTER_LINEAR, cv2.BORDER_CONSTANT)

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

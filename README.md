# Jetson-Nano-CSI-Stereo-Vision
## General Info
Calibration and Stereo Vision for <a href="https://developer.nvidia.com/embedded/jetson-nano-developer-kit">Jetson Nano B01</a> and <a href="https://www.waveshare.com/wiki/IMX219-83_Stereo_Camera">IMX219-83 Stereo camera</a>.<br><br>
![plot](./img/photo.jpg)<br>
## Requirements
Just install JetPack 4.5.1 using Jetson Nano Developer Kit <a href="https://developer.nvidia.com/jetson-nano-sd-card-image">SD Card Image</a>.
## Usage
Clone this repository and run start.py. If you connected everything as in the photo, then nothing needs to be changed.
```
$ git clone https://github.com/ukhov79/Jetson-Nano-CSI-Stereo-Vision
$ cd Jetson-Nano-CSI-Stereo-Vision
$ python3 start.py
```
To start Calibration print chessboard and press 'c'.<br><br>
<img src="./img/Calibration_ChessBoard_9x6.png" width="300" /><br>
To view the calibration results press 's'.<br>
Tap Esc to exit programm.<br>
The calibration data will be saved in /data directory.<br>
You can use Camera class in your project. 
## Example
Need to finish
## TODO
Upload tested solution
## References
https://github.com/JetsonHacksNano/CSI-Camera

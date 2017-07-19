This autpilot is based on the project by Sully Chen: https://github.com/SullyChen/Autopilot-TensorFlow

### 0. Requirements
- numpy (cp35): http://www.lfd.uci.edu/~gohlke/pythonlibs/#numpy
- scipy (cp35): http://www.lfd.uci.edu/~gohlke/pythonlibs/#scipy
- Python 3.5 (embeddable) in directory ETS2Autopilot/python (only for the windows batch-files)
- get-pip.py: https://pip.pypa.io/en/stable/installing/
- vJoy: http://vjoystick.sourceforge.net/site/index.php/download-a-install/download

### 1. Installation (commands in windows cmd and project directory)
- `python\python.exe get-pip.py`
- `python\python.exe -m pip install numpy-*.whl`
- `python\python.exe -m pip install scipy-*.whl`
- CPU-only: `python\python.exe -m pip install opencv-python pillow pygame tensorflow`
- GPU: `python\python.exe -m pip install opencv-python pillow pygame tensorflow-gpu`
- copy vJoyInterface.dll from vJoy installation directory to folder pyvjoy

#### GPU
Read here how to use your NVIDIA GPU for the neural network: 
https://www.tensorflow.org/install/install_windows#requirements_to_run_tensorflow_with_gpu_support

### 2. Configuration
edit settings.py:
- adjust the ids for your joystick/gamepad
- adjust GAME_WINDOW and IMAGE_FRONT

get button and axis ids:
- connect your joystick/gamepad
- run `python\python.exe gamepad_analyzer.py`
- enter the ID of joystick/gamepad
- press buttons or move joysticks to get the IDs

### 3. How to use
1. collect as much data as you can by executing `start_recording.bat`
2. train your autopilot with `start_training.bat`
3. let the computer do the steering with `start_autopilot.bat`

### DEMOS

- \#1 https://www.youtube.com/watch?v=UKqEOmF2N2Q
- \#2 https://www.youtube.com/watch?v=4pzAbGT0PQg


### Problems
If you get an error message like this `error: [Errno 2] No such file or directory: '[..]\ETS2Autopilot-master\python\python35.zip\lib2to3\Grammar.txt'` during installing python modules, follow these steps:
- go to the directory `python\`
- rename the file `python35.zip` to something like `python35x.zip`
- extract the content of the renamed ZIP-file to a **folder** named `python35.zip`

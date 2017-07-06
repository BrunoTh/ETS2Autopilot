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
- `pyhton\python.exe -m pip instal scipy-*.whl`
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

### DEMOS

- \#1 https://www.youtube.com/watch?v=UKqEOmF2N2Q
- \#2 https://www.youtube.com/watch?v=4pzAbGT0PQg

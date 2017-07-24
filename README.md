This autpilot is based on the project by Sully Chen: https://github.com/SullyChen/Autopilot-TensorFlow

### Get started
Please visit https://www.ets2autopilot.com/ for instructions.

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

# MTi Visualization

This repo visualize the quaternion and inversed quaternion from the same MTi sensor.


## Install

Create virtual environment:
```
python -m venv venv
```
Activate the env:
```
venv\Scripts\activate
```
Install the requirements
```
pip install -r requirements.txt
```
Install the xsensdeviceapi lib, located at your MT Software Suite, and install the one that fits your python version.
```
python --version
```
here my version is python 3.8.10, then I install:
```
pip install xsensdeviceapi-2024.1.0-cp38-none-win_amd64.whl
```

## Run
```
python server.py
```

Then open the Chrome Browser, go to:
```
http://127.0.0.1:5000
```

You should see two cubes and its euler angles, the left one is the original quaternion, the right one is the reversed quaternion.


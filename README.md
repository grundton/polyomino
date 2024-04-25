# Polyomino

# Grain Bau
![Title picture. A tetromino covers fiducial markers on a grid surrounded by other polyominoes.](img/Title.png "Polyominos on the AprilTag grid").

The polyomino interface is a pitch lattice exploration interface combining object detection with haptic elements. It uses fiducial markers, the   [AprilTag markers](https://april.eecs.umich.edu/software/apriltag), to represent a square pitch lattice. Covering these markers, intended to be done using polyominos, one can send the pitch information of the covered cells to a Csound script for sonification.

## Installation 
Download the zip file or clone the repository
### Python
Before installing any dependencies, I recommend using a seperate virtual environment
```
conda create -n polyomino python=3.11
```
Now activate the new environment
```
conda activate polyomino
```
To install the required libraries for cloud hands, simply open a terminal at the root directory and execute
```
pip install -r requirements.txt
```
### Csound


## Play 
First activate the python environment.
```
conda activate polyomino
```

To start the python script:
```
python detect.py
```

In a new terminal window, start the csound script. Make sure to find out which -odac option (line 3) you want to use. If you start the script once without the python script running, you can see your options.
```
csound polyomino.csd
```
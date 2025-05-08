# Ground Snapper
![Maya Version](https://img.shields.io/badge/Maya-2020%2B-informational)
![License](https://img.shields.io/badge/License-MIT-green)

A Maya tool to snap selected object to the ground. 

![Maya Keyframe Randomizer](screenshots/gui_example.png)

## Features

- snap object position to closest Ray casted point on world -y
- snap object to hit_face normal slope, maintaining the original direction
- add custom offset from ground, to fine tune intersection
- can use the object bounding box as offset distance 
- practical GUI


## Installation

1. Download `mt_snap_to_ground.py` from this folder
2. Place it in your Maya scripts directory:
   - Windows: `Documents\maya\scripts\`
   - macOS: `~/Library/Preferences/Autodesk/maya/scripts/`
   - Linux: `~/maya/scripts/`
3. To use in Maya, you can chose to run it: 
   1. without GUI
      ```python
      import mt_snap_to_ground as mtsg
      snapper = mtsg.GroundSnapper()
      snapper.updateGround("Ground") # <- add here the name of your ground for quick interaction
      snapper.doIt()

   2. with GUI
      ```python
      import mt_snap_to_ground as mtsg
      snapperUi = mtsg.GroundSnapperGUI()
      snapperUi.show()


## TODO:
Please remeber this is the very first working version of the tool, so not all cases are covered.
In particular, the way the alignment to slope is implemented covers only one case. 
I will cover all different scenarios in the future. 


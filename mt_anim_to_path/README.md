# MT Animation Tools

![Maya Version](https://img.shields.io/badge/Maya-2020%2B-informational)
![License](https://img.shields.io/badge/License-MIT-green)

A collection of Maya animation utilities designed to streamline the animation workflow.

## Tools Included

### MT Animation to Path

Converts keyframe animation to smooth, editable motion paths, making it easier to refine complex animations.

![Animation to Path Tool](https://via.placeholder.com/600x300?text=Animation+to+Path+Tool)

### MT Keyframe Randomizer

Adds controlled randomness to keyframe values and timing, creating more organic and natural animation.

## Installation

1. Clone or download this repository
2. Copy the tool files to your Maya scripts directory:
   - Windows: `Documents\maya\scripts`
   - macOS: `~/Library/Preferences/Autodesk/maya/scripts`
   - Linux: `~/maya/scripts`

## Usage

### Animation to Path

```python
import mt_anim_to_path as mta
mta.show_gui()
```

1. Select the object with keyframe animation
2. Set sample rate (higher value = more detailed path)
3. Define the frame range
4. Click "Do it!" to convert the animation

### Keyframe Randomizer

```python
import mt_keyframe_randomizer as mtk
mtk.show_gui()
```

1. Select objects with keyframes
2. Adjust value and time randomization settings
3. Apply changes immediately with the Dynamic Settings, or use Batch Settings for more control

## Features

- Animation to Path
  - Convert complex keyframe animation to editable curves
  - Customizable sampling rate
  - Maintains proper orientation along path
  - Works with any animated node

- Keyframe Randomizer
  - Add controlled variation to keyframe values
  - Randomize keyframe timing
  - Immediate or batch processing options
  - Perfect for secondary motion

## Requirements

- Maya 2020 or higher

## License

This project is licensed under the MIT License.

---

Created by LostFocusRemedies
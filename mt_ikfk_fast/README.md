# IK/FK Fast Switcher
![Maya Version](https://img.shields.io/badge/Maya-2020%2B-informational)
![License](https://img.shields.io/badge/License-MIT-green)

A Maya tool that provides fast IK/FK switching for character rigs. This headless tool allows you to quickly toggle between IK and FK modes for arms and legs, making character animation workflow more efficient.

## Features

- **Fast IK/FK Switching**: Instantly switch between IK and FK modes
- **Automatic Position Matching**: Seamlessly matches positions and rotations when switching
- **Smart Control Detection**: Automatically detects arm and leg controls based on selection
- **Namespace Support**: Works with namespaced rigs
- **Pole Vector Calculation**: Intelligent pole vector positioning for natural IK poses
- **Headless Operation**: Designed for hotkeys, shelf buttons, or marking menus
- **Customizable Setup**: Easy configuration for different rig naming conventions

## Supported Limbs

- **Arms**: Shoulder, elbow, hand controls with pole vector
- **Legs**: Hip, knee, ankle controls with pole vector
- **Extensible**: Can be adapted for other 3-joint limbs (tail, tentacles, etc.)

## Installation

1. Download the entire `mt_ikfk_fast` folder
2. Place it in your Maya scripts directory:
   - Windows: `Documents\maya\scripts\`
   - macOS: `~/Library/Preferences/Autodesk/maya/scripts/`
   - Linux: `~/maya/scripts/`

## Usage

### Basic Usage
```python
import mt_ikfk_fast.ik_fk_fast as ikfk
ikfk.main()
```

### Advanced Usage
```python
import mt_ikfk_fast.ik_fk_fast as ikfk

# With options
ikfk.main(rounded=True, preserve_selection=False)
```

### Parameters
- `rounded` (bool): Round the IK/FK switch attribute value (default: True)
- `preserve_selection` (bool): Keep current selection after switching (default: False)

### Workflow
1. Select any IK or FK control from an arm or leg
2. Run the script (via hotkey, shelf button, etc.)
3. The tool automatically:
   - Detects if it's an arm or leg control
   - Determines current IK/FK state
   - Switches to the opposite mode
   - Matches positions and orientations
   - Selects the appropriate control for the new mode

## Configuration

The tool uses configuration files that can be customized for your rig:

### Control Setup
Edit `_config.py` to match your rig's naming convention:

```python
ARM_SETUP = {
    "FK_end": "handFk_000_CTL",
    "FK_start": "shoulderFk_000_CTL", 
    "FK_mid": "elbowFk_000_CTL",
    "IK_end": "handIk_000_CTL",
    "IK_pv": "armPoleVector_000_CTL",
    "interface_ctl": "armIkFk_000_CTL",
    # ... additional controls
}
```

### Control Tags
Modify the control detection tags to match your naming:

```python
ARM_CONTROLS_TAGS = frozenset({
    "shoulder", "elbow", "hand", "armPoleVector", "armIkFk"
    # ... additional tags
})
```

## Requirements

- Maya 2020 or later
- Character rig with IK/FK setup
- Controls following left/right naming convention (l_/r_ prefixes)

## Hotkey Setup

To assign to a hotkey in Maya:

1. Go to Windows > Settings/Preferences > Hotkey Editor
2. Create a new Runtime Command:
   ```python
   import mt_ikfk_fast.ik_fk_fast as ikfk
   ikfk.main()
   ```
3. Assign your preferred hotkey

## Notes

- The tool expects controls to have `l_` or `r_` prefixes for left and right sides
- Supports namespaced rigs automatically
- Designed for production use with complex character rigs
- Can be easily extended for additional limb types

## Troubleshooting

- **"No selection found"**: Make sure you have an IK or FK control selected
- **"Selection does not contain a valid side prefix"**: Ensure your controls use `l_` or `r_` prefixes
- **"Selection does not match any IK/FK setup"**: The selected control isn't recognized - check your control tags configuration
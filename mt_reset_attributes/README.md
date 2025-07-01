# Renamer
![Maya Version](https://img.shields.io/badge/Maya-2020%2B-informational)
![License](https://img.shields.io/badge/License-MIT-green)

An animation tool for maya that'll help you with resetting channels of selected control to their default value.

Please note that often the default value will match with value 0.0, but not always. The script is smart enough to reach for the default value, which could be different from 0.0! 

## Features

- reset translation, rotation, scale, and user defined attributes
- if attributes are selected in the channelbox, it'll reset only those

## Installation

1. Download `mt_reset_attributes.py` 
2. Place it in your Maya scripts directory:
   - Windows: `Documents\maya\scripts\`
   - macOS: `~/Library/Preferences/Autodesk/maya/scripts/`
   - Linux: `~/maya/scripts/`
3. To use in Maya, run:
   ```python
   import mt_reset_attributes as mtra
   mtr.main()
   ```

## Example of Usage, if you like Blender behaviour: 
You may assign to a Hotkey `ALT+G` the following, in order to reset only the translation: 
   ```python
   import mt_reset_attributes as mtra
   mtra.main(preserve_selection=False, translation=True, rotation=False, scale=False, custom_attributes=False)
   ```

By default it will try to reset every attribute, unless attributes are selected in the channelbox, then it'll will only try to reset those selected. 
But yeah, you may take something nice from blender and bring it on to maya, plus this one can also be configured to work only on custom_attributes, so yeah, it's even arguably more advanced than the blender one, as far as I know. 

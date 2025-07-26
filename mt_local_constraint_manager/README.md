# Local Constraint Manager
![Maya Version](https://img.shields.io/badge/Maya-2020%2B-informational)
![License](https://img.shields.io/badge/License-MIT-green)

A Maya tool for managing local constraints in animation scenes. Designed for animators to efficiently organize, inspect, and control constraints that belong to the current scene (non-referenced constraints).

## Overview

The Local Constraint Manager provides a centralized interface for handling constraints created by animators in their local scenes. Unlike referenced constraints that come from rigs or other referenced files, local constraints are those created during the animation process and need to be managed independently. This tool helps animators quickly identify constraint relationships, select drivers and driven objects, and clean up unnecessary constraints.

## Features

- View all local (non-referenced) constraints in the scene
- Inspect constraint connections showing driver and driven relationships
- Select drivers and driven objects directly from the interface
- Delete unwanted constraints efficiently
- Real-time constraint list updates
- Clear visual representation of constraint hierarchies
- Automatic filtering of referenced constraints

## Requirements

- Maya (tested with Maya 2020+)
- PyMEL

## Installation

1. Download the entire `mt_local_constraint_manager` folder
2. Place it in your Maya scripts directory:
   - Windows: `C:\Users\<username>\Documents\maya\scripts`
   - macOS: `~/Library/Preferences/Autodesk/maya/scripts`
   - Linux: `~/maya/scripts`

## Usage

### Via UI

```python
# First time use:
from mt_local_constraint_manager.constraint_toolkit_gui import ConstraintToolkitGUI
ConstraintToolkitGUI()

# While developing:
import mt_local_constraint_manager.constraint_toolkit_gui as ct_gui
from imp import reload
reload(ct_gui)
ct_gui.ConstraintToolkitGUI()
```

### Via Python Script

```python
import mt_local_constraint_manager.constraint_toolkit as ct

# Get all local constraints
constraints = ct.get_all_constraints(local=True)

# Get connections for a specific constraint
driver, driven = ct.get_constraint_connections("myConstraint1")
print(f"Driver: {driver}, Driven: {driven}")
```

## UI Controls

- **Constraint List**: Displays all local constraints in the scene with multi-selection support
- **Constraint Connections**: Shows the relationship between driver and driven objects for selected constraints
- **Update List**: Refreshes the constraint list to reflect current scene state
- **Select Driver**: Selects the driving object(s) of the chosen constraint(s)
- **Select Driven**: Selects the driven object(s) of the chosen constraint(s)
- **Delete Driver**: Removes the selected constraint(s) from the scene

## Core Functions

### `get_all_constraints(local=True)`
Returns a list of all constraint nodes in the Maya scene.
- `local` (bool): If True, returns only non-referenced constraints (default: True)

### `get_constraint_connections(constraint_name)`
Returns the driver and driven objects for a specific constraint.
- `constraint_name` (string): Name of the constraint to analyze
- Returns: `[driver, [driven_objects]]`

## How It Works

The tool analyzes Maya's constraint network by:
1. Querying all constraint nodes in the scene
2. Filtering out referenced constraints to focus on local ones
3. Examining constraint connections to identify driver-driven relationships
4. Providing an intuitive interface to interact with these relationships

Local constraints are identified by checking the `isNodeReferenced` property, ensuring that only constraints created in the current scene are managed.

## Workflow Integration

This tool is particularly useful for:
- **Animation Cleanup**: Removing temporary constraints after animation blocking
- **Constraint Debugging**: Understanding complex constraint hierarchies
- **Scene Organization**: Managing constraints in scenes with multiple animated objects
- **Handoff Preparation**: Cleaning up animator-created constraints before final delivery

## Notes

- The tool automatically excludes referenced constraints to prevent accidental modification of rig constraints
- Driver selection works with multiple constraints simultaneously
- The constraint connections display updates automatically when selecting different constraints
- Deleted constraints are immediately removed from the list without requiring manual refresh

## Technical Details

- Uses Maya's constraint query system for reliable constraint detection
- Leverages `targetParentMatrix` connections to identify drivers
- Filters constraint connections to exclude other constraints from driven object lists
- Implements comprehensive logging for debugging and user feedback

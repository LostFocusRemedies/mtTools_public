"""
This script provides a fast IK/FK switching mechanism for character rigs in Maya.
You can use it to quickly toggle between IK and FK modes for arms and legs,
making it easier to animate characters with complex rigs.

the provided setup is of the current production I'm on. 
It's designed for you to adapt to your own rigging setup.

The tool is designed to work headless, assigned to either a hotkey, a shelf button, or marking menu, or 
wathever your heart desires.

Usage:
    import mt_ikfk_fast as ikfk
    ikfk.main(rounded=True, preserve_selection=False)
    
"""

import maya.cmds as cm
import maya.api.OpenMaya as om2
from . import _config as _config

IKStatus = 1
FKStatus = 0


def get_selection_info() -> tuple:
    """
    Get the selected control and its namespace and side.
    returns:
        - The selected control name (str)
    """
    sel = cm.ls(sl=True)
    if not sel:
        cm.error("Error: No selection found. Please select an IK/FK control.")
        return None, None, None
    namespace, _, ctl = sel[0].partition(":")
    ctl = ctl or sel[0]  # Handle case where no namespace is present

    if ctl.startswith("r_"):
        side = "r_"
    elif ctl.startswith("l_"):
        side = "l_"
    else:
        cm.error("Error: Selection does not contain a valid side prefix (r_ or l_).")
        return None, None, None

    return sel[0], namespace, side


def format_setup(base_setup: dict, namespace:str, side:str) -> dict:
    """
    Formats the base setup dictionary with the given namespace and side.
    Args:
        base_setup (dict): The base setup dictionary containing control names.
        namespace (str): The namespace of the character.
        side (str): The side of the character (e.g., "l_" or "r_").
    """
    prefix = f"{namespace}:{side}" if namespace else side
    return {key: f"{prefix}{value}" for key, value in base_setup.items()}


def fk_to_ik(setup: dict, fresh_start:bool=True):
    """
    Convert FK controls to IK controls.
    This function sets the IK end control to the FK end control's position and orientation,
    and calculates the pole vector position based on the FK mid control.
    Args:
        setup (dict): A dictionary containing the setup for the IK/FK controls.
        fresh_start (bool): If True, it resets the attributes of the IK controls to their default values.
    """
    
    if fresh_start:
        reset_attrs = [
            "translateX", "translateY", "translateZ",
            "rotateX", "rotateY", "rotateZ",
            "scaleX", "scaleY", "scaleZ"
        ]
        for attr in reset_attrs:
            value = 1 if "scale" in attr else 0
            cm.setAttr(f"{setup['IK_end']}.{attr}",   value)
            try:
                cm.setAttr(f"{setup['IK_pv']}.{attr}",   value)
            except:
                continue  # IK_pv might not have all attributes
    
    
    if cm.getAttr(f"{setup['IK_pv']}.Lock") > 0.5:
        cm.warning("Warning: Pole vector control is locked")
        distance_factor = 1.0
    else:
        distance_factor = 2.0

    fk_end_raw_matrix = cm.xform(setup["FK_end"], ws=True, q=True, matrix=True)
    fk_end_pos = om2.MVector(fk_end_raw_matrix[12], fk_end_raw_matrix[13], fk_end_raw_matrix[14])
    fk_mid_raw = cm.xform(setup["FK_mid"], ws=True, q=True, t=True)
    fk_mid_pos = om2.MVector(fk_mid_raw[0], fk_mid_raw[1], fk_mid_raw[2])
    fk_start_raw = cm.xform(setup["FK_start"], ws=True, q=True, t=True)
    fk_start_pos = om2.MVector(fk_start_raw[0], fk_start_raw[1], fk_start_raw[2])

    cm.xform(setup["IK_end"], ws=True, matrix=fk_end_raw_matrix)

    mid_point = (fk_end_pos + fk_start_pos) / 2
    pv_origin = fk_mid_pos - mid_point
    pm_raw = pv_origin * distance_factor
    pv_pos = mid_point + pm_raw
    cm.xform(setup["IK_pv"], ws=True, t=(pv_pos.x, pv_pos.y, pv_pos.z))


def ik_to_fk(setup, fresh_start=True, pos=True, rot=True):
    """
    Convert IK controls to FK controls.
    This function sets the FK controls to the position and orientation of the IK controls.
    Args:
        setup (dict): A dictionary containing the setup for the IK/FK controls.
        fresh_start (bool): If True, it resets the attributes of the FK controls to their default values.
        pos (bool): If True, it sets the position of the FK controls.
        rot (bool): If True, it sets the rotation of the FK controls.
    """
    if fresh_start:
        reset_attrs = [
            "translateX", "translateY", "translateZ",
            "rotateX", "rotateY", "rotateZ",
            "scaleX", "scaleY", "scaleZ"
        ]
        for attr in reset_attrs:
            value = 1 if "scale" in attr else 0
            cm.setAttr(f"{setup['FK_end']}.{attr}",   value)
            cm.setAttr(f"{setup['FK_mid']}.{attr}",   value)
            cm.setAttr(f"{setup['FK_start']}.{attr}", value)
        
    cm.matchTransform(setup["FK_start"], setup["IK_start"], pos=pos, rot=rot)
    cm.matchTransform(setup["FK_mid"],   setup["IK_mid"],   pos=pos, rot=rot)
    cm.matchTransform(setup["FK_end"],   setup["IK_end"],   pos=pos, rot=rot)


def main(rounded=True, preserve_selection=False):
    """
    main function to switch between IK and FK.
    It checks the current state of the IK/FK switch and performs the appropriate conversion.
    Args:
        rounded (bool): If True, it rounds the IK/FK switch attribute value.
        preserve_selection (bool): If True, it preserves the current selection after the switch.
    """
    sel, namespace, side = get_selection_info()
    if not sel:
        cm.error("No valid selection found.")
        return

    if any(a in sel.lower() for a in _config.ARM_CONTROLS_TAGS):
        setup = format_setup(_config.ARM_SETUP, namespace, side)
    elif any(l in sel.lower() for l in _config.LEG_CONTROLS_TAGS):
        setup = format_setup(_config.LEG_SETUP, namespace, side)
    else:
        cm.warning("Error: Selection does not match any IK/FK setup.")
        return

    switch_attribute = f"{setup['interface_ctl']}.Ik"
    if rounded:
        current_state = round(cm.getAttr(switch_attribute))
    else:
        current_state = cm.getAttr(switch_attribute)

    if current_state == FKStatus:
        fk_to_ik(setup)
        cm.setAttr(switch_attribute, IKStatus)
        if preserve_selection:
            cm.select(sel)
        else:
            cm.select(f"{setup['IK_end']}")
    elif current_state == IKStatus:
        ik_to_fk(setup)
        cm.setAttr(switch_attribute, FKStatus)
        if preserve_selection:
            cm.select(sel)
        else:
            cm.select(f"{setup['FK_end']}")
    else:
        cm.warning("Error: IK/FK status not recognized")
        return

"""
mt_keyframe_randomizer.py

A Maya tool that allows animators to add randomness to selected keyframes.
Can randomize both keyframe values and timing to create more organic animations.

Usage:
    # As a standalone script
    import mt_keyframe_randomizer as mtk
    
    # When used as part of mtTools_public collection
    import mtTools_public.mt_keyframe_randomizer.mt_keyframe_randomizer as mtk
    
    # For command line usage
    mtk.random_value(-0.5, 0.5)  # Add random offsets between -0.5 and 0.5 to keyframe values
    mtk.random_time(-4, 4)       # Add random offsets between -4 and 4 to keyframe timing
    
    # Or launch the GUI
    mtk.show_gui()

Author: LostFocusRemedies
"""

import maya.cmds as cm
import pymel.core as pm
import random
from typing import Callable, Dict, List, Sequence, Tuple

__all__ = [
    'random_value', 'random_time', 'show_gui', 'randomValue', 'randomTime', 'RandomGui'
]
__version__ = '1.1.0'


def _gather_anim_curves(selection: Sequence[str]) -> List[str]:
    """Return a list of unique animation curves connected to the selected nodes."""
    curves = set()
    for obj in selection:
        try:
            obj_curves = cm.keyframe(obj, q=True, name=True) or []
            for c in obj_curves:
                curves.add(c)
        except Exception:
            # Skip problematic objects but continue overall
            continue
    return list(curves)


def _list_key_times(curve: str, selected_only: bool = True) -> List[float]:
    """Return key times for curve, prefer selected keys, fallback to all."""
    times = cm.keyframe(curve, q=True, sl=selected_only, timeChange=True) or []
    if not times and selected_only:
        times = cm.keyframe(curve, q=True, timeChange=True) or []
    # Ensure sorted for deterministic processing
    return sorted(times)


def random_value(random_min: float, random_max: float, selected_only: bool = True, verbose: bool = True) -> Dict[str, int]:
    """Add random offset (uniform) to the values of keyframes.

    Args:
        random_min: Minimum random offset (inclusive)
        random_max: Maximum random offset (inclusive)
        selected_only: If True, only affect currently selected keys when some are selected.
        verbose: If True, print a summary.

    Returns:
        dict with keys: curves, keys_changed
    """
    sel = cm.ls(sl=True)
    if not sel:
        cm.warning("Nothing selected. Please select an object with animation.")
        return {'curves': 0, 'keys_changed': 0}

    anim_curves = _gather_anim_curves(sel)
    if not anim_curves:
        cm.warning("No animation curves found on selection.")
        return {'curves': 0, 'keys_changed': 0}

    keys_changed = 0
    cm.undoInfo(openChunk=True)
    try:
        for ac in anim_curves:
            key_times = _list_key_times(ac, selected_only=selected_only)
            if not key_times:
                continue
            for kt in key_times:
                # Single command per key; still unavoidable but minimal queries.
                offset = random.uniform(random_min, random_max)
                cm.keyframe(ac, valueChange=offset, relative=True, time=(kt, kt))
                keys_changed += 1
    except Exception as e:
        cm.warning(f"Error in random_value: {e}")
    finally:
        cm.undoInfo(closeChunk=True)

    if verbose:
        print(f"Randomized {keys_changed} keys on {len(anim_curves)} curves (value offsets between {random_min} and {random_max}).")
    return {'curves': len(anim_curves), 'keys_changed': keys_changed}


def random_time(random_min: int, random_max: int, selected_only: bool = True, collision_strategy: str = 'shift', verbose: bool = True) -> Dict[str, int]:
    """Add random offset to the timing of keyframes with collision avoidance.

    Args:
        random_min: Minimum random frame offset
        random_max: Maximum random frame offset
        selected_only: If True only act on selected keys (fallback to all if none selected per curve)
        collision_strategy: 'shift' (increment forward until free) or 'ignore' (allow overlaps)
        verbose: Print summary if True

    Returns:
        dict with keys: curves, keys_changed
    """
    if random_min > random_max:
        random_min, random_max = random_max, random_min

    sel = cm.ls(sl=True)
    if not sel:
        cm.warning("Nothing selected. Please select an object with animation.")
        return {'curves': 0, 'keys_changed': 0}

    anim_curves = _gather_anim_curves(sel)
    if not anim_curves:
        cm.warning("No animation curves found on selection.")
        return {'curves': 0, 'keys_changed': 0}

    keys_changed = 0
    cm.undoInfo(openChunk=True)
    try:
        for ac in anim_curves:
            key_times = _list_key_times(ac, selected_only=selected_only)
            if not key_times:
                continue
            # Map original time to new time
            used_new_times = set(key_times)  # start with existing to reduce chance of collision logic bug
            time_pairs: List[Tuple[float, float]] = []  # (original, new)
            for ot in key_times:
                delta = int(round(random.uniform(random_min, random_max)))
                if delta == 0:
                    # Keep same
                    new_time = ot
                else:
                    new_time = ot + delta
                    if collision_strategy == 'shift':
                        # If occupied, push forward until free
                        while new_time in used_new_times:
                            new_time += 1  # simple forward shift
                used_new_times.add(new_time)
                time_pairs.append((ot, new_time))

            # Apply moves: sort by whether new_time > orig to minimize chain interactions (not critical here)
            for orig, new in time_pairs:
                if new == orig:
                    continue
                delta = new - orig
                cm.keyframe(ac, time=(orig, orig), timeChange=delta, relative=True)
                keys_changed += 1
    except Exception as e:
        cm.warning(f"Error in random_time: {e}")
    finally:
        cm.undoInfo(closeChunk=True)

    if verbose:
        print(f"Randomized timing of {keys_changed} keys on {len(anim_curves)} curves (time offsets between {random_min} and {random_max}).")
    return {'curves': len(anim_curves), 'keys_changed': keys_changed}

class RandomGui(object):
    """GUI for the keyframe randomization tool."""
    def __init__(self):
        # Dynamic sliders (immediate application)
        self.value_slider_dynamic = None
        self.frame_slider_dynamic = None
        # Batch sliders (applied on button)
        self.value_slider_batch = None
        self.frame_slider_batch = None
        self.value_check = None
        self.frame_check = None
        self.randomize_button = None

    def randomize(self, *args):
        """Apply randomization based on current batch GUI settings."""
        try:
            if self.value_check.getValue():
                val = self.value_slider_batch.getValue()
                random_value(-val, val)
            if self.frame_check.getValue():
                frame = self.frame_slider_batch.getValue()
                random_time(-frame, frame)
        except Exception as e:
            cm.warning(f"Error during randomization: {e}")

    def show(self):
        """
        Create and display the randomization GUI.
        """
        win_id = "mtRandomKeyframes"

        if pm.window(win_id, exists=True):
            pm.deleteUI(win_id)

        with pm.window(win_id, title=f"Keyframe Randomizer v{__version__}", height=400, width=300) as win: 
            with pm.columnLayout(rowSpacing=10, adj=True):
                pm.text(label="Select objects with keyframes and adjust settings below", align="center")
                pm.separator()
                
                with pm.frameLayout(label="Dynamic Settings", collapsable=True, collapse=False):
                    with pm.columnLayout(adj=True, rowSpacing=5):
                        pm.text(label="Apply changes immediately when moving sliders", align="left")
                        self.value_slider_dynamic = pm.floatSliderGrp(
                            label="Value", 
                            field=True, 
                            min=-10, 
                            max=10, 
                            value=0.5,
                            changeCommand=(lambda x: random_value(-x, x))
                        )
                        self.frame_slider_dynamic = pm.floatSliderGrp(
                            label="Time", 
                            field=True, 
                            min=-10, 
                            max=10, 
                            value=2,
                            changeCommand=(lambda x: random_time(-x, x))
                        )
                
                with pm.frameLayout(label="Batch Settings", collapsable=True, collapse=False):
                    with pm.columnLayout(adj=True, rowSpacing=5):
                        pm.text(label="Configure settings and click Randomize to apply", align="left")
                        
                        with pm.rowLayout(numberOfColumns=2, adjustableColumn=1, columnWidth2=(250, 50)):
                            self.value_slider_batch = pm.floatSliderGrp(
                                label="Value", 
                                field=True, 
                                min=-10, 
                                max=10, 
                                value=0.5
                            )
                            self.value_check = pm.checkBox(
                                label="", 
                                value=True, 
                                onCommand=lambda x: self.value_slider_batch.setEnable(True),
                                offCommand=lambda x: self.value_slider_batch.setEnable(False)
                            )

                        with pm.rowLayout(numberOfColumns=2, adjustableColumn=1, columnWidth2=(250, 50)):
                            self.frame_slider_batch = pm.floatSliderGrp(
                                label="Time", 
                                field=True, 
                                min=-10, 
                                max=10, 
                                value=2
                            )
                            self.frame_check = pm.checkBox(
                                label="", 
                                value=True, 
                                onCommand=lambda x: self.frame_slider_batch.setEnable(True),
                                offCommand=lambda x: self.frame_slider_batch.setEnable(False)
                            )
                    
                        pm.separator(height=10)
                        self.randomize_button = pm.button(
                            label="Randomize!", 
                            command=self.randomize, 
                            height=40
                        )
                
                pm.separator()
                pm.text(label=f"mtTools - Keyframe Randomizer v{__version__}", align="center")

        win.show()


def show_gui():
    """
    Function to create and show the randomization GUI.
    """
    randomizer = RandomGui()
    randomizer.show()


# For backward compatibility
randomValue = random_value
randomTime = random_time

# Execute this when run directly
if __name__ == "__main__":
    show_gui()
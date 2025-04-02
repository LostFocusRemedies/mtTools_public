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


def random_value(random_min, random_max):
    """
    Add random offset to the values of selected keyframes.
    
    Args:
        random_min (float): Minimum random value offset
        random_max (float): Maximum random value offset
    """
    try:
        sel = cm.ls(sl=True)
        if not sel:
            cm.warning("Nothing selected. Please select an object with animation.")
            return
            
        animCurves = cm.keyframe(q=True, name=True)
        if not animCurves:
            cm.warning("No animation curves found on selection.")
            return

        for ac in animCurves: 
            key_time = cm.keyframe(ac, q=True, sl=True, timeChange=True)
            if not key_time:
                key_time = cm.keyframe(ac, q=True, timeChange=True)
                
            for kt in key_time: 
                value_new = random.uniform(random_min, random_max)
                cm.keyframe(ac, valueChange=value_new, relative=True, time=(kt, kt))
                
        print(f"Successfully randomized values between {random_min} and {random_max}")
    except Exception as e:
        cm.warning(f"Error in random_value: {str(e)}")


def random_time(random_min, random_max):
    """
    Add random offset to the timing of selected keyframes.
    
    Args:
        random_min (float): Minimum random time offset (in frames)
        random_max (float): Maximum random time offset (in frames)
    """
    try:
        sel = cm.ls(sl=True)
        if not sel:
            cm.warning("Nothing selected. Please select an object with animation.")
            return
            
        animCurves = cm.keyframe(q=True, name=True)
        if not animCurves:
            cm.warning("No animation curves found on selection.")
            return

        for ac in animCurves: 
            key_time = cm.keyframe(ac, q=True, sl=True, timeChange=True)
            if not key_time:
                key_time = cm.keyframe(ac, q=True, timeChange=True)
                
            for kt in key_time: 
                value_new = int(random.uniform(random_min, random_max))
                cm.keyframe(ac, timeChange=value_new, relative=True, time=(kt, kt))
                
        print(f"Successfully randomized timing between {random_min} and {random_max} frames")
    except Exception as e:
        cm.warning(f"Error in random_time: {str(e)}")


class RandomGui(object):
    """
    GUI for the keyframe randomization tool.
    """
    def __init__(self):
        self.value_slider = None
        self.frame_slider = None
        self.value_check = None
        self.frame_check = None
        self.randomize_button = None

    def randomize(self, *args):
        """
        Apply randomization based on current GUI settings.
        """
        try:
            if self.value_check.getValue(): 
                val = self.value_slider.getValue()
                random_value(-val, val)
            if self.frame_check.getValue(): 
                frame = self.frame_slider.getValue()
                random_time(-frame, frame)
        except Exception as e:
            cm.warning(f"Error during randomization: {str(e)}")

    def show(self):
        """
        Create and display the randomization GUI.
        """
        win_id = "mtRandomKeyframes"

        if pm.window(win_id, exists=True):
            pm.deleteUI(win_id)

        with pm.window(win_id, title="Keyframe Randomizer", height=400, width=300) as win: 
            with pm.columnLayout(rowSpacing=10, adj=True):
                pm.text(label="Select objects with keyframes and adjust settings below", align="center")
                pm.separator()
                
                with pm.frameLayout(label="Dynamic Settings", collapsable=True, collapse=False):
                    with pm.columnLayout(adj=True, rowSpacing=5):
                        pm.text(label="Apply changes immediately when moving sliders", align="left")
                        self.value_slider = pm.floatSliderGrp(
                            label="Value", 
                            field=True, 
                            min=-10, 
                            max=10, 
                            value=0.5,
                            changeCommand=(lambda x: random_value(-x, x))
                        )
                        self.frame_slider = pm.floatSliderGrp(
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
                            self.value_slider = pm.floatSliderGrp(
                                label="Value", 
                                field=True, 
                                min=-10, 
                                max=10, 
                                value=0.5
                            )
                            self.value_check = pm.checkBox(
                                label="", 
                                value=True, 
                                onCommand=lambda x: self.value_slider.setEnable(True),
                                offCommand=lambda x: self.value_slider.setEnable(False)
                            )

                        with pm.rowLayout(numberOfColumns=2, adjustableColumn=1, columnWidth2=(250, 50)):
                            self.frame_slider = pm.floatSliderGrp(
                                label="Time", 
                                field=True, 
                                min=-10, 
                                max=10, 
                                value=2
                            )
                            self.frame_check = pm.checkBox(
                                label="", 
                                value=True, 
                                onCommand=lambda x: self.frame_slider.setEnable(True),
                                offCommand=lambda x: self.frame_slider.setEnable(False)
                            )
                    
                        pm.separator(height=10)
                        self.randomize_button = pm.button(
                            label="Randomize!", 
                            command=self.randomize, 
                            height=40
                        )
                
                pm.separator()
                pm.text(label="mtTools - Keyframe Randomizer v1.0", align="center")

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
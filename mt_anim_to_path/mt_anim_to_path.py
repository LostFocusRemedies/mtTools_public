"""
mt_anim_to_path.py

A Maya tool that converts keyframe animation to motion path animation.
This utility creates a smooth path from existing animation and applies
it as a motion path constraint, making animation paths more editable.

Usage:
    # As a standalone script
    import mt_anim_to_path as mta
    
    # When used as part of mtTools_public collection
    import mtTools_public.mt_anim_to_path.mt_anim_to_path as mta
    
    # Launch the GUI
    mta.show_gui()

Author: LostFocusRemedies
"""

from functools import wraps
import maya.cmds as cm
import pymel.core as pm


def undo_chunk(func):
    """
    Decorator to wrap a function in an undo chunk.
    This allows the entire operation to be undone with a single undo command.
    """
    @wraps(func)
    def inner(*args, **kwargs):
        cm.undoInfo(openChunk=True)
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            cm.undoInfo(closeChunk=True)
    return inner


class AnimToPathGUI:
    """
    GUI for the Animation to Path tool.
    """
    window_name = "mt_anim_to_path"

    def __init__(self):
        self.control = ""
        self.get_control()
        self.start_frame = cm.playbackOptions(q=True, min=True)
        self.end_frame = cm.playbackOptions(q=True, max=True)
        self.control_ui = None
        self.sample_ui = None
        self.start_frame_ui = None
        self.end_frame_ui = None

    def show(self):
        """
        Display the Animation to Path GUI window.
        """
        if cm.window(self.window_name, q=True, exists=True):
            cm.deleteUI(self.window_name)
        cm.window(self.window_name, title="Animation to Path", width=300, height=200)
        self.build_ui()
        cm.showWindow()

    def build_ui(self):
        """
        Build the user interface elements.
        """
        mh, mw = 12, 12
        grey = 0.25
        bgc = (grey, grey, grey)
        main = cm.frameLayout(label="Animation to Motion Path", labelAlign="center", marginWidth=mw, marginHeight=mh)
        cm.frameLayout(label="Selection Information", labelAlign="center", marginHeight=mh, marginWidth=mw, collapsable=True)
        cm.columnLayout(backgroundColor=bgc)
        self.control_ui = cm.textFieldButtonGrp(label="Control to convert:", text=self.control, buttonLabel="Get from selection", buttonCommand=self.update_control_button)
        self.sample_ui = cm.intSliderGrp(field=True, label="Sample animation:", value=15, minValue=5, maxValue=50)
        self.start_frame_ui = cm.floatFieldGrp(label="Start frame:", value1=self.start_frame)
        self.end_frame_ui = cm.floatFieldGrp(label="End frame:", value1=self.end_frame)
        cm.setParent(main)
        cm.button(label="Do it!", command=self.anim_to_path, height=30)
        
        # Add footer text
        cm.separator()
        cm.text(label="mtTools - Animation to Path v1.0", align="center")

    def get_control(self):
        """
        Get the currently selected control object.
        """
        if not cm.ls(sl=True):
            self.control = ""
        else:
            self.control = cm.ls(sl=True)[0]

    def update_control_button(self):
        """
        Update the control field with the current selection.
        """
        self.get_control()
        cm.textFieldButtonGrp(self.control_ui, e=True, text=self.control)

    @undo_chunk
    def anim_to_path(self, *args):
        """
        Convert keyframe animation to motion path animation.
        
        This function samples the position of an animated object over time,
        creates a curve through those sample points, and applies a motion
        path constraint.
        """
        try:
            # Validate input
            if not self.control:
                cm.warning("Please select a control object first")
                return False
                
            self.namespace = self.control.split(":")[0] if ":" in self.control else ""
            self.sample = cm.intSliderGrp(self.sample_ui, q=True, v=True)
            self.start_frame = cm.floatFieldGrp(self.start_frame_ui, q=True, v1=True)
            self.end_frame = cm.floatFieldGrp(self.end_frame_ui, q=True, v1=True)
            
            frame_increment = (self.end_frame - self.start_frame) // self.sample
            locators = []
            cur_frame = self.start_frame
            cm.currentTime(self.start_frame)

            # Sample animation by creating locators at intervals
            while cur_frame <= (self.end_frame + frame_increment):
                loc = cm.spaceLocator(n=self.control + "_mtPathLoc_" + str(int(cur_frame)))
                cm.matchTransform(loc[0], self.control)
                locators.append(loc[0])
                cur_frame += frame_increment
                cm.currentTime(cur_frame)

            # Collect world positions from locators
            curve_points = []
            for l in locators:
                each_shape = cm.listRelatives(l, shapes=True, path=True)[0]
                loc_linear_position = cm.getAttr("{}.worldPosition".format(each_shape))[0]
                curve_points.append(loc_linear_position)

            # Create curve through points
            curve_path = cm.curve(p=curve_points,
                                n=self.control + "_mtPathCrv"
                                )

            # Remove existing animation
            cm.select(self.control, r=True)
            cm.cutKey(time=(self.start_frame - 1000, self.end_frame + 1000))
            cm.delete(self.control, motionPaths=True, constraints=True)

            # Create motion path constraint
            cm.pathAnimation(self.control,
                            c=curve_path,
                            follow=True,
                            followAxis="z",
                            upAxis="y",
                            worldUpType="vector",
                            fractionMode=True,
                            startU=0.0,
                            startTimeU=self.start_frame,
                            endTimeU=self.end_frame
                            )
                            
            # Clean up locators
            cm.delete(locators)

            # Select control and return to start frame
            cm.select(self.control, replace=True)
            cm.currentTime(self.start_frame)

            # Reset control transformations
            ctl = pm.PyNode(self.control)
            ctl.tx.set(0)
            ctl.ty.set(0)
            ctl.tz.set(0)
            ctl.rx.set(0)
            ctl.ry.set(0)
            ctl.rz.set(0)
            
            print(f"Successfully converted animation to path for {self.control}")
            return True
            
        except Exception as e:
            cm.warning(f"Error in anim_to_path: {str(e)}")
            # Clean up if needed
            if 'locators' in locals() and locators:
                cm.delete(locators)
            return False


def show_gui():
    """
    Function to create and show the Animation to Path GUI.
    """
    anim_to_path_gui = AnimToPathGUI()
    anim_to_path_gui.show()


# Execute this when run directly
if __name__ == "__main__":
    show_gui()
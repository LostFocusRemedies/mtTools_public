"""
mt_snap_to_ground.py

A Maya script to snap and align objects to the ground.

GroundSnapper is a tool to snap a selected object(s) to a set Ground underneath.
At the moment the scripts assumes a direction straight down -Y, as it'll solve 90% of the use cases.
I may update the code in the future.

Usage:
# UI LESS, for your hotkey or shelfbutton, for quick interation
import mtTools_public.mt_snap_to_ground as mtsg
snapper = mtsg.GroundSnapper()
snapper.set_ground("Ground") # add here the name of your ground
snapper.doIt()

# GUI
import mtTools_public.mt_snap_to_ground.mt_snap_to_ground as mtsg
snapperUi = mtsg.GroundSnapperGUI()
snapperUi.show()



Known Issues:
- the alignment will work 90% of the cases, but if the Y-axis of the selected object is the same as the face normal Y-axis, then there likely will be issues.

"""

import pymel.core as pm
from pprint import pprint


class GroundSnapper:
    def __init__(self, *args, **kwargs):
        self.ground = None
        self.set_ground(ground="Ground")  # TO BE UPDATED!!!
        self.ray_direction = pm.dt.Vector(
            0, -1, 0
        )  # assumes the user wants to match straight down -Y
        self.align_rotation = True
        self.align_position = True
        self.use_bb = True # is the tY offset calculated using the Bounding Box? 
        self.offset = 0.0  # otherwise use a custom value. 

    def doIt(self, *args):
        selection = self.getSelectedObjects()
        for s in selection:
            self.rayCast(obj=s)

    def rayCast(self, obj, orient: bool = True, position: bool = True):
        ray_source = pm.dt.Point(pm.xform(obj, q=True, t=True, ws=True))

        hit_result, hit_points, hit_faces = self.ground_shape.intersect(
            raySource=ray_source,
            rayDirection=self.ray_direction,
            tolerance=1e-10,
            space="world",
        )  # to note that hit_points and hit_faces are always lists, hence the plural naming.

        # TODO: here i need to account for all cases where this will not work, so basically
        # if obj_up dot hit_up is 1 or very close to 1 (directions are too similar), 
        # i need to start the calculation using the forward axis.
        # same goes for the other two axis, need to build all the tests. 
        
        if hit_result: 
            obj_pos = obj.getTransformation()[3][:3]
            obj_side = obj.getTransformation()[0][:3]
            obj_up = pm.dt.Vector(obj.getTransformation()[1][:3])
            obj_forward = pm.dt.Vector(obj.getTransformation()[2][:3])

            hit_point = pm.dt.Vector(hit_points[0])

            hit_up = self.ground_shape.getPolygonNormal(hit_faces[0]).normal()
            hit_forward = obj_forward.normal()
            hit_side = hit_up.cross(hit_forward).normal()
            hit_up = hit_forward.cross(hit_side).normal()

            hit_matrix = [
                hit_side[0],
                hit_side[1],
                hit_side[2],
                0.0,
                hit_up[0],
                hit_up[1],
                hit_up[2],
                0.0,
                hit_forward[0],
                hit_forward[1],
                hit_forward[2],
                0.0,
                obj_pos[0],
                obj_pos[1],
                obj_pos[2],
                1.0,
            ]

            if self.align_rotation:
                obj.setMatrix(hit_matrix)
            if self.align_position:
                if self.use_bb: # update the offset to match the bottom of the bounding box
                    bb = obj.getBoundingBoxMin(space="object")
                    self.offset = abs(obj_pos[1] - bb[1]) 
                hit_point[1] += self.offset
                obj.setTranslation(vector=hit_point, space="world")

    # getselection with error handling
    def getSelectedObjects(self):
        selection = pm.selected()
        if not selection:
            pm.error("Nothing is selected, I need at least one object selected.")
            return False
        else:
            return selection

    def set_ground(self, ground):
        # check if it needs conversion to pynode.
        if isinstance(ground, str):
            self.ground = pm.PyNode(ground)
        else:  # here i should really check if it's a pynode and do more testing
            self.ground = ground
        self.ground_shape = self.ground.getShape()


class GroundSnapperGUI:
    def __init__(self):
        self.ground_object = None
        self.Snapper = GroundSnapper()

    def show(self):
        wind_id = "mtGroundSnapper"
        if pm.window(wind_id, q=True, exists=True):
            pm.deleteUI(wind_id)

        with pm.window(wind_id, title="Ground Snapper", width=300) as win:
            with pm.columnLayout(rowSpacing=10,adj=True,columnAttach=("both", 16),columnOffset=("both", 16),):
                pm.text(l="First assign the ground object, then select your objects and snap them to it.",align="left",)
                pm.separator()
                
                with pm.rowLayout(numberOfColumns=2, adjustableColumn=1, columnWidth2=(250, 50)):
                    self.ground_text = pm.textField(editable=False)
                    pm.button(label="Get Ground", command=self.set_ground)

                with pm.columnLayout():
                    self.align_rotation = pm.checkBox(label="Align to Slope",   value=True,changeCommand=self.set_settings)
                    self.align_position = pm.checkBox(label="Align Position",   value=True,changeCommand=self.set_settings)
                    
                    self.use_bb = pm.checkBox(label="Use Bounding Box", value=True, changeCommand=self.set_offset_settings)
                    with pm.rowLayout(numberOfColumns=2, adjustableColumn=1, columnWidth2=(50, 50)):
                        pm.text(label="Y offset: ")
                        self.offset_position = pm.floatField(value=0.0,changeCommand=self.set_offset_settings, enable=False)

                self.snap_btn = pm.button(label="Snap Selection to Ground",command=self.Snapper.doIt,height=40, enable=False,)

                # footer
                pm.separator()
                pm.text(label="mtTools - Ground Snapper v1.0", align="center")

    def set_settings(self, *args):
        self.Snapper.align_rotation = self.align_rotation.getValue()
        self.Snapper.align_position = self.align_position.getValue()
        
    def set_offset_settings(self, *args):
        use_bb = self.use_bb.getValue() # for readability
        self.Snapper.use_bb = use_bb
        self.offset_position.setEnable(not use_bb)
        if not use_bb: 
            self.Snapper.offset = self.offset_position.getValue()
        

    def set_ground(self, *args):
        # Get the selected object and set it as the ground
        selection = pm.selected()
        if not selection:
            pm.warning("Nothing selected. Please select a ground object.")
            return False

        self.Snapper.set_ground(ground=selection[0])
        self.ground_text.setText(str(selection[0]))
        self.snap_btn.setEnable(True)


# ================================================================================
# Development
# ================================================================================

if __name__ == "__main__":
    # doIt(ground="Ground")
    snapper = GroundSnapper()
    snapper.set_ground("Ground")
    snapper.doIt()


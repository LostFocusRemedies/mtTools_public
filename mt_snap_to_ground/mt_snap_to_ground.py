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

"""

import logging
from pprint import pprint
import pymel.core as pm

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class GroundSnapper:
    def __init__(self, *args, **kwargs):
        self.obj = None
        self.ground = None
        self.ground_shape = None
        self.down = pm.dt.Vector(0, -1, 0)
        self.up = pm.dt.Vector(0, 1, 0)
        self.align_rotation = True
        self.align_position = True
        self.use_bb = True  # is the tY offset calculated using the Bounding Box?
        self.user_offset = 0.0  # tY offset dictated by the user

    def do_it(self, *args):
        # TODO ! need to decouple the obj selection from the raycast execution
        selection = self.get_selected_objects()
        for s in selection:
            self.raycast(obj=s)

    def raycast(self, obj, orient: bool = True, position: bool = True):
        
        ray_source = obj.getTranslation(space="world")
                
        logger.debug(f"ray_source = {ray_source}")
        logger.debug(f"ray_direction = {self.down}")

        hit, hit_points, hit_faces = self.ground_shape.intersect(
            raySource=ray_source,
            rayDirection=self.down,
            tolerance=1e-10,
            space="world",
        )

        if not hit:
            logger.warning("No points are projecting to ground.")
            return False

        # definition of what we need to construct the new matrix
        projected_matrix = pm.dt.TransformationMatrix() # the containing matrix
        obj_orient_corrected = pm.dt.EulerRotation(0, obj.getRotation().y, 0) # we are only interested in the direction of the obj, represented by rotY
        
        hit_normal = self.ground_shape.getPolygonNormal(hit_faces[0]) # get the normal of the hit face
        hit_normal = pm.dt.Vector(hit_normal)*self.ground.getMatrix() # ensure we're getting it in world space
        hit_normal.normalize() # ensure it's a direction
        
        angle = pm.dt.Quaternion(self.up, hit_normal) # angle between Y and the normal 
        if self.align_rotation:
            projected_rotation = obj_orient_corrected.asQuaternion() * angle
        else: 
            projected_rotation = obj.getRotation()
            
        if self.align_position: 
            # Always use ground hit point for alignment
            projected_position = hit_points[0]
            if self.use_bb:
                projected_position += self.get_offset_from_bottom(obj=obj, ray_source=hit_points[0])
            projected_position += pm.dt.Vector(0, self.user_offset, 0)
        else: 
            # Keep original position
            projected_position = obj.getTranslation(space="world")    
                        
        projected_scale = obj.getScale() # for consistency in readability
        
        projected_matrix.setTranslation(projected_position, space="world")
        projected_matrix.setRotation(projected_rotation)
        projected_matrix.setScale(projected_scale, space="world")
        
        logger.debug(f"matrix: {projected_matrix}")
        
        # finally apply the matrix
        # obj.setMatrix(projected_matrix)
        # Handle rigged objects with Offset Parent Matrix differently
        if obj.hasAttr('offsetParentMatrix'):
            # Use direct world space transforms for rigged controls
            if self.align_position:
                obj.setTranslation(projected_position, space="world")
            if self.align_rotation:
                obj.setRotation(projected_rotation, space="world")
        else:
            # For regular objects
            if obj.getParent():
                # Convert to parent space
                parent_inverse = obj.getParent().getMatrix().inverse()
                local_matrix = projected_matrix * parent_inverse
                obj.setMatrix(local_matrix)
            else:
                # No parent, use as is
                obj.setMatrix(projected_matrix)
                

    def get_offset_from_bottom(self, obj, ray_source, *args):
        obj_shape = obj.getShape()
        
        if isinstance(obj_shape, pm.nt.NurbsCurve): # if nurbs curve do nothing
            return(0)
        
        hit, hit_points, hit_faces = obj_shape.intersect(
            raySource=ray_source,
            rayDirection=self.up,
            tolerance=1e-10,
            space="world",
        )
        
        y = abs(hit_points[0].y - obj.getTranslation().y)
        
        return(pm.dt.Vector(0,y,0))


    # getselection with error handling
    def get_selected_objects(self):
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
                    self.align_rotation = pm.checkBox(label="Align to Slope",value=True,changeCommand=self.set_settings,)
                    self.align_position = pm.checkBox(label="Align Position",value=True,changeCommand=self.set_settings,)

                    self.use_bb = pm.checkBox(label="Use Bounding Box",value=True,changeCommand=self.set_offset_settings,)
                    with pm.rowLayout(numberOfColumns=2, adjustableColumn=1, columnWidth2=(50, 50)):
                        pm.text(label="Y offset: ")
                        self.offset_position = pm.floatField(value=0.0,changeCommand=self.set_offset_settings,enable=False,)

                self.snap_btn = pm.button(
                    label="Snap Selection to Ground",
                    command=self.Snapper.do_it,
                    height=40,
                    enable=False,
                )

                # footer
                pm.separator()
                pm.text(label="mtTools - Ground Snapper v1.1", align="center")

    def set_settings(self, *args):
        self.Snapper.align_rotation = self.align_rotation.getValue()
        self.Snapper.align_position = self.align_position.getValue()

    def set_offset_settings(self, *args):
        use_bb = self.use_bb.getValue()  # for readability
        self.Snapper.use_bb = use_bb
        self.offset_position.setEnable(not use_bb)
        if not use_bb:
            self.Snapper.user_offset = self.offset_position.getValue()

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

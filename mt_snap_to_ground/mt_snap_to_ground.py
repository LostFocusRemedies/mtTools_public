import pymel.core as pm
from pprint import pprint


def doIt(ground:str = "Ground"):
    ground = pm.PyNode(f"{ground}")
    groundShape = ground.getShape() # get the ground object from the user
    sel = pm.selected()
    if not sel: 
        pm.error("You gotta select something")
        return(False)
    
    ray_source = pm.dt.Point(
        pm.xform(sel, q=True, translation = True, worldSpace=True))
    
    ray_direction = pm.dt.Vector(0,-1,0)
    
    hit_result, hit_points, hit_faces = groundShape.intersect(
        raySource = ray_source, 
        rayDirection = ray_direction, 
        tolerance = 1e-10,
        space="world" 
    )
    
    if hit_result: 
        orient_to_normal(sel[0], groundShape, hit_faces[0], hit_points[0])
    else: 
        pm.warning("couldn't find any intersection!")

def move_to_point(obj, hit_point, hit_face, bounding_box=False):
    if bounding_box == True: 
        offset = obj.getTranslation() - obj.getBoundingBoxMin()
        hit_point = pm.dt.Vector(hit_point.x, hit_point.y + offset.y, hit_point.z)
    else: 
        hit_point = pm.dt.Vector(hit_point)
    obj.setTranslation(vector = hit_point,space = "world")
    
def orient_to_normal(obj, groundShape, hit_face_id, hit_point):
    obj_side    = obj.getTransformation()[0][:3]
    obj_up      = pm.dt.Vector(obj.getTransformation()[1][:3])
    obj_forward = pm.dt.Vector(obj.getTransformation()[2][:3])
    obj_pos     = obj.getTransformation()[3][:3]
    
    hit_point = pm.dt.Vector(hit_point)
    
    hit_up = groundShape.getPolygonNormal(hit_face_id).normal()
    hit_forward = obj_forward.normal()
    hit_side = hit_up.cross(hit_forward).normal()
    hit_up = hit_forward.cross(hit_side).normal()
    
    hit_matrix = [
        hit_side[0],    hit_side[1],    hit_side[2],    0.0,
        hit_up[0],      hit_up[1],      hit_up[2],      0.0,
        hit_forward[0], hit_forward[1], hit_forward[2], 0.0,
        0.0,   0.0,   0.0,   1.0
    ]
    
    obj.setMatrix(hit_matrix)
    obj.setTranslation(vector=hit_point, space = "world")
    

if __name__ == "__main__":
    doIt( ground = "Ground")

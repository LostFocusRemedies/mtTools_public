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
    # move_to_point(sel[0], hit_points[0], hit_faces[0])
        orient_to_normal(sel[0], groundShape, hit_faces[0], hit_points[0])
    else: 
        pm.warning("couldn't find any intersection!")

def move_to_point(obj, hit_point, hit_face):
    offset = obj.getTranslation() - obj.getBoundingBoxMin()
    hit_point_offsetted = pm.dt.Vector(hit_point.x, hit_point.y + offset.y, hit_point.z)
    obj.setTranslation(vector = hit_point_offsetted,space = "world")
    # obj.ty.set(obj.ty.get()+offset.y) # this works for basic cases. 
    
def orient_to_normal(obj, groundShape, hit_face_id, hit_point):
    y_axis = groundShape.getNormals(space="transform")[hit_face_id]

    
    
    hit_loc = pm.spaceLocator(n="hit_point", p=hit_point)
    y_loc = pm.spaceLocator(n="y_loc", p=y_axis)
    return(False)
    x_loc = pm.spaceLocator(n="x_loc", p=x_axis)
    z_loc = pm.spaceLocator(n="z_loc", p=z_axis)
    print(f"x_axis : {x_axis}")
    print(f"y_axis : {y_axis}")
    print(f"z_axis : {z_axis}")
    
    
    
    
    hit_normal = groundShape.getNormals(space="world")[hit_face_id]
    hit_direction = pm.dt.Vector(hit_normal)
    up_vector = pm.dt.Vector(0,1,0)
   
    z_axis = hit_direction
    x_axis = up_vector.cross(z_axis).normal()
    y_axis = z_axis.cross(x_axis)
    
    transformMatrix = [
        x_axis.x, x_axis.y, x_axis.z, 0,
        y_axis.x, y_axis.y, y_axis.z, 0,
        z_axis.x, z_axis.y, z_axis.z, 0,
        hit_point.x, hit_point.y, hit_point.z, 1 
    ]
    
    obj.setTransformation(transformMatrix)
    







if __name__ == "__main__":
    doIt( ground = "Ground")
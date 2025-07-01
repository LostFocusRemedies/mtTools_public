import maya.cmds as cm
import maya.mel as mel


def main(preserve_selection=False, translation=True, rotation=True, scale=True, custom_attributes=True):
    """Reset the attributes of selected objects to their default values.

    Args:
        preserve_selection (bool, optional): Preserve the attributes selection in the channelbox after resetting. Defaults to False.
        translation (bool, optional): only reset the translation, similar to blender ALT+G. Defaults to True.
        rotation (bool, optional): only reset the rotation, similar to blender ALT+R. Defaults to True.
        scale (bool, optional): only reset the scale, similar to blender ALT+S. Defaults to True.
        custom_attributes (bool, optional): only resets custom attributes. Defaults to True.
    """
    selected_objs = cm.ls(sl=True)
    if not selected_objs:
        cm.warning("No objects selected.")
        return
    channelbox_name = mel.eval('$temp=$gChannelBoxName')
    selected_attrs = cm.channelBox(channelbox_name, q=True, sma=True)
    trs_attrs = []
    if not selected_attrs:
        if translation:
            trs_attrs += ["translateX", "translateY", "translateZ"]
        if rotation:
            trs_attrs += ["rotateX", "rotateY", "rotateZ"]
        if scale:
            trs_attrs += ["scaleX", "scaleY", "scaleZ"]
        to_reset = trs_attrs

    for obj in selected_objs:
        to_reset = selected_attrs if selected_attrs else trs_attrs[:]
        if not selected_attrs and custom_attributes:
            obj_custom_attrs = cm.listAttr(obj, k=True, l=False, userDefined=True) or []
            to_reset.extend(obj_custom_attrs)
        for attr in to_reset:
            if cm.objExists(f"{obj}.{attr}"):
                try:
                    default_val = cm.attributeQuery(attr, node=obj, listDefault=True)[0]
                    cm.setAttr(f"{obj}.{attr}", default_val)
                except:
                    continue  # skip attributes without defaults

    if not preserve_selection:
        cm.channelBox("mainChannelBox", e=True, select=None)
        
        
        
        

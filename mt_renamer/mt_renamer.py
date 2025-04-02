import maya.cmds as cm

def show_gui():
    """
    An enhanced object renamer for Maya that:
    1. Shows the current object name and highlights it in the input field
    2. Supports auto-numbering with # placeholders (e.g. Cube_### becomes Cube_001, Cube_002, etc.)
    3. Handles single and multiple object selections intelligently
    4. Supports pressing Enter to rename
    """
    selection = cm.ls(sl=True)
    
    if not selection:
        cm.warning("Nothing selected. Please select one or more objects.")
        return None
        
    current_name = selection[0]
    
    # Create a dialog with built-in Enter key support
    result = cm.promptDialog(
        title="MT Enhanced Object Renamer",
        message="Enter new name (use # for numbering):",
        text=current_name,
        button=["OK", "Cancel"],
        defaultButton="OK",
        cancelButton="Cancel",
        dismissString="Cancel"
    )
    
    # Process the result when OK is clicked or Enter is pressed
    if result == "OK":
        new_name_pattern = cm.promptDialog(query=True, text=True)
        return process_rename(selection, new_name_pattern)
    else:
        return None

def process_rename(objects, new_name_pattern):
    """
    Process the renaming operation based on input pattern
    """
    if '#' in new_name_pattern:
        renamed_objects = rename_with_numbering(objects, new_name_pattern)
    else:
        if len(objects) == 1:
            renamed_objects = [cm.rename(objects[0], new_name_pattern)]
        else:
            renamed_objects = rename_with_numbering(objects, new_name_pattern + "_###")
    
    if renamed_objects:
        cm.select(renamed_objects)
        
    if len(renamed_objects) == 1:
        cm.inViewMessage(message=f"Renamed to: {renamed_objects[0]}", pos='midCenter', fade=True)
    else:
        cm.inViewMessage(message=f"Renamed {len(renamed_objects)} objects", pos='midCenter', fade=True)
    
    return renamed_objects

def rename_with_numbering(objects, pattern):
    """
    Renames objects using a pattern with # as placeholder for sequential numbers
    Examples:
    - "Cube_#" with 3 objects becomes: Cube_1, Cube_2, Cube_3
    - "Cube_##" with 3 objects becomes: Cube_01, Cube_02, Cube_03
    - "Cube_###" with 3 objects becomes: Cube_001, Cube_002, Cube_003
    """
    import re
    hash_sequences = re.findall(r'#+', pattern)
    
    if not hash_sequences:
        pattern = pattern + "_###"
        hash_sequences = ["###"]
    
    paddings = [len(seq) for seq in hash_sequences]
    
    name_template = pattern
    for i, seq in enumerate(hash_sequences):
        name_template = name_template.replace(seq, '{' + str(i) + '}', 1)
    
    renamed_objects = []
    for i, obj in enumerate(objects, 1):
        formatted_numbers = []
        for padding in paddings:
            formatted_numbers.append(str(i).zfill(padding))
        
        new_name = name_template.format(*formatted_numbers)
        
        renamed_objects.append(cm.rename(obj, new_name))
    
    return renamed_objects

"""
Here you can find the configuration for the IK/FK setup in Maya.
ARM_SETUP and LEG_SETUP dictionaries define the control names used by the IK/FK switch.
ARM_CONTROLS_TAGS and LEG_CONTROLS_TAGS are sets of tags used to identify arm and leg controls in the scene.

TORSO_CONTROLS_TAGS contains tags for torso-related controls. It's here just as an example of what you can achieve extra, infact, 
if you were to add a TORSO_SETUP dictionary, you could easily extend the functionality to include torso IK/FK switching.

that goes for every other kind of 3 jointed limb, like tail, tentacles. 
"""

ARM_SETUP = {
    "FK_end": "handFk_000_CTL",
    "FK_start": "shoulderFk_000_CTL",
    "FK_mid": "elbowFk_000_CTL",
    "IK_end": "handIk_000_CTL",
    "IK_start": "shoulderIk_000_JNT",
    "IK_mid": "elbowIk_000_JNT",
    "IK_pv": "armPoleVector_000_CTL",
    "AlignIkToWrist": "handBind_000_JNT",
    "interface_ctl": "armIkFk_000_CTL",
    "FK_end_jnt": "handFk_000_JNT",
    "IK_end_jnt": "handIk_000_JNT",
}

LEG_SETUP = {
    "FK_end": "ankleFk_000_CTL",
    "FK_start": "legFk_000_CTL",
    "FK_mid": "kneeFk_000_CTL",
    "IK_end": "footIk_000_CTL",
    "IK_start": "legIk_000_JNT",
    "IK_mid": "kneeIk_000_JNT",
    "IK_pv": "legPoleVector_000_CTL",
    "AlignIkToWrist": "ankleBind_000_JNT",
    "interface_ctl": "legIkFk_000_CTL",
    "FK_end_jnt": "ankleFk_000_JNT",
    "IK_end_jnt": "ankleIk_000_JNT",
}


ARM_CONTROLS_TAGS = frozenset(
    {
        "clavicle",
        "shoulder",
        "elbow",
        "hand",
        "thumb",
        "index",
        "middle",
        "ring",
        "pinky",
        "armPoleVector",
        "armIkFk",
        "sleeve",
        "arm"
    }
)

LEG_CONTROLS_TAGS = frozenset(
    {   
        "pelvis", 
        "leg", 
        "knee", 
        "foot", 
        "ankle", 
        "toe", 
        "legPoleVector", 
        "legIkFk",
        "pant",
        "calf",
        "thigh",
    }
)



TORSO_CONTROLS_TAGS = frozenset(
    {
        "chest",
        "hip",
        "neck",
        "spine"
    }
)

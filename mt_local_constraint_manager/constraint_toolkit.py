import maya.cmds as cm

from . import logger



def get_all_constraints(local=True) -> list:
    """
    Returns a list of all constraint nodes in the Maya scene.
    """
    if local:
        # get all the constraints that are not referenced
        constraints = cm.ls(type="constraint", long=True, referencedNodes=False)
        constraints = [
            c for c in constraints if not cm.referenceQuery(c, isNodeReferenced=True)
        ] or []
        logger.debug(f"Found {len(constraints)} local constraints in the scene.")
    else:
        constraints = cm.ls(type="constraint")
    logger.debug(f"Found {len(constraints)} constraints in the scene.")
    if constraints:
        constraints = [c.split("|")[-1] for c in constraints]
    return constraints


def get_constraint_connections(constraint_name: str) -> list:
    """
    Return a tuple. The first element is the driver (which can only be one), the second is a list of all the driven objects.
    """
    if not cm.objExists(constraint_name):
        logger.warning(f"Constraint {constraint_name} does not exist.")
        return []

    # Get the driver of the constraint
    driver = cm.listConnections(
        f"{constraint_name}.target[0].targetParentMatrix",
        source=True,
        destination=False,
    )
    if not driver:
        logger.warning(f"No driver found for constraint {constraint_name}.")
        return []

    # Get the driven objects
    driven = list(set(cm.listConnections(constraint_name, s=False, d=True))) or []
    driven = [d for d in driven if "Constraint" not in d]  # Exclude other constraints
    logger.debug(
        f"Constraint {constraint_name} has driver: {driver[0]} and driven: {driven}"
    )

    return [driver[0], driven]



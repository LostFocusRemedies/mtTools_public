"""
import mttools_public.mt_local_constraints_manager.constraints_toolkit_gui as ct
from imp import reload
reload(ct)

ct.ConstraintToolkitGUI()
"""


import maya.cmds as cm
import pymel.core as pm  # just for the GUI
from . import constraint_toolkit as ct
from . import logger


class ConstraintToolkitGUI:
    """Constraint Toolkit GUI"""
    def __init__(self):
        self.window_name = "ConstraintToolkitWindow"
        self.create_ui()
        pm.showWindow(self.window_name)

    def create_ui(self):
        if pm.window(self.window_name, exists=True):
            try:
                pm.deleteUI(self.window_name)
            except Exception as e:
                logger.error(f"Error deleting UI: {e}")
        pm.window(self.window_name, t="Constraint Toolkit", wh=(362, 256), sizeable=False)
        self.populate_ui()

    def populate_ui(self):
        pm.columnLayout(adjustableColumn=True)
        with pm.frameLayout(l="Constraint Toolkit", mh=10, mw=10):
            with pm.rowLayout(nc=2, adjustableColumn=2):
                with pm.columnLayout(adjustableColumn=True):
                    self.constr_tsl = pm.textScrollList(
                        "constraintList",
                        allowMultiSelection=True,
                        append=ct.get_all_constraints(),
                        height=150,
                        selectCommand=self.select_constraints,
                    )
                    self.constr_conn_tf = pm.textField(
                        "constraintConnections",
                        editable=False,
                        text="Select a constraint to see connections.",
                    )
                with pm.columnLayout(adjustableColumn=True):
                    pm.button(
                        label="Update List",
                        command=self.update_list,
                    )
                    pm.separator(h=10, style="none")
                    self.sel_driver_btn = pm.button(
                        l="Select Driver", c=self.select_driver, enable=False
                    )
                    self.sel_driven_btn = pm.button(
                        l="Select Driven", c=self.select_driven, enable=False
                    )
                    pm.separator(h=10, style="none")
                    self.delete_btn = pm.button(
                        label="Delete Driver",
                        command=self.delete_constraints,
                        enable=False,
                    )
            pm.separator(h=6)
            pm.text("mt_Tools - Local Constraints Manager", align="center")

    def select_driver(self, *args):
        """
        Selects the driver of the selected constraint in the textScrollList.
        """
        selected_constraints = self.constr_tsl.getSelectItem()
        if not selected_constraints:
            logger.warning("No constraints selected.")
            return

        all_drivers = []
        for constraint in selected_constraints:
            driver, _ = ct.get_constraint_connections(constraint)
            all_drivers.append(driver)

        if all_drivers:
            cm.select(all_drivers, replace=True)
            logger.info(f"Selected driver: {driver}")
        else:
            logger.warning("No driver found for the selected constraint.")

    def select_driven(self, *args):
        """
        Selects the driven objects of the selected constraint in the textScrollList.
        """
        selected_constraints = self.constr_tsl.getSelectItem()
        if not selected_constraints:
            logger.warning("No constraints selected.")
            return

        all_driven = []
        for constraint in selected_constraints:
            _, driven = ct.get_constraint_connections(constraint)
            all_driven.extend(driven)

        if all_driven:
            cm.select(all_driven, replace=True)
            logger.info(f"Selected driven objects: {driven}")
        else:
            logger.warning("No driven objects found for the selected constraint.")

    def update_constr_conn_tf(self, *args):
        """
        updates the textField with the connections of the selected constraint.
        It'll show the driver and driven nodes.
        """
        selected_constraints = self.constr_tsl.getSelectItem()
        if not selected_constraints:
            pm.textField(
                self.constr_conn_tf, edit=True, text="No constraints selected."
            )
            return

        connections = ct.get_constraint_connections(selected_constraints[0])
        if connections:
            driver, driven = connections
            connection_text = f"{driver} ------> {driven}"
        else:
            connection_text = "No connections found."

        pm.textField(self.constr_conn_tf, edit=True, text=connection_text)

    def delete_constraints(self, *args):
        """
        Deletes the selected constraints from the textScrollList.
        """
        selected_constraints = self.constr_tsl.getSelectItem()
        if not selected_constraints:
            logger.warning("No constraints selected for deletion.")
            return

        for constraint in selected_constraints:
            if cm.objExists(constraint):
                cm.delete(constraint)
                logger.info(f"Deleted constraint: {constraint}")
            else:
                logger.warning(f"Constraint {constraint} does not exist.")

        self.update_list()

    def update_list(self, *args):
        """
        Updates the constraint list in the textScrollList.
        """
        constraints = ct.get_all_constraints()
        self.constr_tsl.removeAll()
        self.constr_tsl.append(constraints)
        self.sel_driven_btn.setEnable(False)
        self.sel_driver_btn.setEnable(False)
        self.delete_btn.setEnable(False)
        logger.info(f"Updated constraint list with {len(constraints)} items.")

    def select_constraints(self, *args):
        # selected_constraints = pm.textScrollList(self.constr_tsl, edit=True, selectItem=selected_constraints)
        selected_constraints = self.constr_tsl.getSelectItem()
        if selected_constraints:
            self.sel_driven_btn.setEnable(True)
            self.sel_driver_btn.setEnable(True)
            self.delete_btn.setEnable(True)
            cm.select(selected_constraints, replace=True)
            self.update_constr_conn_tf()
            logger.info(f"Selected constraints: {selected_constraints}")
        else:
            logger.warning("No constraints selected.")
            
    def _window_size(self):
        """
        Returns the current window size. for debugging purposes.
        """
        size = pm.window(self.window_name, query=True, widthHeight=True)
        if size is None:
            logger.warning("Window size not found, returning default size (300, 400).")
        logger.debug(f"Current window size: {size}")
        return size

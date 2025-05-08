"""
Label creator, created for Studio library and charcater study 
in early stages of production, to better present poses and animations

import mtLabelCreator as mtlc
reload(mtlc)

names = "some sample labels separated by a space"
mtlc.labelCreator(names = names, frameOffset = 5)

or for the UI

#import mtLabelCreator as mtlc
#reload(mtlc)

-- while developing:
try:
   LabelCreatorUI.close() # pylint: disable=E0601
   LabelCreatorUI.deleteLater()
except:
   pass

LabelCreatorUI = mtlc.LabelCreatorUI()
LabelCreatorUI.show()

-- deployed:

from mtLabelCreator import LabelCreatorUI
LabelCreatorUI.show_dialog()

"""

import maya.cmds as cm
import pymel.core as pm
import maya.app.type.typeToolSetup as mtype
import maya.mel as mel
import pprint
import time

class LabelCreator(object):
    def __init__(self):
        self.USER_BUFFER_NAME = "labels_user_buffer"
        self.TRANSFORM_BUFFER_NAME = "labels_transforms_buffer"
        self.PARENT_BUFFER_NAME = "labels_parent_buffer"
        # self.FIRST_FRAME = pm.playbackOptions(q=True, animationStartTime=True)
        self.FIRST_FRAME = pm.currentTime(q=True)


    def labelCreator(self, names, cam="cam", frameOffset=5, overwrite=True, preserve=False, setTimeRange=True, legacyKeyframes=False):
        
        if not cm.objExists(cam):
            raise cm.error("camera is not existent!")

        if overwrite == True:
            self.deleteLabels()

        self.frameOffset = frameOffset
        names = self.parseStringIntoList(names)
        frame = self.FIRST_FRAME
        cam = pm.PyNode(cam)

        self.allTexts = []

        for each in names:
            mtype.createTypeTool(text=each)
            
            currentTextShapeNode = pm.ls(sl=True)[0]
            typeNode = currentTextShapeNode.listConnections()[0]
            # typeNode.alignmentMode.set(2)

            currentTextTransformNode = currentTextShapeNode.getTransform() 
            currentTextTransformNode.rename(each)

            currentTextTransformNode.visibility.setKey(value=0, time=frame-1)
            if legacyKeyframes:
                currentTextTransformNode.visibility.setKey(value=1, time=frame)
                currentTextTransformNode.visibility.setKey(value=0, time=frame + self.frameOffset)

            frame += self.frameOffset
            self.allTexts.append(currentTextTransformNode)


        pm.select(self.allTexts, r=True)
        user_buffer = pm.group(name = self.USER_BUFFER_NAME)
        transforms_buffer = pm.group(name = self.TRANSFORM_BUFFER_NAME)
        parent_buffer = pm.group(name = self.PARENT_BUFFER_NAME)

        # !!!!!!!!!!!!!!!
        if not legacyKeyframes:
            self.createCtlWithConditions(self.allTexts, user_buffer)
        else:
            self.updateScreen()

        if not preserve:
            self.deleteHistory()
        
        if setTimeRange:
            self.setTimeRange()

        transforms_buffer.translateX.set(-0.652)
        transforms_buffer.translateY.set(-0.35)
        transforms_buffer.translateZ.set(-2.70)
        transforms_buffer.scaleX.set(0.006)
        transforms_buffer.scaleY.set(0.006)
        transforms_buffer.scaleZ.set(0.001)
        transforms_buffer.translateX.lock(True)
        transforms_buffer.translateY.lock(True)
        transforms_buffer.translateZ.lock(True)
        transforms_buffer.rotateX.lock(True)
        transforms_buffer.rotateY.lock(True)
        transforms_buffer.rotateZ.lock(True)
        transforms_buffer.scaleX.lock(True)
        transforms_buffer.scaleY.lock(True)
        transforms_buffer.scaleZ.lock(True)

        # pm.parentConstraint(cam, parent_buffer)
        cam.translateX >> parent_buffer.translateX
        cam.translateY >> parent_buffer.translateY
        cam.translateZ >> parent_buffer.translateZ
        cam.rotateX >> parent_buffer.rotateX
        cam.rotateY >> parent_buffer.rotateY
        cam.rotateZ >> parent_buffer.rotateZ


        #TODO utils function for this
        #pprint.pprint( cm.listAttr(typeTool))


    def createCtlWithConditions(self, labelList, parent):
        time=self.FIRST_FRAME
        
        parent_attribute_name = "labelsVisibility"
        parent.addAttr(parent_attribute_name, at="short", k=True, min=0, max=len(labelList), defaultValue=1)
        
        for num, label in enumerate(labelList, start=1):
            condition_node_string = cm.shadingNode("condition", asUtility=True, name=("condition_%s" % num))
            condition_node = pm.PyNode(condition_node_string)

            parent.labelsVisibility >> condition_node.firstTerm

            condition_node.secondTerm.set(num)
            condition_node.colorIfTrueR.set(1)
            condition_node.colorIfFalseR.set(0)

            condition_node.outColorR >> label.visibility

            parent.labelsVisibility.setKey(value=num, time=time)
            time += self.frameOffset


    def wait(self):
        time.sleep(1 * len(self.allTexts))


    def parseStringIntoList(self, namesString):
        namesList = [w for w in namesString.split(" ")]
        return namesList


    def deleteLabels(self):
        if pm.objExists(self.PARENT_BUFFER_NAME):
            try: 
                mel.eval("MLdeleteUnused")
                pm.delete(self.PARENT_BUFFER_NAME, hi="below")
            except : 
                raise Warning

    def updateScreen(self):
        pm.currentTime( self.FIRST_FRAME + 1, edit=True)
        pm.currentTime( self.FIRST_FRAME, edit=True)


    def deleteHistory(self):
        pm.delete(self.allTexts, constructionHistory=True)

    
    def setTimeRange(self):
        print("setting time range")
        last_frame = self.FIRST_FRAME + (len(self.allTexts) * self.frameOffset) -1

        pm.playbackOptions( min = self.FIRST_FRAME,
                            max = last_frame)



#----------------------------------------------------------------------------------------------------------- UI
# UI

from PySide2 import QtCore, QtWidgets, QtGui
from shiboken2 import wrapInstance

import maya.OpenMaya as om
import maya.OpenMayaUI as omui

def getMayaMainWindow():

    mayaMainWindow = omui.MQtUtil.mainWindow()
    ptr = wrapInstance(int(mayaMainWindow), QtWidgets.QWidget)
    return ptr


class MyLineEdit(QtWidgets.QLineEdit):

    enter_pressed = QtCore.Signal(str)

    def keyPressEvent(self, e):
        super(MyLineEdit, self).keyPressEvent(e)

        if e.key() == QtCore.Qt.Key_Enter or e.key()==QtCore.Qt.Key_Return:
            self.enter_pressed.emit("Enter Key Pressed")
        

class LabelCreatorUI(QtWidgets.QDialog):

    dlg_instance = None # maintain a single instance of the dialog in Production

    @classmethod
    def show_dialog(cls):
        if not cls.dlg_instance:
            cls.dlg_instance = LabelCreatorUI()

        if cls.dlg_instance.isHidden():
            cls.dlg_instance.show()
        else:
            cls.dlg_instance.raise_()
            cls.dlg_instance.activateWindow()


    def __init__(self, parent=getMayaMainWindow()):
        self.labelCreator = LabelCreator()        

        super(LabelCreatorUI, self).__init__(parent)
        self.setWindowTitle("mt Label Creator UI 1.0.0")
        self.setMinimumWidth(500)
        self.setMinimumHeight(100)
        self.setMaximumWidth(500)
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)
        
        self.create_widgets()
        self.create_layouts()
        self.create_connections()


    def create_widgets(self):
        instruction_text_string = "To create labels, each label must be one word separated by an empty space, you can create as many labels as you want! Then select the camera, and it will be parented to it! Cheers"
        self.instructions_text = QtWidgets.QLabel(instruction_text_string)
        self.instructions_text.setWordWrap(True)

        self.listNames_text = QtWidgets.QLabel("Labels:")
        # self.listNames_plainTextEdit = MyLineEdit("type all names separated by one space")
        self.listNames_plainTextEdit = QtWidgets.QPlainTextEdit("type all names separated by one space")
        self.listNames_plainTextEdit.selectAll()

        self.cameraName_text = QtWidgets.QLabel("Camera:")
        self.cameraName_lineEdit = MyLineEdit("cam:icare_animCam")
        self.cameraName_lineEdit.setReadOnly(True)
        self.cameraName_lineEdit.setMaximumWidth(150)
        self.setColortoLocked(self.cameraName_lineEdit)
        self.cameraNamefromSel_btn = QtWidgets.QPushButton("From Selection")
        self.cameraNamefromSel_btn.setMaximumWidth(80)
        self.cameraNamefromView_btn = QtWidgets.QPushButton("From Viewport")
        self.cameraNamefromView_btn.setMaximumWidth(80)

        self.frameOffset_text = QtWidgets.QLabel("Frames Offset:")
        self.frameOffset_lineEdit = MyLineEdit("5")
        self.frameOffset_lineEdit.setMaximumWidth(150)

        self.overwrite_label = QtWidgets.QLabel("overwrite existing labels:")
        self.overwrite_checkbox = QtWidgets.QCheckBox()
        self.overwrite_checkbox.setChecked(True)
        self.preserveType_label = QtWidgets.QLabel("preserve History:")
        self.preserveType_checkbox = QtWidgets.QCheckBox()
        self.preserveType_checkbox.setChecked(True)
        self.setTimeRange_label = QtWidgets.QLabel("Set Time Range")
        self.setTimeRange_checkbox = QtWidgets.QCheckBox()
        self.setTimeRange_checkbox.setChecked(True)

        self.create_btn = QtWidgets.QPushButton("Create")
        self.deleteHistory_btn = QtWidgets.QPushButton("Delete History")
        self.close_btn = QtWidgets.QPushButton("Close")


        self.listNames_plainTextEdit.setToolTip("Write all your Labels separated by one single blank space :\" \" ")
        self.frameOffset_lineEdit.setToolTip("set the duration of in frames of each label. Will start form the current frame.")
        self.overwrite_checkbox.setToolTip("Delete previously created Label Group")
        self.preserveType_checkbox.setToolTip("if checked you will preserve the \"Type\" node, and be able to modify the text later")
        self.setTimeRange_checkbox.setToolTip("will set the time range to the actual lenght of the labels animation")
        self.deleteHistory_btn.setToolTip("Will delete the history of all labels, increasing performance, but the text will not be editable anymore.")

    def create_layouts(self):
        grid_layout = QtWidgets.QGridLayout()
        grid_layout.addWidget(self.instructions_text, 0,0,1,4)
        grid_layout.addWidget(self.listNames_text, 1,0, QtCore.Qt.AlignRight)
        grid_layout.addWidget(self.listNames_plainTextEdit, 1,1,1,3)
        grid_layout.addWidget(self.cameraName_text, 2,0, QtCore.Qt.AlignRight)
        grid_layout.addWidget(self.cameraName_lineEdit, 2,1)
        grid_layout.addWidget(self.cameraNamefromSel_btn, 2,2)
        grid_layout.addWidget(self.cameraNamefromView_btn, 2,3)
        grid_layout.addWidget(self.frameOffset_text, 4,0, QtCore.Qt.AlignRight)
        grid_layout.addWidget(self.frameOffset_lineEdit, 4,1)
        
        grid_layout.addWidget(self.overwrite_label, 5,0, QtCore.Qt.AlignRight)
        grid_layout.addWidget(self.overwrite_checkbox, 5,1)
        # grid_layout.addWidget(self.preserveType_label, 5,0)
        # grid_layout.addWidget(self.preserveType_checkbox, 5,1)
        grid_layout.addWidget(self.setTimeRange_label, 6,0, QtCore.Qt.AlignRight)
        grid_layout.addWidget(self.setTimeRange_checkbox, 6,1)
        
        # form_layout = QtWidgets.QFormLayout()
        # form_layout.addRow("List of names: ", self.listNames_plainTextEdit)

        button_layout = QtWidgets.QHBoxLayout()
        # button_layout.addStretch()
        button_layout.addWidget(self.create_btn)
        button_layout.addWidget(self.deleteHistory_btn)
        button_layout.addWidget(self.close_btn)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addLayout(grid_layout)
        main_layout.addLayout(button_layout)

    def create_connections(self):
        self.cameraNamefromSel_btn.clicked.connect(self.getSelectedCamera)
        self.cameraNamefromView_btn.clicked.connect(self.getActiveCamera)
        self.create_btn.clicked.connect(self.callLabelCreator)
        self.deleteHistory_btn.clicked.connect(self.labelCreator.deleteHistory)
        self.close_btn.clicked.connect(self.close)

    
    #############################################################
    # METHODS NOT RELATED TO BUILD UI

    def selectText(self):
        cursor = self.listNames_plainTextEdit.textCursor()
        cursor.setPosition(0)
        cursor.setPosition(500, QtGui.QTextCursor.KeepAnchor)


    def on_enter_pressed(self, text):
        print("TODO")

    
    def raiseErrorRed(self, lineEdit):
        self.cameraName_lineEdit.setStyleSheet
        
        # set to red
        lineEdit.setStyleSheet("""
                    QLineEdit{
                        background-color: rgb(255,100,100);
                        color: rgb(0,0,0)
                    }""")

        lineEdit.setText("You must select something!")
        raise Warning("You must select something!")
        return
    
    
    def getSelectedCamera(self):
        cam = cm.ls(sl=True)
        if not cam:
            self.raiseErrorRed(self.cameraName_lineEdit)
            return None
        
        self.setColortoLocked(self.cameraName_lineEdit)
        
        cam = cam[0]
        self.cameraName_lineEdit.setText(cam)
        return cam

    def getActiveCamera(self):
        pan = pm.getPanel(withFocus=True)
        cam = pm.windows.modelPanel(pan,q=True,camera=True)
        
        self.setColortoLocked(self.cameraName_lineEdit)

        self.cameraName_lineEdit.setText(cam)
        return cam

    def setColortoLocked(self, lineEdit):
        lineEdit.setStyleSheet("""
        QLineEdit{
            background-color: rgb(100,100,100);
            color: rgb(40,40,40)}""")
        return

    def callLabelCreator(self):
        names        = self.listNames_plainTextEdit.toPlainText()
        frameOffset  = int(self.frameOffset_lineEdit.text())
        cam          = self.cameraName_lineEdit.text()
        overwrite    = self.overwrite_checkbox.isChecked()
        preserve     = self.preserveType_checkbox.isChecked()
        setTimeRange = self.setTimeRange_checkbox.isChecked()

        self.labelCreator.labelCreator( names, 
                                        cam,
                                        frameOffset=frameOffset, 
                                        overwrite=overwrite, 
                                        preserve=preserve, 
                                        setTimeRange=setTimeRange
                                        )




""" This is Step 1. The user selects the pre- and, if preferred, post-contrast
	volumes.
"""

from __main__ import qt, ctk, slicer

from SegmentationWizardStep import *
from Helper import *

""" VolumeSelectStep inherits from SegmentationWizardStep, with itself inherits
	from a ctk workflow class. 
"""

class VolumeSelectStep(SegmentationWizardStep) :

	def __init__(self, stepid):

		""" This method creates a drop-down menu including the whole step.
			The description also acts as a tooltip for the button. There may be 
			some way to override this. The initialize method is inherited
			from ctk.
		"""

		self.initialize( stepid )
		self.setName( '1. Volume Selection' )

		self.__parent = super(VolumeSelectStep, self)

	def createUserInterface(self):

		""" This method uses qt to create a user interface. qMRMLNodeComboBox
			is a drop down menu for picking MRML files. MRML files have to be
			added to a "scene," i.e. the main Slicer container, hence setMRMLScene.
		"""

		self.__layout = self.__parent.createUserInterface()

		step_label = qt.QLabel( 'Choose the volume you would like to threshold. If you are calculating a subtraction map, check the \"Calculate Subtraction Map\" box and select a post-contrast image.' )
		step_label.setWordWrap(True)
		self.__primaryGroupBox = qt.QGroupBox()
		self.__primaryGroupBox.setTitle('Information')
		self.__primaryGroupBoxLayout = qt.QFormLayout(self.__primaryGroupBox)

		self.__subtractionMappingGroupBox = qt.QGroupBox()
		self.__subtractionMappingGroupBox.setTitle('Volume Selection')
		self.__subtractionMappingGroupBoxLayout = qt.QFormLayout(self.__subtractionMappingGroupBox)

		baselineScanLabel = qt.QLabel( 'Primary / Pre-Contrast Image:' )
		self.__baselineVolumeSelector = slicer.qMRMLNodeComboBox()
		self.__baselineVolumeSelector.toolTip = "Select the volume you wish to threshold. If you are calculating a subtraction map, this will be the pre-contrast scan."
		self.__baselineVolumeSelector.nodeTypes = ['vtkMRMLScalarVolumeNode']
		self.__baselineVolumeSelector.setMRMLScene(slicer.mrmlScene)
		self.__baselineVolumeSelector.addEnabled = 0

		subtractionMappingLabel = qt.QLabel( 'Calculate Subtraction Map:' )
		self.__enableSubtractionMapping = qt.QCheckBox()
		self.__enableSubtractionMapping.checked = False
		self.__enableSubtractionMapping.setToolTip("Check if you would like to calculate a subtraction map")
		self.__enableSubtractionMapping.connect('clicked()', self.setSubtractionMapping)

		followupScanLabel = qt.QLabel( 'Post-Contrast Image:' )
		self.__followupVolumeSelector = slicer.qMRMLNodeComboBox()
		self.__followupVolumeSelector.toolTip = "Choose the post-contrast scan"
		self.__followupVolumeSelector.nodeTypes = ['vtkMRMLScalarVolumeNode']
		self.__followupVolumeSelector.setMRMLScene(slicer.mrmlScene)
		self.__followupVolumeSelector.addEnabled = 0
		self.__followupVolumeSelector.enabled = 0

		self.__layout.addRow(self.__primaryGroupBox)
		self.__primaryGroupBoxLayout.addRow( step_label )
		self.__subtractionMappingGroupBoxLayout.addRow( baselineScanLabel, self.__baselineVolumeSelector )

		self.__layout.addRow(self.__subtractionMappingGroupBox)
		self.__subtractionMappingGroupBoxLayout.addRow( subtractionMappingLabel, self.__enableSubtractionMapping )
		self.__subtractionMappingGroupBoxLayout.addRow( followupScanLabel, self.__followupVolumeSelector )

		self.updateWidgetFromParameters(self.parameterNode())

		# This timer is a trick to wait for buttons to load BEFORE deleting them.
		qt.QTimer.singleShot(0, self.killButton)

	def setSubtractionMapping(self):
		# Links check box to the "greying out" of the followup volume selection.
		self.__followupVolumeSelector.enabled = self.__enableSubtractionMapping.checked

	def validate( self, desiredBranchId ):

		self.__parent.validate( desiredBranchId )

		# Check that the selectors are not empty / the same
		baseline = self.__baselineVolumeSelector.currentNode()
		followup = self.__followupVolumeSelector.currentNode()

		if self.__enableSubtractionMapping.checked:
			if baseline != None and followup != None:
				baselineID = baseline.GetID()
				followupID = followup.GetID()
				if baselineID != '' and followupID != '' and baselineID != followupID:
			
					pNode = self.parameterNode()
					pNode.SetParameter('baselineVolumeID', baselineID)
					pNode.SetParameter('followupVolumeID', followupID)
					pNode.SetParameter('originalBaselineVolumeID', baselineID)
					pNode.SetParameter('originalFollowupVolumeID', followupID)

					self.__parent.validationSucceeded(desiredBranchId)
				else:
					self.__parent.validationFailed(desiredBranchId, 'Error','Please select distinctive pre- and post-contrast volumes.')
			else:
				self.__parent.validationFailed(desiredBranchId, 'Error','Please select pre- and post-contrast volumes if you wish to compute a subtraction map. Otherwise, uncheck "calculate subtraction map"')
		else:
			if baseline != None:
				baselineID = baseline.GetID()
				if baselineID != '':
			
					pNode = self.parameterNode()
					pNode.SetParameter('baselineVolumeID', baselineID)
					pNode.SetParameter('followupVolumeID', '')
					pNode.SetParameter('originalBaselineVolumeID', baselineID)
					pNode.SetParameter('originalFollowupVolumeID', '')					

					self.__parent.validationSucceeded(desiredBranchId)
				else:
					self.__parent.validationFailed(desiredBranchId, 'Error','Please select a valid volume to threshold.')
			else:
				self.__parent.validationFailed(desiredBranchId, 'Error','Please select a volume to threshold before continuing.')				

	def killButton(self):

		# Find 'next' and 'back' buttons to control step flow in individual steps.
		stepButtons = slicer.util.findChildren(className='ctkPushButton')
		
		backButton = ''
		nextButton = ''
		for stepButton in stepButtons:
			if stepButton.text == 'Next':
				nextButton = stepButton
			if stepButton.text == 'Back':
				backButton = stepButton

		backButton.hide()

		# ctk creates an unwanted final page button. This method gets rid of it.
		bl = slicer.util.findChildren(text='ReviewStep')
		if len(bl):
			bl[0].hide()

	def onEntry(self, comingFrom, transitionType):

		super(VolumeSelectStep, self).onEntry(comingFrom, transitionType)

		self.updateWidgetFromParameters(self.parameterNode())

		pNode = self.parameterNode()
		pNode.SetParameter('currentStep', self.stepid)

		qt.QTimer.singleShot(0, self.killButton)

	def onExit(self, goingTo, transitionType):   

		super(SegmentationWizardStep, self).onExit(goingTo, transitionType) 

	def updateWidgetFromParameters(self, parameterNode):

		# Gratuitous
		pNode = self.parameterNode()

		pNode.SetParameter('baselineVolumeID', '')	
		pNode.SetParameter('followupVolumeID', '')
		pNode.SetParameter('originalBaselineVolumeID', '')	
		pNode.SetParameter('originalFollowupVolumeID', '')

		pNode.SetParameter('registrationVolumeID', '')
		pNode.SetParameter('baselineNormalizeVolumeID', '')
		pNode.SetParameter('followupNormalizeVolumeID', '')
		pNode.SetParameter('subtractVolumeID', '')

		pNode.SetParameter('clippingMarkupNodeID', '')
		pNode.SetParameter('clippingModelNodeID', '')
		pNode.SetParameter('outputList', '')	
		pNode.SetParameter('modelList', '')	

		pNode.SetParameter('thresholdedLabelID', '')
		pNode.SetParameter('croppedVolumeID', '')
		pNode.SetParameter('nonThresholdedLabelID', '')

		pNode.SetParameter('roiNodeID', '')
		pNode.SetParameter('roiTransformID', '')

		pNode.SetParameter('vrDisplayNodeID', '')
		pNode.SetParameter('intensityThreshRangeMin', '')
		pNode.SetParameter('intensityThreshRangeMax', '')
		pNode.SetParameter('vrThreshRange', '')

		# To save parameters from step to step.
		baselineVolumeID = parameterNode.GetParameter('originalBaselineVolumeID')
		followupVolumeID = parameterNode.GetParameter('originalFollowupVolumeID')
		if baselineVolumeID != None or baselineVolumeID != '':
			self.__baselineVolumeSelector.setCurrentNode(Helper.getNodeByID(baselineVolumeID))
		if followupVolumeID != None or followupVolumeID != '':
			self.__followupVolumeSelector.setCurrentNode(Helper.getNodeByID(followupVolumeID))

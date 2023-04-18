# -------------------------------------------------------
# Copyright (c) 2023 Shengyang Zhuang
# Acoustic Robotics Systems Lab, Institute of Robotics and Intelligent Systems,
# Department of Mechanical and Process Engineering, ETH Zurich.
# All rights reserved.
#
#
# Acknowledgments:
# - Thank you to Prajwal Agrawal and Prof Daniel Ahmed for their advice and guidance.
#
#*********************************WARNING!****************************************
#---------------------------------------------------------------------------------
#
#This project is under active development!
#
#---------------------------------------------------------------------------------
#
# Version: Initial release within ARSL group. Uploaded online with permission from Shengyang Zhuang, Prajwal Agrawal.
#
# Dependencies:
# - This code depends on vamtoolbox released by UC Berkeley. Information regarding installing
# should refer to https://github.com/computed-axial-lithography/VAMToolbox.
# - VAMToolbox is a Python library to support the generation of the light projections and the control of a DLP
# projector for tomographic volumetric additive manufacturing. It provides visualization, various optimization
# techniques, and flexible projection geometries to assist in the creation of sinograms and reconstructions
# for simulated VAM.
#
# Usage instructions:
# - Install vamtoolbox and CUDA(optional if choosing Disabled when running).
# - Follow the instructions in the README to run the code.
#
# Contact information:
# - Email: szhuang@student.ethz.ch (valid until June 2023)
#          shengyangzhuang@outlook.com
# - Phone: +41 0765457239 (Switzerland, valid until June 2023)
#          +86 18050099261 (China)
# - Personal Website: https://shengyangzhuang.github.io/
# - GitHub Homepage: https://github.com/shengyangzhuang
# -------------------------------------------------------


from PyQt5 import QtCore, QtGui, QtWidgets, QtOpenGL
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsPixmapItem
from PyQt5.QtGui import QPixmap
from PyQt5.QtGui import QPixmap, QImage, QPalette, QBrush, QColor
from PyQt5.QtWidgets import QGraphicsPixmapItem
from PyQt5.QtGui import QOpenGLShader, QOpenGLShaderProgram, QOpenGLContext
from PyQt5.QtWidgets import QOpenGLWidget
import os
import vedo
import numpy as np
import sys
import os
import vamtoolbox as vam
import logging

current_dir = os.path.dirname(os.path.realpath(__file__))
dir_main= os.path.dirname(current_dir)
print("Main Directory:", dir_main)

class Opt(QWidget):
    def __init__(self):
        super(Opt, self).__init__()
        #######################################################################################
        #######################################################################################
        #######################################################################################
        #######################################################################################
        #######################################################################################
        '''
        TO DO: CHANGE THE PATH ACCORDING TO YOUR OWN LAPTOP
        '''
        #######################################################################################
        #######################################################################################
        #######################################################################################
        #######################################################################################
        #######################################################################################

        current_dir = os.path.dirname(os.path.realpath(__file__))
        global dir_main
        dir_main= os.path.dirname(current_dir)
        print("Software Directory:", dir_main)
        ui_file_1 = os.path.join(dir_main, 'designer', '3DOptimization.ui')
        uic.loadUi(ui_file_1, self)
        self.show()
        print("Showing optimization window...")
        self.textBrowser.append("Showing optimization window...")
        print("Please enter the name of the optimization object and press Load STL model to select STL file to start optimizzation")
        self.textBrowser.append("Please enter the name of the optimization object and press Load STL model to select STL file to start optimization")
        self.pushButton.clicked.connect(self.previewSTL)
        self.pushButton_2.clicked.connect(self.runSTL)
        self.spinBox.valueChanged.connect(self.changeParas)
        self.spinBox_2.valueChanged.connect(self.changeParas)
        self.doubleSpinBox.valueChanged.connect(self.changeParas)
        self.doubleSpinBox_2.valueChanged.connect(self.changeParas)
        self.pushButton_3.clicked.connect(self.imageSequence)
        self.spinBox_3.valueChanged.connect(self.changeParas)
        self.spinBox_4.valueChanged.connect(self.changeParas)
        self.spinBox_5.valueChanged.connect(self.changeParas)
        self.doubleSpinBox_3.valueChanged.connect(self.changeParas)
        self.pushButton_4.clicked.connect(self.loadImageSequence)
        self.spinBox_8.valueChanged.connect(self.changeParas)
        self.spinBox_9.valueChanged.connect(self.changeParas)


    def changeParas(self, value):
            # Define a dictionary that maps spin box object names to parameter names
            name_to_param = {
                "spinBox": "resolution",
                "spinBox_2": "Max iteration",
                "doubleSpinBox": "dh",
                "doubleSpinBox_2": "dl",
                "spinBox_3": "width",
                "spinBox_4": "height",
                "spinBox_5": "RotationAngle",
                "spinBox_8": "RotationVelocity",
                "spinBox_9": "Duration",
                "doubleSpinBox_3": "ImageScalingFactor"
            }

            # Get the name of the spin box that was changed
            sender_name = self.sender().objectName()
            # Print the name and new value of the spin box that was changed
            if sender_name in name_to_param:
                param_name = name_to_param[sender_name]
                print(f"Parameters changed: {param_name}={value}")
                self.textBrowser.append(f"Parameters changed: {param_name}={value}")

    def previewSTL(self):
        # Create the file dialog box and get the STL filename selected by the user
        stl_filename, _ = QFileDialog.getOpenFileName(self, "Open STL File", "", "STL Files (*.stl)")

        if stl_filename:
            mesh_window = vedo.show(vedo.load(stl_filename), viewup="x")
            mesh_window.close()
            return
        else:
            # The user deselected the file and did not perform any operation
            return

    def runSTL(self):
        # Create the file dialog box and get the STL filename selected by the user
        stl_filename, _ = QFileDialog.getOpenFileName(self, "Open STL File", "", "STL Files (*.stl)")
        if stl_filename:
            # ask user to input file name
            file_name = self.lineEdit.text()
            #######################################################################################
            #######################################################################################
            #######################################################################################
            #######################################################################################
            #######################################################################################
            '''
            TO DO: CHANGE THE PATH ACCORDING TO YOUR OWN LAPTOP
            '''
            #######################################################################################
            #######################################################################################
            #######################################################################################
            #######################################################################################
            #######################################################################################
            target_file_path = dir_main + "\mytarget" + file_name + ".target"
            sino_file_path = dir_main + "mysinogram/" + file_name + ".sino"
            recon_file_path = dir_main + "mysinogram/" + file_name + ".recon"
            if file_name:
                resolution = self.spinBox.value()
                iteration = self.spinBox_2.value()
                h = self.doubleSpinBox.value()
                l = self.doubleSpinBox_2.value()
                method = self.comboBox.currentText()  # Gets the current options for comboBox
                check = self.comboBox_6.currentText()
                # If the user selects the file, create a target geo and display it
                print("Starts running voxelization")
                self.textBrowser.append("Starts running voxelization")
                target_geo = vam.geometry.TargetGeometry(stlfilename=stl_filename, resolution=resolution)
                print("Target geometry from stl is created")
                self.textBrowser.append("Target geometry from stl is created")
                target_geo.show()
                # target_geo is a geometry.TargetGeometry object
                # save the object as mytarget.target
                # ".target" is the default file extension
                target_geo.save(target_file_path)
                print(f"geometry.TargetGeometry object saved as {target_file_path}")
                self.textBrowser.append(f"geometry.TargetGeometry object saved as {target_file_path}")
                print("Voxelization finishes")
                self.textBrowser.append("Voxelization finishes")
                print("Displaying the voxel array")
                self.textBrowser.append("Displaying the voxel array")
                import vedo
                vol = vedo.Volume(target_geo.array).legosurface(vmin=0.5, vmax=1.5)
                vol.show(viewup="x")
                print("Voxel array vedo plot finishes")
                self.textBrowser.append("Voxel array vedo plot finishes")
                #vol.close()

                import numpy as np
                num_angles = 360
                angles = np.linspace(0, 360 - 360 / num_angles, num_angles)
                # Set the CUDA options according to the comboBox options
                try:
                    if check == 'Enabled':
                        proj_geo = vam.geometry.ProjectionGeometry(angles, ray_type='parallel', CUDA=True)
                    elif check == 'Disabled':
                        proj_geo = vam.geometry.ProjectionGeometry(angles, ray_type='parallel', CUDA=False)
                except Exception as e:
                    print("CUDA Error:", e)

                print("1D array of evenly spaced angles at which to perform projection is created")
                self.textBrowser.append("1D array of evenly spaced angles at which to perform projection is created")
                print("Optimization starts")
                self.textBrowser.append("Optimization starts")

                if method == 'PM':
                    optimizer_params = vam.optimize.Options(method='PM', n_iter=iteration, d_h=h, d_l=l,
                                                            filter='hamming',
                                                            verbose='plot')
                elif method == 'OSMO':
                    optimizer_params = vam.optimize.Options(method='OSMO', n_iter=iteration, filter='hamming',
                                                            verbose='plot')
                elif method == 'CAL':
                    optimizer_params = vam.optimize.Options(method='CAL', n_iter=iteration, filter='hamming',
                                                            verbose='plot')
                else:
                    optimizer_params = vam.optimize.Options(method='FBP', filter='hamming', verbose='plot')

                opt_sino, opt_recon, error = vam.optimize.optimize(target_geo, proj_geo, optimizer_params)
                opt_recon.show()
                print("Showing the reconstruction plots")
                self.textBrowser.append("Showing the reconstruction plots")
                opt_sino.show()
                print("Showing the sinogram plots")
                self.textBrowser.append("Showing the sinogram plots")
                print("Optimization finished")
                self.textBrowser.append("Optimization finished")
                # sino is a geometry.Sinogram object
                # save the sinogram as mysinogram.sino
                # ".sino" is the default file extension
                if sino_file_path:
                    opt_sino.save(sino_file_path)
                if recon_file_path:
                    opt_recon.save(recon_file_path)
                print("Saving reconstruction and sinogram files")
                self.textBrowser.append("Saving reconstruction and sinogram files")

                import vedo
                import vedo.applications
                vol = vedo.Volume(opt_recon.array, mode=0)
                vedo.applications.RayCastPlotter(vol, bg='black').show(viewup="x")
                print("Displaying the optimized reconstruction array")
                self.textBrowser.append("Displaying the optimized reconstruction array")
                # Close the plot window
                #vol.close()
            return
        return

    def imageSequence(self):
        d1 = self.spinBox_3.value()
        d2 = self.spinBox_4.value()
        rotation = self.spinBox_5.value()
        scaling = self.doubleSpinBox_3.value()
        print("Loading the optimized sinogram")
        self.textBrowser.append("Loading the optimized sinogram")
        sino_filename, _ = QFileDialog.getOpenFileName(self, "Open sino File", "", "sino Files (*.sino)")
        sino = vam.geometry.loadVolume(sino_filename)
        print("Creating image sequence configurations")
        self.textBrowser.append("Creating image sequence configurations")
        # iconfig0 = vam.imagesequence.ImageConfig(image_dims=(1920, 1080), array_num=2, array_offset=450)
        iconfig1 = vam.imagesequence.ImageConfig(image_dims=(d1, d2), rotate_angle=rotation, size_scale=scaling)
        print("Creating image sequence objects")
        self.textBrowser.append("Creating image sequence objects")
        # image_seq = vam.imagesequence.ImageSeq(image_config=iconfig0, sinogram=sino)
        # image_seq.preview()
        image_seq = vam.imagesequence.ImageSeq(image_config=iconfig1, sinogram=sino)
        #image_seq.preview()
        # imgseq is a imagesequence.ImageSeq object
        # save the imagesequence as myimagesequence.imgseq
        # ".imgseq" is the default file extension
        imageSeq_file_name, _ = QFileDialog.getSaveFileName(self, "Save ImageSequence", "",
                                                            "Image Sequence Files (*.imgseq)")
        if imageSeq_file_name:
            image_seq.save(imageSeq_file_name)
            print(f"geometry.Reconstruction object saved as {imageSeq_file_name}")
            self.textBrowser.append(f"geometry.Reconstruction object saved as {imageSeq_file_name}")

        checkVideos = self.comboBox_7.currentText()
        if checkVideos == 'Enabled':
            vRotation = self.spinBox_8.value()
            duration = self.spinBox_9.value()

            save_path, _ = QFileDialog.getSaveFileName(
                self, "Save As", "", "Video Files (*.mp4)")
            if save_path:
                self.vam.imagesequence.ImageSeq.saveAsVideo(
                    self, save_path=save_path, rot_vel=vRotation, duration=duration)


        checkImages = self.comboBox_8.currentText()
        if checkImages == 'Enabled':
            prefix = self.lineEdit_2.text()
            save_path, _ = QFileDialog.getSaveFileName(
                self, "Save As", "", "Images Files (*.png)")
            if save_path:
                self.saveAsImages(self, save_dir = save_path, image_prefix = prefix, image_type = '.png')

    def loadImageSequence(self):
        # to load saved ImageSeq objects, use the method in the imagesequence module
        # loadImageSeq()
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(None, "Select Image Sequence File", "",
                                                  "Image Sequence Files (*.imgseq)", options=options)
        print("Please select the image sequence file")
        self.textBrowser.append("Please select the image sequence file")
        if fileName:
            imgseq_load = vam.imagesequence.loadImageSeq(fileName)
            self.imgseq = imgseq_load
            self.current_frame = 0
            self.update()
            self.imgseq.preview()
            print(f"Starts showing image sequence {fileName}")
            self.textBrowser.append(f"Starts showing image sequence {fileName}")
        return


class Pjt(QWidget):
    def __init__(self):
        super(Pjt, self).__init__()
        #######################################################################################
        #######################################################################################
        #######################################################################################
        #######################################################################################
        #######################################################################################
        '''
        TO DO: CHANGE THE PATH ACCORDING TO YOUR OWN LAPTOP
        '''
        #######################################################################################
        #######################################################################################
        #######################################################################################
        #######################################################################################
        #######################################################################################
        ui_file_4 = os.path.join(dir_main, 'designer', 'Projection.ui')
        uic.loadUi(ui_file_4,self)
        self.setWindowTitle("Projection Window")

        self.show()
        print("Showing projection window...")
        self.textBrowser.append("Showing projection window...")
        print("Please specify the intended projecting parameters and choose a projection type")
        self.textBrowser.append("Please specify the intended projecting parameters and choose a projection type")
        self.pushButton_2.clicked.connect(self.pjtImgseq)
        self.spinBox_3.valueChanged.connect(self.changeParas)
        self.spinBox_4.valueChanged.connect(self.changeParas)
        self.spinBox_2.valueChanged.connect(self.changeParas)
        self.spinBox.valueChanged.connect(self.changeParas)
        self.spinBox_6.valueChanged.connect(self.changeParas)
        self.spinBox_5.valueChanged.connect(self.changeParas)
        self.spinBox_7.valueChanged.connect(self.changeParas)
        self.pushButton_3.clicked.connect(self.pjtSino)
        self.spinBox_8.valueChanged.connect(self.changeParas)
        self.doubleSpinBox.valueChanged.connect(self.changeParas)
        self.spinBox_9.valueChanged.connect(self.changeParas)
        self.spinBox_10.valueChanged.connect(self.changeParas)
        self.spinBox_11.valueChanged.connect(self.changeParas)
        self.spinBox_12.valueChanged.connect(self.changeParas)
        self.pushButton_4.clicked.connect(self.pjtVideo)
        self.pushButton_5.clicked.connect(self.pjtFolder)

    def changeParas(self, value):
        # Define a dictionary that maps spin box object names to parameter names
        name_to_param = {
            "spinBox_3": "d1",
            "spinBox_4": "d2",
            "spinBox": "arrayNum",
            "spinBox_2": "arrayOffset",
            "spinBox_6": "duration",
            "spinBox_5": "vRotation",
            "spinBox_7": "startIndex",
            "spinBox_8": "rotationAngle",
            "doubleSpinBox": "scaling",
            "spinBox_9": "c1",
            "spinBox_10": "c2",
            "spinBox_11": "c3",
            "spinBox_12": "screen_num",

        }

        # Get the name of the spin box that was changed
        sender_name = self.sender().objectName()

        # If the sender_name is in name_to_param, print the parameter name and new value
        if sender_name in name_to_param:
            param_name = name_to_param[sender_name]
            print(f"Parameter changed: {param_name}={value}")
            self.textBrowser.append(f"Parameter changed: {param_name}={value}")

    def pjtImgseq(self):
        d1 = self.spinBox_3.value()
        d2 = self.spinBox_4.value()
        arrayNum = self.spinBox.value()
        arrayOffset = self.spinBox_2.value()
        duration = self.spinBox_6.value()
        vRotation = self.spinBox_5.value()
        startIndex = self.spinBox_7.value()
        rotationAngle = self.spinBox_8.value()
        scaling = self.doubleSpinBox.value()
        c1 = self.spinBox_9.value()
        c2 = self.spinBox_10.value()
        c3 = self.spinBox_11.value()
        screen_num = self.spinBox_12.value()
        window = self.comboBox.currentText()
        if __name__ == '__main__':
            # Sinogram object
            options = QFileDialog.Options()
            options |= QFileDialog.DontUseNativeDialog
            fileName, _ = QFileDialog.getOpenFileName(None, "Select Sinogram File", "",
                                                      "Sinogram Files (*.sino)", options=options)

            if fileName:
                sino = vam.geometry.loadVolume(fileName)
                iconfig = vam.imagesequence.ImageConfig(image_dims=(d1, d2), rotate_angle=rotationAngle,
                                                        size_scale=scaling)
                image_seq = vam.imagesequence.ImageSeq(image_config=iconfig, sinogram=sino)
                if window == 'False':
                    vam.dlp.players.player(image_seq=image_seq, pause_bg_color=(c1, c2, c3), duration=duration,
                                       rot_vel=vRotation, start_index=startIndex, windowed=False, screen_num=screen_num)
                elif window == 'True':
                    vam.dlp.players.player(image_seq=image_seq, pause_bg_color=(c1, c2, c3), duration=duration,
                                           rot_vel=vRotation, start_index=startIndex, windowed=True,
                                           screen_num=screen_num)
                self.textBrowser.append("Start projecting image sequence...")
                print("Start projecting image sequence...")
            return

    def pjtSino(self):
        d1 = self.spinBox_3.value()
        d2 = self.spinBox_4.value()
        # arrayNum = self.spinBox.value()
        # arrayOffset = self.spinBox_2.value()
        # duration = self.spinBox_6.value()
        vRotation = self.spinBox_5.value()
        # startIndex = self.spinBox_7.value()
        rotationAngle = self.spinBox_8.value()
        scaling = self.doubleSpinBox.value()
        screen_num = self.spinBox_12.value()
        window = self.comboBox.currentText()
        self.textBrowser.append("Please specify the intended projecting parameters and select the sinogram file")
        print("Please specify the intended projecting parameters and select the sinogram file")


        if __name__ == '__main__':
            # Sinogram object
            options = QFileDialog.Options()
            options |= QFileDialog.DontUseNativeDialog
            fileName, _ = QFileDialog.getOpenFileName(None, "Select Sinogram File", "",
                                                      "Sinogram Files (*.sino)", options=options)
            if fileName:
                # Sinogram object
                sino = vam.geometry.loadVolume(fileName)
                iconfig = vam.imagesequence.ImageConfig(image_dims=(d1, d2), rotate_angle=rotationAngle,
                                                        size_scale=scaling)
                if window == 'False':
                    vam.dlp.players.player(sinogram=sino, image_config=iconfig, rot_vel=vRotation, windowed=False,
                                       screen_num=screen_num)
                elif window == 'True':
                    vam.dlp.players.player(sinogram=sino, image_config=iconfig, rot_vel=vRotation, windowed=True,
                                       screen_num=screen_num)
                self.textBrowser.append("Start projecting sinogram object...")
                print("Start projecting sinogram object...")
            return

    def pjtVideo(self):
        self.textBrowser.append("Please specify the intended projecting parameters and select the mp4 video file")
        print("Please specify the intended projecting parameters and select the mp4 video file")
        d1 = self.spinBox_3.value()
        d2 = self.spinBox_4.value()
        # arrayNum = self.spinBox.value()
        # arrayOffset = self.spinBox_2.value()
        # duration = self.spinBox_6.value()
        vRotation = self.spinBox_5.value()
        # startIndex = self.spinBox_7.value()
        rotationAngle = self.spinBox_8.value()
        scaling = self.doubleSpinBox.value()
        screen_num = self.spinBox_12.value()
        fps = self.comboBox_2.currentText()
        window = self.comboBox.currentText()
        if __name__ == '__main__':
            # Sinogram object
            options = QFileDialog.Options()
            options |= QFileDialog.DontUseNativeDialog
            fileName, _ = QFileDialog.getOpenFileName(None, "Select mp4 File", "",
                                                      "Sinogram Files (*.mp4)", options=options)
            if fileName:
                if window == 'False':
                    vam.dlp.players.player(video=fileName, rot_vel=vRotation, windowed=False, screen_num=screen_num)
                elif window == 'True':
                    vam.dlp.players.player(video=fileName, rot_vel=vRotation, windowed=True, screen_num=screen_num)
                self.textBrowser.append("Start projecting video...")
                print("Start projecting video...")
            return

    def pjtFolder(self):
            self.textBrowser.append("Please specify the intended projecting parameters and select the image folder")
            print("Please specify the intended projecting parameters and select the image folder")
            d1 = self.spinBox_3.value()
            d2 = self.spinBox_4.value()
            # arrayNum = self.spinBox.value()
            # arrayOffset = self.spinBox_2.value()
            # duration = self.spinBox_6.value()
            vRotation = self.spinBox_5.value()
            # startIndex = self.spinBox_7.value()
            rotationAngle = self.spinBox_8.value()
            scaling = self.doubleSpinBox.value()
            screen_num = self.spinBox_12.value()
            fps = self.comboBox_2.currentText()
            window = self.comboBox.currentText()
            if __name__ == '__main__':
                dialog = QFileDialog()
                dialog.setFileMode(QFileDialog.Directory)
                if dialog.exec_() == QFileDialog.Accepted:
                    images_dir = dialog.selectedFiles()[0]
                    if window == 'True':
                        vam.dlp.players.player(images_dir=images_dir, rot_vel=vRotation, windowed=True)
                    elif window == 'False':
                        vam.dlp.players.player(images_dir=images_dir, rot_vel=vRotation, windowed=False)
                    self.textBrowser.append("Start projecting image folder...")
                    print("Start projecting image folder...")
                return



class Main1(QWidget):
    def __init__(self):
        super(Main1, self).__init__()
        #######################################################################################
        #######################################################################################
        #######################################################################################
        #######################################################################################
        #######################################################################################
        '''
        TO DO: CHANGE THE PATH ACCORDING TO YOUR OWN LAPTOP
        '''
        #######################################################################################
        #######################################################################################
        #######################################################################################
        #######################################################################################
        #######################################################################################
        ui_file_2 = os.path.join(dir_main, 'designer', 'MainWindow1.ui')
        uic.loadUi(ui_file_2, self)
        print("Showing main window...")
        self.textBrowser.append("Showing main window...")

        self.show()
        self.pushButton.clicked.connect(self.focus)
        self.pushButton_2.clicked.connect(self.axis)
        self.pushButton_6.clicked.connect(self.runSTL)
        self.spinBox.valueChanged.connect(self.changeParas)
        self.spinBox_2.valueChanged.connect(self.changeParas)
        self.pushButton_3.clicked.connect(self.pjtSino)
        self.spinBox_4.valueChanged.connect(self.changeParas)
        self.spinBox_3.valueChanged.connect(self.changeParas)
        self.doubleSpinBox.valueChanged.connect(self.changeParas)
        self.pushButton_5.clicked.connect(self.previewSTL)

    @staticmethod
    def focus():
        vam.dlp.setup.Focus(slices=20, N_screen=(1920, 1080))

    @staticmethod
    def axis():
        vam.dlp.setup.AxisAlignment(half_line_thickness=1, half_line_separation=200)


    def changeParas(self, value):
        # Define a dictionary that maps spin box object names to parameter names
        name_to_param = {
            "spinBox": "resolution",
            "spinBox_2": "Max iteration",
            "spinBox_3": "rotation velocity",
            "spinBox_4": "duration",
            "doubleSpinBox": "scaling factor"
        }

        # Get the name of the spin box that was changed
        sender_name = self.sender().objectName()

        # Print the name and new value of the spin box that was changed
        if sender_name in name_to_param:
            param_name = name_to_param[sender_name]
            print(f"Parameters changed: {param_name}={value}")
            self.textBrowser.append(f"Parameters changed: {param_name}={value}")

    def previewSTL(self):
        # Create the file dialog box and get the STL filename selected by the user
        stl_filename, _ = QFileDialog.getOpenFileName(self, "Open STL File", "", "STL Files (*.stl)")
        print("Please select an STL file to preview")
        self.textBrowser.append("Please select an STL file to preview")

        if stl_filename:
            mesh_window = vedo.show(vedo.load(stl_filename), viewup="x")
            mesh_window.close()
            return
        else:
            # The user deselected the file and did not perform any operation
            return

    def runSTL(self):
        try:
            print("Please select an STL file")
            self.textBrowser.append("Please select an STL file")
            # Create the file dialog box and get the STL filename selected by the user
            stl_filename, _ = QFileDialog.getOpenFileName(self, "Open STL File", "", "STL Files (*.stl)")
            print("STL file preparation finishes")
            self.textBrowser.append("STL file preparation finishes")
            print('Please input the saved name and optimization parameters, then press \"Run 3D Optimization\"')
            self.textBrowser.append("Please input the saved name and optimization parameters, then press \"Run 3D "
                                    "Optimization\"")
            if stl_filename:
                # ask user to input file name
                file_name = self.lineEdit_2.text()
                #######################################################################################
                #######################################################################################
                #######################################################################################
                #######################################################################################
                #######################################################################################
                '''
                TO DO: CHANGE THE PATH ACCORDING TO YOUR OWN LAPTOP
                '''
                #######################################################################################
                #######################################################################################
                #######################################################################################
                #######################################################################################
                #######################################################################################
                target_file_path = dir_main + "mytarget/" + file_name + ".target"
                sino_file_path = dir_main + "mysinogram/" + file_name + ".sino"
                recon_file_path = dir_main + "mysinogram/" + file_name + ".recon"
                if file_name:
                    resolution = self.spinBox.value()
                    iteration = self.spinBox_2.value()
                    method = self.comboBox.currentText()  # Gets the current options for comboBox
                    check = self.comboBox_2.currentText() # Gets the current options for comboBox_2

                    print("Starts running voxelization")
                    self.textBrowser.append("Starts running voxelization")
                    target_geo = vam.geometry.TargetGeometry(stlfilename=stl_filename, resolution=resolution)
                    print("Target geometry from stl is created")
                    self.textBrowser.append("Target geometry from stl is created")
                    target_geo.show()

                    # target_geo is a geometry.TargetGeometry object
                    # save the object as mytarget.target
                    # ".target" is the default file extension
                    target_geo.save(target_file_path)
                    print(f"geometry.TargetGeometry object saved as {target_file_path}")
                    self.textBrowser.append(f"geometry.TargetGeometry object saved as {target_file_path}")
                    print("Voxelization finishes")
                    self.textBrowser.append("Voxelization finishes")
                    print("Displaying the voxel array")
                    self.textBrowser.append("Displaying the voxel array")
                    import vedo
                    import numpy as np
                    # Create a Volume object and display it
                    vol = vedo.Volume(target_geo.array).legosurface(vmin=0.5, vmax=1.5)
                    vol.show(viewup="x")
                    # Print a message indicating that the plot has finished
                    print("Voxel array vedo plot finishes")
                    self.textBrowser.append("Voxel array vedo plot finishes")
                    #vol.close()

                    # Define projection geometry
                    num_angles = 360
                    angles = np.linspace(0, 360 - 360 / num_angles, num_angles)
                    # Set the CUDA options according to the comboBox options
                    try:
                        if check == 'Enabled':
                            proj_geo = vam.geometry.ProjectionGeometry(angles, ray_type='parallel', CUDA=True)
                        elif check == 'Disabled':
                            proj_geo = vam.geometry.ProjectionGeometry(angles, ray_type='parallel', CUDA=False)
                    except Exception as e:
                        print("CUDA Error:", e)
                    print("1D array of evenly spaced angles at which to perform projection is created")
                    self.textBrowser.append("1D array of evenly spaced angles at which to perform projection is created")
                    print("Optimization starts")
                    self.textBrowser.append("Optimization starts")
                    # Set the optimization parameters according to the comboBox options
                    if method == 'PM':
                        optimizer_params = vam.optimize.Options(method='PM', n_iter=iteration, d_h=0.85, d_l=0.60,
                                                                filter='hamming', verbose='plot')
                    elif method == 'OSMO':
                        optimizer_params = vam.optimize.Options(method='OSMO', n_iter=iteration, filter='hamming',
                                                                verbose='plot')
                    elif method == 'CAL':
                        optimizer_params = vam.optimize.Options(method='CAL', n_iter=iteration, filter='hamming',
                                                                verbose='plot')
                    else:
                        optimizer_params = vam.optimize.Options(method='FBP', filter='hamming', verbose='plot')

                    opt_sino, opt_recon, error = vam.optimize.optimize(target_geo, proj_geo, optimizer_params)
                    opt_recon.show()
                    print("Showing the reconstruction plots")
                    self.textBrowser.append("Showing the reconstruction plots")
                    opt_sino.show()
                    print("Showing the sinogram plots")
                    self.textBrowser.append("Showing the sinogram plots")
                    print("Optimization finished")
                    self.textBrowser.append("Optimization finished")
                    if sino_file_path:
                        opt_sino.save(sino_file_path)
                    if recon_file_path:
                        opt_recon.save(recon_file_path)
                    print("Saving reconstruction and sinogram files")
                    self.textBrowser.append("Saving reconstruction and sinogram files")
                    import vedo
                    import vedo.applications
                    vol = vedo.Volume(opt_recon.array, mode=0)
                    vedo.applications.RayCastPlotter(vol, bg='black').show(viewup="x")
                    print("Displaying the optimized reconstruction array")
                    self.textBrowser.append("Displaying the optimized reconstruction array")
                    # Close the plot window
                    #vol.close()
                return
            return

        except Exception as e:
            print("Error:", e)

    def pjtSino(self):
        duration = self.spinBox_4.value()
        vRotation = self.spinBox_3.value()
        scaling = self.doubleSpinBox.value()
        print("Please select the sinogram file for projection")
        self.textBrowser.append("Please select the sinogram file for projection")
        print("And specify the main intended projecting parameters")
        self.textBrowser.append("And specify the main intended projecting parameters")

        if __name__ == '__main__':
            # Sinogram object
            options = QFileDialog.Options()
            options |= QFileDialog.DontUseNativeDialog
            fileName, _ = QFileDialog.getOpenFileName(None, "Select Sinogram File", "",
                                                      "Sinogram Files (*.sino)", options=options)

            if fileName:
                try:
                    # Sinogram object
                    sino = vam.geometry.loadVolume(fileName)
                    iconfig = vam.imagesequence.ImageConfig(image_dims=(1920, 1080), rotate_angle=0, size_scale=scaling)
                    vam.dlp.players.player(sinogram=sino, image_config=iconfig, rot_vel=vRotation,
                                           windowed=False,
                                           screen_num=-1, duration=duration)
                except Exception as e:
                    print("Error:", e)
                print("Projecting sinogram object...")
                self.textBrowser.append("Projecting sinogram object...")
            return


class MainGUI(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainGUI, self).__init__()
        #######################################################################################
        #######################################################################################
        #######################################################################################
        #######################################################################################
        #######################################################################################
        '''
        TO DO: CHANGE THE PATH ACCORDING TO YOUR OWN LAPTOP
        '''
        #######################################################################################
        #######################################################################################
        #######################################################################################
        #######################################################################################
        #######################################################################################
        ui_file_3 = os.path.join(dir_main, 'designer', 'MainWindow.ui')
        uic.loadUi(ui_file_3, self)
        self.show()
        print("Showing welcoming window...")
        self.statusbar.showMessage(
            "© Copyright 2023 — Acoustic Robotics Systems Laboratory, made by Shengyang Zhuang and Prajwal Agrawal")

        # Connect the signal slot for a menu item
        self.actionMain.triggered.connect(self.showMain)
        self.aprojection.triggered.connect(self.showPjt)
        self.action3D_Optimization.triggered.connect(self.showOpt)

    def showMain(self):
        try:
            main1_widget = Main1()
            self.setCentralWidget(main1_widget)
        except Exception as e:
            print("Error loading ui:", e)

    def showPjt(self):
        try:
            # Load the UI file for Pjt and create the window
            pjt_widget = Pjt()
            # Set the Pjt window to the center of the main window
            self.setCentralWidget(pjt_widget)
        except Exception as e:
            print("Error loading ui:", e)

    def showOpt(self):
        print("showing optimization window...")
        # Load the UI file for Opt and create the window
        opt_widget = Opt()
        # Set the Opt window to the center of the main window
        self.setCentralWidget(opt_widget)


def main():
    app = QApplication([])
    w = MainGUI()
    print("MainGUI object created. Starting event loop...")
    w.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()

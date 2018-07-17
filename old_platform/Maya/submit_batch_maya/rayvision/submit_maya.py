#! /usr/bin/env python
# coding=utf-8
import os
import pymel.core as pm
import munu
import pprint
import re


class Task(dict):

    def __init__(self):
        ''

    def is_app_logined(self):
        projetct_info = self.get_projects()
        if isinstance(projetct_info, dict):
            return 1

    def get_projects(self):
        return munu.RvOs.get_projects()

    def is_valid_frames(self, frames):
        is_valid = 1
        frames = frames.replace(" ", "")
        for i in frames.split(","):
            if not re.findall(r'^\d+$', i) and not re.findall(r'^\d+-\d+\[\d+\]$', i):
                is_valid = 0

        return is_valid

    def is_positive_number(self, number):
        number = str(number)
        if re.findall(r'^\d+$', number):
            return 1

    def is_valid_test_frames(self, test_frames, frames):
        is_valid = 1
        test_frames = test_frames.replace(" ", "")

        for i in test_frames.split(","):
            if not re.findall(r'^\d+$', i) and not re.findall(r'^\d+-\d+$', i):
                is_valid = 0

        if is_valid:
            for i in munu.Frames(test_frames):
                if i not in munu.Frames(self["frames"]):
                    is_valid = 0

        return is_valid


class MayaTask2(Task):

    def __init__(self):
        Task.__init__(self)
        self.render_settings = pm.PyNode("defaultRenderGlobals")
        self.resolution_settings = pm.PyNode("defaultResolution")
        self.start_frame = int(self.render_settings.startFrame.get())
        self.end_frame = int(self.render_settings.endFrame.get())
        self.by_frame = int(self.render_settings.byFrameStep.get())

    def get_width(self):
        return int(self.resolution_settings.width.get())

    def get_height(self):
        return int(self.resolution_settings.height.get())

    def get_camera(self):
        return pm.ls(type="camera")

    def get_renderable_camera(self):
        return [i.name() for i in pm.ls(type="camera") if i.renderable.get()][0]

    def get_frames(self):
        return "%s-%s[%s]" % (self.start_frame, self.end_frame, self.by_frame)

    def get_test_frames(self):
        return "%s,%s,%s" % (self.start_frame,
                             (self.start_frame + self.end_frame) / 2,
                             self.end_frame)

    def get_scene_name(self):
        return pm.sceneName()


class SubmitMayaUi(MayaTask2):

    def __init__(self):
        MayaTask2.__init__(self)
        self.template = self.create_liuqiang_template()
        self.settings_crtl = {}
        self.button_crtl = {}
        if self.is_app_logined():
            self.show_window()
            self.set_default()
        else:
            self.show_confirm_dialog("Please login Renderbus Desktop APP firstly!", close=0)

    def create_liuqiang_template(self):
        template = pm.uiTemplate('liuqiang_template', force=1)
        template.define(pm.frameLayout, borderVisible=1, labelVisible=1,
                        width=410, borderStyle="etchedIn")
        template.define(pm.columnLayout)
        template.define(pm.rowLayout, numberOfColumns=2, cw2=[150, 100])
        template.define(pm.button, width=100, align='right')
        template.define(pm.text, align='left')
        template.define(pm.textFieldGrp, cl2=["right", "left"], cw2=[150, 80])
        template.define(pm.optionMenuGrp, cl2=["right", "left"], cw2=[150, 100])
        template.define(pm.checkBox)
        template.define(pm.checkBoxGrp, cl2=["right", "left"])
        return template

    def show_window(self):
        window_name = "SubmitMayaRenderTaskToRayvisionCloud"

        if pm.window(window_name, q=1, ex=1):
            pm.deleteUI(window_name)
        if pm.windowPref(window_name, exists=1):
            pm.windowPref(window_name, remove=1)

        with pm.window(window_name, sizeable=0) as self.window:
            with self.template:
                with pm.columnLayout():
                    with pm.frameLayout("Project"):
                        with pm.optionMenuGrp(label='Select Project') as self.settings_crtl["project"]:
                            projetct_info = self.get_projects()
                            if isinstance(projetct_info, dict):
                                for i in sorted(projetct_info.values()):
                                    pm.menuItem(label=i)

                    with pm.frameLayout("Frame Range"):
                        self.settings_crtl["frames"] = pm.textFieldGrp(label="Frame Range")

                    with pm.frameLayout("Renderable Cameras"):
                        with pm.rowLayout():
                            pm.text("")
                            self.settings_crtl["enable_custom_camera"] = pm.checkBox(label="Enable Custom Camera",
                                                                                     cc=self.enable_custom_camera)
                        with pm.optionMenuGrp(label='Renderable Camera') as self.settings_crtl["camera"]:
                            for i in sorted(self.get_camera()):
                                pm.menuItem(label=i)

                    with pm.frameLayout("Image Size"):
                        self.settings_crtl["width"] = pm.textFieldGrp(label="Width")
                        self.settings_crtl["height"] = pm.textFieldGrp(label="Height")

                    with pm.frameLayout("Test frames"):
                        with pm.rowLayout():
                            pm.text("")
                            self.settings_crtl["enable_test_frames"] = pm.checkBox(label="Enable Test Frames",
                                                                                   cc=self.enable_test_frames)
                        self.settings_crtl["test_frames"] = pm.textFieldGrp(label="Test Frames")
                        with pm.optionMenuGrp(label='After Test Frames finish') as self.settings_crtl["after_test_frames"]:
                            pm.menuItem(label="Auto full speed render after test frames finish")
                            pm.menuItem(label="Stop the task after test frames finish")

                    with pm.frameLayout("Tiles Render"):
                        with pm.optionMenuGrp(label='tiles Size') as self.settings_crtl["tiles"]:
                            for i in [1, 2, 4, 8, 16, 32, 64]:
                                pm.menuItem(label=i)
                        with pm.rowLayout():
                            pm.text("")
                            pm.text("1.Output image suffix should be image format type\n"
                                    "(abc.jpg),not be number(abc.iff.1011).")
                        with pm.rowLayout():
                            pm.text("")
                            pm.text("2.Only support mentalray and arnold currently.\n"
                                    "Please supply us renderer and image format if\n"
                                    "you want to use this function,we will test and\n"
                                    "feedback to you asap.")

                    with pm.frameLayout("Cloud Render Node Rquirement"):
                        with pm.optionMenuGrp(label='Memory Rquirement') as self.settings_crtl["memory_requirement"]:
                            for i in ["Normal", "64GB", "96GB", "128GB"]:
                                pm.menuItem(label=i)

                    with pm.rowLayout():
                        pm.text("")
                        self.button_crtl["submit"] = pm.button(label="SUBMIT", c=self.press_submit)

    def set_default(self):
        self.settings_crtl["enable_custom_camera"].setValue(0)
        self.settings_crtl["camera"].setValue(self.get_renderable_camera())
        self.settings_crtl["camera"].setEnable(0)

        self.settings_crtl["enable_test_frames"].setValue(0)
        self.settings_crtl["test_frames"].setEnable(0)
        self.settings_crtl["after_test_frames"].setEnable(0)
        self.settings_crtl["test_frames"].setText(self.get_test_frames())
        self.settings_crtl["frames"].setText(self.get_frames())

        self.settings_crtl["width"].setText(self.get_width())
        self.settings_crtl["height"].setText(self.get_height())

    def enable_custom_camera(self, *args):
        self.settings_crtl["camera"].setEnable(val=self.settings_crtl["enable_custom_camera"].getValue())

    def enable_test_frames(self, *args):
        self.settings_crtl["test_frames"].setEnable(val=self.settings_crtl["enable_test_frames"].getValue())
        self.settings_crtl["after_test_frames"].setEnable(val=self.settings_crtl["enable_test_frames"].getValue())

    def press_submit(self, *args):
        self.get_ui_settings()
        if not self.check_ui_settings():
            return 0

        if os.path.exists(self["scene_name"]):
            if munu.RvOs.get_desktop_app():
                task = munu.MayaTask(munu.get_submit_options(self))
                task.set_custom_settings(self)
                result = task.submit2()
                if result is None:
                    self.show_confirm_dialog("submit task spended too much time!")
                elif result == 0:
                    self.show_confirm_dialog()
                else:
                    self.show_confirm_dialog("submit task encounted error!")
            else:
                self.show_confirm_dialog("Please login Renderbus Desktop APP firstly!")
        else:
            self.show_confirm_dialog("Please save your maya file first!")

    def get_ui_settings(self, *args):
        for i in self.settings_crtl:
            if "getText" in dir(self.settings_crtl[i]):
                self[i] = self.settings_crtl[i].getText()
            elif "getValue" in dir(self.settings_crtl[i]):
                self[i] = self.settings_crtl[i].getValue()

        if self.settings_crtl["enable_test_frames"].getValue():
            self["after_test_frames"] = self.settings_crtl["after_test_frames"].getSelect()
            if self["after_test_frames"] == 1:
                self["after_test_frames"] = "fullSpeed"
            else:
                self["after_test_frames"] = "stop"
        else:
            self["test_frames"] = ""
            self["after_test_frames"] = ""

        self["scene_name"] = self.get_scene_name()
        # pprint.pprint(self)

        if self["memory_requirement"] == "Normal":
            self["memory_requirement"] = ""

    def check_ui_settings(self):
        is_valid = 1
        if not self.is_valid_frames(self["frames"]):
            is_valid = 0
            self.show_confirm_dialog("Invalid render frame range,please input again(Example 1,3,5,10-20[1],30-40[2])", close=0)

        if self["test_frames"]:
            if not self.is_valid_test_frames(self["test_frames"], self["frames"]):
                is_valid = 0
                self.show_confirm_dialog("Prior frames not in render frames,please input again.", close=0)

        if not self.is_positive_number(self["width"]) or not self.is_positive_number(self["height"]):
            is_valid = 0
            self.show_confirm_dialog("Invalid resolution setting,please input again.", close=0)

        return is_valid

    def show_confirm_dialog(self, error_message="", close=1):
        if error_message:
            pm.confirmDialog(title="Failed!", button="OK", message=error_message)
        else:
            pm.confirmDialog(title="Success!", button="OK", message="Submit render task Success!")

        if close:
            pm.deleteUI(self.window)

if __name__ == "__main__":
    SubmitMayaUi()

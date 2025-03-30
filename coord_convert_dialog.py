# -*- coding: utf-8 -*-
"""
/***************************************************************************
 CoordConvertDialog
                                 A QGIS plugin
 Converts coordinates between WGS84, GCJ02, and BD09
                              -------------------
        begin                : 2025
 ***************************************************************************/
"""

import os
import webbrowser

from qgis.PyQt import uic
from qgis.PyQt.QtCore import QSettings
from qgis.PyQt.QtWidgets import QMessageBox, QDialog, QButtonGroup, QComboBox
from qgis.core import QgsMapLayerProxyModel, QgsProject


# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'coord_convert_dialog_base.ui'))


class CoordConvertDialog(QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        """Constructor."""
        super(CoordConvertDialog, self).__init__(parent)
        # Set up the user interface from Designer
        self.setupUi(self)
        
        # 初始化语言设置
        settings = QSettings()
        # 默认使用中文
        self.locale = settings.value('CoordConvert/locale', 'zh')
        
        # 设置翻译字典
        self.translations = {
            'en': {
                'Coordinate Converter': 'Coordinate Converter',
                'Input': 'Input',
                'Input Layer:': 'Input Layer:',
                'Input Coordinate System': 'Input Coordinate System',
                'WGS84': 'WGS84',
                'GCJ02 (Mars Coordinates)': 'GCJ02 (Mars Coordinates)',
                'BD09 (Baidu Coordinates)': 'BD09 (Baidu Coordinates)',
                'Output': 'Output',
                'Use Temporary Layer': 'Use Temporary Layer',
                'Output Path:': 'Output Path:',
                'Browse...': 'Browse...',
                'Output Format:': 'Output Format:',
                'Output Coordinate System': 'Output Coordinate System',
                'Load Output Layer When Completed': 'Load Output Layer When Completed',
                'Convert': 'Convert',
                'Language Changed': 'Language Changed',
                'The language has been changed to English successfully.': 'The language has been changed to English successfully.',
                'Language changed, but some text may not be translated.': 'Language changed, but some text may not be translated.',
                'Error': 'Error',
                'Failed to switch language': 'Failed to switch language',
                'Select a layer': 'Select a layer',
                'About': 'About'
            },
            'zh': {
                'Coordinate Converter': '坐标转换器',
                'Input': '输入',
                'Input Layer:': '输入图层:',
                'Input Coordinate System': '输入坐标系',
                'WGS84': 'WGS84',
                'GCJ02 (Mars Coordinates)': 'GCJ02 (火星坐标)',
                'BD09 (Baidu Coordinates)': 'BD09 (百度坐标)',
                'Output': '输出',
                'Use Temporary Layer': '使用临时图层',
                'Output Path:': '输出路径:',
                'Browse...': '浏览...',
                'Output Format:': '输出格式:',
                'Output Coordinate System': '输出坐标系',
                'Load Output Layer When Completed': '完成时加载输出图层',
                'Convert': '转换',
                'Language Changed': '语言已更改',
                'The language has been changed to English successfully.': '语言已成功更改为中文。',
                'Language changed, but some text may not be translated.': '语言已更改，但某些文本可能未被翻译。',
                'Error': '错误',
                'Failed to switch language': '切换语言失败',
                'Select a layer': '选择图层',
                'About': '关于'
            }
        }
        
        # 更新语言按钮文本
        self.update_language_button_text()
        
        # 应用初始翻译
        self.apply_translations()
        
        # 初始化UI组件 - 移动到翻译字典设置后
        self.initialize_ui()
        
        # 连接语言切换按钮
        self.btnSwitchLanguage.clicked.connect(self.switch_language)
        
        # 连接关于按钮
        self.btnAbout.clicked.connect(self.open_about_page)
        
        # 修改帮助按钮行为 - 移除帮助按钮
        self.button_box.setStandardButtons(self.button_box.Close)
        
        # 连接临时图层复选框
        self.chkUseTemporaryLayer.toggled.connect(self.toggle_output_controls)
        
        # 确保临时图层选项默认被勾选并触发相关控件状态
        self.chkUseTemporaryLayer.setChecked(True)
        self.toggle_output_controls(True)
        
        # 设置其他连接
        self.setup_connections()
        
        # 创建坐标系统单选按钮组
        self.input_crs_group = QButtonGroup(self)
        self.input_crs_group.addButton(self.radioButton_wgs84_in)
        self.input_crs_group.addButton(self.radioButton_gcj02_in)
        self.input_crs_group.addButton(self.radioButton_bd09_in)
        
        self.output_crs_group = QButtonGroup(self)
        self.output_crs_group.addButton(self.radioButton_wgs84_out)
        self.output_crs_group.addButton(self.radioButton_gcj02_out)
        self.output_crs_group.addButton(self.radioButton_bd09_out)
        
        # 设置默认单选按钮选择
        self.radioButton_wgs84_in.setChecked(True)
        self.radioButton_gcj02_out.setChecked(True)
        
        # 连接输入坐标系单选按钮的信号
        self.radioButton_wgs84_in.toggled.connect(self.on_input_crs_changed)
        self.radioButton_gcj02_in.toggled.connect(self.on_input_crs_changed)
        self.radioButton_bd09_in.toggled.connect(self.on_input_crs_changed)
        
        # 初始调用一次，确保初始状态正确
        self.on_input_crs_changed()

    def open_about_page(self):
        """打开关于页面"""
        webbrowser.open("https://github.com/solidjerryc/chinese-coordinate-converter")

    def initialize_ui(self):
        """初始化UI组件"""
        # 初始化输入图层下拉框
        self.setup_input_layer_combobox()

    def setup_input_layer_combobox(self):
        """设置输入图层下拉框"""
        # 清空下拉框
        self.cboInputLayer.clear()
        
        # 填充矢量图层列表
        self.populate_vector_layers()
        
        # 使用下拉框的 showPopup 事件来触发图层列表刷新
        # 这比之前使用 view().pressed 更可靠
        self.cboInputLayer.showPopup = self.on_input_layer_popup
        
        # 确保图层下拉框是可用的
        self.cboInputLayer.setEnabled(True)
        
        # 如果有图层，默认选择第一个图层
        if self.cboInputLayer.count() > 0:
            self.cboInputLayer.setCurrentIndex(0)

    def on_input_layer_popup(self):
        """当输入图层下拉框弹出时触发"""
        # 首先刷新图层列表
        self.refresh_vector_layers()
        
        # 然后调用原始的 showPopup 方法显示下拉列表
        # 使用 super() 获取 QComboBox 类，然后调用其 showPopup 方法
        QComboBox.showPopup(self.cboInputLayer)

    def populate_vector_layers(self):
        """填充矢量图层列表"""
        # 获取当前项目中的所有矢量图层
        vector_layers = [layer for layer in QgsProject.instance().mapLayers().values() 
                        if layer.type() == 0]  # 0表示矢量图层类型
        
        # 添加所有矢量图层到下拉框
        for layer in vector_layers:
            self.cboInputLayer.addItem(layer.name(), layer.id())

    def refresh_vector_layers(self):
        """刷新矢量图层列表"""
        # 保存当前选中的图层ID
        current_layer_id = self.cboInputLayer.currentData()
        
        # 清空下拉框
        self.cboInputLayer.clear()
        
        # 重新填充矢量图层列表
        self.populate_vector_layers()
        
        # 尝试重新选择之前选中的图层
        if current_layer_id:
            index = self.cboInputLayer.findData(current_layer_id)
            if index >= 0:
                self.cboInputLayer.setCurrentIndex(index)
        # 如果没有之前选中的图层但有图层列表，选择第一个
        elif self.cboInputLayer.count() > 0:
            self.cboInputLayer.setCurrentIndex(0)

    def setup_connections(self):
        """设置UI组件的连接"""
        # 在这里添加设置连接的代码
        pass
        
    def toggle_output_controls(self, checked):
        """根据是否使用临时图层切换输出控件的启用状态"""
        # 如果使用临时图层，禁用输出路径和格式选择控件
        self.leOutputPath.setEnabled(not checked)
        self.btnBrowse.setEnabled(not checked)
        self.cboOutputFormat.setEnabled(not checked)
        
    def on_input_crs_changed(self):
        """当输入坐标系改变时，更新输出坐标系的可选状态"""
        # 首先启用所有输出坐标系选项
        self.radioButton_wgs84_out.setEnabled(True)
        self.radioButton_gcj02_out.setEnabled(True)
        self.radioButton_bd09_out.setEnabled(True)
        
        # 然后禁用与当前选中的输入坐标系相同的输出选项
        if self.radioButton_wgs84_in.isChecked():
            self.radioButton_wgs84_out.setEnabled(False)
            # 如果当前禁用的选项是被选中的，自动选中下一个可选选项
            if self.radioButton_wgs84_out.isChecked():
                self.radioButton_gcj02_out.setChecked(True)
        elif self.radioButton_gcj02_in.isChecked():
            self.radioButton_gcj02_out.setEnabled(False)
            if self.radioButton_gcj02_out.isChecked():
                self.radioButton_wgs84_out.setChecked(True)
        elif self.radioButton_bd09_in.isChecked():
            self.radioButton_bd09_out.setEnabled(False)
            if self.radioButton_bd09_out.isChecked():
                self.radioButton_wgs84_out.setChecked(True)

    def update_language_button_text(self):
        """根据当前语言设置语言切换按钮的文本"""
        self.btnSwitchLanguage.setText("En/Zh")
    
    def tr(self, text):
        """根据当前语言获取文本的翻译"""
        return self.translations.get(self.locale, {}).get(text, text)
            
    def apply_translations(self):
        """应用当前语言的翻译到UI"""
        # 窗口标题
        self.setWindowTitle(self.tr('Coordinate Converter'))
        
        # 组框
        self.groupBox.setTitle(self.tr('Input'))
        self.label.setText(self.tr('Input Layer:'))
        self.groupBoxInputCRS.setTitle(self.tr('Input Coordinate System'))
        self.radioButton_wgs84_in.setText(self.tr('WGS84'))
        self.radioButton_gcj02_in.setText(self.tr('GCJ02 (Mars Coordinates)'))
        self.radioButton_bd09_in.setText(self.tr('BD09 (Baidu Coordinates)'))
        
        self.groupBox_2.setTitle(self.tr('Output'))
        self.chkUseTemporaryLayer.setText(self.tr('Use Temporary Layer'))
        self.label_2.setText(self.tr('Output Path:'))
        self.btnBrowse.setText(self.tr('Browse...'))
        self.label_3.setText(self.tr('Output Format:'))
        self.groupBoxOutputCRS.setTitle(self.tr('Output Coordinate System'))
        self.radioButton_wgs84_out.setText(self.tr('WGS84'))
        self.radioButton_gcj02_out.setText(self.tr('GCJ02 (Mars Coordinates)'))
        self.radioButton_bd09_out.setText(self.tr('BD09 (Baidu Coordinates)'))
        self.chkLoadOutput.setText(self.tr('Load Output Layer When Completed'))
        
        # 按钮
        self.btnConvert.setText(self.tr('Convert'))
        
        # 刷新图层下拉框中的"选择图层"文本
        if self.cboInputLayer.count() > 0:
            self.cboInputLayer.setItemText(0, self.tr('Select a layer'))
            
    def switch_language(self):
        """切换界面语言"""
        try:
            # 切换语言设置
            if self.locale == 'zh':
                self.locale = 'en'
            else:
                self.locale = 'zh'
                
            # 保存语言设置到QSettings
            settings = QSettings()
            settings.setValue('CoordConvert/locale', self.locale)
            
            # 更新语言按钮文本
            self.update_language_button_text()
            
            # 应用新的翻译
            self.apply_translations()
                               
        except Exception as e:
            print(f"Error in switch_language: {str(e)}")
            QMessageBox.critical(self, self.tr('Error'), f"{self.tr('Failed to switch language')}: {str(e)}")

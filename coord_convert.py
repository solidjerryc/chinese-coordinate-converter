# -*- coding: utf-8 -*-
"""
/***************************************************************************
 CoordConvert
                                 A QGIS plugin
 Converts coordinates between WGS84, GCJ02, and BD09
                              -------------------
        begin                : 2025
 ***************************************************************************/
"""

import os
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication, Qt, QVariant
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction, QFileDialog, QMessageBox
from qgis.core import QgsVectorLayer, QgsVectorFileWriter, QgsCoordinateReferenceSystem, QgsField, QgsFeature, QgsGeometry, QgsPoint, QgsPointXY, QgsProject, QgsWkbTypes

# Import the code for the dialog
from .coord_convert_dialog import CoordConvertDialog
from .util.transform import Transform

class CoordConvert:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        
        # Initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        
        # 初始化翻译字典 - 移到前面，确保在tr()调用前定义
        self.translations = {
            'en': {
                '&Coordinate Converter': '&Coordinate Converter',
                'Coordinate Converter': 'Coordinate Converter',
                'Convert coordinates between WGS84, GCJ02, and BD09': 'Convert coordinates between WGS84, GCJ02, and BD09',
                'Select output file': 'Select output file',
                'Shapefile (*.shp)': 'Shapefile (*.shp)',
                'GeoPackage (*.gpkg)': 'GeoPackage (*.gpkg)',
                'No input layer selected': 'No input layer selected',
                'Error': 'Error',
                'Converting': 'Converting',
                'Conversion completed': 'Conversion completed'
            },
            'zh': {
                '&Coordinate Converter': '&坐标转换器',
                'Coordinate Converter': '坐标转换器',
                'Convert coordinates between WGS84, GCJ02, and BD09': '在WGS84、GCJ02和BD09之间转换坐标',
                'Select output file': '选择输出文件',
                'Shapefile (*.shp)': 'Shapefile文件 (*.shp)',
                'GeoPackage (*.gpkg)': 'GeoPackage文件 (*.gpkg)',
                'No input layer selected': '未选择输入图层',
                'Error': '错误',
                'Converting': '转换中',
                'Conversion completed': '转换完成'
            }
        }
        
        # 获取当前语言设置
        settings = QSettings()
        self.locale = settings.value('CoordConvert/locale', 'zh')
        
        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Coordinate Converter')
        self.dlg = None  # 稍后初始化对话框

        # Check if plugin was started the first time in current QGIS session
        # Must be set in initGui() to survive plugin reloads
        self.first_start = None
        
        # 翻译字典
        self.translations = {
            'en': {
                '&Coordinate Converter': '&Coordinate Converter',
                'Coordinate Converter': 'Coordinate Converter',
                'Convert coordinates between WGS84, GCJ02, and BD09': 'Convert coordinates between WGS84, GCJ02, and BD09',
                'Select output file': 'Select output file',
                'Shapefile (*.shp)': 'Shapefile (*.shp)',
                'GeoPackage (*.gpkg)': 'GeoPackage (*.gpkg)',
                'No input layer selected': 'No input layer selected',
                'Error': 'Error',
                'Converting': 'Converting',
                'Conversion completed': 'Conversion completed'
            },
            'zh': {
                '&Coordinate Converter': '&坐标转换器',
                'Coordinate Converter': '坐标转换器',
                'Convert coordinates between WGS84, GCJ02, and BD09': '在WGS84、GCJ02和BD09之间转换坐标',
                'Select output file': '选择输出文件',
                'Shapefile (*.shp)': 'Shapefile文件 (*.shp)',
                'GeoPackage (*.gpkg)': 'GeoPackage文件 (*.gpkg)',
                'No input layer selected': '未选择输入图层',
                'Error': '错误',
                'Converting': '转换中',
                'Conversion completed': '转换完成'
            }
        }

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """获取指定字符串的翻译"""
        return self.translations.get(self.locale, {}).get(message, message)

    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            # Adds plugin icon to Plugins toolbar
            self.iface.addToolBarIcon(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        # 使用SVG图标而不是PNG图标
        icon_path = os.path.join(self.plugin_dir, 'icon.svg')
        self.add_action(
            icon_path,
            text=self.tr(u'Coordinate Converter'),
            callback=self.run,
            parent=self.iface.mainWindow())

        # will be set False in run()
        self.first_start = True

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Coordinate Converter'),
                action)
            self.iface.removeToolBarIcon(action)
            
    def select_output_file(self):
        """让用户选择输出文件路径"""
        current_path = self.dlg.leOutputPath.text()
        file_filter = f"{self.tr('Shapefile (*.shp)')};; {self.tr('GeoPackage (*.gpkg)')}"

        filename, _ = QFileDialog.getSaveFileName(
            self.dlg,
            self.tr("Select output file"),
            current_path,
            file_filter
        )
        
        if filename:
            self.dlg.leOutputPath.setText(filename)
            
    def convert_coordinates(self):
        """执行坐标转换操作"""
        # 获取输入图层
        layer_idx = self.dlg.cboInputLayer.currentIndex()
        if layer_idx == -1:
            QMessageBox.critical(self.dlg, self.tr('Error'), self.tr('No input layer selected'))
            return
            
        layer_id = self.dlg.cboInputLayer.currentData()
        input_layer = QgsProject.instance().mapLayer(layer_id)
        
        if not input_layer:
            QMessageBox.critical(self.dlg, self.tr('Error'), self.tr('No input layer selected'))
            return
        
        # 确定输入坐标系
        input_crs = None
        if self.dlg.radioButton_wgs84_in.isChecked():
            input_crs = "WGS84"
        elif self.dlg.radioButton_gcj02_in.isChecked():
            input_crs = "GCJ02"
        elif self.dlg.radioButton_bd09_in.isChecked():
            input_crs = "BD09"
        
        # 确定输出坐标系
        output_crs = None
        if self.dlg.radioButton_wgs84_out.isChecked():
            output_crs = "WGS84"
        elif self.dlg.radioButton_gcj02_out.isChecked():
            output_crs = "GCJ02"
        elif self.dlg.radioButton_bd09_out.isChecked():
            output_crs = "BD09"
        
        # 如果输入和输出坐标系相同，则提示用户并返回
        if input_crs == output_crs:
            QMessageBox.information(self.dlg, self.tr('Information'), 
                                 self.tr('Input and output coordinate systems are the same. No conversion needed.'))
            return
        
        # 确定输出路径
        use_temp_layer = self.dlg.chkUseTemporaryLayer.isChecked()
        output_path = ""
        output_format = "GPKG"
        
        if not use_temp_layer:
            output_path = self.dlg.leOutputPath.text()
            if not output_path:
                QMessageBox.critical(self.dlg, self.tr('Error'), self.tr('Please specify an output path'))
                return
            output_format = self.dlg.cboOutputFormat.currentData()
        
        # 创建一个Transform实例
        transformer = Transform()
        
        # 创建一个临时图层来保存转换后的要素
        crs = input_layer.crs()
        if use_temp_layer:
            output_layer_name = f"{input_layer.name()}_{input_crs}_to_{output_crs}"
            output_layer = QgsVectorLayer(f"Point?crs={crs.authid()}", output_layer_name, "memory")
        else:
            # 获取输出格式的驱动名称
            driver_name = output_format
            output_layer = None
        
        # 准备输出图层的字段
        if use_temp_layer:
            output_provider = output_layer.dataProvider()
            output_provider.addAttributes(input_layer.fields())
            output_layer.updateFields()
        
        # 创建输出文件的参数
        if not use_temp_layer:
            fields = input_layer.fields()
            crs = input_layer.crs()
            
            options = QgsVectorFileWriter.SaveVectorOptions()
            options.driverName = driver_name
            
            transform_context = QgsProject.instance().transformContext()
            
            error = QgsVectorFileWriter.create(
                output_path,
                fields,
                input_layer.wkbType(),
                crs,
                transform_context,
                options
            )
            
            if error[0] != QgsVectorFileWriter.NoError:
                QMessageBox.critical(self.dlg, self.tr('Error'), f"{self.tr('Error creating output file')}: {error[1]}")
                return
                
            output_layer = QgsVectorLayer(output_path, os.path.basename(output_path), "ogr")
        
        # 开始坐标转换
        self.iface.messageBar().pushMessage(self.tr('Converting'), self.tr('Converting coordinates...'), level=0, duration=3)
        
        total_features = input_layer.featureCount()
        features = []
        
        # 处理每个要素
        for i, feature in enumerate(input_layer.getFeatures()):
            geom = feature.geometry()
            
            if geom.type() == QgsWkbTypes.PointGeometry:
                if geom.isMultipart():
                    points = geom.asMultiPoint()
                    new_points = []
                    for point in points:
                        # 转换坐标
                        x, y = point.x(), point.y()
                        new_x, new_y = self.transform_coordinates(x, y, input_crs, output_crs, transformer)
                        new_points.append(QgsPointXY(new_x, new_y))
                    
                    new_geom = QgsGeometry.fromMultiPointXY(new_points)
                else:
                    point = geom.asPoint()
                    # 转换坐标
                    x, y = point.x(), point.y()
                    new_x, new_y = self.transform_coordinates(x, y, input_crs, output_crs, transformer)
                    new_geom = QgsGeometry.fromPointXY(QgsPointXY(new_x, new_y))
            else:
                # 如果不是点几何，则保持不变
                new_geom = geom
            
            # 创建新要素
            new_feature = QgsFeature(feature)
            new_feature.setGeometry(new_geom)
            features.append(new_feature)
            
            # 更新进度条（如果有）
            if self.dlg.progressBar.isVisible():
                progress = (i + 1) / total_features * 100
                self.dlg.progressBar.setValue(int(progress))
        
        # 将新要素添加到输出图层
        if use_temp_layer:
            output_provider.addFeatures(features)
        else:
            output_layer.dataProvider().addFeatures(features)
        
        # 如果用户勾选了加载输出图层选项，则加载图层到地图
        if self.dlg.chkLoadOutput.isChecked():
            QgsProject.instance().addMapLayer(output_layer)
        
        # 完成消息
        self.iface.messageBar().pushMessage(self.tr('Conversion completed'), self.tr('Coordinate conversion has been completed successfully.'), level=0, duration=3)

    def transform_coordinates(self, x, y, input_crs, output_crs, transformer):
        """根据输入和输出坐标系统转换坐标"""
        # WGS84 -> GCJ02
        if input_crs == "WGS84" and output_crs == "GCJ02":
            return transformer.wgs2gcj(x, y)
        # WGS84 -> BD09
        elif input_crs == "WGS84" and output_crs == "BD09":
            return transformer.wgs2bd(x, y)
        # GCJ02 -> WGS84
        elif input_crs == "GCJ02" and output_crs == "WGS84":
            return transformer.gcj2wgs(x, y)
        # GCJ02 -> BD09
        elif input_crs == "GCJ02" and output_crs == "BD09":
            return transformer.gcj2bd(x, y)
        # BD09 -> WGS84
        elif input_crs == "BD09" and output_crs == "WGS84":
            return transformer.bd2wgs(x, y)
        # BD09 -> GCJ02
        elif input_crs == "BD09" and output_crs == "GCJ02":
            return transformer.bd2gcj(x, y)
        # 默认情况下返回原始坐标
        else:
            return x, y

    def run(self):
        """Run method that performs all the real work"""

        # 每次运行时重新创建对话框，确保获取最新的翻译设置
        self.dlg = CoordConvertDialog()

        # Only create GUI ONCE in callback, so that it will only load when the plugin is started
        if self.first_start == True:
            self.first_start = False
            
        # 确保语言设置是最新的
        settings = QSettings()
        self.locale = settings.value('CoordConvert/locale', 'zh')
            
        # Connect signals
        self.dlg.btnBrowse.clicked.connect(self.select_output_file)
        self.dlg.btnConvert.clicked.connect(self.convert_coordinates)
        
        # 填充图层下拉框和输出格式选项
        self.populate_layer_combobox()
        self.populate_output_format_combobox()
        
        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            pass
            
    def populate_layer_combobox(self):
        """填充图层下拉框"""
        self.dlg.cboInputLayer.clear()
        layers = QgsProject.instance().mapLayers().values()
        for layer in layers:
            if isinstance(layer, QgsVectorLayer) and layer.wkbType() in [1, 4]:  # Point or MultiPoint
                self.dlg.cboInputLayer.addItem(layer.name(), layer.id())
                
    def populate_output_format_combobox(self):
        """填充输出格式下拉框"""
        self.dlg.cboOutputFormat.clear()
        self.dlg.cboOutputFormat.addItem("ESRI Shapefile (*.shp)", "ESRI Shapefile")
        self.dlg.cboOutputFormat.addItem("GeoPackage (*.gpkg)", "GPKG")
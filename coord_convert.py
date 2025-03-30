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
                'Coordinate Converter': 'Coordinate Converter',
                'Convert coordinates between WGS84, GCJ02, and BD09': 'Convert coordinates between WGS84, GCJ02, and BD09',
                'Select output file': 'Select output file',
                'Shapefile (*.shp)': 'Shapefile (*.shp)',
                'GeoPackage (*.gpkg)': 'GeoPackage (*.gpkg)',
                'No input layer selected': 'No input layer selected',
                'Error': 'Error',
                'Converting': 'Converting',
                'Conversion completed': 'Conversion completed',
                'Information': 'Information',
                'Input and output coordinate systems are the same. No conversion needed.': 'Input and output coordinate systems are the same. No conversion needed.',
                'Please specify an output path': 'Please specify an output path',
                'Cannot create directory': 'Cannot create directory',
                'Cannot write to output file': 'Cannot write to output file',
                'Cannot overwrite existing file': 'Cannot overwrite existing file',
                'Error creating output file': 'Error creating output file',
                'Exception creating output file': 'Exception creating output file',
                'Error opening output file': 'Error opening output file',
                'Exception opening output file': 'Exception opening output file',
                'Output layer is not valid. Features could not be saved.': 'Output layer is not valid. Features could not be saved.',
                'Exception adding features': 'Exception adding features',
                'Output layer could not be loaded to the map.': 'Output layer could not be loaded to the map.',
                'Exception loading layer to map': 'Exception loading layer to map',
                'Warning': 'Warning',
                'Some features may not have been saved correctly.': 'Some features may not have been saved correctly.',
                'The input layer contains no features. Nothing to convert.': 'The input layer contains no features. Nothing to convert.',
                'No valid features could be converted.': 'No valid features could be converted.',
                'Converting coordinates...': 'Converting coordinates...',
                'Coordinate conversion has been completed successfully.': 'Coordinate conversion has been completed successfully.'
            },
            'zh': {
                'Coordinate Converter': '坐标转换器',
                'Convert coordinates between WGS84, GCJ02, and BD09': '在WGS84、GCJ02和BD09之间转换坐标',
                'Select output file': '选择输出文件',
                'Shapefile (*.shp)': 'Shapefile文件 (*.shp)',
                'GeoPackage (*.gpkg)': 'GeoPackage文件 (*.gpkg)',
                'No input layer selected': '未选择输入图层',
                'Error': '错误',
                'Converting': '转换中',
                'Conversion completed': '转换完成',
                'Information': '信息',
                'Input and output coordinate systems are the same. No conversion needed.': '输入和输出坐标系相同，无需转换。',
                'Please specify an output path': '请指定输出路径',
                'Cannot create directory': '无法创建目录',
                'Cannot write to output file': '无法写入输出文件',
                'Cannot overwrite existing file': '无法覆盖现有文件',
                'Error creating output file': '创建输出文件时出错',
                'Exception creating output file': '创建输出文件时发生异常',
                'Error opening output file': '打开输出文件时出错',
                'Exception opening output file': '打开输出文件时发生异常',
                'Output layer is not valid. Features could not be saved.': '输出图层无效。无法保存要素。',
                'Exception adding features': '添加要素时发生异常',
                'Output layer could not be loaded to the map.': '无法将输出图层加载到地图中。',
                'Exception loading layer to map': '加载图层到地图时发生异常',
                'Warning': '警告',
                'Some features may not have been saved correctly.': '某些要素可能未正确保存。',
                'The input layer contains no features. Nothing to convert.': '输入图层不包含要素。没有需要转换的内容。',
                'No valid features could be converted.': '没有有效的要素可以转换。',
                'Converting coordinates...': '正在转换坐标...',
                'Coordinate conversion has been completed successfully.': '坐标转换已成功完成。'
            }
        }
        
        # 获取当前语言设置
        settings = QSettings()
        self.locale = settings.value('CoordConvert/locale', 'zh')
        
        # Declare instance attributes
        self.actions = []
        # Use a fixed menu name that won't be translated to avoid duplicate menu entries
        self.menu = 'Coordinate Converter'
        self.dlg = None  # 稍后初始化对话框

        # Check if plugin was started the first time in current QGIS session
        # Must be set in initGui() to survive plugin reloads
        self.first_start = None

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
            text=self.tr('Coordinate Converter'),
            callback=self.run,
            parent=self.iface.mainWindow())

        # will be set False in run()
        self.first_start = True

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.menu,  # Use the fixed menu name, not the translated one
                action)
            self.iface.removeToolBarIcon(action)
            
    def select_output_file(self):
        """让用户选择输出文件路径"""
        current_path = self.dlg.leOutputPath.text()
        
        # 构建文件过滤器字符串，包含所有支持的格式
        format_filters = []
        for i in range(self.dlg.cboOutputFormat.count()):
            item_text = self.dlg.cboOutputFormat.itemText(i)
            format_filters.append(self.tr(item_text))
        
        file_filter = ";;".join(format_filters)
        
        # 获取当前选择的格式作为默认选择
        selected_filter = self.dlg.cboOutputFormat.currentText()

        filename, selected_filter = QFileDialog.getSaveFileName(
            self.dlg,
            self.tr("Select output file"),
            current_path,
            file_filter,
            selected_filter
        )
        
        if filename:
            self.dlg.leOutputPath.setText(filename)
            
            # 根据选择的过滤器更新格式下拉框
            for i in range(self.dlg.cboOutputFormat.count()):
                if self.dlg.cboOutputFormat.itemText(i) == selected_filter:
                    self.dlg.cboOutputFormat.setCurrentIndex(i)
                    break
            
            # 确保文件扩展名正确
            self.update_file_extension()
            
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
        output_format = ""
        
        if not use_temp_layer:
            output_path = self.dlg.leOutputPath.text()
            if not output_path:
                QMessageBox.critical(self.dlg, self.tr('Error'), self.tr('Please specify an output path'))
                return
                
            # 检查目录是否存在，如果不存在则尝试创建
            output_dir = os.path.dirname(output_path)
            if output_dir and not os.path.exists(output_dir):
                try:
                    os.makedirs(output_dir)
                except Exception as e:
                    QMessageBox.critical(self.dlg, self.tr('Error'), 
                                      f"{self.tr('Cannot create directory')}: {output_dir}\n{str(e)}")
                    return
                
            # 检查文件是否可写
            if os.path.exists(output_path):
                try:
                    # 检查文件是否被锁定
                    with open(output_path, 'a'):
                        pass
                except IOError as e:
                    QMessageBox.critical(self.dlg, self.tr('Error'), 
                                      f"{self.tr('Cannot write to output file')}: {output_path}\n{str(e)}")
                    return
                    
            # 获取选择的输出格式
            output_format = self.dlg.cboOutputFormat.currentData()
            
            # 确保文件扩展名正确
            self.update_file_extension()
            output_path = self.dlg.leOutputPath.text()  # 重新获取可能已更新的路径
                
            # 如果用户手动输入了文件路径，根据扩展名确定格式
            if output_format == "":
                ext = os.path.splitext(output_path)[1].lower()
                if ext == '.shp':
                    output_format = "ESRI Shapefile"
                elif ext == '.gpkg':
                    output_format = "GPKG"
                elif ext == '.geojson':
                    output_format = "GeoJSON"
                elif ext == '.kml':
                    output_format = "KML"
                elif ext == '.tab':
                    output_format = "MapInfo File"
                elif ext == '.dxf':
                    output_format = "DXF"
                else:
                    # 默认使用Shapefile
                    output_format = "ESRI Shapefile"
                    output_path += '.shp'
                    self.dlg.leOutputPath.setText(output_path)
        
        # 创建一个Transform实例
        transformer = Transform()
        
        # 获取输入图层的几何类型和CRS
        crs = input_layer.crs()
        geometry_type = input_layer.wkbType()
        
        # 创建一个临时图层来保存转换后的要素
        if use_temp_layer:
            output_layer_name = f"{input_layer.name()}_{input_crs}_to_{output_crs}"
            
            # 根据几何类型创建正确的内存图层
            if input_layer.geometryType() == QgsWkbTypes.PointGeometry:
                geometry_name = "Point"
            elif input_layer.geometryType() == QgsWkbTypes.LineGeometry:
                geometry_name = "LineString"
            elif input_layer.geometryType() == QgsWkbTypes.PolygonGeometry:
                geometry_name = "Polygon"
            else:
                geometry_name = "Unknown"
                
            # 处理多部分几何
            if QgsWkbTypes.isMultiType(geometry_type):
                geometry_name = f"Multi{geometry_name}"
                
            # 创建适当类型的内存图层
            output_layer = QgsVectorLayer(f"{geometry_name}?crs={crs.authid()}", output_layer_name, "memory")
        else:
            # 获取输出格式的驱动名称
            driver_name = output_format
            output_layer = None
        
        # 准备输出图层的字段
        if use_temp_layer:
            output_provider = output_layer.dataProvider()
            output_provider.addAttributes(input_layer.fields())
            output_layer.updateFields()
        
        # 开始坐标转换 - 提前处理数据，确保有数据可写入
        total_features = input_layer.featureCount()
        if total_features == 0:
            QMessageBox.warning(self.dlg, self.tr('Warning'), 
                             self.tr('The input layer contains no features. Nothing to convert.'))
            return
            
        features = []
        
        # 处理每个要素
        self.iface.messageBar().pushMessage(self.tr('Converting'), self.tr('Converting coordinates...'), level=0, duration=3)
        for i, feature in enumerate(input_layer.getFeatures()):
            geom = feature.geometry()
            
            # 根据几何类型进行不同的转换
            if geom.type() == QgsWkbTypes.PointGeometry:
                new_geom = self.transform_point_geometry(geom, input_crs, output_crs, transformer)
            elif geom.type() == QgsWkbTypes.LineGeometry:
                new_geom = self.transform_line_geometry(geom, input_crs, output_crs, transformer)
            elif geom.type() == QgsWkbTypes.PolygonGeometry:
                new_geom = self.transform_polygon_geometry(geom, input_crs, output_crs, transformer)
            else:
                # 如果是未知几何类型，则保持不变
                new_geom = geom
            
            # 创建新要素，保留所有原始属性
            new_feature = QgsFeature(feature)
            new_feature.setGeometry(new_geom)
            features.append(new_feature)
            
            # 更新进度条（如果有）
            if self.dlg.progressBar.isVisible():
                progress = (i + 1) / total_features * 100
                self.dlg.progressBar.setValue(int(progress))
                
        # 确保有要素可写入
        if not features:
            QMessageBox.warning(self.dlg, self.tr('Warning'), 
                             self.tr('No valid features could be converted.'))
            return
                
        # 创建输出文件（仅在不使用临时图层时）
        if not use_temp_layer:
            fields = input_layer.fields()
            
            # 先尝试删除同名文件，避免文件锁定问题
            if os.path.exists(output_path):
                try:
                    os.remove(output_path)
                    # 等待一小段时间确保文件系统更新
                    import time
                    time.sleep(0.5)
                except OSError as e:
                    QMessageBox.critical(self.dlg, self.tr('Error'), 
                                      f"{self.tr('Cannot overwrite existing file')}: {output_path}\n{str(e)}")
                    return
            
            options = QgsVectorFileWriter.SaveVectorOptions()
            options.driverName = driver_name
            
            transform_context = QgsProject.instance().transformContext()
            
            try:
                # Update handling of QgsVectorFileWriter.create() return value for newer QGIS versions
                writer_result = QgsVectorFileWriter.create(
                    output_path,
                    fields,
                    geometry_type,  # 使用原始图层的WKB类型
                    crs,
                    transform_context,
                    options
                )
                
                # Check if writer_result is a tuple (older QGIS versions) or an object (newer versions)
                if isinstance(writer_result, tuple):
                    error = writer_result[0]
                    if error != QgsVectorFileWriter.NoError:
                        error_msg = writer_result[1] if len(writer_result) > 1 else "Unknown error"
                        QMessageBox.critical(self.dlg, self.tr('Error'), f"{self.tr('Error creating output file')}: {error_msg}")
                        return
                    # 在旧版本中不需要获取writer对象，直接继续
                else:
                    # For newer QGIS versions (but not too new)
                    if hasattr(writer_result, 'hasError') and writer_result.hasError():
                        QMessageBox.critical(self.dlg, self.tr('Error'), 
                                          f"{self.tr('Error creating output file')}: {writer_result.errorMessage()}")
                        return
            except Exception as e:
                QMessageBox.critical(self.dlg, self.tr('Error'), 
                                  f"{self.tr('Exception creating output file')}: {str(e)}")
                return
                
            # 确保文件已关闭并刷新
            del writer_result
            
            # 等待一小段时间，确保文件系统有时间完成文件写入
            import time
            time.sleep(1.0)  # 增加等待时间到1秒
                
            # 在创建完文件后打开图层
            try:
                output_layer = QgsVectorLayer(output_path, os.path.basename(output_path), "ogr")
                
                # 验证图层是否有效
                if not output_layer or not output_layer.isValid():
                    error_msg = ""
                    if output_layer:
                        error_msg = output_layer.dataProvider().error().message()
                    QMessageBox.critical(self.dlg, self.tr('Error'), 
                                      f"{self.tr('Error opening output file')}: {output_path}\n{error_msg}")
                    return
            except Exception as e:
                QMessageBox.critical(self.dlg, self.tr('Error'), 
                                  f"{self.tr('Exception opening output file')}: {output_path}\n{str(e)}")
                return
        
        # 将新要素添加到输出图层
        if use_temp_layer:
            success = output_provider.addFeatures(features)
            if not success:
                QMessageBox.warning(self.dlg, self.tr('Warning'), 
                                 self.tr('Some features may not have been saved correctly.'))
        else:
            # 确保图层有效
            try:
                if output_layer and output_layer.isValid():
                    success = output_layer.dataProvider().addFeatures(features)
                    if not success:
                        QMessageBox.warning(self.dlg, self.tr('Warning'), 
                                         self.tr('Some features may not have been saved correctly.'))
                else:
                    QMessageBox.critical(self.dlg, self.tr('Error'), 
                                      self.tr('Output layer is not valid. Features could not be saved.'))
                    return
            except Exception as e:
                QMessageBox.critical(self.dlg, self.tr('Error'), 
                                  f"{self.tr('Exception adding features')}: {str(e)}")
                return
        
        # 如果用户勾选了加载输出图层选项，则加载图层到地图
        if self.dlg.chkLoadOutput.isChecked():
            try:
                if output_layer and output_layer.isValid():
                    QgsProject.instance().addMapLayer(output_layer)
                else:
                    QMessageBox.warning(self.dlg, self.tr('Warning'), 
                                     self.tr('Output layer could not be loaded to the map.'))
            except Exception as e:
                QMessageBox.warning(self.dlg, self.tr('Warning'), 
                                 f"{self.tr('Exception loading layer to map')}: {str(e)}")
        
        # 完成消息
        self.iface.messageBar().pushMessage(self.tr('Conversion completed'), self.tr('Coordinate conversion has been completed successfully.'), level=0, duration=3)

    def transform_point_geometry(self, geom, input_crs, output_crs, transformer):
        """转换点"""
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
        
        return new_geom
        
    def transform_line_geometry(self, geom, input_crs, output_crs, transformer):
        """转换线"""
        if geom.isMultipart():
            multipolyline = geom.asMultiPolyline()
            new_multipolyline = []
            
            for polyline in multipolyline:
                new_polyline = []
                for point in polyline:
                    x, y = point.x(), point.y()
                    new_x, new_y = self.transform_coordinates(x, y, input_crs, output_crs, transformer)
                    new_polyline.append(QgsPointXY(new_x, new_y))
                new_multipolyline.append(new_polyline)
            
            new_geom = QgsGeometry.fromMultiPolylineXY(new_multipolyline)
        else:
            polyline = geom.asPolyline()
            new_polyline = []
            
            for point in polyline:
                x, y = point.x(), point.y()
                new_x, new_y = self.transform_coordinates(x, y, input_crs, output_crs, transformer)
                new_polyline.append(QgsPointXY(new_x, new_y))
            
            new_geom = QgsGeometry.fromPolylineXY(new_polyline)
        
        return new_geom
        
    def transform_polygon_geometry(self, geom, input_crs, output_crs, transformer):
        """转换面"""
        if geom.isMultipart():
            multipolygon = geom.asMultiPolygon()
            new_multipolygon = []
            
            for polygon in multipolygon:
                new_polygon = []
                for ring in polygon:
                    new_ring = []
                    for point in ring:
                        x, y = point.x(), point.y()
                        new_x, new_y = self.transform_coordinates(x, y, input_crs, output_crs, transformer)
                        new_ring.append(QgsPointXY(new_x, new_y))
                    new_polygon.append(new_ring)
                new_multipolygon.append(new_polygon)
            
            new_geom = QgsGeometry.fromMultiPolygonXY(new_multipolygon)
        else:
            polygon = geom.asPolygon()
            new_polygon = []
            
            for ring in polygon:
                new_ring = []
                for point in ring:
                    x, y = point.x(), point.y()
                    new_x, new_y = self.transform_coordinates(x, y, input_crs, output_crs, transformer)
                    new_ring.append(QgsPointXY(new_x, new_y))
                new_polygon.append(new_ring)
            
            new_geom = QgsGeometry.fromPolygonXY(new_polygon)
        
        return new_geom

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
            # 支持所有矢量图层类型，不仅仅是点
            if isinstance(layer, QgsVectorLayer):
                self.dlg.cboInputLayer.addItem(layer.name(), layer.id())
                
    def populate_output_format_combobox(self):
        """填充输出格式下拉框"""
        self.dlg.cboOutputFormat.clear()
        self.dlg.cboOutputFormat.addItem("ESRI Shapefile (*.shp)", "ESRI Shapefile")
        self.dlg.cboOutputFormat.addItem("GeoPackage (*.gpkg)", "GPKG")
        self.dlg.cboOutputFormat.addItem("GeoJSON (*.geojson)", "GeoJSON")
        self.dlg.cboOutputFormat.addItem("KML (*.kml)", "KML")
        self.dlg.cboOutputFormat.addItem("MapInfo File (*.tab)", "MapInfo File")
        self.dlg.cboOutputFormat.addItem("DXF (*.dxf)", "DXF")
        
        # 连接信号以实现联动效果
        self.dlg.cboOutputFormat.currentIndexChanged.connect(self.on_format_changed)
        self.dlg.leOutputPath.textChanged.connect(self.on_path_changed)
    
    def on_format_changed(self):
        """当输出格式改变时更新文件扩展名"""
        self.update_file_extension()
    
    def on_path_changed(self):
        """当路径改变时更新格式下拉框"""
        path = self.dlg.leOutputPath.text()
        if path:
            ext = os.path.splitext(path)[1].lower()
            format_data = None
            
            # 根据文件扩展名来确定当前格式
            if ext == '.shp':
                format_data = "ESRI Shapefile"
            elif ext == '.gpkg':
                format_data = "GPKG"
            elif ext == '.geojson':
                format_data = "GeoJSON"
            elif ext == '.kml':
                format_data = "KML"
            elif ext == '.tab':
                format_data = "MapInfo File"
            elif ext == '.dxf':
                format_data = "DXF"
            
            # 设置格式下拉框
            if format_data:
                for i in range(self.dlg.cboOutputFormat.count()):
                    if self.dlg.cboOutputFormat.itemData(i) == format_data:
                        # 暂时断开信号连接，避免循环调用
                        self.dlg.cboOutputFormat.blockSignals(True)
                        self.dlg.cboOutputFormat.setCurrentIndex(i)
                        self.dlg.cboOutputFormat.blockSignals(False)
                        break
    
    def update_file_extension(self):
        """根据当前选择的格式更新文件扩展名"""
        path = self.dlg.leOutputPath.text()
        if not path:
            return
            
        # 获取当前格式对应的扩展名
        current_format = self.dlg.cboOutputFormat.currentData()
        extension = ''
        
        if current_format == "ESRI Shapefile":
            extension = '.shp'
        elif current_format == "GPKG":
            extension = '.gpkg'
        elif current_format == "GeoJSON":
            extension = '.geojson'
        elif current_format == "KML":
            extension = '.kml'
        elif current_format == "MapInfo File":
            extension = '.tab'
        elif current_format == "DXF":
            extension = '.dxf'
        
        # 更新路径扩展名
        if extension:
            base_path = os.path.splitext(path)[0]
            new_path = base_path + extension
            
            # 只有在路径实际变化时才更新，避免光标位置重置
            if new_path != path:
                self.dlg.leOutputPath.blockSignals(True)
                self.dlg.leOutputPath.setText(new_path)
                self.dlg.leOutputPath.blockSignals(False)
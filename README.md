# QGIS Chinese Coordinate Converter Plugin

A QGIS plugin for Chinese coordinate system conversion, allowing transformation between WGS-84 (non-offset coordinates), GCJ-02 (used by National Bureau of Surveying and Mapping, AutoNavi, Tencent), and BD-09 (Baidu) coordinate systems.

## Supported Coordinate Systems

This plugin supports conversion between the following coordinate systems:

- **WGS84**: International standard used by GPS
- **GCJ02**: Chinese national standard (a.k.a. "Mars Coordinates"), offset from WGS84
- **BD09**: Baidu coordinate system, based on GCJ02 with additional transformations

## Features

- Vector data conversion between WGS84, GCJ02, and BD09 coordinate systems
- Support for multiple output formats (Temporary Layer, Shapefile, GeoJSON, KML, GeoPackage)

## Usage

1. Open QGIS and load your vector layer
2. Launch the "Coordinate Converter" from the menu or toolbar
3. Select the input layer from the dropdown list
4. Choose the source coordinate system (WGS84, GCJ02, or BD09)
5. Specify the output file path and format
6. Select the target coordinate system
7. Click "Convert" to start the conversion process
8. The progress will be displayed in the progress bar
9. After completion, the converted layer will be loaded into QGIS (if the option is selected)

## License

This plugin is licensed under the GPLv2 License.

## Acknowledgments

This plugin uses coordinate conversion code from [coord-convert](https://github.com/sshuair/coord-convert) project by sshuair.

---

# QGIS火星坐标转换插件

中国火星坐标转换QGIS插件，用于WGS-84(未偏移坐标), GCJ-02（国家测绘局、高德、腾讯）, BD-09(百度)三者之间的互相转换。

## 支持的坐标系统

该插件支持以下坐标系统之间的转换：

- **WGS84**：GPS使用的国际标准
- **GCJ02**：国测局02坐标系，也称为"火星坐标"，与WGS84有偏移
- **BD09**：百度09坐标系，基于GCJ02并有额外的转换

## 功能特点

- 矢量数据在WGS84、GCJ02和BD09坐标系之间互转
- 支持多种输出格式（临时图层、Shapefile、GeoJSON、KML、GeoPackage）

## 使用方法

1. 打开QGIS并加载矢量图层
2. 从菜单或工具栏启动"坐标转换器"
3. 从下拉列表中选择输入图层
4. 选择坐标系统（WGS84、GCJ02或BD09）
5. 指定输出文件路径和格式
6. 选择输出坐标系统
7. 点击"转换"开始转换过程
8. 转换进度将在进度条中显示
9. 完成后，转换后的图层将被加载到QGIS中（如果选中了该选项）

## 许可证

该插件采用GPLv2许可证授权。

## 致谢

本插件使用了sshuair的[coord-convert](https://github.com/sshuair/coord-convert)项目中的坐标转换代码。

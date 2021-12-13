

margin = 50
print("-------")
e = iface.mapCanvas().extent()


project = QgsProject.instance()
manager = project.layoutManager()
layout_name = 'Automatic layout'
layouts_list = manager.printLayouts()
# Just 4 debug
# remove any duplicate layouts
for layout in layouts_list:
    if layout.name() == layout_name:
        manager.removeLayout(layout)
    #     reply = QMessageBox.question(None, (u'Delete layout...'),
    #                                  (
    #                                      u"There's already a layout named '%s'\nDo you want to delete it?")
    #                                  % layout_name,
    #                                  QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
    #     if reply == QMessageBox.No:
    #         return
    #     else:
    #         manager.removeLayout(layout)
    #         print((u"Previous layout names '%s' removed... ") % layout_name)

layout = QgsPrintLayout(project)
layout.initializeDefaults()
# manager.addLayout(layout)
layout.setName(layout_name)

# Determine and set best layout orientation
map_width = e.xMaximum() - e.xMinimum()
map_height = e.yMaximum() - e.yMinimum()
# # map_ratio = map_width / map_height
# layout_width = layout.pageCollection().page(0).pageSize().width()
# layout_height = layout.pageCollection().page(0).pageSize().height()
# # layout_ratio = layout_width / layout_height
page_size = QgsApplication.pageSizeRegistry().find(layout.pageCollection().page(0).pageSize())  # eg. 'A4' str
landscape = False

if map_width <= map_height:
    # portrait
    print("Portrait")
    layout.pageCollection().page(0).setPageSize(page_size, QgsLayoutItemPage.Orientation.Portrait)
else:
    # landscape
    print("Landscape")
    layout.pageCollection().page(0).setPageSize(page_size, QgsLayoutItemPage.Orientation.Landscape)
    landscape = True

# Calculate scale ratio between layout size and map size
layout_width = layout.pageCollection().page(0).pageSize().width()
layout_height = layout.pageCollection().page(0).pageSize().height()
if landscape:
    scale_ratio = (layout_width / map_width)
    if map_height * scale_ratio > layout_height:
        scale_ratio = map_height / layout_height
else:
    scale_ratio = layout_height / map_height
    if map_width * scale_ratio > layout_width:
        scale_ratio = map_height / layout_height



# Add map
print("Adding map")
my_map = QgsLayoutItemMap(layout)

print("mapw: %r / maph: %r" % (map_width, map_height))
print(scale_ratio)
previous_height = map_height
previous_width = map_width

if landscape:
    print("Landscape")

    map_width = layout_width
    map_height = round(map_height * scale_ratio, 3)
    print("ori_mapw: %r / ori_maph: %r" % (map_width, map_height))
    # workaround don't now why in special case it has to be changed !:#
    if map_height > layout_height:
        
        map_height = layout_height
        map_width = round(previous_width / scale_ratio, 3)
        print("corr_mapw: %r / corr_maph: %r" % (map_width, map_height))
else:

    print("Portrait")
    map_width = round(map_width * scale_ratio, 3)
    map_height = layout_height
    print("ori_mapw: %r / ori_maph: %r" % (map_width, map_height))
    # workaround  : don't now why in special case it has to be changed !:#
    if map_width > map_height :
        map_width = layout_width
        map_height = round(previous_height / scale_ratio, 3)
        print("corr_mapw: %r / corr_maph: %r" % (map_width, map_height))
        # print('correction')
        # map_width = round(previous_width * scale_ratio, 3)
        pass

map_width = map_width - margin
map_height = map_height - margin
my_map.setRect(0, 0, map_width, map_height)
my_map.setExtent(e)
layout.addLayoutItem(my_map)
my_map.refresh()
map_real_width = my_map.rect().size().width()
map_real_height = my_map.rect().size().height()
x_offset = (layout_width - map_real_width) / 2
y_offset = (layout_height - map_real_height) / 2
print("x_offset: %r / y_offset: %r" % (x_offset, y_offset))
print("real_mapw: %r / real_maph: %r" % (map_real_width, map_real_height))
my_map.setBackgroundColor(QColor(255, 255, 255, 255))
my_map.setFrameEnabled(True)
my_map.attemptMove(QgsLayoutPoint(x_offset, y_offset, QgsUnitTypes.LayoutMillimeters))
layout.addLayoutItem(my_map)
# Add legend
print((u"Adding legend"))
lyrs_to_add = [l for l in QgsProject().instance().layerTreeRoot().children() if l.isVisible()]
legend = QgsLayoutItemLegend(layout)
legend.setTitle('Legend')
legend.setAutoUpdateModel(False)
group = legend.model().rootGroup()
group.clear()
for l in lyrs_to_add:
    if l.nodeType() == 0:
        subgroup = group.addGroup(l.name())
        checked = l.checkedLayers()
        for c in checked:
            subgroup.addLayer(c)
    elif l.nodeType() == 1:
        group.addLayer(l.layer())

layout.addItem(legend)
legend.adjustBoxSize()
legend.setFrameEnabled(True)
legend.attemptMove(QgsLayoutPoint(x_offset, y_offset, QgsUnitTypes.LayoutMillimeters))
legend.refresh()

print(legend.sizeWithUnits())
# Add scale bar
print((u"Adding scale bar"))
scalebar = QgsLayoutItemScaleBar(layout)
scalebar.setStyle('Single Box')
scalebar.setLinkedMap(my_map)
scalebar.applyDefaultSize()
scalebar.applyDefaultSettings()
scalebar.setUnits(QgsUnitTypes.DistanceKilometers)
scalebar.setUnitsPerSegment(scalebar.unitsPerSegment() / 1000)
scalebar.setUnitLabel('km')
scalebar.update()
layout.addLayoutItem(scalebar)
scalebar.attemptMove(QgsLayoutPoint(map_real_width + x_offset - scalebar.rect().size().width() - 5,
                                    map_real_height + y_offset - scalebar.rect().size().height() - 5,
                                    QgsUnitTypes.LayoutMillimeters))

# Add north arrow
print((u"Add north arrow"))
north = QgsLayoutItemPicture(layout)
north.setPicturePath("/home/sylvain/Cloud/github.com/AutoLayoutTool/images/north-arrow.svg")
layout.addLayoutItem(north)
north.attemptResize(QgsLayoutSize(8, 13, QgsUnitTypes.LayoutMillimeters))
north.attemptMove(QgsLayoutPoint(3 + x_offset, map_real_height + y_offset - 15, QgsUnitTypes.LayoutMillimeters))

# Finally add layout to the project via its manager
manager.addLayout(layout)

iface.openLayoutDesigner(layout)
print("♪♪ This is the end, my friend ♪♪")
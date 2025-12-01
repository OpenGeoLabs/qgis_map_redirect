# -*- coding: utf-8 -*-
from qgis.PyQt.QtCore import QObject
from qgis.PyQt.QtWidgets import QAction
from qgis.core import QgsProject, QgsCoordinateReferenceSystem, QgsCoordinateTransform
from qgis.utils import iface
import webbrowser
from math import log2, pi

class MapRedirect(QObject):
    def __init__(self, iface):
        super().__init__()
        self.iface = iface
        self.canvas = iface.mapCanvas()

    def initGui(self):
        self.canvas.contextMenuAboutToShow.connect(self.my_handler)

    def unload(self):
        try:
            self.canvas.contextMenuAboutToShow.disconnect(self.my_handler)
        except:
            pass

    def get_webmap_zoom_level(self):

        crs_3857 = QgsCoordinateReferenceSystem("EPSG:3857")
        transform = QgsCoordinateTransform(
            iface.mapCanvas().mapSettings().destinationCrs(),
            crs_3857,
            QgsProject.instance()
        )

        extent = iface.mapCanvas().extent()

        extent_3857 = transform.transformBoundingBox(extent)

        width_m = extent_3857.width()

        R = 6378137

        zoom = log2((2 * pi * R) / width_m)

        return round(zoom)

    def get_wgs_point(self):
        pt_xy = iface.mapCanvas().mouseLastXY()
        map_point = iface.mapCanvas().getCoordinateTransform().toMapCoordinates(pt_xy.x(), pt_xy.y())

        crs_src = iface.mapCanvas().mapSettings().destinationCrs()
        crs_wgs = QgsCoordinateReferenceSystem("EPSG:4326")
        xform = QgsCoordinateTransform(crs_src, crs_wgs, QgsProject.instance())

        wgs_point = xform.transform(map_point)

        return wgs_point


    def get_mapy_com_url(self):
        wgs_point = self.get_wgs_point()
        zoom_level = self.get_webmap_zoom_level()
        url = f"https://mapy.com/cs/zakladni?x={wgs_point.x():.8f}&y={wgs_point.y():.8f}&z={zoom_level}&ovl=7"
        return url


    def get_openstreetmap_org_url(self):
        wgs_point = self.get_wgs_point()
        zoom_level = self.get_webmap_zoom_level()
        url = f"https://www.openstreetmap.org/#map={zoom_level}/{wgs_point.y():.8f}/{wgs_point.x():.8f}"
        return url


    def get_googlemaps(self):
        wgs_point = self.get_wgs_point()
        zoom_level = self.get_webmap_zoom_level()
        url = f"https://www.google.com/maps/@{wgs_point.y():.8f},{wgs_point.x():.8f},{zoom_level}z"
        return url


    def open_mapy_com(self):
        webbrowser.open(self.get_mapy_com_url())


    def open_openstreetmap_org(self):
        webbrowser.open(self.get_openstreetmap_org_url())


    def open_googlemaps(self):
        webbrowser.open(self.get_googlemaps())


    def my_handler(self, menu):
        a = QAction("Open in Mapy.com", menu)
        a.triggered.connect(self.open_mapy_com)
        menu.addAction(a)

        b = QAction("Open in OpenStreetMap", menu)
        b.triggered.connect(self.open_openstreetmap_org)
        menu.addAction(b)

        c = QAction("Open in GoogleMaps", menu)
        c.triggered.connect(self.open_googlemaps)
        menu.addAction(c)



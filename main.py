import math
import os
import sys
from PyQt5.QtGui import QPixmap
import pygame
import requests

from dgj_podskazka.distance import lonlat_distance
from dgj_podskazka.geo import reverse_geocode
from dgj_podskazka.bis import find_business
import PyQt5
from PyQt5.QtWidgets import QMainWindow, QApplication, QLabel

LAT_STEP = 0.008  # Шаги при движении карты по широте и долготе
LON_STEP = 0.002
coord_to_geo_x = 0.0000428  # Пропорции пиксельных и географических координат.
coord_to_geo_y = 0.0000428


class SearchResult(object):
    def __init__(self, point, address, postal_code=None):
        self.point = point
        self.address = address
        self.postal_code = postal_code


def ll(x, y):
    return "{0},{1}".format(x, y)


class MapParams(object):
    # Параметры по умолчанию.
    def __init__(self):
        self.lat = 55.729738  # Координаты центра карты на старте.
        self.lon = 37.664777
        self.zoom = 15  # Масштаб карты на старте.
        self.type = "map"  # Тип карты на старте.

        self.search_result = None  # Найденный объект для отображения на карте.
        self.use_postal_code = False

    # Преобразование координат в параметр ll
    def ll(self):
        return ll(self.lon, self.lat)


    # Преобразование экранных координат в географические.
    def screen_to_geo(self, pos):
        dy = 225 - pos[1]
        dx = pos[0] - 300
        lx = self.lon + dx * coord_to_geo_x * math.pow(2, 15 - self.zoom)
        ly = self.lat + dy * coord_to_geo_y * math.cos(math.radians(self.lat)) * math.pow(2,
                                                                                          15 - self.zoom)
        return lx, ly

    # Добавить результат геопоиска на карту.
    def add_reverse_toponym_search(self, pos):
        point = self.screen_to_geo(pos)
        toponym = reverse_geocode(ll(point[0], point[1]))
        self.search_result = SearchResult(
            point,
            toponym["metaDataProperty"]["GeocoderMetaData"]["text"] if toponym else None,
            toponym["metaDataProperty"]["GeocoderMetaData"]["Address"].get(
                "postal_code") if toponym else None)

    # Добавить результат поиска организации на карту.
    def add_reverse_org_search(self, pos):
        self.search_result = None
        point = self.screen_to_geo(pos)
        org = find_business(ll(point[0], point[1]))
        if not org:
            return

        org_point = org["geometry"]["coordinates"]
        org_lon = float(org_point[0])
        org_lat = float(org_point[1])

        # Проверяем, что найденный объект не дальше 50м от места клика.
        if lonlat_distance((org_lon, org_lat), point) <= 50:
            self.search_result = SearchResult(point, org["properties"]["CompanyMetaData"]["name"])


def load_map(mp):
    map_request = "http://static-maps.yandex.ru/1.x/?ll={ll}&z={z}&l={type}".format(ll=mp.ll(),
                                                                                    z=mp.zoom,
                                                                                    type=mp.type)
    if mp.search_result:
        map_request += "&pt={0},{1},pm2grm".format(mp.search_result.point[0],
                                                   mp.search_result.point[1])

    response = requests.get(map_request)
    if not response:
        print("Ошибка выполнения запроса:")
        print(map_request)
        print("Http статус:", response.status_code, "(", response.reason, ")")
        sys.exit(1)
    map_file = "map.png"
    try:
        with open(map_file, "wb") as file:
            file.write(response.content)
    except IOError as ex:
        print("Ошибка записи временного файла:", ex)
        sys.exit(2)

    return map_file


class MapWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # uic.loadUi("../UI/Menu.ui", self)
        self.maximumWidth()
        self.setMaximumSize(950, 720)
        self.setMinimumSize(950, 720)
        print(self.size())
        self.setWindowTitle("MENU")

    def load_image(self, file):
        pixmap = QPixmap(file)
        self.label = QLabel(self)
        self.label.setPixmap(pixmap)
        # print(self.label.size())
        self.label.resize(self.width(), self.height())
        self.label.move(170, 0)
        # self.resize(self.width(), self.height())


def main():
    app = QApplication(sys.argv)
    mp = MapParams()
    map_file = load_map(mp)
    ex = MapWindow()
    ex.load_image(map_file)
    ex.show()
    os.remove(map_file)
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()

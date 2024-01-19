import math

class Room:
    def __init__(self, area, aspect_ratio, type=None):
        self.type = type
        self.area = area
        self.aspect_ratio = aspect_ratio
        self.length = 0
        self.width = 0
        self.rotatable = True

    def resize(self, area):
        self.area = area
        self.length = math.sqrt(1 / self.aspect_ratio * area)
        self.width = math.sqrt(self.aspect_ratio * area)

    @property
    def length(self):
        return self._length

    @length.setter
    def length(self, length):
        length = math.sqrt(self.aspect_ratio * self.area)
        self._length = length

    @property
    def width(self):
        return self._width

    @width.setter
    def width(self, width):
        width = math.sqrt(1 / self.aspect_ratio * self.area)
        self._width = width

class Patient_room(Room):
    def __init__(self, room_number):
        self.room_number = room_number
        self.type = 'Patient Room'
        self.area = 351
        self.aspect_ratio = 1.5
        self.length = 0
        self.width = 0
        self.rotatable = False

class HUC(Room):
    def __init__(self, room_number):
        self.room_number = room_number
        self.type = 'HUC'
        self.area = 151
        self.aspect_ratio = 1.2
        self.length = 0
        self.width = 0
        self.rotatable = True

class Nurse_station(Room):
    def __init__(self, room_number):
        self.room_number = room_number
        self.type = 'Nurse Station'
        self.area = 420
        self.aspect_ratio = 1.7
        self.length = 0
        self.width = 0
        self.rotatable = True

class Waiting_room(Room):
    def __init__(self, room_number):
        self.room_number = room_number
        self.type = 'Waiting Room'
        self.area = 400
        self.aspect_ratio = 1.1
        self.length = 0
        self.width = 0
        self.rotatable = True

class Storage_alcove(Room):
    def __init__(self, room_number):
        self.room_number = room_number
        self.type = 'Storage Alcove'
        self.area = 73
        self.aspect_ratio = 1.3
        self.length = 0
        self.width = 0
        self.rotatable = True

class Break_room(Room):
    def __init__(self, room_number):
        self.room_number = room_number
        self.type = 'Break Room'
        self.area = 370
        self.aspect_ratio = 1.66
        self.length = 0
        self.width = 0
        self.rotatable = True
import project
import rooms

def test_generate_counts():
    assert project.generate_counts(1) == (1, 1, 1, 1, 1, 1)
    assert project.generate_counts(10) == (10, 1, 1, 1, 2, 1)
    assert project.generate_counts(100) == (100, 5, 7, 5, 13, 5)

def test_generate_floorplan():
    assert project.generate_floorplan([(2,3,True), (3,2,True), (2,3,True)], 18) >= 0.9

def test_generate_rooms():
    assert project.generate_rooms((1, 1, 1, 1, 1, 1))[-1:] == (1765,)
    assert project.generate_rooms((1, 1, 1, 1, 1, 1))[-2:-1][0][:1][0] == [15.297058540778355, 22.94558781116753, False]
    assert project.generate_rooms((100, 5, 7, 5, 13, 5))[-1:] == (43594,)

def test_resize_room():
    room = rooms.Room(200, 1.2)
    assert (room.length, room.width) == (15.491933384829668, 12.909944487358057)
    room.resize(300)
    assert (room.length, room.width) == (18.973665961010276, 15.811388300841896)
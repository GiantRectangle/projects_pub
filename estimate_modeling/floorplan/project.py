import rectangle_packing_solver as rps   # https://libraries.io/pypi/rectangle-packing-solver
import pandas as pd
import math
from tabulate import tabulate
import rooms as rm


def main():
    counts = generate_counts(15)
    inventory, rooms, rectangles, net_area = generate_rooms(counts)
    percent_filled = generate_floorplan(rectangles, net_area)
    print(f'solved with {percent_filled:.0%} percent filled')
    print(tabulate(rooms, headers=rooms.columns, tablefmt='pipe'))

def generate_floorplan(rectangles, net_area):
    problem = rps.Problem(rectangles=rectangles)
    solution = rps.Solver().solve(problem=problem, height_limit=90)
    rps.Visualizer().visualize(solution=solution)
    bb = solution.floorplan.bounding_box
    gross_area = bb[0] * bb[1]
    percent_filled = net_area / gross_area
    return percent_filled

def generate_rooms(counts):
    inventory = []
    rooms = []
    rectangles = []
    net_area = []
    beds, num_huc, num_nurse_stn, num_wtg_rm, num_stg_alc, num_brk_rm = counts
    for i in range(beds):
        p = rm.Patient_room(i)
        inventory.append(p)
        rooms.append([p.type, p.room_number, p.area])
        rectangles.append([p.width, p.length, p.rotatable])
        net_area.append(p.area)
    for i in range(num_huc):
        h = rm.HUC(i)
        inventory.append(h)
        rooms.append([h.type, h.room_number, h.area])
        rectangles.append([h.width, h.length, h.rotatable])
        net_area.append(h.area)
    for i in range(num_nurse_stn):
        n = rm.Nurse_station(i)
        inventory.append(n)
        rooms.append([n.type, n.room_number, n.area])
        rectangles.append([n.width, n.length, n.rotatable])
        net_area.append(n.area)
    for i in range(num_wtg_rm):
        w = rm.Waiting_room(i)
        inventory.append(w)
        rooms.append([w.type, w.room_number, w.area])
        rectangles.append([w.width, w.length, w.rotatable])
        net_area.append(w.area)
    for i in range(num_stg_alc):
        s = rm.Storage_alcove(i)
        inventory.append(s)
        rooms.append([s.type, s.room_number, s.area])
        rectangles.append([s.width, s.length, s.rotatable])
        net_area.append(s.area)
    for i in range(num_brk_rm):
        b = rm.Break_room(i)
        inventory.append(b)
        rooms.append([b.type, b.room_number, b.area])
        rectangles.append([b.width, b.length, b.rotatable])
        net_area.append(b.area)
    rooms = pd.DataFrame(rooms).rename(columns={0: 'room_type', 1: 'room_number', 2: 'total_room_size'})
    rooms = rooms[['room_type', 'total_room_size']].groupby(by='room_type').sum()
    return inventory, rooms, rectangles, sum(net_area)

def generate_counts(beds):    
    num_huc = math.ceil(1/20*beds)
    num_nurse_stn = math.ceil(1/15*beds)
    num_wtg_rm = math.ceil(1/20*beds)
    num_stg_alc = math.ceil(1/8*beds)
    num_brk_rm = math.ceil(1/20*beds)
    return beds, num_huc, num_nurse_stn, num_wtg_rm, num_stg_alc, num_brk_rm

if __name__ == '__main__':
    main()
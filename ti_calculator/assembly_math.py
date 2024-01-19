import math

def main():
    aspect_ratio = aspect_ratio_calculator()
    area, width, length, perimiter = assembly_math(aspect_ratio)
    print(f'for a rectangle of area {area} where the aspect ratio is {aspect_ratio}, it will be length{length: .3f}, width{width: .3f}, and the perimiter will be{perimiter: .0f}')

def aspect_ratio_calculator():
    while True:
        try:
            x,y = [float(i) for i in input('enter the room length and with in feet as comma-seperated decimals: ').replace(' ', '').split(',')]
            if x > y:
                return x / y
            else:
                return y / x
        except ValueError as e:
            pass
        except EOFError as e:
            break

def assembly_math(m_aspect_ratio=None, m_area=None):
    while True:
        try:
            if not m_aspect_ratio:
                m_aspect_ratio = aspect_ratio_calculator()
            if not m_area:
                m_area =float(input('enter the room area in square feet: ').replace(' ', ''))
            width = math.sqrt(m_area * m_aspect_ratio)
            length = math.sqrt(m_area * 1/m_aspect_ratio)
            perimiter = 2 * (width + length)
            return m_area, width, length, perimiter
        except ValueError as e:
            pass
        except EOFError as e:
            break

if __name__ == '__main__':
    main()
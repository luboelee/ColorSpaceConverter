import argparse


class MyColorSpaceConverter:
    def __init__(self):
        self.coefficients = {
            'bt601': (0.299, 0.587, 0.114),
            'bt709': (0.2126, 0.7152, 0.0722)
        }

    def _clamp(self, value):
        return max(0, min(255, int(round(value))))

    def rgb_to_yuv(self, r, g, b, standard='bt601', range_type='limited'):
        kr, kg, kb = self.coefficients.get(standard, self.coefficients['bt601'])
        
        y_raw = kr * r + kg * g + kb * b
        u_raw = (b - y_raw) / (2 * (1 - kb))
        v_raw = (r - y_raw) / (2 * (1 - kr))

        if range_type == 'full':
            y = y_raw
            u = u_raw + 128
            v = v_raw + 128
        else:
            # Limited Range
            # Y: 16 ~ 235 (scale 219/255)
            # U, V: 16 ~ 240 (scale 224/255) + 128 offset
            y = (219.0 / 255.0) * y_raw + 16
            u = (224.0 / 255.0) * u_raw + 128
            v = (224.0 / 255.0) * v_raw + 128

        return self._clamp(y), self._clamp(u), self._clamp(v)

    def yuv_to_rgb(self, y, u, v, standard='bt601', range_type='limited'):
        kr, kg, kb = self.coefficients.get(standard, self.coefficients['bt601'])

        if range_type == 'full':
            y_norm = y
            u_norm = u - 128
            v_norm = v - 128
        else:
            y_norm = (y - 16) * (255.0 / 219.0)
            u_norm = (u - 128) * (255.0 / 224.0)
            v_norm = (v - 128) * (255.0 / 224.0)
        
        r = y_norm + (2 * (1 - kr)) * v_norm
        b = y_norm + (2 * (1 - kb)) * u_norm
        g = (y_norm - kr * r - kb * b) / kg

        return self._clamp(r), self._clamp(g), self._clamp(b)


def test():
    converter = MyColorSpaceConverter()
    
    print("--- Red Color (255, 0, 0) Conversion [Limited Range] ---")
    
    y6, u6, v6 = converter.rgb_to_yuv(255, 0, 0, standard='bt601')
    print(f"BT.601 YUV: ({y6}, {u6}, {v6})")

    y7, u7, v7 = converter.rgb_to_yuv(255, 0, 0, standard='bt709')
    print(f"BT.709 YUV: ({y7}, {u7}, {v7})")
    
    print("\n>> Description: In Limited range, since the weight of Red in BT.709 (0.21) is lower than in BT.601 (0.29),")
    print("   in BT.601 (0.29), the Y value (brightness) for the same red color is calculated to be lower in BT.709.")


    print("\n\n")
    print("--- Red Color (255, 0, 0) Conversion [Full Range] ---")
    
    y6, u6, v6 = converter.rgb_to_yuv(255, 0, 0, standard='bt601', range_type='full')
    print(f"BT.601 YUV: ({y6}, {u6}, {v6})")

    y7, u7, v7 = converter.rgb_to_yuv(255, 0, 0, standard='bt709', range_type='full')
    print(f"BT.709 YUV: ({y7}, {u7}, {v7})")
    
    print("\n>> Description: In Full range, because the Red coefficient in BT.709 (0.21) is lower than that of BT.601 (0.29),")
    print("   the resulting Y value (luma) for an identical red input is lower in BT.709.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Color Space Converter')
    parser.add_argument('-y', '--yuv', nargs='*', help='YUV value (Y, U, V)', type=int)
    parser.add_argument('-r', '--rgb', nargs='*', help='RGB value (R, G, B)', type=int)
    parser.add_argument('-s', '--standard', default='bt601', choices=['bt601', 'bt709'], help='Color Space Standard (bt601, bt709)', type=str)
    parser.add_argument('-t', '--range', default='full', choices=['full', 'limited', 'fr', 'lr'], help='Color Range (full, fr, limited, lr)', type=str)
    
    args = parser.parse_args()
    if args.yuv == None and args.rgb == None:
        print("[Error] ./python3 my_color_space_converter.py -h\n")
        exit(-1)

    color_range = args.range
    if args.range == 'fr':
        color_range = 'full'
    elif args.range == 'lr':
        color_range = 'limited'

    converter = MyColorSpaceConverter()
    if args.yuv != None:
        v0, v1, v2 = converter.yuv_to_rgb(args.yuv[0], args.yuv[1], args.yuv[2], standard=args.standard, range_type=color_range)
        print(f'Converter YUV to RGB {args.standard}, {color_range}: {args.yuv[0]}, {args.yuv[1]}, {args.yuv[2]} --> {v0}, {v1}, {v2}')
    elif args.rgb != None:
        v0, v1, v2 = converter.rgb_to_yuv(args.rgb[0], args.rgb[1], args.rgb[2], standard=args.standard, range_type=color_range)
        print(f'Converter RGB to YUV {args.standard}, {color_range}: {args.rgb[0]}, {args.rgb[1]}, {args.rgb[2]} --> {v0}, {v1}, {v2}')

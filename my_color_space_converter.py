import argparse


class MyColorSpaceConverter:
    def __init__(self):
        self.coefficients = {
            'bt601':  (0.2990, 0.5870, 0.1140), # SDTV
            'bt709':  (0.2126, 0.7152, 0.0722), # HDTV
            'bt2020': (0.2627, 0.6780, 0.0593)  # UHDTV (4K/8K)
        }

    def _clamp(self, value, max_val):
        return max(0, min(max_val, int(round(value))))

    def _get_range_params(self, bit_depth, range_type):
        max_val = (1 << bit_depth) - 1  # 8bit=255, 10bit=1023
        
        shift = bit_depth - 8
        scale_factor = 1 << shift 

        if range_type == 'full':
            y_offset = 0
            y_range = max_val
            uv_offset = 128 * scale_factor
            uv_range = max_val
        else:
            y_offset = 16 * scale_factor
            y_range = 219 * scale_factor
            uv_offset = 128 * scale_factor
            uv_range = 224 * scale_factor
            
        return max_val, y_offset, y_range, uv_offset, uv_range

    def rgb_to_yuv(self, r, g, b, standard='bt709', range_type='limited', bit_depth=8):
        kr, kg, kb = self.coefficients.get(standard, self.coefficients['bt709'])
        max_val, y_off, y_rng, uv_off, uv_rng = self._get_range_params(bit_depth, range_type)

        r_n = r / max_val
        g_n = g / max_val
        b_n = b / max_val

        y_raw = kr * r_n + kg * g_n + kb * b_n
        u_raw = (b_n - y_raw) / (2 * (1 - kb))
        v_raw = (r_n - y_raw) / (2 * (1 - kr))

        y = y_rng * y_raw + y_off
        u = uv_rng * u_raw + uv_off
        v = uv_rng * v_raw + uv_off

        return self._clamp(y, max_val), self._clamp(u, max_val), self._clamp(v, max_val)

    def yuv_to_rgb(self, y, u, v, standard='bt709', range_type='limited', bit_depth=8):
        kr, kg, kb = self.coefficients.get(standard, self.coefficients['bt709'])
        max_val, y_off, y_rng, uv_off, uv_rng = self._get_range_params(bit_depth, range_type)

        y_n = (y - y_off) / y_rng
        u_n = (u - uv_off) / uv_rng
        v_n = (v - uv_off) / uv_rng

        r_n = y_n + (2 * (1 - kr)) * v_n
        b_n = y_n + (2 * (1 - kb)) * u_n
        g_n = (y_n - kr * r_n - kb * b_n) / kg

        r = r_n * max_val
        g = g_n * max_val
        b = b_n * max_val

        return self._clamp(r, max_val), self._clamp(g, max_val), self._clamp(b, max_val)


def test():
    cvt = MyColorSpaceConverter()

    print("=== 1. 10-bit BT.2020 Limited Range Test ===")
    # 10-bit Red (1023, 0, 0)
    # What is the Y value in BT.2020 Limited Range?
    r_in, g_in, b_in = 1023, 0, 0
    y, u, v = cvt.rgb_to_yuv(r_in, g_in, b_in, standard='bt2020', range_type='limited', bit_depth=10)
    
    print(f"Input RGB(10-bit): ({r_in}, {g_in}, {b_in})")
    print(f"-> BT.2020 YUV:    ({y}, {u}, {v})")
    print(f"   (Note: 10-bit Limited Y range is 64~940, UV center is 512)")
    
    # Verify inverse conversion
    r_out, g_out, b_out = cvt.yuv_to_rgb(y, u, v, standard='bt2020', range_type='limited', bit_depth=10)
    print(f"-> Restore RGB:    ({r_out}, {g_out}, {b_out})")
    
    print("\n=== 2. BT.709 vs BT.2020 Difference (8-bit) ===")
    # Check the difference in Y value (Luma) for the same Green color across standards
    # Since BT.2020 has a much wider Green gamut, the Y weight (0.678 vs 0.715)
    # is applied slightly differently compared to BT.709, even for the same RGB value (0, 255, 0).
    y709, _, _ = cvt.rgb_to_yuv(0, 255, 0, standard='bt709')
    y2020, _, _ = cvt.rgb_to_yuv(0, 255, 0, standard='bt2020')
    
    print(f"Pure Green(0,255,0) Luma(Y) Value:")
    print(f"BT.709  : {y709}")
    print(f"BT.2020 : {y2020}")

def run_all_cases(args):
    standard_array = ['bt601', 'bt709', 'bt2020']
    range_array = ['full', 'limited']
    bit_depth_array = [8, 10]
    
    converter = MyColorSpaceConverter()
    
    # RGB --> YUV --> RGB
    # YUV LR, FR, BT601, BT709, BT2020
    if args.rgb != None:
        for standard in standard_array:
            for range_type in range_array:
                for bit_depth in bit_depth_array:
                    r, g, b = args.rgb[0], args.rgb[1], args.rgb[2]
                    y, u, v = converter.rgb_to_yuv(r, g, b, standard=standard, range_type=range_type, bit_depth=bit_depth)
                    r_out, g_out, b_out = converter.yuv_to_rgb(y, u, v, standard=standard, range_type=range_type, bit_depth=bit_depth)
                    print(f'Converter RGB --> YUV --> RGB {standard}, {range_type}, {bit_depth}bit: {r}, {g}, {b} --> {y}, {u}, {v} --> {r_out}, {g_out}, {b_out}')
    elif args.yuv != None:
        # YUV --> RGB --> YUV
        for standard in standard_array:
            for range_type in range_array:
                for bit_depth in bit_depth_array:
                    y, u, v = args.yuv[0], args.yuv[1], args.yuv[2]
                    r, g, b = converter.yuv_to_rgb(y, u, v, standard=standard, range_type=range_type, bit_depth=bit_depth)
                    y_out, u_out, v_out = converter.rgb_to_yuv(r, g, b, standard=standard, range_type=range_type, bit_depth=bit_depth)
                    print(f'Converter YUV --> RGB --> YUV {standard}, {range_type}, {bit_depth}bit: {y}, {u}, {v} --> {r}, {g}, {b} --> {y_out}, {u_out}, {v_out}')

    print("\n")

def run_specific_case(args):
    color_range = args.range
    if args.range == 'fr':
        color_range = 'full'
    elif args.range == 'lr':
        color_range = 'limited'

    converter = MyColorSpaceConverter()
    if args.yuv != None:
        v0, v1, v2 = converter.yuv_to_rgb(args.yuv[0], args.yuv[1], args.yuv[2], standard=args.standard, range_type=color_range, bit_depth=args.bit_depth)
        print(f'Converter YUV to RGB {args.standard}, {color_range}: {args.yuv[0]}, {args.yuv[1]}, {args.yuv[2]} --> {v0}, {v1}, {v2}\n')
    elif args.rgb != None:
        v0, v1, v2 = converter.rgb_to_yuv(args.rgb[0], args.rgb[1], args.rgb[2], standard=args.standard, range_type=color_range, bit_depth=args.bit_depth)
        print(f'Converter RGB to YUV {args.standard}, {color_range}: {args.rgb[0]}, {args.rgb[1]}, {args.rgb[2]} --> {v0}, {v1}, {v2}\n')    


def cts_checker(args):
    converter = MyColorSpaceConverter()
    
    if args.rgb == None:
        print("[Error] For cts issue check, RGB value is required.")
        exit(-1)
    
    standard_array = ['bt601', 'bt709']
    range_array = ['full', 'limited']
    bit_depth_array = [8]
    
    r = args.rgb[0]
    g = args.rgb[1]
    b = args.rgb[2]
    
    # exprected(RGB): 120, 194, 87  --> real(RGB): 125, 209, 90
    idx = 0
    for std_src in standard_array:
        for std_dst in standard_array:
            for range_src in range_array:
                for range_dst in range_array:
                    y, u, v = converter.rgb_to_yuv(r, g, b, standard=std_src, range_type=range_src, bit_depth=8)
                    r_out, g_out, b_out = converter.yuv_to_rgb(y, u, v, standard=std_dst, range_type=range_dst, bit_depth=8)
                    print(f'{idx}.Converter RGB --> YUV{std_src}, {range_src} --> RGB{std_dst}, {range_dst}, 8bit: {r}, {g}, {b} --> {y}, {u}, {v} --> {r_out}, {g_out}, {b_out}')
                    idx += 1

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Color Space Converter. [10bit supported]', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-y', '--yuv', nargs='*', help='YUV value (Y, U, V)', type=int)
    parser.add_argument('-r', '--rgb', nargs='*', help='RGB value (R, G, B)', type=int)
    parser.add_argument('-s', '--standard', default='bt601', choices=['bt601', 'bt709', 'bt2020'], help='Color Space Standard', type=str)
    parser.add_argument('-t', '--range', default='full', choices=['full', 'limited', 'fr', 'lr'], help='Color Range', type=str)
    parser.add_argument('-b', '--bit-depth', default=8, choices=[8, 10], help='Bit Depth', type=int)
    parser.add_argument('-a', '--all', default=0, choices=[0, 1, 2], help='Enable all test', type=int)
    
    args = parser.parse_args()
    if args.yuv == None and args.rgb == None:
        print("[Error] ./python3 my_color_space_converter.py -h\n")
        exit(-1)

    if args.all == 0:
        run_specific_case(args)
    elif args.all == 1:
        run_all_cases(args)
    elif args.all == 2:
        cts_checker(args)
    else:
        print("[Error] ./python3 my_color_space_converter.py -h\n")
        exit(-1)

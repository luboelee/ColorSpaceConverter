# ColorSpaceConver README
"ColorSpaceConverter" converts between YUV and RGB, supporting BT.601 and BT.709 standards as well as Limited and Full color ranges.
<br><br>

## Usage
To show help description, you can use -h option.
```
python3 .\my_color_space_converter.py -h
```

These are supported options

```
options:
  -h, --help            show this help message and exit
  -y [YUV ...], --yuv [YUV ...]                         YUV value (Y, U, V)
  -r [RGB ...], --rgb [RGB ...]                         RGB value (R, G, B)
  -s {bt601,bt709}, --standard {bt601,bt709}            Color Space Standard (bt601, bt709)
  -t {full,limited,fr,lr}, --range {full,limited,fr,lr} Color Range (full, fr, limited, lr)
```

-----------------------------------------------
These are RGB to YUV simple examples.

```
python3 .\my_color_space_converter.py -r 0 255 0 
```
Converter RGB to YUV bt601, full: 0, 255, 0 --> 150, 44, 21

```
python3 .\my_color_space_converter.py -r 0 255 0 -s bt709 -t limited
```
Converter RGB to YUV bt709, limited: 0, 255, 0 --> 173, 42, 26

<br><br>
This is a example of YUV to RGB
```
python3 .\my_color_space_converter.py -y 173 42 26 -s bt709 -t limited
```
Converter YUV to RGB bt709, limited: 173, 42, 26 --> 0, 255, 1

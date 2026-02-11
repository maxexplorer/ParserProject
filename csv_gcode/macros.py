def dimple(y: float) -> str:
    return f"""G90
G0 Y{y} 
G00 X0 Y{y}
G91
G00 X-26.5 Y0
M3
G03 X-5.0 I-2.5 J0.
X5.0 I2.5 J0.
M5
G00 X-140.978 Y0.072
M3
G03 X-5.0 I-2.5 J0.
X5.0 I2.5 J0.
M5
G00 X140.978 Y0
"""


def end_truss_start(y: float) -> str:
    return f"""G90
G0 Y{y}
G00 X0 Y{y}
G91
G00 X-151.884 Y-18.089
M3
G01 X103
M5
G00 X36.341 Y-0.001
M3
G03 X-36.414 Y-0.018 I-18.207 J-0.118
M5
G00 X36.42 Y0.017
M3
G01 X2.0
M5
G00 X11.347 Y-4.133
M3
G01 X-11.276 Y4.104
M5
G00 X-142.512 Y-0.006
M3
G03 X-36.414 Y-0.018 I-18.207 J-0.118
M5
G00 X-0.064 Y0.014
M3
G01 X-2.0
M5
G00 X-0.057 Y-0.04
M3
G01 X-11.277 Y-4.104
M5
G00 X203.6 Y22.274
"""


def end_truss_finish(y: float) -> str:
    return f"""G90
G0 Y{y}
G00 X0 Y{y}
G91
G00 X-190.537 Y18.168
M3
G01 X-11.214 Y4.153
M5
G00 X13.286 Y-4.21
M3
G03 X36.414 Y-0.018 I18.207 J0.1
M5
G00 X-0.002 Y0.167
M3
G01 X104.099 Y-0.012
M5
G00 X-0.075 Y-0.141
M3
G03 X36.414 Y-0.017 I18.207 J0.1
M5
G00 X0.056 Y-0.002
M3
G01 X1.991 Y0.113
M5
G00 X11.418 Y4.567
M3
G01 X-11.386 Y-4.551
M5
G00 X-178.938 Y-0.157
M3
G01 X-2.021 Y0.041
M5
G00 X192.345 Y-18.101
"""


def lip_notch(y: float) -> str:
    return f"""G90
G0 Y{y}
G00 X0 Y{y}
G91
G00 X-189.64 Y-27.724
M3
G01 Y54.0
M5
G00 X-12.0 Y9.867
M3
G01 X11.975 Y-9.88
M5
G00 X-8.488 Y-62.55
M3
G01 Y0.087
M5
G00 X-3.561 Y-1.452
M3
G01 X12.106 Y9.944
M5
G00 X178.434 Y0.107
M3
G01 Y54.0
M5
G00 X0.053 Y-0.084
M3
G01 X12.599 Y10.92
M5
G00 X-12.635 Y-64.668
M3
G01 X12.957 Y-9.449
M5
G00 Y-0.769
"""


def web_notch(y: float) -> str:
    return f"""G90
G0 Y{y}
G00 X0 Y{y}
G91
G00 X-48.106 Y-25.23
M3
G01 Y0.016
M5
G00 X0.019 Y-2.494
M3
G01 Y54.292
M5
G00 X-0.029 Y-0.021
M3
G01 X-51.763 Y3.478
M5
G00 X-52.187 Y-2.764
M3
G01 X52.276 Y2.732
M5
G00 X-0.39 Y-59.986
M3
G01 X52.015 Y2.257
M5
G00 X-52.005 Y-2.272
M3
G01 X-51.977 Y3.259
M5
G00 X0.024 Y-0.017
M3
G01 X0.004 Y54.13
M5
G00 X51.907 Y0
"""


def service(y: float) -> str:
    return f"""G90
G0 Y{y}
G00 X0 Y{y}
G91
G00 X-82.5 Y0
M3
G03 X-35.132 I-17.566 J0.
X35.132 I17.566 J0.
M5
G00 Y0
"""


def cut(length) -> str:
    return f"""G90
G0 Y{length}
G00 X0 Y{length}
G91
G00 X-201.9 Y0.0
M3
G01 X204.0
M5
%
"""


def cut_length(length: float) -> str:
    return f"""G90
G0 Y{length + 4}
G00 X0 Y{length + 4}
G91
%
(Layout "Model")
(ABViewer 15 trial version - www.cadsofttools.com )
(Contour 0)
G00 X-201.9 Y0.0
M3
G01 X204.0
M5
M02
%
"""


macros = {
    'DIMPLE': dimple,
    'END_TRUSS_START': end_truss_start,
    'END_TRUSS_FINISH': end_truss_finish,
    'LIP NOTCH': lip_notch,
    'WEB NOTCH': web_notch,
    'SERVICE': service,
    'CUT': cut,
    'CUT_LENGTH': cut_length,
}

command_map = {
    'DIMPLE': 'DIMPLE',
    'END_TRUSS': ('END_TRUSS_START', 'END_TRUSS_FINISH'),
    'LIP NOTCH': 'LIP NOTCH',
    'WEB NOTCH': 'WEB NOTCH',
    'SERVICE': 'SERVICE',
}

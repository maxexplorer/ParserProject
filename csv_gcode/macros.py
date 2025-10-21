def dimple(y: float) -> str:
    return f"""DIMPLE G0 Y{y}
%
(Layout "Model")
(ABViewer 15 trial version - www.cadsofttools.com )
G94 G90 G17 G21 F450
(Contour 0)
G00 X0. Y2.5
M3
G03 X-5. I-2.5 J0.
X0. I2.5 J0.
M5
(Contour 1)
G00 X-143.978 Y2.572
M3
G03 X-148.978 I-2.5 J0.
X-143.978 I2.5 J0.
M5
G00 X0. Y0.
M30
%
"""


def end_truss_start(y: float) -> str:
    return f"""END_TRUSS START G0 Y{y}
%
(Layout "Model")
(ABViewer 15 trial version - www.cadsofttools.com )
G94 G90 G17 G21 F450
(Contour 0)
G00 X-153.694 Y-18.089
M3
G01 X-49.694
M5
(Contour 1)
G00 X-13.353 Y-18.09
M3
G03 X-49.767 Y-18.108 I-18.207 J-0.118
M5
(Contour 2)
G00 X-13.347 Y-18.091
M3
G01 X-11.347
M5
(Contour 3)
G00 X0. Y-22.224
M3
G01 X-11.276 Y-18.12
M5
(Contour 4)
G00 X-153.788 Y-18.126
M3
G03 X-190.202 Y-18.144 I-18.207 J-0.118
M5
(Contour 5)
G00 X-190.266 Y-18.13
M3
G01 X-192.266
M5
(Contour 6)
G00 X-192.323 Y-18.17
M3
G01 X-203.6 Y-22.274
M5
G00 X0. Y0.
M30
%
"""


def end_truss_finish(y: float) -> str:
    return f"""END_TRUSS FINISH G0 Y{y}
%
(Layout "Model")
(ABViewer 15 trial version - www.cadsofttools.com )
G94 G90 G17 G21 F450
(Contour 0)
G00 X-192.387 Y18.168
M3
G01 X-203.601 Y22.321
M5
(Contour 5)
G00 X-190.315 Y18.111
M3
G03 X-153.901 Y18.093 I18.207 J0.1
M5
(Contour 4)
G00 X-153.903 Y18.26
M3
G01 X-49.804 Y18.248
M5
(Contour 6)
G00 X-49.879 Y18.107
M3
G03 X-13.465 Y18.09 I18.207 J0.1
M5
(Contour 3)
G00 X-13.409 Y18.088
M3
G01 X-11.418 Y18.201
M5
(Contour 2)
G00 X0. Y22.768
M3
G01 X-11.386 Y18.217
M5
(Contour 1)
G00 X-190.324 Y18.06
M3
G01 X-192.345 Y18.101
M5
G00 X0. Y0.
M30
%
"""


def lip_notch(y: float) -> str:
    return f"""LIP_NOTCH G0 Y{y}
%
(Layout "Model")
(ABViewer 15 trial version - www.cadsofttools.com )
G94 G90 G17 G21 F450
(Contour 0)
G00 X-191.44 Y9.93
M3
G01 Y63.93
M5
(Contour 3)
G00 X-203.44 Y73.796
M3
G01 X-191.465 Y63.916
M5
(Contour 1)
G00 X-199.953 Y1.365
M3
G01 Y1.452
M5
(Contour 4)
G00 X-203.514 Y0.
M3
G01 X-191.408 Y9.944
M5
(Contour 2)
G00 X-12.974 Y10.051
M3
G01 Y64.051
M5
(Contour 5)
G00 X-12.921 Y63.967
M3
G01 X-0.322 Y74.886
M5
(Contour 6)
G00 X-12.957 Y10.218
M3
G01 X0. Y0.769
M5
G00 Y0.
M30
%
"""


def web_notch(y: float) -> str:
    return f"""WEB_NOTCH G0 Y{y}
%
(Layout "Model")
(ABViewer 15 trial version - www.cadsofttools.com )
G94 G90 G17 G21 F450
(Contour 0)
G00 X-0.019 Y4.762
M3
G01 Y4.778
M5
(Contour 2)
G00 X0. Y2.284
M3
G01 Y56.576
M5
(Contour 3)
G00 X-0.029 Y56.555
M3
G01 X-51.792 Y60.033
M5
(Contour 4)
G00 X-103.979 Y57.269
M3
G01 X-51.703 Y60.001
M5
(Contour 1)
G00 X-52.093 Y0.015
M3
G01 X-0.078 Y2.272
M5
(Contour 5)
G00 X-52.083 Y0.
M3
G01 X-104.06 Y3.259
M5
(Contour 6)
G00 X-104.036 Y3.242
M3
G01 X-104.032 Y57.372
M5
G00 X0. Y0.
M30
%
"""


def service(y: float) -> str:
    return f"""SERVICE G0 Y{y}
%
(Layout "Model")
(ABViewer 15 trial version - www.cadsofttools.com )
G94 G90 G17 G21 F450
(Contour 0)
G00 X0. Y17.566
M3
G03 X-35.132 I-17.566 J0.
X0. I17.566 J0.
M5
G00 Y0.
M30
%
"""


def cut() -> str:
    return f"""CUT
%
(Layout "Model")
(ABViewer 15 trial version - www.cadsofttools.com )
G94 G90 G17 G21 F450
(Contour 0)
G00 X-102. Y-0.034
M3
G01 X102.
M5
G00 X0. Y0.
M30
%
"""


def cut_length(length: float) -> str:
    return f"""CUT LENGTH G0 Y{length + 21}
%
(Layout "Model")
(ABViewer 15 trial version - www.cadsofttools.com )
G94 G90 G17 G21 F450
(Contour 0)
G00 X-102. Y-0.034
M3
G01 X102.
M5
G00 X0. Y0.
M30
%
"""


macros = {
    'DIMPLE': dimple,
    'END_TRUSS_START': end_truss_start,
    'END_TRUSS_FINISH': end_truss_finish,
    'LIP_NOTCH': lip_notch,
    'WEB_NOTCH': web_notch,
    'SERVICE': service,
    'CUT': cut,
    'CUT_LENGTH': cut_length,
}



command_map = {
    'DIMPLE': 'DIMPLE',
    'END_TRUSS': ('END_TRUSS_START', 'END_TRUSS_FINISH'),
    'LIP_NOTCH': 'LIP_NOTCH',
    'WEB_NOTCH': 'WEB_NOTCH',
    'SERVICE': 'SERVICE',
}



def dimple(y: float) -> str:
    return f"""
G0 Y{y}
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


def end_truss(y: float) -> str:
    return f"""
G0 Y{y}
%
(Layout "Model")
(ABViewer 15 trial version - www.cadsofttools.com )
G94 G90 G17 G21 F450
(Contour 0)
G00 X-153.694 Y4.185
M3
G01 X-49.694
M5
(Contour 1)
G00 X-13.353 Y4.184
M3
G03 X-49.767 Y4.166 I-18.207 J-0.118
M5
(Contour 2)
G00 X-13.347 Y4.183
M3
G01 X-11.347
M5
(Contour 3)
G00 X0. Y0.05
M3
G01 X-11.276 Y4.154
M5
(Contour 4)
G00 X-153.788 Y4.148
M3
G03 X-190.202 Y4.13 I-18.207 J-0.118
M5
(Contour 5)
G00 X-190.266 Y4.144
M3
G01 X-192.266
M5
(Contour 6)
G00 X-192.323 Y4.104
M3
G01 X-203.6 Y0.
M5
G00 X0.
M30
%
"""


def lip_notch(y: float) -> str:
    return f"""
G0 Y{y}
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
    return f"""
G0 Y{y}
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
    return f"""
G0 Y{y}
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


def cut(y: float) -> str:
    return f"""
G0 Y{y}
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
    'END_TRUSS': end_truss,
    'LIP_NOTCH': lip_notch,
    'WEB_NOTCH': web_notch,
    'SERVICE': service,
    'CUT': cut,
}



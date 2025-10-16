# macros.py

def dimple(x: float, y: float) -> str:
    return f"""(--- DIMPLE ---)
G0 X{x} Y{y} Z5
G1 Z-2 F200
G4 P0.5
G0 Z5
"""

def lip_notch(x: float, y: float) -> str:
    return f"""(--- LIP NOTCH ---)
G0 X{x} Y{y} Z5
G1 Z-1 F150
G1 X{x+20}
G0 Z5
"""

def end_truss(x: float, y: float) -> str:
    return f"""(--- END TRUSS ---)
G0 X{x} Y{y} Z5
G1 Z-3 F300
G1 X{x+100}
G1 Y{y+50}
G1 X{x}
G1 Y{y}
G0 Z5
"""

def web_notch(x: float, y: float) -> str:
    return f"""(--- WEB NOTCH ---)
G0 X{x} Y{y} Z5
G1 Z-2 F200
G1 X{x+40}
G0 Z5
"""

def service(x: float, y: float) -> str:
    return f"""(--- SERVICE ---)
G0 X{x} Y{y} Z5
G2 I10 J0 Z-2 F250
G0 Z5
"""

MACROS = {
    "DIMPLE": dimple,
    "LIP NOTCH": lip_notch,
    "END_TRUSS": end_truss,
    "WEB_NOTCH": web_notch,
    "SERVICE": service
}

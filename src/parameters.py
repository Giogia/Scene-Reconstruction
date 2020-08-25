# MODEL SETTINGS
MODELS = ['Claudia']
# ['Carla', 'Claudia', 'Eric']
ANIMATIONS = ['Attack']
# ['Attack', 'Backbend', 'Backflip', 'Catwalk', 'Cheer', 'Finger Taunt', 'Flying Kick', 'March']
EXTENSION = 'fbx'
POLY_NUMBER = 250
SCALE = 0.1

# CAMERAS SETTINGS
CAMERAS_NUMBER = 8
DISTANCE = 3
HEIGHT = 2
FOV = 60
NEAR_PLANE = 0.1
FAR_PLANE = 5 * DISTANCE

# CAMERA POSITION SETTINGS
DISTANCE_NOISE: float = DISTANCE * 0.5  # meters
HEIGHT_NOISE: float = HEIGHT  # meters
YAW_NOISE: float = 10  # degrees
FOV_NOISE: float = 10  # degrees

# RENDERING SETTINGS
RESOLUTION_X = 960
RESOLUTION_Y = 540
OUTPUT_RESOLUTION = 100  # percentage

# ANIMATION SETTINGS
START_FRAME = 1
END_FRAME = 200

RESET_SCENE = False
UPDATE_VIEWS = False

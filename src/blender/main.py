from .scene import setup_scene
from .render import setup_rendering_parameters, render
import os
import sys
from pathlib import Path
from bpy import data

from . parameters import *

# PATH TO REPOSITORY
PATH = Path(data.filepath).parent

sys.path.append(os.path.dirname(data.filepath))


def main():

    # Explore directory and run for every model in models
    models_directory = os.listdir(os.path.join(PATH, 'models'))

    for folder in models_directory:
        if os.path.isdir(os.path.join(PATH, 'models', folder)):

            models = os.listdir(os.path.join(PATH, 'models', folder))

            for model in models:
                if model.endswith('.fbx'):

                    name = os.path.splitext(model)[0]
                    model = setup_scene(name)

                    # Render
                    setup_rendering_parameters()

                    # render(model, TRAINING_SAMPLES, training=True)
                    render(model, TEST_SAMPLES)


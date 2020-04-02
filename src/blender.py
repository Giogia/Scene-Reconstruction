import os
import sys
from pathlib import Path
from bpy import data
from importlib import reload

from . import scene, render_utils, parameters

# PATH TO REPOSITORY
PATH = Path(data.filepath).parent

sys.path.append(os.path.dirname(data.filepath))


def main():

    reload(scene)
    reload(render_utils)
    reload(parameters)

    # Explore directory and run for every model in models
    models_directory = os.listdir(os.path.join(PATH, 'models'))

    for folder in models_directory:
        if os.path.isdir(os.path.join(PATH, 'models', folder)):

            models = os.listdir(os.path.join(PATH, 'models', folder))

            for model in models:
                if model.endswith('.fbx'):

                    name = os.path.splitext(model)[0]
                    model = scene.setup_scene(name)

                    # Render
                    render_utils.setup_rendering_parameters()

                    # render(model, TRAINING_SAMPLES, training=True)
                    render_utils.render(model, parameters.TEST_SAMPLES)





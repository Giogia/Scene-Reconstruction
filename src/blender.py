import os
import sys
from pathlib import Path
from bpy import data
from importlib import reload

from . import scene, camera, renderer, parameters

reload(scene)
reload(camera)
reload(renderer)
reload(parameters)

from .scene import Scene
from .camera import Camera
from .renderer import Renderer

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
                if model.endswith('.obj'):

                    name = os.path.splitext(model)[0]
                    if name not in parameters.MODELS:
                        break

                    # Render
                    scene = Scene(name, reset=True)
                    model = scene.model
                    camera = Camera()
                    renderer = Renderer()
                    path = os.path.join(PATH, 'data', model.name)
                    renderer.render(camera, model, path)






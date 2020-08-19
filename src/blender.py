import os
import sys
from importlib import reload
from pathlib import Path

from bpy import data

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
    
    print(PATH)

    # Explore directory and run for every model in models
    models_directory = os.listdir(os.path.join(PATH, 'models'))

    for folder in models_directory:
        if os.path.isdir(os.path.join(PATH, 'models', folder)):

            models = os.listdir(os.path.join(PATH, 'models', folder))
            for model in models:
                if model.endswith('.' + parameters.EXTENSION):

                    file_name = os.path.splitext(model)[0]

                    if all(name.lower() not in file_name for name in parameters.MODELS):
                        break
                    else:
                        name = [name for name in parameters.MODELS if name.lower() in file_name][0]

                        path = os.path.abspath(os.path.join(PATH, os.pardir,
                                                            'Neural-Volumes', 'experiments', name, 'data'))

                        # Render
                        scene = Scene(path, name, file_name, reset=True)
                        model = scene.model
                        camera = Camera()
                        renderer = Renderer()
                        renderer.retarget(model, scene.animations[0])
                        renderer.render(camera, model, path, update_views=False)







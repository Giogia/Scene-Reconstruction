import os
import sys
from importlib import reload
from pathlib import Path

from bpy import data

from . import scene_utils, camera_utils, renderer_utils, parameters

reload(scene_utils)
reload(camera_utils)
reload(renderer_utils)
reload(parameters)

from .scene_utils import Scene
from .camera_utils import Camera
from .renderer_utils import Renderer

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

                        # Render
                        scene = Scene(name, file_name, reset=parameters.RESET_SCENE)
                        camera = Camera()
                        renderer = Renderer()
                        
                        model = scene.model

                        for animation in scene.animations:

                            path = os.path.abspath(os.path.join(PATH, os.pardir,
                                                                'Neural-Volumes', 'experiments', name, 'data', animation.name))
                            renderer.retarget(model, animation)
                            renderer.render(camera, model, path, update_views=parameters.UPDATE_VIEWS)







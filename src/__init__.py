from . scene import setup_scene
from . render_sets import render_test, render_training
from bpy import context
from pathlib import Path
import os


PATH = os.path.abspath(Path(context.scene.sw_settings.filepath).parents[1])


def main():

    # Explore directory and run for every model in models
    for directory in os.listdir(os.path.join(PATH, 'models')):
        if os.path.isdir(os.path.join(PATH, 'models', directory)):

            for file in os.listdir(os.path.join(PATH, 'models', directory)):
                if file.endswith('.fbx'):
                    name = os.path.splitext(file)[0]

                    model = setup_scene(name)
                    render_test(model)
                    render_training(model)

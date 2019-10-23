from . scene import setup_scene
from . render_sets import render_test, render_training
import os
import sys
from pathlib import Path
from bpy import data

# PATH TO REPOSITORY
PATH = Path(data.filepath).parent

sys.path.append(os.path.dirname(data.filepath))


def main():

    # Explore directory and run for every model in models
    for directory in os.listdir(os.path.join(PATH, 'models')):
        if os.path.isdir(os.path.join(PATH, 'models', directory)):

            for file in os.listdir(os.path.join(PATH, 'models', directory)):
                if file.endswith('.fbx'):
                    name = os.path.splitext(file)[0]

                    model = setup_scene(name)
                    render_test(model)
                    # render_training(model)

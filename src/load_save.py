import csv
from ast import literal_eval
from math import degrees


def read_csv(file, field, row_number=0):
    
    reader = csv.DictReader(open(file))
    row = list(reader)[row_number]

    return literal_eval(row[field])


def csv_setup(file, header):

    writer = csv.writer(file)
    writer.writerow(header)

    return writer


def save_model_parameters(file, model):

    header = ['Name', 'Location', 'Rotation', 'Scale', 'Dimensions']
    writer = csv.writer(file, header)

    location = [coordinate for coordinate in model.location]
    rotation = [degrees(angle) for angle in model.rotation_euler]
    scale = [scale for scale in model.scale]
    dimensions = [dimension for dimension in model.dimensions]
    writer.writerow([model.name, location, rotation, scale, dimensions])
    file.flush()
    
    
def save_camera_parameters(name, camera, writer, file):

    location = [coordinate for coordinate in camera.location]
    rotation = [degrees(angle) for angle in camera.rotation_euler]
    writer.writerow([name, location, rotation, degrees(camera.data.angle)])
    file.flush()

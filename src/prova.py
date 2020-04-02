from pyntcloud import PyntCloud

cloud = PyntCloud.from_file("../test/Fox/mesh.ply")
cloud.plot()
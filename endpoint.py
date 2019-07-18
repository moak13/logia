from inspect import getsourcefile
import os.path
import sys

current_path = os.path.abspath(getsourcefile(lambda:0))
current_dir = os.path.dirname(current_path)
parent_dir = current_dir[:current_dir.rfind(os.path.sep)]

sys.path.insert(0, parent_dir)

from api import *

api.add_resource(UploadFile, '/upload')
api.add_resource(Generate, '/generate')
api.add_resource(NumpyData, '/numpies')


if __name__ == '__main__':
    app.run(host= "127.0.0.1", port=3000, debug=False)
import lasio
import pandas as pd
import matplotlib.pyplot as plt

from flask import Flask, request, jsonify
from flask_restful import Resource, Api
from inspect import getsourcefile
import os, datetime
import os.path
import sys
from werkzeug.utils import secure_filename
from utils.model import ModelClass

current_path = os.path.abspath(getsourcefile(lambda: 0))
current_dir = os.path.dirname(current_path)
parent_dir = current_dir[:current_dir.rfind(os.path.sep)]

sys.path.insert(0, parent_dir)

app = Flask(__name__)
api = Api(app)
model = ModelClass()

UPLOAD_FOLDER = 'UPLOAD_FOLDER'
DIR = os.makedirs(os.path.join(app.instance_path, UPLOAD_FOLDER), exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# def renameFile(file):
#     #dt = str(datetime.datetime())
#     dt = "newFile"
#     new_name = dt + '.las'
#     new_file = os.rename(file.filename, new_name)
#     return new_file

class UploadFile(Resource):
    def post(self):
        file = request.files['file']
        file.save(os.path.join(app.instance_path, UPLOAD_FOLDER, secure_filename(file.filename)))
        state = os.getcwd()
        for r, d, f in os.walk(state):
            for file in f:
                if '.las' in file:
                    base = os.path.join(r, file)
                    model.setFile(base)
                    return 'File Uploaded'

                    # las = lasio.read(base)
                    # df = las.df()
                    # data = jsonify(df.to_json())
                    # return data

class Generate(Resource):
    def post(self):
        file = model.getFile()
        las = lasio.read(file)
        data = las.df()
        # REST = jsonify(data.to_json())
        # return REST

        sheet = data[['TVDE', 'GR', 'P16H', 'P40H', 'RHOB', 'TNPH']]
        sheet = sheet.dropna()
        sheet.set_index('TVDE')
        sheet.describe()
        sheet.head(10)

        print(sheet)

        # rest = jsonify(sheet.to_json())

        # return rest

        sheet = sheet.drop(sheet[(sheet['RHOB'] < 1.65) | (sheet['RHOB'] > 2.65) 
                            | (sheet['GR'] < 1) | (sheet['GR'] > 150) 
                            | (sheet['TNPH'] < 0) | (sheet['TNPH'] > 0.6) 
                            | (sheet['P16H'] < 0.1) | (sheet['P16H'] > 2000) 
                            | (sheet['P40H'] < 0.1) | (sheet['P40H'] > 2000)].index)

        window = 25
        for i in list(sheet):
            sheet[i] = pd.Series(sheet[i].rolling(window = window, min_periods = 1).mean())
        
        fig = plt.figure(figsize=(20,10))

        ax1 = fig.add_subplot(1, 3, 1)
        ax1.scatter(sheet['GR'], sheet['TVDE'], color = 'm', alpha = 0.5)
        ax1.set_ylabel('TVDE', fontsize = '14')
        ax1.set_xlabel('GR', fontsize = '14')
        plt.ylim(7000, 9000)
        plt.gca().invert_yaxis()

        ax2 = fig.add_subplot(1, 3, 2)
        ax2.scatter(sheet['P16H'], sheet['TVDE'], color = 'g', alpha = 0.5)
        ax2.set_xlabel('P16H', fontsize = '14')
        ax2.set_xscale('log')
        plt.ylim(7000, 9000)
        plt.gca().invert_yaxis()

        ax3 = fig.add_subplot(1, 3, 2)
        ax3.scatter(sheet['P40H'], sheet['TVDE'], color = 'm', alpha = 0.5)
        ax3 = ax2.twiny()
        ax3.set_xlabel('P40H', fontsize = '14')
        ax3.set_xscale('log')
        plt.ylim(7000, 9000)
        plt.gca().invert_yaxis()

        ax4 = fig.add_subplot(1, 3, 3)
        ax4.scatter(sheet['RHOB'], sheet['TVDE'], color = 'r', alpha = 0.5)
        ax4.set_xlabel('RHOB', fontsize = '14')
        plt.xlim(1.65, 2.65)

        ax5 = fig.add_subplot(1, 3, 3)
        ax5 = ax4.twiny()
        ax5.scatter(sheet['TNPH'], sheet['TVDE'], color = 'k', alpha = 0.5)
        ax5.set_xlabel('TNPH', fontsize = '14')
        plt.xlim(0 , 0.6)
        plt.ylim(7000, 9000)
        plt.gca().invert_yaxis()

        return plt.show()
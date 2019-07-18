import lasio
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from flask import Flask, request, jsonify
from flask_restful import Resource, Api
from inspect import getsourcefile
import os
import datetime
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
DIR = os.makedirs(os.path.join(app.instance_path,
                               UPLOAD_FOLDER), exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Handles the well log generation

class UploadFile(Resource):
    def post(self):
        file = request.files['file']
        file.save(os.path.join(app.instance_path, UPLOAD_FOLDER,
                               secure_filename(file.filename)))
        state = os.getcwd()
        for r, d, f in os.walk(state):
            for file in f:
                if '.las' in file:
                    base = os.path.join(r, file)
                    model.setFile(base)
                    return 'File Uploaded'

class Generate(Resource):
    def post(self):
        file = model.getFile()
        las = lasio.read(file)
        data = las.df()

        sheet = data[['TVDE', 'GR', 'P16H', 'P40H', 'RHOB', 'TNPH']]
        sheet = sheet.dropna()
        sheet.set_index('TVDE')
        sheet.describe()
        sheet.head(10)

        sheet = sheet.drop(sheet[(sheet['RHOB'] < 1.65) | (sheet['RHOB'] > 2.65)
                                 | (sheet['GR'] < 0) | (sheet['GR'] > 150)
                                 | (sheet['TNPH'] > 0.6) | (sheet['TNPH'] < 0)
                                 | (sheet['P16H'] < 0.2) | (sheet['P16H'] > 2000)
                                 | (sheet['P40H'] < 0.2) | (sheet['P40H'] > 2000)].index)

        sheet = sheet.copy(deep=True)

        window = 17
        for i in list(sheet):
            sheet[i] = pd.Series(sheet[i]).rolling(
                window=window, min_periods=1).mean()

        fig = plt.figure(figsize=(20, 10))

        ax1 = fig.add_subplot(1, 3, 1)
        ax1.plot(sheet['GR'], sheet['TVDE'],
                 color='g', alpha=0.7, linestyle='-')
        ax1.set_ylabel('TVDE', fontsize='14')
        ax1.set_xlabel('GR', fontsize='14')
        ax1.grid(alpha=0.4)
        plt.ylim(7100, 8000)
        plt.gca().invert_yaxis()

        ax2 = fig.add_subplot(1, 3, 2)
        ax2.plot(sheet['P16H'], sheet['TVDE'],
                 color='b', alpha=0.7, linestyle='-')
        ax2.set_xlabel('P16H', fontsize='14')
        ax2.set_xscale('log')
        ax2.grid(alpha=0.4)
        plt.ylim(7100, 8000)
        plt.gca().invert_yaxis()

        ax3 = fig.add_subplot(1, 3, 2)
        ax3 = ax2.twiny()
        ax3.plot(sheet['P40H'], sheet['TVDE'],
                 color='m', alpha=0.7, linestyle='-')
        ax3.set_xlabel('P40H', fontsize='14')
        ax3.set_xscale('log')
        ax3.grid(alpha=0.4)
        plt.ylim(7100, 8000)
        plt.gca().invert_yaxis()

        ax4 = fig.add_subplot(1, 3, 3)
        ax4.plot(sheet['RHOB'], sheet['TVDE'],
                 color='r', alpha=0.7, linestyle='-')
        ax4.set_xlabel('RHOB', fontsize='14')
        ax4.grid(alpha=0.4)
        plt.xlim(1.65, 2.65)

        ax5 = fig.add_subplot(1, 3, 3)
        ax5 = ax4.twiny()
        ax5.plot(sheet['TNPH'], sheet['TVDE'],
                 color='b', alpha=0.7, linestyle='-')
        ax5.set_xlabel('TNPH', fontsize='14')
        ax5.grid(alpha=0.4)
        plt.xlim(0.6, 0)
        plt.ylim(7100, 8000)
        plt.gca().invert_yaxis()
        plt.show()

# Handles the seismic generation

class NumpyData(Resource):
    def post(self):
        numpyy = request.files['file']
        numpyy.save(os.path.join(app.instance_path, UPLOAD_FOLDER, secure_filename(numpyy.filename)))
        state = os.getcwd()
        for r, d, f in os.walk(state):
            for file in f:
                if '.npy' in file:
                    base = os.path.join(r, file)
                    print(base)
                    seabed = np.load(base)
                    print(seabed)
                    seabed *= -1
                    fig = plt.figure(figsize=(15, 6), facecolor='white')
                    ax = fig.add_subplot(111)
                    im = ax.imshow(seabed, cmap='GnBu_r', aspect=0.5, origin='lower')
                    ax.set_xlabel('X Side', size = 20.0); ax.set_ylabel('Y Side', size = 20.0)
                    cb = plt.colorbar(im, label='TNT sha')
                    mi, ma = np.floor(np.nanmin(seabed)), np.ceil(np.nanmax(seabed))
                    cb.set_clim(mi, ma)
                    cb.outline.set_visible(False)
                    step = 2
                    levels = np.arange(10*(mi//10), ma+step, step)  
                    lws = [0.5 if l%10 else 1 for l in levels]
                    cs = ax.contour(seabed, levels=levels, linewidths=lws, linestyles='solid', colors=[(0,0,0,0.4)])
                    ax.clabel(cs, fmt='%d', fontsize = 6.0)
                    ax.grid(color='w', alpha=0.4)
                    plt.setp([ax.spines.values()], color='w')
                    plt.show()

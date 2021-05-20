from typing import Optional

import tempfile
import os
from fastapi import FastAPI, File, Form, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import numpy as np
import eikonalfm as fm
from utils import extract_curve
from skimage import io
from scipy.ndimage.filters import gaussian_filter
# import matplotlib.pyplot as plt
# import matplotlib.rcsetup as rcsetup

app = FastAPI()

origins = ["http://localhost:3000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def parse_raw_point(rawPoint):
    x, y = map(float, rawPoint.split(','))
    return [y, x]

def parse_raw_points(rawPoints):
    return [parse_raw_point(rawPoint) for rawPoint in rawPoints.split(';')]

@app.post("/files/")
async def create_file(file: UploadFile = File(...), rawPoints = Form(...)):
    points = np.round(parse_raw_points(rawPoints)).astype('int')

    _, file_extension = os.path.splitext(file.filename)
    f = tempfile.NamedTemporaryFile(suffix=file_extension)
    f.write(file.file.read())
    # close file ?

    img = io.imread(f.name)
    img = img[:, :, 1]

    gauss = gaussian_filter(img, 1)
    gx = np.gradient(gauss, axis=0)
    gy = np.gradient(gauss, axis=1)
    metric = 1/(1e-4 + gx ** 2 + gy ** 2)

    curves = []
    for i in range(len(points)-1):
        dist_map = fm.fast_marching(1/metric, points[i], (1, 1), 2)
        curves.append(extract_curve(dist_map, points[i+1]))
    dist_map = fm.fast_marching(1/metric, points[-1], (1, 1), 2)
    curves.append(extract_curve(dist_map, points[0]))

    # fig = plt.figure(figsize=(20, 10))
    # plt.imshow(img, 'gray')
    # for c in curves:
    #     plt.plot(c[:, 1], c[:, 0], c='r')
    # plt.scatter(points[:, 1], points[:, 0], c='y')
    # plt.show()

    return {"curves": list(map(lambda a: a.tolist(), curves))}

from flask import render_template,abort,request,flash
#from flask_login import login_required
#from app import firebase
import sys
import os
from app import videos
from config import basedir
from app.main import bp
from app.main.models import Detected
from app.main.forms import DetectionForm,SearchForm

from werkzeug.utils import secure_filename

import tensorflow as tf
from keras.models import load_model
from keras.preprocessing.image import load_img,img_to_array
from keras.applications.vgg19 import VGG19,preprocess_input,decode_predictions
from keras.applications.vgg16 import VGG16
from PIL import Image
import numpy as np
from pathlib import Path
import cv2
import math

UPLOAD_FOLDER =  os.path.join(basedir, 'app/static/videos')

def remove_path(path: Path):
    if path.is_file() or path.is_symlink():
        path.unlink()
        return
    for p in path.iterdir():
        remove_path(p)
    path.rmdir()
	
#@firebase.jwt_required
#@login_required
@bp.route('/', methods=['GET', 'POST', 'PUT'])
def index():
	form = DetectionForm()
	detections = {}
	try:
		if request.method == 'POST':
			if form.validate_on_submit():
				files = []
				for f in os.listdir(UPLOAD_FOLDER):
					filename = os.path.join(UPLOAD_FOLDER, f)
					if os.path.isfile(filename):
						os.remove(filename)
					else:
						remove_path(Path(filename))
						#os.rmdir(filename)
				file = request.files['file']
				videofile = videos.save(file, name='video.')
				model = VGG16(weights = os.path.join(basedir, 'app/weights/vgg16_weights_tf_dim_ordering_tf_kernels.h5'), include_top=True)
				videofile = os.path.join(UPLOAD_FOLDER, videofile)
				cv = cv2.VideoCapture(videofile)
				frame_rate = cv.get(5)
				count = 0
				while(cv.isOpened()):
					frame_id = cv.get(1)
					ret, frame = cv.read()
					if (ret != True):
						break
					if (frame_id % math.floor(frame_rate) == 0):
						framefile = os.path.join(UPLOAD_FOLDER, 'frame.jpg')
						x = frame
						#x = Image.fromarray(x)
						#x = x.resize((224,224), Image.NEAREST)
						#x = np.array(x)
						#x = x.astype(np.float32)
						#x = cv2.resize(x, (224, 224))
						#x = x / 255.0
						cv2.imwrite(framefile, frame)
						x = load_img(framefile, target_size=(224,224,3))
						x = img_to_array(x)
						x = np.expand_dims(x, axis=0)
						x = preprocess_input(x)
						preds = model.predict(x)
						pred = decode_predictions(preds, top=1)[0]
						#print('Predicted:', pred)
						for p in pred:
							if len(p) > 0 and p[2] >= 0.1:
								if not os.path.isdir(os.path.join(UPLOAD_FOLDER, p[1])):
									os.makedirs(os.path.join(UPLOAD_FOLDER, p[1]))
								if p[1] in detections:
									detection = detections[p[1]]
									if p[2] > detection.percent:
										detection.percent = p[2]
								else:
									detection = Detected()
									detection.label = p[1]
									detection.percent = p[2]
									detection.frame = 'static/videos/' + p[1] + '/frame.jpg'
									detections[p[1]] = detection
								framefile2 = os.path.join(UPLOAD_FOLDER, p[1] + '/frame.jpg')
								#cv2.imwrite(filename2, frame)
								os.replace(framefile, framefile2)
					count = count + 1
				cv.release()
				if len(detections) == 0:
					flash('Nothing was detected')
	except Exception as ex:
		detections = {}
		flash(str(ex))
	return render_template('main/cgg.html', form=form, form2=SearchForm(), detections=detections.values())
	

#@firebase.jwt_required
#@login_required
@bp.route('/search', methods=['POST', 'GET'])
def search():
	form = SearchForm()
	detections = {}
	try:
		if request.method == 'POST':
			if form.validate_on_submit():
				search = request.form['search'].lower()
				print(request.form['search'])
				for f in os.listdir(UPLOAD_FOLDER):
					filename = os.path.join(UPLOAD_FOLDER, f)
					if not os.path.isfile(filename):
						if not f.lower().find(search) >= 0:
							continue
						for f2 in os.listdir(filename):
							filename2 = os.path.join(filename, f2)
							if os.path.isfile(filename2):
								detection = Detected()
								detection.label = f
								#detection.percent = ???
								detection.frame = 'static/videos/' + f + '/' + f2
								detections[f] = detection
								break
			if len(detections) == 0:
						flash('No match found')
	except Exception as ex:
		detections = {}
		flash(str(ex))
	return render_template('main/cgg.html', form=DetectionForm(), form2=form, detections=detections.values())
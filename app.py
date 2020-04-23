#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 12 00:16:35 2020

@author: utsav
"""

# flask APP
from Aadhaar import Aadhaar_Card
from flask import Flask, request, Response
import jsonpickle
import cv2
import numpy as np
import uuid
import base64
import os
# Initialize the Flask application
#app = Flask(__name__)
app = Flask(__name__, static_url_path='',static_folder='public');
config = {'orient' : True,    #corrects orientation of image default -> True
          'skew' : False,     #corrects skewness of image default -> True
          'crop': True,       #crops document out of image default -> True
          'contrast' : True,  #Bnw for Better OCR default -> True
          'psm': [3,4,6],     #Google Tesseract  psm modes by default 3,4,6. 
          'mask_color': (0, 165, 255),  #Masking color BGR Format
          'brut_psm': [3,4,6]     #Note : Keep only one psm for brut mask (6) is good to start
          }



def to_image_string(image_filepath):
    return base64.b64encode(open(image_filepath, 'rb').read())#.encode('base64')

def delete_file(path):
  if os.path.exists(path):
    os.remove(path)
#    print("Removed the file %s" % path)
#  else:
#    print("Sorry, file %s does not exist." % path)



#-----------------------------------[1]  Index.html for GUI-----------------------------------------------------
def get_file(filename):  # pragma: no cover
    try:
        src = os.path.join(filename)
        return open(src).read()
    except IOError as exc:
        return str(exc)

@app.route('/', methods=['GET'])
def indexfile():  # pragma: no cover
    content = get_file('public/imagebase64.html')
    return Response(content, mimetype="text/html")
#---------------------------------------------------------------------------------------



#------------------------------------[2] Validate method to check sequence in aadhar Number-----------------------------------------------
@app.route('/api/validate', methods=['GET','POST'])
def validate():
    ac = Aadhaar_Card(config);
    r = request.get_json(force=True)   #content type application/json
    content_type = 'application/json'
    headers = {'content-type': content_type}
    ac = Aadhaar_Card(config);
    validity=ac.validate(str(r['test_number']))
    
    return Response(response=jsonpickle.encode({'validity':validity}), status=200, mimetype="application/json", headers=headers)
#-----------------------------------------------------------------------------------------------------------------------------------------


#------------------------------------[3] Extract Aadhaar from a base64 image--------------------------------------------------------------
@app.route('/api/ocr', methods=['GET','POST'])
def ocr():
    ac = Aadhaar_Card(config);
    requestid=uuid.uuid4();
    temp_name = "input/"+str(requestid)+".png" 
    r = request.get_json(force=True)  #force=True #content type application/json
    
    image = r['doc_b64'] # raw data with base64 encoding
    
    decoded_data = base64.b64decode(image)
    np_data = np.fromstring(decoded_data,np.uint8)
    
    img = cv2.imdecode(np_data,cv2.IMREAD_UNCHANGED)
    cv2.imwrite(temp_name,img)
    content_type = 'application/json'
    headers = {'content-type': content_type}
    try:
        #print("Extracting Addhar")
        print(ac.uuid);
        aadhar=ac.extract(temp_name)
        delete_file(temp_name)
        return Response(response=jsonpickle.encode({'aadhaar_list':aadhar}), status=200, mimetype="application/json", headers=headers)
    except Exception as e:
        print(e)
        return Response(response=jsonpickle.encode({'aadhaar_list':''}), status=200, mimetype="application/json", headers=headers)
#-----------------------------------------------------------------------------------------------------------------------------------------



#------------------------------------[4] Mask aadhaar number card for given aadhaar card number-------------------------------------------
@app.route('/api/mask', methods=['GET','POST'])
def mask():
    ac = Aadhaar_Card(config);
    flag_mask = 0
    requestid=uuid.uuid4();
    temp_name = "input/"+str(requestid)+".png" 
    r = request.get_json(force=True)  #force=True #content type application/json
    #temp_name = "temp_unmasked.png" 
    image = r['doc_b64'] # raw data with base64 encoding
    decoded_data = base64.b64decode(image)
    np_data = np.fromstring(decoded_data,np.uint8)

    img = cv2.imdecode(np_data,cv2.IMREAD_UNCHANGED)
    cv2.imwrite(temp_name,img)
    write = "temp_masked.png"
    flag_mask = ac.mask_image(temp_name, write, r['aadhaar'])
    delete_file(temp_name)
    content_type = 'application/json'
    headers = {'content-type': content_type}

    if flag_mask == 0:
        return Response(response=jsonpickle.encode({'doc_b64_masked':'None', 'is_masked': False}), status=200, mimetype="application/json", headers=headers)
    else:
        img_bytes = to_image_string(write)
        delete_file(write)
        #convert byte to string
        encoded_string = img_bytes.decode("utf-8")
        return Response(response=jsonpickle.encode({'doc_b64_masked':encoded_string, 'is_masked': True}), status=200, mimetype="application/json", headers=headers)
#-----------------------------------------------------------------------------------------------------------------------------------------


#Brut Mask any Readable Number from Aadhaar (works good for low res and bad quality images)
@app.route('/api/brut_mask', methods=['GET','POST'])
def brut_mask():
    ac = Aadhaar_Card(config);
    r = request.get_json(force=True)  #force=True #content type application/json
    temp_name = "temp_unmasked.png" 
    image = r['doc_b64'] # raw data with base64 encoding
    decoded_data = base64.b64decode(image)
    np_data = np.fromstring(decoded_data,np.uint8)
    img = cv2.imdecode(np_data,cv2.IMREAD_UNCHANGED)
    cv2.imwrite(temp_name,img)
    write = "temp_brut_masked.png"
    mask_status = ac.mask_nums(temp_name, write)
    delete_file(temp_name)
    content_type = 'application/json'
    headers = {'content-type': content_type}

    img_bytes = to_image_string(write)
    delete_file(write)
    #convert byte to string
    encoded_string = img_bytes.decode("utf-8")
    return Response(response=jsonpickle.encode({'doc_b64_brut_masked':encoded_string, 'mask_status': mask_status}), status=200, mimetype="application/json", headers=headers)



#Usecase : You have an aadhaar doc, you want to mask first 8 digits of the aadhaar card
#Process : Image -> Extract Text -> Check for aadhaar number -> Mask first 8 digits // check validity of aadhaar number optional
#          If aadhaar card number is not found using OCR, try brut mode and mask possible numbers.

@app.route('/api/Mask8Digits', methods=['GET','POST'])
def sample_pipe():
    ac = Aadhaar_Card(config);
    flag_mask = 0
    r = request.get_json(force=True)  #force=True #content type application/json
    temp_name = "temp_unmasked.png" 
    image = r['doc_b64'] # raw data with base64 encoding
    decoded_data = base64.b64decode(image)
    np_data = np.fromstring(decoded_data,np.uint8)
    img = cv2.imdecode(np_data,cv2.IMREAD_UNCHANGED)
    cv2.imwrite(temp_name,img)
    aadhaar_list = ac.extract(temp_name)
    content_type = 'application/json'
    headers = {'content-type': content_type}
    
    if len(aadhaar_list) == 0 and r['brut']:
        mode_executed = "BRUT-OCR-MASKING"
        write = "temp_brut_masked.png"
        mask_status = ac.mask_nums(temp_name, write)
        delete_file(temp_name)
        img_bytes = to_image_string(write)
        delete_file(write)
        #convert byte to string
        encoded_string = img_bytes.decode("utf-8")
        return Response(response=jsonpickle.encode({'doc_b64_masked':encoded_string, 'is_masked': True,'mode_executed' : mode_executed}), status=200, mimetype="application/json", headers=headers)
        
    if len(aadhaar_list) == 0 and not r['brut']:
        mode_executed = "OCR-MASKING"
        return Response(response=jsonpickle.encode({'doc_b64_masked':'None', 'is_masked': False, 'error':'Unable to find aadhaar number','mode_executed' : mode_executed}), status=200, mimetype="application/json", headers=headers)
        
    if len(aadhaar_list) > 0 :
        mode_executed = "OCR-MASKING"
        # for masking first 8 digits from the number
        ori_aadhaar_list = aadhaar_list
        aadhaar_list = list(map(lambda x: x[:8] , aadhaar_list)) # Comment out this incase you want to mask entire aadhaar
        write = "temp_masked.png"
        flag_mask = ac.mask_image(temp_name, write, aadhaar_list)
        delete_file(temp_name)
        img_bytes = to_image_string(write)
        delete_file(write)
        #convert byte to string
        encoded_string = img_bytes.decode("utf-8")
        valid_aadhaar_list = list(filter(lambda x: (ac.validate(x) == 1) , ori_aadhaar_list))
        return Response(response=jsonpickle.encode({'doc_b64_masked':encoded_string, 'is_masked': True,'mode_executed' : mode_executed, 'aadhaar_list':ori_aadhaar_list, 'valid_aadhaar_list':valid_aadhaar_list}), status=200, mimetype="application/json", headers=headers)

# start flask app
app.run(host="0.0.0.0", port=9001,threaded=True) #debug = True



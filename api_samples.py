#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 26 20:59:22 2020

@author: utsav
"""

import numpy as np
import cv2
import base64
import requests
import json

def to_image_string(image_filepath):
    return base64.b64encode(open(image_filepath, 'rb').read())#.encode('base64')

def from_base64(base64_data):
    nparr = np.fromstring(base64_data.decode('base64'), np.uint8)
    return cv2.imdecode(nparr, cv2.IMREAD_ANYCOLOR)

def hit_api_validate(number):
    # prepare headers for http request
    content_type = 'application/json'
    headers = {'content-type': content_type}
    addr = 'http://localhost:9001'
    url = addr + '/api/validate'
    response = requests.post(url, json={"test_number": number} , headers=headers)
    return json.loads(response.text)

def hit_api_extract(filepath):
    img_bytes = to_image_string(filepath)
    #convert byte to string
    encoded_string = img_bytes.decode("utf-8")
    # prepare headers for http request
    content_type = 'application/json'
    headers = {'content-type': content_type}
    addr = 'http://localhost:9001'
    url = addr + '/api/ocr'
    response = requests.post(url, json={"doc_b64": encoded_string} , headers=headers)
    return json.loads(response.text)


def hit_api_mask_aadhaar(filepath,number_list):
    img_bytes = to_image_string(filepath)
    #convert byte to string
    encoded_string = img_bytes.decode("utf-8")
    # prepare headers for http request
    content_type = 'application/json'
    headers = {'content-type': content_type}
    addr = 'http://localhost:9001'
    url = addr + '/api/mask'
    response = requests.post(url, json={"doc_b64": encoded_string, 'aadhaar': number_list}, headers=headers)
    
    r = json.loads(response.text)
    if r['is_masked']:
        save_name = "masked_"+filepath
        decoded_data = base64.b64decode(r['doc_b64_masked'])
        np_data = np.fromstring(decoded_data,np.uint8)
        img = cv2.imdecode(np_data,cv2.IMREAD_UNCHANGED)
        cv2.imwrite(save_name,img)
        return "masked document saved as "+ save_name
    else:
        return "Unable to find given number in the image :/ (try brut mode)"


def hit_api_brut_mask(input_name,output_name):
    img_bytes = to_image_string(input_name)
    #convert byte to string
    encoded_string = img_bytes.decode("utf-8")
    # prepare headers for http request
    content_type = 'application/json'
    headers = {'content-type': content_type}
    addr = 'http://localhost:9001'
    url = addr + '/api/brut_mask'
    response = requests.post(url, json={"doc_b64": encoded_string}, headers=headers)
    r = json.loads(response.text)
    save_name = output_name
    decoded_data = base64.b64decode(r['doc_b64_brut_masked'])
    np_data = np.fromstring(decoded_data,np.uint8)
    img = cv2.imdecode(np_data,cv2.IMREAD_UNCHANGED)
    cv2.imwrite(save_name,img)
    return "masked document saved as "+ save_name

def hit_api_sample_pipe(input_name,output_name,brut = False):
    img_bytes = to_image_string(input_name)
    #convert byte to string
    encoded_string = img_bytes.decode("utf-8")
    # prepare headers for http request
    content_type = 'application/json'
    headers = {'content-type': content_type}
    addr = 'http://localhost:9001'
    url = addr + '/api/sample_pipe'
    response = requests.post(url, json={"doc_b64": encoded_string, "brut" : brut}, headers=headers)
    r = json.loads(response.text)
    if r['is_masked']:
        save_name = output_name
        decoded_data = base64.b64decode(r['doc_b64_masked'])
        np_data = np.fromstring(decoded_data,np.uint8)
        img = cv2.imdecode(np_data,cv2.IMREAD_UNCHANGED)
        cv2.imwrite(save_name,img)
        print("Execution Mode =>",r['mode_executed'])
        if r['mode_executed'] == "OCR-MASKING":
            print("Aadhaar List =>",r['aadhaar_list'])
            print("Validated Aadhaar list =>",r['valid_aadhaar_list'])
        return "masked document saved as "+ save_name
    else:
        print("Execution Mode =>",r['mode_executed'])
        print("Error =>",r['error'])
        return "Unable to find given number in the image :/ (try brut mode)"



#####################Usage => ###################

#Validates Aadhaar card numbers using Verhoeff Algorithm.
number = 397788000234 
print(hit_api_validate(number))


#Extract aadhaar Number from image '1.png'

image = '1.png' # I assume you have a way of picking unique filenames
print(hit_api_extract(image))  #Returns empty list if aadhaar is not found


#Mask aadhaar number card for given aadhaar card number

aadhaar_list = ['397788000234']
image = '1.png' # I assume you have a way of picking unique filenames
print(hit_api_mask_aadhaar(image,aadhaar_list))  #saves masked image as masked+image => masked_1.png

#Brut Mask any Readable Number from Aadhaar (works good for low res and bad quality images)

image = '1.png' # I assume you have a way of picking unique filenames
masked_image = 'brut_masked.png' # I assume you have a way of picking unique filenames
print(hit_api_brut_mask(image,masked_image))


#Usecase : You have an aadhaar doc, you want to mask first 8 digits of the aadhaar card
#Process : Image -> Extract Text -> Check for aadhaar number -> Mask first 8 digits // check validity of aadhaar number
#          If aadhaar card number is not found using OCR, try brut mode and mask possible numbers.

#This is implemented in app.py Now lets hit this pipeline here

image = '1.png' # I assume you have a way of picking unique filenames
masked_image = 'masked_aadhaar.png' # I assume you have a way of picking unique filenames
brut_mode = True #uses brut mode incase if ocr fails
print(hit_api_sample_pipe(image,masked_image,brut_mode))



#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 20 00:16:35 2020

@author: utsav
"""

import cv2
#from PIL import Image
import pytesseract
from pytesseract import Output
import re
#import os
import numpy as np
import math
from scipy import ndimage
import face_recognition

class Aadhaar_Card():
    #Constructor
    def __init__(self,config = {'orient' : True,'skew' : True,'crop': True,'contrast' : True,'psm': [3,4,6],'mask_color': (0, 165, 255), 'brut_psm': [6]}):
        self.config = config
    # Validates Aadhaar card numbers using Verhoeff Algorithm.
    # Fails if the fake number is generated using same Algorithm.
    def validate(self,aadhaarNum):
        
        mult = [[0, 1, 2, 3, 4, 5, 6, 7, 8, 9], [1, 2, 3, 4, 0, 6, 7, 8, 9, 5], [2, 3, 4, 0, 1, 7, 8, 9, 5, 6],
            [3, 4, 0, 1, 2, 8, 9, 5, 6, 7], [4, 0, 1, 2, 3, 9, 5, 6, 7, 8], [5, 9, 8, 7, 6, 0, 4, 3, 2, 1],
            [6, 5, 9, 8, 7, 1, 0, 4, 3, 2], [7, 6, 5, 9, 8, 2, 1, 0, 4, 3], [8, 7, 6, 5, 9, 3, 2, 1, 0, 4],
            [9, 8, 7, 6, 5, 4, 3, 2, 1, 0]]

        perm = [[0, 1, 2, 3, 4, 5, 6, 7, 8, 9], [1, 5, 7, 6, 2, 8, 3, 0, 9, 4], [5, 8, 0, 3, 7, 9, 6, 1, 4, 2],
            [8, 9, 1, 6, 0, 4, 3, 5, 2, 7], [9, 4, 5, 3, 1, 2, 6, 8, 7, 0], [4, 2, 8, 6, 5, 7, 3, 9, 0, 1],
            [2, 7, 9, 3, 8, 0, 6, 4, 1, 5], [7, 0, 4, 6, 9, 1, 3, 2, 5, 8]]


        try:
            i = len(aadhaarNum)
            j = 0
            x = 0

            while i > 0:
                i -= 1
                x = mult[x][perm[(j % 8)][int(aadhaarNum[i])]]
                j += 1
            if x == 0:
                return 1 
            else:
                return 0 

        except ValueError:
            return 0 
        except IndexError:
            return 0 
        

        
    def extract(self, path):  #("path of input image")
        self.image_path = path
        self.read_image_cv()
        if self.config['orient']:

            try:
                self.cv_img = self.rotate(self.cv_img)
            except:
                self.read_image_pil()
            else:
                self.cv_img.save('1_temp.png')
                self.pil_img = Image.open('1_temp.png')     
                os.remove('1_temp.png')
        
        self.pil_img = self.pil_img.convert('RGBA')
            
        if self.config['skew']:
            print("skewness correction not available")
        
        if self.config['crop']:
            print("Smart Crop not available")
        
        if self.config['contrast']:
            self.pil_img  = self.contrast_image(self.pil_img )
            print("correcting contrast")
            
        aadhaars = set()
        for i in range(len(self.config['psm'])):
            t = self.text_extractor(self.pil_img,self.config['psm'][i])
            anum = self.is_aadhaar_card(t)
            uid = self.find_uid(t)


            if anum != "Not Found" and len(uid) == 0:
                if len(anum) - anum.count(' ') == 12:
                   aadhaars.add(anum.replace(" ", ""))
            if anum == "Not Found" and len(uid) != 0:

                aadhaars.add(uid[0].replace(" ", ""))
            if anum != "Not Found" and len(uid) != 0:
                if len(anum) - anum.count(' ') == 12:
                   aadhaars.add(anum.replace(" ", ""))
                #print(uid[0].strip())
                aadhaars.add(uid[0].replace(" ", ""))

        return list(aadhaars)
    
    def mask_image(self, path, write, aadhaar_list):
        #print("Read Path => ", path, " write path => ",write, "aadhaar list =>",aadhaar_list)
        self.mask_count = 0
        self.mask = cv2.imread(str(path), cv2.IMREAD_COLOR)
        for j in range(len(self.config['psm'])):
            for i in range(len(aadhaar_list)):
                #print(" Runing mode: Aadhaar number:",aadhaar_list[i]," PSM => ",self.config['psm'][j])
                if (self.mask_aadhaar(aadhaar_list[i],write,self.config['psm'][j]))>0:
                    self.mask_count = self.mask_count + 1
                #print(" :\/ ",self.mask_count)
            
        #print("Final Mask Count =>",self.mask_count)
        cv2.imwrite(write,self.mask)
        return self.mask_count
    
    def mask_aadhaar(self, uid, out_path, psm):
        d = self.box_extractor(self.mask, psm)
        n_boxes = len(d['level'])
        color = self.config['mask_color'] #BGR
        count_of_match = 0
        for i in range(n_boxes):
            string = d['text'][i].strip()
            if string.isdigit() and string in uid and len(string)>=2:
                (x, y, w, h) = (d['left'][i], d['top'][i], d['width'][i], d['height'][i])
                cv2.rectangle(self.mask, (x, y), (x + w, y + h), color, cv2.FILLED)
                count_of_match = count_of_match + 1 
            else:
                count_of_match = count_of_match + 0
        return count_of_match 

    def read_image_cv(self):
        self.cv_img = cv2.imread(str(self.image_path), cv2.IMREAD_COLOR)
        
    def read_image_pil(self):
        self.pil_img = Image.open(self.image_path)
        
    def mask_nums(self, input_file, output_file):
        img = cv2.imread(str(input_file), cv2.IMREAD_COLOR)
        for i in range(len(self.config['brut_psm'])):      #'brut_psm': [6]
            d = self.box_extractor(img,self.config['brut_psm'][i])
            n_boxes = len(d['level'])
            color = self.config['mask_color']  #BGR
            for i in range(n_boxes):
                string = d['text'][i].strip()
                if string.isdigit() and len(string)>=1:
                    #print('Number to be Masked =>',string)
                    (x, y, w, h) = (d['left'][i], d['top'][i], d['width'][i], d['height'][i])
                    #print("Rectangles =>",(x, y, w, h))
                    cv2.rectangle(img, (x, y), (x + w, y + h), color, cv2.FILLED)

        cv2.imwrite(output_file,img)

        return "Done"
    
    
    
    # Corrects orientation of image using tesseract OSD if rotation Angle is < 100.
    def rotate(self,image, center = None, scale = 1.0):

        rotate_angle=int(re.search('(?<=Rotate: )\d+', pytesseract.image_to_osd(image)).group(0))

        if rotate_angle > 100:
            
            img = Image.fromarray(image, 'RGB')
            b, g, r = img.split()
            img = Image.merge("RGB", (r, g, b))
            return img

        else:
            angle=360-int(re.search('(?<=Rotate: )\d+', pytesseract.image_to_osd(image)).group(0))
            (h, w) = image.shape[:2]

            if center is None:
                center = (w / 2, h / 2)

            # Perform the rotation
            M = cv2.getRotationMatrix2D(center, angle, scale)
            rotated = cv2.warpAffine(image, M, (w, h))

            img = Image.fromarray(rotated, 'RGB')
            b, g, r = img.split()
            img = Image.merge("RGB", (r, g, b))

            return img
        
    # Turns images BnW using pixels, didn't have much success with this and skipped in final production 
    def contrast_image(self, img):
        pix = img.load()
        # taking pixel value for using in ocr
        for y in range(img.size[1]):
            for x in range(img.size[0]):
                if pix[x, y][0] < 102 or pix[x, y][1] < 102 or pix[x, y][2] < 102:
                    pix[x, y] = (0, 0, 0, 255)
                else:
                    pix[x, y] = (255, 255, 255, 255)
        return img
    
    # Extracts Texts from images
    def text_extractor(self, img, psm):
        config  = ('-l eng --oem 3 --psm '+ str(psm))
        t = pytesseract.image_to_string(img, lang='eng', config = config)
        return t
    # Extracts Texts and their bounding boxes in form of txt
    def box_extractor(self, img, psm):
        config  = ('-l eng --oem 3 --psm '+ str(psm))
        t = pytesseract.image_to_data(img, lang='eng', output_type=Output.DICT, config=config) 
        return t

    def find_uid(self,text2):
        # Searching for UID
        uid = set()
        try:
            newlist = []
            for xx in text2.split('\n'):
                newlist.append(xx)
            newlist = list(filter(lambda x: len(x) > 12, newlist))
            for no in newlist:
                #print(no)
                if re.match("^[0-9 ]+$", no):
                    uid.add(no)

        except Exception:
            pass
        return list(uid)
    
    #Function to validate if an image contains text showing its an aadhaar card
    def is_aadhaar_card(self, text):
               res=text.split()
               aadhaar_number=''
               for word in res:
                  if len(word) == 4 and word.isdigit():
                      aadhaar_number=aadhaar_number  + word + ' '
               if len(aadhaar_number)>=14:
                   return aadhaar_number
                   
               else:

                    return "Not Found"
                
                

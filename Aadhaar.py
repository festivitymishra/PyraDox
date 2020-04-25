# -*- coding: utf-8 -*-
"""
Created on Fri Apr 24 20:01:19 2020

@author: Kshitija Surange
"""


import cv2
from PIL import Image
import pytesseract
from pytesseract import Output
import re

import numpy as np
import math
from scipy import ndimage
import face_recognition
import uuid
import os

class Aadhaar_Card():
    #Constructor
    def __init__(self,config = {'orient' : True,'skew' : True,'crop': True,'contrast' : True,'psm': [3,4,6],'mask_color': (0, 165, 255), 'brut_psm': [6]}):
        self.config = config
        self.uuid=uuid.uuid4();
    # Validates Aadhar card numbers using Verhoeff Algorithm.
    # Fails if the fake number is generated using same Algorithm.
    def validate(self,aadharNum):
        
        mult = [[0, 1, 2, 3, 4, 5, 6, 7, 8, 9], [1, 2, 3, 4, 0, 6, 7, 8, 9, 5], [2, 3, 4, 0, 1, 7, 8, 9, 5, 6],
            [3, 4, 0, 1, 2, 8, 9, 5, 6, 7], [4, 0, 1, 2, 3, 9, 5, 6, 7, 8], [5, 9, 8, 7, 6, 0, 4, 3, 2, 1],
            [6, 5, 9, 8, 7, 1, 0, 4, 3, 2], [7, 6, 5, 9, 8, 2, 1, 0, 4, 3], [8, 7, 6, 5, 9, 3, 2, 1, 0, 4],
            [9, 8, 7, 6, 5, 4, 3, 2, 1, 0]]

        perm = [[0, 1, 2, 3, 4, 5, 6, 7, 8, 9], [1, 5, 7, 6, 2, 8, 3, 0, 9, 4], [5, 8, 0, 3, 7, 9, 6, 1, 4, 2],
            [8, 9, 1, 6, 0, 4, 3, 5, 2, 7], [9, 4, 5, 3, 1, 2, 6, 8, 7, 0], [4, 2, 8, 6, 5, 7, 3, 9, 0, 1],
            [2, 7, 9, 3, 8, 0, 6, 4, 1, 5], [7, 0, 4, 6, 9, 1, 3, 2, 5, 8]]


        try:
            i = len(aadharNum)
            j = 0
            x = 0

            while i > 0:
                i -= 1
                x = mult[x][perm[(j % 8)][int(aadharNum[i])]]
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
            self.cv_img = self.rotate(self.cv_img)
            '''

            try:
                self.cv_img = self.rotate(self.cv_img)
            except:
                self.read_image_pil()
            else:
                self.cv_img.save('1_temp.png')
                self.pil_img = Image.open('1_temp.png')     
                os.remove('1_temp.png')
        
        self.pil_img = self.pil_img.convert('RGBA')
        '''
            
        '''

            try:
                self.cv_img = self.rotate(self.cv_img)
            except:
                self.read_image_pil()
            else:
                self.cv_img.save('1_temp.png')
                self.pil_img = Image.open('1_temp.png')     
                os.remove('1_temp.png')
        
        self.pil_img = self.pil_img.convert('RGBA')
        '''
            
        if self.config['skew']:
            print("skewness correction not available")
        
        if self.config['crop']:
            print("Smart Crop not available")
        
        if self.config['contrast']:

            self.cv_img  = self.contrast_image(self.cv_img)
            #self.pil_img  = self.contrast_image(self.pil_img )

            print("correcting contrast")
            
        aadhars = set()
        for i in range(len(self.config['psm'])):
            t = self.text_extractor(self.cv_img,self.config['psm'][i])

            anum = self.is_aadhar_card(t)

            uid = self.find_uid(t)


            if anum != "Not Found" and len(uid) == 0:
                if len(anum) - anum.count(' ') == 12:
                   aadhars.add(anum.replace(" ", ""))
            if anum == "Not Found" and len(uid) != 0:

                aadhars.add(uid[0].replace(" ", ""))
            if anum != "Not Found" and len(uid) != 0:
                if len(anum) - anum.count(' ') == 12:
                   aadhars.add(anum.replace(" ", ""))
                #print(uid[0].strip())
                aadhars.add(uid[0].replace(" ", ""))

        return list(aadhars)
    
    def mask_image(self, path, write, aadhar_list):
        #print("Read Path => ", path, " write path => ",write, "aadhar list =>",aadhar_list)
        self.mask_count = 0
        self.mask = cv2.imread(str(path), cv2.IMREAD_COLOR)
        for j in range(len(self.config['psm'])):
            for i in range(len(aadhar_list)):
                #print(" Runing mode: Aadhar number:",aadhar_list[i]," PSM => ",self.config['psm'][j])
                if (self.mask_aadhar(aadhar_list[i],write,self.config['psm'][j]))>0:
                    self.mask_count = self.mask_count + 1
                #print(" :\/ ",self.mask_count)
            
        #print("Final Mask Count =>",self.mask_count)
        cv2.imwrite(write,self.mask)
        return self.mask_count
    
    def mask_aadhar(self, uid, out_path, psm):
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

    '''
    def read_image_pil(self):
        self.pil_img = Image.open(self.image_path)
    '''

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
    

    def rotate_only(self, img, angle_in_degrees):
        self.img = img
        self.angle_in_degrees = angle_in_degrees
        rotated = ndimage.rotate(self.img, self.angle_in_degrees)
        return rotated
    
    def is_image_upside_down(self, img):
        self.img = img
        face_locations = face_recognition.face_locations(self.img)
        encodings = face_recognition.face_encodings(self.img, face_locations)
        image_is_upside_down = (len(encodings) == 0)
        return image_is_upside_down
    
    ''' 
    def save_image(self, img):
        self.img = img
        cv2.imwrite('orientation_corrected.jpg', self.img)

           
    def display(self, img, frameName="OpenCV Image"):
        self.img = img
        self.frameName = frameName
        h, w = self.img.shape[0:2]   
        neww = 800
        newh = int(neww*(h/w))
        self.img = cv2.resize(self.img, (neww, newh))
        cv2.imshow(self.frameName, self.img)
        cv2.waitKey(0)
    '''
    
    # Corrects orientation of image using tesseract OSD if rotation Angle is < 100.
    def rotate(self,img):
        #def orientation_correction(img): #, save_image = False):
        # GrayScale Conversion for the Canny Algorithm 
        self.img = img
        img_gray = cv2.cvtColor(self.img, cv2.COLOR_BGR2GRAY) 
        #self.display(img_gray)
        # Canny Algorithm for edge detection was developed by John F. Canny not Kennedy!! :)
        img_edges = cv2.Canny(img_gray, 100, 100, apertureSize=3)
        #self.display(img_edges)
        # Using Houghlines to detect lines
        lines = cv2.HoughLinesP(img_edges, 1, math.pi / 180.0, 100, minLineLength=100, maxLineGap=5)
        img_copy = self.img.copy()
        for x in range(0, len(lines)):
            for x1,y1,x2,y2 in lines[x]:
                cv2.line(img_copy,(x1,y1),(x2,y2),(0,255,0),2)
        #cv2.imshow('hough',img_copy)
        #cv2.waitKey(0)
        
        angles = []
        for x1, y1, x2, y2 in lines[0]:
            angle = math.degrees(math.atan2(y2 - y1, x2 - x1))
            angles.append(angle)
        
        # Getting the median angle
        median_angle = np.median(angles)
        # Rotating the image with this median angle
        img_rotated = self.rotate_only(self.img, median_angle)
        #self.display(img_rotated)
        
        if self.is_image_upside_down(img_rotated):
            print("rotate to 180 degree")
            angle = -180
            img_rotated_final = self.rotate_only(img_rotated, angle)
            #self.save_image(img_rotated_final)
            #self.display(img_rotated_final)
            if self.is_image_upside_down(img_rotated_final):
                print("Kindly check the uploaded image, face encodings still not found!")
                return img_rotated
            else:
                print("image is now straight")
                return img_rotated_final
        else:
            #self.display(img_rotated)
            print("image is straight")
            return img_rotated

        
    # Turns images BnW using pixels, didn't have much success with this and skipped in final production 
    def contrast_image(self, img):
        self.img = img
        gray = cv2.cvtColor(self.img, cv2.COLOR_BGR2GRAY)
        #gray = cv2.bitwise_not(gray)
        thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
        #self.display(thresh)
        return thresh
    
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
    
    #Function to validate if an image contains text showing its an aadhar card
    def is_aadhar_card(self, text):
               res=text.split()
               aadhar_number=''
               for word in res:
                  if len(word) == 4 and word.isdigit():
                      aadhar_number=aadhar_number  + word + ' '
               if len(aadhar_number)>=14:
                   return aadhar_number
                   
               else:

                    return "Not Found"


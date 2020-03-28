# PyraDox

PyraDox is a simple tool which helps in document **digitization** by extracting text information and **masking** of personal information with the help of Tesseract-ocr.

![Aadhaar to JSON](AadhaarCardOCR1.jpg?raw=true "Aadhaar Card image")

#### Currently Supports :- 

* **Aadhaar Card** is a 12-digit unique identity number that can be obtained voluntarily by residents or passport holders of India, based on their biometric and demographic data. The data is collected by the Unique Identification Authority of India (UIDAI), a statutory authority established in January 2009 by the government of India. 

*****************************************************

## Installation

### Tesseract-ocr
This tools need tesseract-ocr engine. Help yourself with this --
* https://github.com/tesseract-ocr/tesseract/wiki

#### Windows

Install tesseract using [windows installer](https://github.com/UB-Mannheim/tesseract/wiki) available at : 

* https://github.com/UB-Mannheim/tesseract/wiki

#### Linux

Tesseract is available directly from many Linux distributions. The package is generally called 'tesseract' or 'tesseract-ocr' - search your distribution's repositories to find it. Thus you can install Tesseract 4.x and it's developer tools on Ubuntu 18.x bionic by simply running:

```bash
sudo apt install tesseract-ocr
sudo apt install libtesseract-dev
```
Refer [here](https://github.com/tesseract-ocr/tesseract/wiki) for more on installation on all other systems.

#### macOS

##### Homebrew

To install Tesseract run this command:

```bash
brew install tesseract
```
### Dependency


Use the package manager [pip](https://pip.pypa.io/en/stable/) to install requirements.

```bash
pip install -r requirements.txt
```
Having hard time with pyt

Add path if **pytesseract** is unable to find  Tesseract-ocr path. [stackoverflow](https://stackoverflow.com/questions/50951955/pytesseract-tesseractnotfound-error-tesseract-is-not-installed-or-its-not-i)
```bash
pytesseract.pytesseract.tesseract_cmd = r'C:\Users\USER\AppData\Local\Tesseract-OCR\tesseract.exe'
```
*****************************************************


## Usage

##### Initialisation & Configuration 

```python
from Aadhaar import Aadhaar_Card
config = {'orient' : True,   #corrects orientation of image default -> True
          'skew' : True,     #corrects skewness of image default -> True
          'crop': True,      #crops document out of image default -> True
          'contrast' : True, #Bnw for Better OCR default -> True
          'psm': [3,4,6],    #Google Tesseract  psm modes default -> 3,4,6 
          'mask_color': (0, 165, 255),  #Masking color BGR Format
          'brut_psm': [6]    #Keep only one for brut mask (6) is good to start
          }

obj = Aadhaar_Card(config)
```

##### A. Validate Aadhaar card numbers using Verhoeff Algorithm.
```python
obj.validate("397788000234") #Binary Output 1|0
```
##### B. Extract Aadhaar Number from image
```python
aadhaar_list = obj.extract("path of input image") #supported types (png, jpeg, jpg)
```
##### C. Mask Aadhaar number card for given Aadhaar card number #Binary Output 1|0
```python
flag = obj.mask("path of input image", "path of output image", aadhaar_list) #supported types (png, jpeg, jpg)
```
##### D. Brut Mask any Readable Number from Aadhaar (works well on low res, bad quality images)
```python
obj.mask_nums("path of input image", "path of output image") #supported types (png, jpeg, jpg)

```
*****************************************************
## PyraDox-API
##### Built with flask
##### Find  Usefull Examples of Request - Response [api_samples](docs/api_samples.py)
> defaults_url = http://localhost:9001     
> headers = {'content-type': 'application/json'}

```bash
python app.py
```

##### A. Validate Aadhaar card numbers using Verhoeff Algorithm. url = '/api/validate'
```python
request_json = {"test_number": number} 
response_json = {'validity': 0 } #0|1 -> invalid|valid
```
##### B. Extract Aadhaar Number from image. url = '/api/ocr'
```python
request_json = {"doc_b64": encoded_string}
response_json = {'aadhaar_list':['397788000234']} #enpty list if unable to find
```
##### C. Mask Aadhaar number card for given Aadhaar card number. url =  '/api/mask'
```python
request_json = {"doc_b64": encoded_string, 'aadhaar': number_list}
response_json = {'doc_b64_masked':encoded_string, 'is_masked': True} #if is_masked False then doc_b64_masked is None
```
##### D. Brut Mask any Readable Number from Aadhaar (works well on low res, bad quality images). url =  '/api/brut_mask'
```python
request_json = {"doc_b64": encoded_string}
response_json = {'doc_b64_brut_masked': encoded_string, 'mask_status': 'Done'}

```
##### E. Bonus :100: Complete Sample Pipeline. url =  '/api/sample_pipe'
###### Usecase : Take an aadhaar card, extract its aadhaar number while checking number's validty, mask first 8 digits. If aadhaar number is not readable then mask possible numbers (brut mode) .
```python
request_json = {"doc_b64": encoded_string, "brut" : True}
response_json = {'doc_b64_masked':encoded_string, 'is_masked': True,'mode_executed' : "OCR-MASKING", 'aadhaar_list':"extracted_aadhaar_list", 'valid_aadhaar_list':valid_aadhaar_list}
```

*****************************************************
## Docker
##### Build Your Own Image
```bash
docker build -t pyradox .
docker run -p 9001:9001 pyradox
```

*****************************************************
## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

#### Tasks

- [x] Finish Dockerfile
- [ ] Push Docker image to hub
- [ ] Add Class Preprocessing
- [ ] [Add Badges](https://shields.io/)

Please make sure to update tests as appropriate.

## License
[MIT](https://choosealicense.com/licenses/mit/)

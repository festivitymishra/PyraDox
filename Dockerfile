FROM debian:buster-slim as buildstage
LABEL maintainer="Utsav Mishra <https://festivitymishra.github.io/>"

# Install dependencies and Google tesseract
RUN apt-get update && \
    apt-get install -y git pkg-config && \
    apt-get install -y libsm6 libxext6 libxrender-dev && \
    apt-get install -y python-pip && \
    apt-get install -y tesseract-ocr && \
    apt-get install -y libtesseract-dev


# Build Python APP Here
RUN mkdir aadhaar_ocr_masking

COPY requirements.txt /aadhaar_ocr_masking/requirements.txt
RUN pip install -r /aadhaar_ocr_masking/requirements.txt

COPY Aadhaar.py /aadhaar_ocr_masking/Aadhaar.py
COPY app.py /aadhaar_ocr_masking/app.py

RUN mkdir /aadhaar_ocr_masking/temp
RUN mkdir /aadhaar_ocr_masking/public

COPY public/* /aadhaar_ocr_masking/public/

WORKDIR /aadhaar_ocr_masking
CMD ["python", "app.py"]

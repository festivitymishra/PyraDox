
FROM debian:buster-slim as buildstage
LABEL maintainer="Utsav Mishra <https://festivitymishra.github.io/>"

# Install OS dependencies and Google tesseract
RUN apt-get update && \
    apt-get install -y git pkg-config && \
    apt-get install -y libsm6 libxext6 libxrender-dev && \
    apt-get install -y cmake && \
    apt-get install -y python-pip && \
    apt-get install -y tesseract-ocr && \
    apt-get install -y libtesseract-dev

# Create and set working directory for Python app
WORKDIR /aadhaar_ocr_masking

# Install pip dependencies
COPY requirements.txt requirements.txt
RUN python -m pip install -r requirements.txt

# Copy project files to workdir
COPY Aadhaar.py app.py ./

CMD ["python", "app.py"]


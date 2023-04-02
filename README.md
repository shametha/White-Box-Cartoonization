# Whitebox Cartoonizer

## Backend
## Installation

### Application works on:

- Flask==1.0.2
- gunicorn==20.0.4
- Pillow==6.2.0
- opencv_python==4.2.0.34
- tensorflow==2.1.0
- google-cloud-storage==1.29.0
- algorithmia==1.3.0
- scikit-video==1.1.11
- tf_slim==1.1.0
- PyYaml==5.3.1
- flask-ngrok


### Using `miniconda or anaconda`

1. Make a virtual environment using `create` and activate it
```
conda create -n cartoon
conda activate cartoon
```
2. Install python dependencies
```
pip install -r requirements.txt
```
3. Run the webapp (here localhost : http://127.0.0.1:8080 ) Be sure to set the appropriate values in `config.yaml` file before running the application.
```
python app.py
```

### Using `virtualenv`

1. Make a virtual environment using `virutalenv` and activate it
```
virtualenv -p python3 cartoonize
source cartoonize/bin/activate
```
2. Install python dependencies
```
pip install -r requirements.txt
```
3. Run the webapp. Be sure to set the appropriate values in `config.yaml` file before running the application.
```
python app.py
```

## Frontend
- HTML 5
- CSS 3
- Javascript
- Flask

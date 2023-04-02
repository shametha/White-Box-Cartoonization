import os
import io
import uuid
import sys
import yaml
import traceback
from video_cartoonizer import run

with open('./config.yaml', 'r') as fd:
    opts = yaml.safe_load(fd)

sys.path.insert(0, './white_box_cartoonizer/')

import cv2
from flask import Flask, render_template, make_response, flash, send_from_directory
import flask
from PIL import Image
import numpy as np
import skvideo.io
if opts['colab-mode']:
    from flask_ngrok import run_with_ngrok #to run the application on colab using ngrok


from cartoonize import WB_Cartoonize

if not opts['run_local']:
    if 'GOOGLE_APPLICATION_CREDENTIALS' in os.environ:
        from gcloud_utils import upload_blob, generate_signed_url, delete_blob, download_video
    else:
        raise Exception("GOOGLE_APPLICATION_CREDENTIALS not set in environment variables")
    from video_api import api_request
    # Algorithmia (GPU inference)
    import Algorithmia

app = Flask(__name__)
if opts['colab-mode']:
    run_with_ngrok(app)   #starts ngrok when the app is run

app.config['UPLOAD_FOLDER_VIDEOS'] = 'static/uploaded_videos'
app.config['CARTOONIZED_FOLDER'] = 'static/cartoonized_images'

app.config['OPTS'] = opts

## Init Cartoonizer and load its weights 
web_animator = WB_Cartoonize(os.path.abspath("white_box_cartoonizer/saved_models/"), opts['gpu'])

def convert_bytes_to_image(img_bytes):
    """Convert bytes to numpy array

    Args:
        img_bytes (bytes): Image bytes read from flask.

    Returns:
        [numpy array]: Image numpy array
    """
    
    image_pil = Image.open(io.BytesIO(img_bytes))
    if image_pil.mode=="RGBA":
        result_img = Image.new("RGB", image_pil.size, (255,255,255))
        result_img.paste(image_pil, mask=image_pil.split()[3])
    else:
        result_img = image_pil.convert('RGB')
    
    result_img = np.array(result_img)
    
    return result_img

@app.route('/')
@app.route('/cartoonize', methods=["POST", "GET"])
def cartoonize():
    opts = app.config['OPTS']
    if flask.request.method == 'POST':
        try:
            if flask.request.files.get('image'):
                img = flask.request.files["image"].read()
                
                ## Read Image and convert to PIL (RGB) if RGBA convert appropriately
                image = convert_bytes_to_image(img)

                img_name = str(uuid.uuid4())
                
                cartoon_image = web_animator.infer(image)
                
                cartoonized_img_name = os.path.join(app.config['CARTOONIZED_FOLDER'], img_name + ".jpg")
                cv2.imwrite(cartoonized_img_name, cv2.cvtColor(cartoon_image, cv2.COLOR_RGB2BGR))
                
                if not opts["run_local"]:
                    # Upload to bucket
                    output_uri = upload_blob("cartoonized_images", cartoonized_img_name, img_name + ".jpg", content_type='image/jpg')

                    # Delete locally stored cartoonized image
                    os.system("rm " + cartoonized_img_name)
                    cartoonized_img_name = generate_signed_url(output_uri)
                    

                return render_template("griddash.html", cartoonized_image=cartoonized_img_name)

            if flask.request.files.get('video'):
                
                filename = str(uuid.uuid4()) + ".mp4"
                video = flask.request.files["video"]
                original_video_path = os.path.join("templates", filename)
                video.save(original_video_path)

                run(filename)

                final_cartoon_video_path = "http://127.0.0.1:8080/video/" + filename; 
                return render_template("griddash.html", cartoonized_video=final_cartoon_video_path)
        
        except Exception:
            print(traceback.print_exc())
            flash("Our server hiccuped :/ Please upload another file! :)")
            return render_template("griddash.html")
    else:
        return render_template("griddash.html")

@app.route('/video/<path:path>')
def send_report(path):
    return send_from_directory('static', path)

if __name__ == "__main__":
    # Commemnt the below line to run the Appication on Google Colab using ngrok
    if opts['colab-mode']:
        app.run()
    else:
        app.run(debug=False, host='127.0.0.1', port=int(os.environ.get('PORT', 8080)))
#!/home/sardor/anaconda3/bin/python
from flask import jsonify,render_template, Flask, flash, session, request, redirect, url_for
from werkzeug import secure_filename
from imageai.Detection import ObjectDetection
from keras import backend as K
import os

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

app = Flask(__name__)
execution_path = os.getcwd()





########### check file format
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
   

################ default route. html
@app.route('/')
def index():
    return render_template('upload.html')

################################## main function
@app.route('/get-image', methods=['POST'])
def upload():
    imagefile = request.files['fileimage']
    if imagefile and allowed_file(imagefile.filename):
#            execution_path = os.getcwd()
        detector = ObjectDetection()
        detector.setModelTypeAsRetinaNet()
        detector.setModelPath( os.path.join(execution_path , "resnet50_coco_best_v2.0.1.h5"))
        detector.loadModel()
        print(type(detector))
#            imagefile.save(os.path.join('uploads/', imagefile.filename))
        print('!!!!!!!!!!!!!!image get!!!!!!!!!!!'+imagefile.filename+'!!!!!!!')
        print(type(imagefile),'\n\n')
        print(os.path.join(execution_path, 'uploads/'+imagefile.filename))
        detections = detector.detectCustomObjectsFromImage(input_image=imagefile,
           minimum_percentage_probability=60)
        tags = []
        for eachObject in detections:
#               print(eachObject["name"] + " : " + eachObject["percentage_probability"] )
#               print("--------------------------------")
            tags.append({''+eachObject["name"] : ''+eachObject["percentage_probability"]})
        K.clear_session()
        return jsonify({'tags': tags})
    
    
    


def getImageTags(image):
#    execution_path = os.getcwd()
#    
#    detector = ObjectDetection()
#    detector.setModelTypeAsRetinaNet()
#    detector.setModelPath( os.path.join(execution_path , "resnet50_coco_best_v2.0.1.h5"))
#    detector.loadModel()
#    custom_objects = detector.CustomObjects(person=True, car=True)
#    detections = detector.detectCustomObjectsFromImage(input_image=os.path.join(execution_path , "child.jpg"),
#                                                       output_image_path=os.path.join(execution_path , "child2.jpg"), minimum_percentage_probability=20)# custom_objects=custom_objects, minimum_percentage_probability=65)
    print('\nfunc getImagetTags()\n\n')
    try:
#        image.save(os.path.join('uploads/', image.filename))
        detections = detector.detectCustomObjectsFromImage(input_image=image,
               output_image_path=os.path.join(execution_path, 'uploads/'+image.filename),
               minimum_percentage_probability=60)# custom_objects=custom_objects, minimum_percentage_probability=65)
        print('\nendfunc\n\n')
    except Exception as err:
        return print(repr(err)+'\n\n')
    tags = []
    for eachObject in detections:
       print(eachObject["name"] + " : " + eachObject["percentage_probability"] )
       print("--------------------------------")
       tags.append({''+eachObject["name"] : ''+eachObject["percentage_probability"]})
    return tags








@app.route('/get-posted-image', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['fileimage']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
#            filename = secure_filename(file.filename)
            tags = getImageTags(file)
            return jsonify({'tags': tags})
            
            #file.save(os.path.join('uploads/', filename))
            #return 'upload success'
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=fileimage>
      <input type=submit value=Upload>
    </form>
    '''



if __name__ == '__main__':   
    app.secret_key = 'super secret key'
    app.run(debug=True)
    
    
#if __name__ == '__main__':
#    
##    execution_path = os.getcwd()
##    
##    detector = ObjectDetection()
##    detector.setModelTypeAsRetinaNet()
##    detector.setModelPath( os.path.join(execution_path , "resnet50_coco_best_v2.0.1.h5"))
##    detector.loadModel()
#    
#    app.secret_key = 'super secret key'
##    app.config['SESSION_TYPE'] = 'filesystem'
#    
##    sess.init_app(app)
#    app.run(debug=True)
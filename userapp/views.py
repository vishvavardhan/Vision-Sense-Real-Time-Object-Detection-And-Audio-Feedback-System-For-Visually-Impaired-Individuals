from django.shortcuts import render,redirect
from django.http import JsonResponse
import random
from django.conf import settings
from django.core.files.storage import default_storage
import os
from django.core.mail import send_mail
from django.utils.datastructures import MultiValueDictKeyError
from userapp.models import User
from django.contrib import messages
import urllib.request
import urllib.parse
from django.contrib.auth import logout
from django.http import HttpResponse
import cv2
import numpy as np
import pyttsx3




def user_logout(request):
    logout(request)
    messages.info(request,"Logout Successfully ")
    return redirect('login')
# Create your views here.

def sendSMS(user,otp,mobile):
    data =  urllib.parse.urlencode({'username':'Codebook','apikey': '56dbbdc9cea86b276f6c' , 'mobile': mobile,
        'message' : f'Hello {user}, your OTP for account activation is {otp}. This message is generated from https://www.codebook.in server. Thank you', 'senderid': 'CODEBK'})
    data = data.encode('utf-8')
    request = urllib.request.Request("https://smslogin.co/v3/api.php?")
    f = urllib.request.urlopen(request, data)
    return f.read()



def generate_otp(length=4):
    otp = ''.join(random.choices('0123456789', k=length))
    return otp


def index(request):
    return render(request,"index.html")


def about(request):
    return render(request,"about.html")


def login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        try:
            user = User.objects.get(user_email=email)   
            if user.user_password == password:
                print(f"User ID set in session: {user.user_id}")
                if user.otp_status == 'Verified':
                    request.session['user_id_login'] = user.user_id
                    messages.success(request, 'Login successful!')
                    return redirect('dashboard')
                else:
                    request.session['user_id_register'] = user.user_id
                    otp = generate_otp()
                    user.otp = otp
                    user.save()
                    subject = 'OTP Verification for Account Activation'
                    otp = f'Your OTP for verification is: {user.otp}'
                    message = f'Hello {user.user_name},\n\nYou are attempting to log in to your query account. Your OTP for login verification is: {otp}\n\nIf you did not request this OTP, please ignore this email.'
                    from_email = settings.EMAIL_HOST_USER
                    recipient_list = [user.user_email]
                    resp =  sendSMS(user.user_name,user.otp,user.user_phone)
                    send_mail(subject, message, from_email, recipient_list, fail_silently=False)
                    messages.success(request, 'Otp sent to mail and phone number !')
                    return redirect('otp')
            else:
                messages.error(request, 'Incorrect Password')
                return redirect('login')
        except User.DoesNotExist:
            messages.error(request, 'Invalid Login Details')
            return redirect('login')
    return render(request,"login.html")




def register(request):
    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        password = request.POST.get('password')
        location = request.POST.get('address')
        profile = request.FILES.get('profile')
        try:
            User.objects.get(user_email = email)
            messages.info(request, 'Email Already Exists!')
            return redirect('register')
        except:
            otp = generate_otp()
            user = User.objects.create(user_name=name, user_email=email, user_phone=phone, user_profile=profile, user_password=password, user_location=location,otp=otp)
            print(user)
            request.session['user_id_register'] = user.user_id
            subject = 'OTP Verification for Account Activation'
            otp = f'Your OTP for verification is: {user.otp}'
            message = f'Hello {user.user_name},\n\nYou are attempting to log in to your query account. Your OTP for login verification is: {otp}\n\nIf you did not request this OTP, please ignore this email.'
            from_email = settings.EMAIL_HOST_USER
            recipient_list = [user.user_email]
            resp =  sendSMS(user.user_name,user.otp,user.user_phone)
            send_mail(subject, message, from_email, recipient_list, fail_silently=False)
            messages.success(request, 'Otp sent to mail and Phonenumber !')
            return redirect('otp')
    return render(request,"register.html")





def otp(request):
    user_id = request.session.get('user_id_register')
    print(f"User ID retrieved from session: {user_id}")
    user = User.objects.get(user_id=user_id)
    print(user)
    if request.method == "POST":
        otp_entered = request.POST.get('otp')
        print(otp_entered,"otp enterd")
        print(user_id)
        if not otp_entered:
            messages.error(request, 'Please enter the OTP')
            print("OTP not entered")
            return redirect('otp')
        try:
            user = User.objects.get(user_id=user_id)
            if str(user.otp) == otp_entered:
                user.otp_status = 'Verified'
                user.save()
                # user_id = request.session['user_id']
                messages.success(request, 'OTP verification successful!')
                return redirect('login')
            else:
                messages.error(request, 'Invalid OTP entered')
                print("Invalid OTP entered")
                return redirect('otp')
        except User.DoesNotExist:
            messages.error(request, 'Invalid user')
            print("Invalid user")
            return redirect('register')
    return render(request,"otp.html")







def contact(request):
    return render(request,"contact.html")




def dashboard(request):
    processed_image_url = None
    if request.method == 'POST' and request.FILES.get('imageUpload'):
        init_engine()
        uploaded_file = request.FILES['imageUpload']
        file_name = default_storage.save(uploaded_file.name, uploaded_file)
        file_url = default_storage.url(file_name)
        print("File URL:", file_url)
        # Call detect_objects function with the uploaded image path
        processed_image_data = detect_objects(default_storage.path(file_name))  # Pass the absolute path of the uploaded image
        # Check if processed_image_data is not None
        if processed_image_data is not None:
            # Save the processed image to a temporary file
            temp_file_name = "processed_image.jpg"
            temp_file_path = default_storage.path(temp_file_name)
            with open(temp_file_path, "wb") as temp_file:
                temp_file.write(processed_image_data)
            # Get the URL of the processed image
            processed_image_url = default_storage.url(temp_file_name)
            # Close the engine after processing
            close_engine()
        else:
            # Handle the case where image processing failed
            messages.info(request,"This image is not Vaild please Upload another Img")
            return render(request, "user-dashboard.html")
    return render(request, "user-dashboard.html", {'processed_image_url': processed_image_url})



# Load the pre-trained YOLO weights and configuration
net = cv2.dnn.readNetFromDarknet("yolov3.cfg",
                                 "yolov3.weights")

# Load the COCO class labels
with open('coco.names', 'r') as f:
    classes = f.read().splitlines()

# Set the input image size for YOLO
input_size = (416, 416)

# Initialize the text-to-speech engine
engine = pyttsx3.init()




# Initialize the text-to-speech engine
engine = None

def init_engine():
    global engine
    engine = pyttsx3.init()

def close_engine():
    global engine
    if engine:
        engine.stop()
        engine = None

def detect_objects(image_path):
    # Read the input image
    frame = cv2.imread(image_path)
    
    # Check if the image is valid and non-empty
    if frame is None or frame.size == 0:
        print("Error: Unable to read the input image.")
        return None  # Return None if the image is invalid

    # Create a blob from the input frame and set it as the input for the neural network
    blob = cv2.dnn.blobFromImage(frame, 1/255.0, input_size, swapRB=True, crop=False)
    net.setInput(blob)

    # Run the forward pass to get the YOLO output
    output_layers_names = net.getUnconnectedOutLayersNames()
    layer_outputs = net.forward(output_layers_names)

    # Process the YOLO output
    boxes = []
    confidences = []
    class_ids = []

    for output in layer_outputs:
        for detection in output:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]
            if confidence > 0.5:  # Set a confidence threshold
                center_x = int(detection[0] * frame.shape[1])
                center_y = int(detection[1] * frame.shape[0])
                width = int(detection[2] * frame.shape[1])
                height = int(detection[3] * frame.shape[0])
                left = int(center_x - width/2)
                top = int(center_y - height/2)

                boxes.append([left, top, width, height])
                confidences.append(float(confidence))
                class_ids.append(class_id)

    # Apply non-maximum suppression to remove redundant overlapping boxes
    indices = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)

    # Draw the bounding boxes and labels on the frame
    if len(indices) > 0:
        for i in indices.flatten():
            x, y, w, h = boxes[i]
            label = classes[class_ids[i]]
            confidence = confidences[i]

            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            cv2.putText(frame, f'{label}: {confidence:.2f}', (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            # Speak the label name
            engine.say(label)
            engine.runAndWait()

    # Encode the modified frame as a JPEG image
    _, jpeg_img = cv2.imencode('.jpg', frame)

    # Return the JPEG image data
    return jpeg_img.tobytes()




def profile(request):
    user_id  = request.session.get('user_id_login')
    user = User.objects.get(user_id=user_id)
    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        try:
            profile = request.FILES['profile']
            user.user_profile = profile
        except MultiValueDictKeyError:
            profile = user.user_profile
        password = request.POST.get('password')
        location = request.POST.get('location')
        user.user_name = name
        user.user_email = email
        user.user_phone = phone
        user.user_password = password
        user.user_location = location
        user.save()
        messages.success(request , 'updated succesfully!')
        return redirect('profile')
    return render(request,"profile.html",{'i':user})





def start_object_detection(request):
    try:
        print('start_object_detection function called.')
        
        # Check if image data is present in request.FILES
        if 'image' not in request.FILES:
            raise ValueError('No image file found in the request.')
        
        # Load the pre-trained YOLO weights and configuration
        net = cv2.dnn.readNetFromDarknet("yolov3.cfg", "yolov3.weights")

        # Load the COCO class labels
        with open('coco.names', 'r') as f:
            classes = f.read().splitlines()

        # Set the input image size for YOLO
        input_size = (416, 416)

        # Convert the received image data into numpy array
        nparr = np.frombuffer(request.FILES['image'].read(), np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        print('Image data received:', img.shape) 

        # Create a blob from the input frame and set it as the input for the neural network
        print('Creating blob from input frame...')
        blob = cv2.dnn.blobFromImage(img, 1/255.0, input_size, swapRB=True, crop=False)
        net.setInput(blob)

        # Run the forward pass to get the YOLO output
        print('Running forward pass to get YOLO output...')
        output_layers_names = net.getUnconnectedOutLayersNames()
        layer_outputs = net.forward(output_layers_names)

        # Process the YOLO output
        print('Processing YOLO output...')
        boxes = []
        confidences = []
        class_ids = []

        for output in layer_outputs:
            for detection in output:
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]
                if confidence > 0.5:  # Set a confidence threshold
                    center_x = int(detection[0] * img.shape[1])
                    center_y = int(detection[1] * img.shape[0])
                    width = int(detection[2] * img.shape[1])
                    height = int(detection[3] * img.shape[0])
                    left = int(center_x - width/2)
                    top = int(center_y - height/2)

                    boxes.append([left, top, width, height])
                    confidences.append(float(confidence))
                    class_ids.append(class_id)

        # Apply non-maximum suppression to remove redundant overlapping boxes
        print('Applying non-maximum suppression...')
        indices = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)

        detected_objects = []

        # Process the detected objects
        print('Processing detected objects...')
        if len(indices) > 0:
            for i in indices.flatten():
                label = classes[class_ids[i]]
                confidence = confidences[i]
                detected_objects.append({'label': label, 'confidence': confidence})
                print(f'Detected object: {label} (Confidence: {confidence:.2f})')

        # Speak the detected objects aloud
        print('Announcing detected objects aloud...')
        engine = pyttsx3.init()
        for obj in detected_objects:
            label = obj['label']
            engine.say(label)
            engine.runAndWait()

        return JsonResponse(detected_objects, safe=False)

    except Exception as e:
        print(f'Error in object detection: {str(e)}')
        return JsonResponse({'error': str(e)}, status=500)
    






from django.http import StreamingHttpResponse, Http404
import cv2
import threading
import numpy as np



class VideoCamera(object):
    def __init__(self):
        self.running = True
        self.video = cv2.VideoCapture(0 + cv2.CAP_DSHOW)
        (self.grabbed, self.frame) = self.video.read()
        self.thread = threading.Thread(target=self.update, args=())
        self.thread.start()

        self.engine = pyttsx3.init()

        self.net = cv2.dnn.readNetFromDarknet("yolov3.cfg", "yolov3.weights")
        self.classes = []
        with open("coco.names", 'r') as f:
            self.classes = [line.strip() for line in f.readlines()]
        self.layer_names = self.net.getLayerNames()
        self.output_layers = [self.layer_names[i - 1] for i in self.net.getUnconnectedOutLayers().flatten()]

    def __del__(self):
        self.stop()

    def stop(self):
        self.running = False
        self.thread.join()
        self.video.release()
        self.engine.stop()

    def get_frame(self):
        image = self.frame
        height, width, channels = image.shape
        blob = cv2.dnn.blobFromImage(image, 0.00392, (416, 416), (0, 0, 0), True, crop=False)
        self.net.setInput(blob)
        outs = self.net.forward(self.output_layers)

        class_ids = []
        confidences = []
        boxes = []
        for out in outs:
            for detection in out:
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]
                if confidence > 0.5:
                    center_x = int(detection[0] * width)
                    center_y = int(detection[1] * height)
                    w = int(detection[2] * width)
                    h = int(detection[3] * height)
                    x = int(center_x - w / 2)
                    y = int(center_y - h / 2)

                    boxes.append([x, y, w, h])
                    confidences.append(float(confidence))
                    class_ids.append(class_id)

        indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)
        if len(indexes) > 0:
            indexes = indexes[0]
            if indexes.ndim == 0:
                indexes = [indexes]  # Convert single numpy.int32 to list
            for i in indexes:
                x, y, w, h = boxes[i]
                label = str(self.classes[class_ids[i]])
                confidence = confidences[i]
                cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(image, f"{label} {confidence:.2f}", (x, y + 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

                # Speak the label name
                self.engine.say(label)
                self.engine.runAndWait()

        ret, jpeg = cv2.imencode('.jpg', image)
        return jpeg.tobytes()

    def update(self):
        while self.running:
            (self.grabbed, self.frame) = self.video.read()
            
def gen(camera):
    try:
        while True:
            frame = camera.get_frame()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
    finally:
        camera.stop()

def video_feed(request):
    cam = VideoCamera()
    try:
        return StreamingHttpResponse(gen(cam),
                                     content_type='multipart/x-mixed-replace; boundary=frame')
    except Exception as e:
        print("ABORTED: ", str(e))
        raise Http404("Video feed not found")

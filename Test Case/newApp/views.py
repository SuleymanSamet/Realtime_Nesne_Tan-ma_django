from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from .models import Userinfo
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from .forms import ObjectRecognitionForm
import cv2
from .forms import CeviriForm
from googletrans import Translator


def index(request):
    return render(request, 'index.html')


def register(request):
    if request.method == "POST":
        name = request.POST.get('name')
        surname = request.POST.get('surname')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')

        if password == password2:
            Buyukharf = False
            Numara = False

            for i in password:
                if i.isupper():
                    Buyukharf=True
                if i.isnumeric():
                    Numara=True
            if Buyukharf and Numara and len(password)>=6:
                if not User.objects.filter(username=username).exists():
                    if not User.objects.filter(email=email).exists():
                        user = User.objects.create_user(first_name=name, last_name=surname, username=username, email=email, password=password)
                        user.save()
                        userinfo=Userinfo(user=user, password=password)
                        userinfo.save()
                        return redirect('login')
                    else:
                        messages.info(request, 'this email is being used')
                        return redirect('register')
                else:
                    messages.info(request, 'this username is being used')
                    return redirect('register')
            else:
                messages.info(request, 'Your password does not contain uppercase letters or numbers ')
                return redirect('register')
        else:

            return redirect('register')
    return render(request, 'User/register.html')


def kullanici_giris(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)
        if user is not None:
            auth_login(request, user)
            return redirect('index')
        else:
            messages.info(request, 'Check Your Username and Password')

    return render(request, 'User/login.html')


def cikis(request):
    auth_logout(request)
    return redirect('index')


def forgotpassword(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        user = User.objects.get(email=email)
        userinfo = Userinfo.objects.get(user=user)
        subject = 'PAROLA HATIRLATMA'
        message = "Merhaba :" + userinfo.user.first_name + " " + userinfo.user.last_name +  '\nKaldığın yerden devam etmek için PAROLAN: ' + userinfo.password
        email_from = settings.EMAIL_HOST_USER
        recipient_list = [user.email]
        send_mail( subject, message, email_from, recipient_list )
        return redirect('login')
    else:
        return render(request, 'User/forgotpassword.html')


def nesne_tanıma(request):

    if request.method == 'POST':
        form = ObjectRecognitionForm(request.POST)
        if form.is_valid():

            language = form.cleaned_data['language']
            object_translation = form.cleaned_data['object_translation']

            return redirect('nesne_tanima')

    else:
        form = ObjectRecognitionForm()

    # Opencv DNN
    net = cv2.dnn.readNet("dnn_model/yolov4-tiny.weights", "dnn_model/yolov4-tiny.cfg")
    model = cv2.dnn_DetectionModel(net)
    model.setInputParams(size=(320, 320), scale=1 / 255)

    # Load class lists
    classes = []
    with open("dnn_model/classes.txt", "r") as file_object:
        for class_name in file_object.readlines():
            class_name = class_name.strip()
            classes.append(class_name)

    # Initialize camera
    cap = cv2.VideoCapture(0)

    detected_objects = []  # Nesne tanıma sonuçlarını tutacak liste

    while True:
        ret, frame = cap.read()

        (class_ids, scores, bboxes) = model.detect(frame, confThreshold=0.3, nmsThreshold=0.4)

        for class_id, score, bbox in zip(class_ids, scores, bboxes):
            (x, y, w, h) = bbox
            cv2.rectangle(frame, (x, y), (x + w, y + h), (200, 0, 50), 3)
            class_name = classes[class_id]
            cv2.putText(frame, class_name, (x, y - 10), cv2.FONT_HERSHEY_PLAIN, 3, (200, 0, 50), 2)

            detected_objects.append({"class_name": class_name})

        cv2.imshow("Frame", frame)
        key = cv2.waitKey(1)
        if key == 27:
            break

    cap.release()
    cv2.destroyAllWindows()

    context = {
        'detected_objects': detected_objects,
        'form': form,
    }

    return render(request, 'Nesne_Tanıma.html', context)


def ceviri(request):
    ceviri_metni = None

    if request.method == 'POST':
        form = CeviriForm(request.POST)
        if form.is_valid():
            metin = form.cleaned_data['metin']
            dil = form.cleaned_data['dil']
            cevirmen = Translator()
            ceviri = cevirmen.translate(metin, dest=dil).text
            ceviri_metni = ceviri

    else:
        form = CeviriForm()

    context = {
        'form': form,
        'ceviri_metni': ceviri_metni,
    }

    return render(request, 'index.html', context)

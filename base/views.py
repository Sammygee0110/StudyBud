from django.shortcuts import render, redirect
from .models import Room, Topic, Message
from .forms import RoomForm, UserForm
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout

# Create your views here.

rooms = Room.objects.all()

def loginPage(request):
    page = 'login'

    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        username = request.POST.get("username").title()
        password = request.POST.get("password")

        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, "User not found")
        
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("home")
        else:
            messages.error(request, "Incorrect Username or Password")

    context = {"page":page}
    return render(request, "login_register.html", context)

def registerPage(request):
    form = UserCreationForm()
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.title()
            user.save()
            return redirect("login")
        else:
            messages.error(request, "Invalid values inputed")
    return render(request, "login_register.html", {"form":form})

def logoutUser(request):
    logout(request)
    return redirect("home")

def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) |
        Q(name__icontains=q) |
        Q(description__icontains=q)
    )

    room_messages = Message.objects.filter(Q(room__topic__name__icontains=q))
    topics = Topic.objects.all()[:5]
    room_count = rooms.count()
    context = {"rooms":rooms, "topics":topics, "room_count":room_count, "room_messages":room_messages}
    return render(request, 'home.html', context)

def userProfie(request, pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()
    room_messages = user.message_set.all()
    topics = Topic.objects.all()
    context = {"user": user, "rooms":rooms, "room_messages":room_messages, "topics":topics}
    return render(request, "profile.html", context)

def updateUser(request):
    user = request.user
    form  = UserForm(instance=user)
    if request.method == "POST":
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user-profile', pk=user.id)
    return render(request, 'update-user.html', {"form":form})

def room(request, pk):
    room = Room.objects.get(id=pk)
    room_messages = room.message_set.all()
    obj = room.topic.name
    message = Message()
    participants = room.participants.all()

    if request.method == "POST":
        message = Message.objects.create(
            user = request.user,
            room=room,
            body = request.POST.get("message")
        )
        room.participants.add(request.user)

        return redirect("room", pk=room.id)

    context = {"room":room, "room_messages":room_messages, "message":message, "participants":participants, "obj":obj}

    return render(request, 'room.html', context)

@login_required(login_url="login")
def createRoom(request):
    form = RoomForm()
    topics = Topic.objects.all()
    if request.method == "POST":
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)

        Room.objects.create(
            host=request.user,
            topic=topic,
            name=request.POST.get('name'),
            description=request.POST.get('description')
        )
        return redirect("home")
    context = {"form":form, "topics":topics}
    return render(request, "room_form.html", context)

@login_required(login_url="login")
def updateRoom(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)
    if request.method == "POST":
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        room.name = request.POST.get('name')
        room.topic = topic
        room.description = request.POST.get('description')
        room.save()
        return redirect("home")
    context = {"form":form, "room":room}
    return render(request, "room_form.html", context)

@login_required(login_url="login")
def deleteRoom(request, pk):
    if request.method == "POST":
        room.delete()
        return redirect("home")
    return render(request, "delete.html", {"obj":room})

@login_required(login_url="login")
def deleteMessage(request, pk):
    message = Message.objects.get(id=pk)
    if request.method == "POST":
        message.delete()
        return redirect("home")
    return render(request, "delete.html", {"obj":message})

def topicsPage(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    topics = Topic.objects.filter(name__icontains=q)
    return render(request, "topics.html", {"topics":topics})

def activityPage(request):
    room_messages = Message.objects.filter()
    return render(request, 'activity.html', {"room_messages":room_messages})
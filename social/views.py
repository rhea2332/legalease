''' View functions '''
import json

from django.shortcuts import get_object_or_404, render, redirect
from django.utils import timezone
from django.http import HttpResponse, Http404, JsonResponse
from django.contrib import auth
from django.contrib.auth.decorators import login_required
import requests

from social.models import User, Profile, Message
from social.templatetags.social_extras import display_message
from social.forms import LoginForm, SignupForm
from social.nlp import article_summarize

appname = "Legal-Ease App"

@login_required
def editor(request):

    print("---GET request caught")
    if request.method == 'POST':
        print("---POST request caught")
        text_to_summarise = request.POST ['input_text']
        summarised_text = article_summarize(text_to_summarise)

        print ("Intercepted Text:\n", text_to_summarise)
        print ("Summarised Text:\n", summarised_text)

        return render(request, 'social/pages/editor.html', {
            'page': 'editor',
            'summarised_text': summarised_text[0],
            'text_to_summarise': text_to_summarise
        })

    return render(request, 'social/pages/editor.html', { 'page': 'editor' })

def signup(request):
    form = SignupForm()

    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            # create a new user
            new_user = User.objects.create(username=username)
            # set user's password
            new_user.set_password(password)
            new_user.save()
            # authenticate user
            # establishes a session, will add user object as attribute
            # on request objects, for all subsequent requests until logout
            user = auth.authenticate(username=username, password=password)
            if user is not None:
                auth.login(request, user)
                return redirect('social:messages')

    return render(request, 'social/auth/signup.html', { 'form': SignupForm })

def login(request):

    form = LoginForm()

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = auth.authenticate(username=username, password=password)
            if user is not None:
                auth.login(request, user)
                return redirect('social:messages')

            # failed authentication
            return render(request, 'errors/error.html', {
                'error' : 'User not registered. Sign up first.'
            })

        # invalid form
        return render(request, 'social/auth/login.html', {
            'form': form
        })

    return render(request, 'social/auth/login.html', { 'form': form })



@login_required
def logout(request):
    auth.logout(request)
    return redirect('social:login')


def view_profile(request, view_username):
    '''This function is only called from'''
    
    username = request.user.username
    greeting = "Your" if username == view_username else view_username + "'s"
    try:
       user = User.objects.get(username=view_username)
    except User.DoesNotExist:
       context = {
          'error' : 'User ' + view_username + ' does not exist'
       }
       return render(request, 'social/errors/error.html', context)
    context = {
        'view_user': view_username,
        'greeting': greeting,
        'profile': user.profile,
    }
    return render(request, 'social/pages/member.html', context)

@login_required
def documents(request):
    user = request.user

    # follow new friend
    if 'add' in request.GET:
        friend_username = request.GET['add']
        try:
            friend = User.objects.get(username=friend_username)
        except User.DoesNotExist:
            raise Http404('User does not exist')
        user.following.add(friend)
        user.save()
    # unfollow a friend
    if 'remove' in request.GET:
        friend_username = request.GET['remove']
        try:
            friend = User.objects.get(username=friend_username)
        except User.DoesNotExist:
            raise Http404('User does not exist')
        user.following.remove(friend)
        user.save()
    # view user profile
    if 'view' in request.GET:
        return view_profile(request, user, request.GET['view'])
    else:
        return render(request, 'social/pages/documents.html', {
            'page': 'documents',
            'user': user,
            'documents': User.objects.exclude(username=user.username),
        })


@login_required
def profile(request):
    user = request.user

    if 'text' in request.POST and request.POST['text']:
        text = request.POST['text'][:4096]
        if user.profile:
            user.profile.text = text
            user.profile.save()
        else:
            profile = Profile(text=text)
            profile.save()
            user.profile = profile
        user.save()
    context = {
        'user': user,
        'page': 'profile',
        'profile' : user.profile,
        'session_key': request.session.session_key,
        'meta' : request.META,
    }

    return render(request, 'social/pages/profile.html', context)


@login_required
def messages_jquery(request):
    user = request.user

    if request.method == 'GET':
        # Whose messages are we viewing?
        if 'view' in request.GET:
            view = request.GET['view']
            try: 
                view_user = User.objects.get(username=view)
            except User.DoesNotExist:
                raise Http404('User does not exist')
            profile = view_user.profile
            # public messages that 'view_user' has received
            m1 = Message.objects.filter(recip=view_user,public=True)
            # public messages that 'view_user' has sent
            m2 = Message.objects.filter(sender=view_user,public=True)
            # messages 'user' sent 'view_user'
            m3 = Message.objects.filter(sender=user,recip=view_user)
            # messages 'view_user' sent 'user'
            m4 = Message.objects.filter(sender=view_user,recip=user)
            # union of the four query sets
            messages = m1.union(m2,m3,m4).order_by('-time')
        else:
            view = user.username
            profile = user.profile
            # all messages I sent
            m1 = Message.objects.filter(sender=user)
            # all messages I received
            m2 = Message.objects.filter(recip=user)
            # union of the two query sets
            messages = m1.union(m2).order_by('-time')

        context = {
            'user': user,
            'page': 'messages',
            'profile': profile,
            'view': view,
            'messages': messages,
        }

        return render(request, 'social/pages/messages-jquery.html', context)

    if request.method == 'POST':
        if 'recip' in request.POST:
            recip = request.POST['recip']
            recip_user = get_object_or_404(User, username=recip)
            text = request.POST['text'][:4095]
            pm = request.POST['pm'] == 'yes'
            message = Message.objects.create(
                sender=user,
                recip=recip_user,
                public=pm,
                time=timezone.now(),
                text=text,
            )
            return HttpResponse(display_message(message, user.username))
        else:
            raise Http404('Recip missing in POST request')


@login_required
def messages_vue(request):
    user = request.user
    view = request.GET['view'] if 'view' in request.GET else user.username

    if user.username != view:
        view_user = get_object_or_404(User, username=view)
        profile = view_user.profile
        messages = user.messages_with(view_user)
    else:
        profile = user.profile
        messages = user.messages

    vue_data = json.dumps({
        'user': user.to_dict(),
        'view': view,
        'profile': profile.to_dict() if profile else None,
        'messages': [ message.to_dict() for message in messages ],
    })

    return render(request, 'social/pages/homepage.html', {
        'vue_data': vue_data,
    })


@login_required
def upload_image(request):
    user = request.user

    if 'img_file' in request.FILES:
        image_file = request.FILES['img_file']
        if not user.profile:
            # if user doesn't have a profile yet
            # need to create a profile first
            profile = Profile(text='')
            profile.save()
            user.profile = profile
            user.save()
        user.profile.image = image_file
        user.profile.save()
        return HttpResponse(user.profile.image.url)
    else:
        raise Http404('Image file not received')


@login_required
def legal_dictionary(request): 
    if request.method == "POST":
        
        word = request.POST['word']
        print("----------------------------------")
        print(word)

        API_KEY = "ad99c07d-26d2-4bdf-acf4-b1fd34186f09"
        API = f'https://www.dictionaryapi.com/api/v3/references/collegiate/json/{word}?key={API_KEY}'
        
        response = requests.get(API)
        
        if response.status_code != 200:
            response = 'Some Error Occured, Try Again Later!'
        
        print("----------------------------------")
        print("API: ", API)
        response = response.json()[0]
        print("response:\n")
        
        print('\n')
        print(json.dumps(response, indent=4))
        print('\n')
        
        try:    
            stems = response['meta']['stems']
            print("stems: ", stems)
            print('\n')
        except Exception:
            stems = None
            print("Stems Not Printed")

        try:    
            meaning = response['def'][0]['sseq'][0]
            meaning = meaning[0][1]['dt'][0][1]
            
            print("meaning: ", meaning)
            print('\n')
        except Exception:
            meaning = None
            print("Meaning Not printed")

        try:    
            uros = response['uros']
            uros_dict = []
            for ure in uros.values():
                uros_dict.append([ure.key, ure.value])
            
            uros = uros_dict
            print("uros: ", uros)
            print('\n')
        except Exception:
            uros = None
            print("Uros Not Printed")

        try:    
            shortdef = response['shortdef']
            print("Short Def: ", shortdef)
        except Exception:
            shortdef = None
            print("ShortDef not printed")
        
        print("----------------------------------")
    
        return render(request, 'social/pages/legal_dict.html', context={
            'stems': stems,
            'meaning': meaning,
            'uros': uros,
            'shortdef': shortdef,
        })
        
    return render(request, 'social/pages/legal_dict.html')
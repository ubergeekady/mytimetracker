from django.shortcuts import render
from googleapiclient.discovery import build
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
import google_auth_oauthlib.flow
from django.conf import settings
import json
import os

CLIENT_CONFIG = {'web': {
    'client_id': settings.GOOGLE_CLIENT_ID,
    'auth_uri': 'https://accounts.google.com/o/oauth2/auth',
    'token_uri': 'https://www.googleapis.com/oauth2/v3/token',
    'auth_provider_x509_cert_url': 'https://www.googleapis.com/oauth2/v1/certs',
    'client_secret': settings.GOOGLE_CLIENT_SECRET,
    'redirect_uris': settings.REDIRECT_URIS,
    'javascript_origins': settings.JAVASCRIPT_ORIGINS}}
SCOPES = ['https://www.googleapis.com/auth/userinfo.email','https://www.googleapis.com/auth/userinfo.profile','openid']

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

def loginview(request):
    if request.user.is_authenticated:
        return redirect(reverse('home'))
    code = request.GET.get('code', False)
    if code:
        flow = google_auth_oauthlib.flow.Flow.from_client_config(
            client_config=CLIENT_CONFIG,
            scopes=SCOPES)
        flow.redirect_uri = 'http://localhost:8000'
        authorization_response = request.build_absolute_uri()
        flow.fetch_token(authorization_response=authorization_response)
        credentials = flow.credentials
        service = build('oauth2', 'v2', credentials=credentials)
        user_info = service.userinfo().get().execute()
        try:
            user = User.objects.get(email=user_info['email'])
            login(request,user)
            return redirect(reverse('home'))        
        except:
            user = User.objects.create_user(username=user_info['email'], first_name = user_info['name'], email = user_info['email'], password=None)
            user.save()
            login(request,user)
            return redirect(reverse('home'))
    else:
        error = request.GET.get('error', False)
        authUrl = get_authorization_url()
        return render(request, 'login.html', {'authUrl':authUrl, 'error':error})

@login_required
def home(request):
    return render(request, 'index.html')

@login_required
def logoutview(request):
    logout(request)
    return redirect(reverse('login'))

def get_authorization_url():
    flow = google_auth_oauthlib.flow.Flow.from_client_config(
        client_config=CLIENT_CONFIG,
        scopes=SCOPES)
    flow.redirect_uri = 'http://localhost:8000'
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true')    
    return authorization_url

def credentials_to_dict(credentials):
  return {'token': credentials.token,
          'refresh_token': credentials.refresh_token,
          'token_uri': credentials.token_uri,
          'client_id': credentials.client_id,
          'client_secret': credentials.client_secret,
          'scopes': credentials.scopes}

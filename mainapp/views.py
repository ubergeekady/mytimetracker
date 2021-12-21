from django.http.response import HttpResponse
from django.shortcuts import render
from googleapiclient.discovery import build
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseForbidden
from django.conf import settings
from . import forms
from . import models
import os
import google_auth_oauthlib.flow

CLIENT_CONFIG = {'web': {
    'client_id': settings.GOOGLE_CLIENT_ID,
    'auth_uri': 'https://accounts.google.com/o/oauth2/auth',
    'token_uri': 'https://www.googleapis.com/oauth2/v3/token',
    'auth_provider_x509_cert_url': 'https://www.googleapis.com/oauth2/v1/certs',
    'client_secret': settings.GOOGLE_CLIENT_SECRET,
    'redirect_uris': settings.REDIRECT_URIS,
    'javascript_origins': settings.JAVASCRIPT_ORIGINS}}
SCOPES = ['https://www.googleapis.com/auth/userinfo.email','https://www.googleapis.com/auth/userinfo.profile','openid']
reduri = settings.REDIRECT_URIS
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

def loginview(request):
    if request.user.is_authenticated:
        return redirect(reverse('dashboardview'))
    code = request.GET.get('code', False)
    if code:
        flow = google_auth_oauthlib.flow.Flow.from_client_config(
            client_config=CLIENT_CONFIG,
            scopes=SCOPES)
        flow.redirect_uri = reduri
        authorization_response = request.build_absolute_uri()
        flow.fetch_token(authorization_response=authorization_response)
        credentials = flow.credentials
        service = build('oauth2', 'v2', credentials=credentials)
        user_info = service.userinfo().get().execute()
        try:
            user = User.objects.get(email=user_info['email'])
            login(request,user)
            return redirect(reverse('dashboardview'))        
        except:
            user = User.objects.create_user(username=user_info['email'], first_name = user_info['name'], email = user_info['email'], password=None)
            user.save()
            login(request,user)
            return redirect(reverse('dashboardview'))
    else:
        error = request.GET.get('error', False)
        authUrl = get_authorization_url()
        return render(request, 'login.html', {'authUrl':authUrl, 'error':error})

@login_required
def logoutview(request):
    logout(request)
    return redirect(reverse('loginview'))

@login_required
def dashboardview(request):
    return render(request, 'dashboard.html')

@login_required
def clientlist(request):
    client_list = models.Client.objects.filter(owner=request.user)
    return render(request, 'clientlist.html', {'client_list':client_list})

@login_required
def clientnew(request):
    page_header = "New Client"
    if request.method == 'POST':
        form = forms.ClientForm(request.POST)
        if form.is_valid():
            form.instance.owner = request.user
            form.save()
            return redirect(reverse('clientlist'))
    else:
        form = forms.ClientForm()
    return render(request, 'clientpage.html', {'page_header':page_header,'form':form})

@login_required
def clientedit(request, client_id):
    clientobj = get_object_or_404(models.Client, pk=client_id)
    page_header = "Edit Client: "+clientobj.name
    if clientobj.owner != request.user:
        return HttpResponseForbidden()
    if request.method == 'POST':
        form = forms.ClientForm(request.POST , instance=clientobj)
        if form.is_valid():
            form.save()
            return redirect(reverse('clientlist'))
    else:
        form = forms.ClientForm(instance=clientobj)
    return render(request, 'clientpage.html', {'page_header':page_header,'form':form})

@login_required
def clientdelete(request, client_id):
    clientobj = get_object_or_404(models.Client, pk=client_id)
    projectcount = models.Project.objects.filter(client = clientobj).count()
    if projectcount == 0:
        clientobj.delete()
        return redirect(reverse('clientlist'))
    return redirect(reverse('clientlist'))


@login_required
def projectlist(request, client_id):
    clientobj = get_object_or_404(models.Client, pk=client_id)
    page_header = "List Of Projects For Client: "+clientobj.name
    if clientobj.owner != request.user:
        return HttpResponseForbidden()
    project_list = models.Project.objects.filter(owner=request.user, client=clientobj)
    return render(request, 'projectlist.html', {'page_header':page_header,'client_id':client_id, 'project_list':project_list})

@login_required
def projectnew(request, client_id):
    clientobj = get_object_or_404(models.Client, pk=client_id)
    page_header = "New Project For Client "+clientobj.name
    if request.method == 'POST':
        form = forms.ProjectForm(request.POST)
        if form.is_valid():
            form.instance.owner = request.user
            form.instance.client = clientobj
            form.save()
            return redirect(reverse('projectlist', kwargs={'client_id':clientobj.id}))
    else:
        form = forms.ProjectForm()
    return render(request, 'projectpage.html', {'page_header':page_header, 'form':form})


@login_required
def projectedit(request, project_id):
    projectobj = get_object_or_404(models.Project, pk=project_id)
    page_header = "Edit Project: "+projectobj.name
    if projectobj.owner != request.user:
        return HttpResponseForbidden()
    if request.method == 'POST':
        form = forms.ProjectForm(request.POST , instance=projectobj)
        if form.is_valid():
            form.save()
            return redirect(reverse('projectlist', kwargs={'client_id':projectobj.clientobj.id}))
    else:
        form = forms.ProjectForm(instance=projectobj)
    return render(request, 'projectpage.html', {'page_header':page_header,'form':form})

@login_required
def projectdelete(request, project_id):
    projectobj = get_object_or_404(models.Project, pk=project_id)
    taskCount = models.Task.objects.filter(project = projectobj).count()
    if taskCount == 0:
        projectobj.delete()
        return redirect(reverse('projectlist', kwargs={'client_id':projectobj.clientobj.id}))
    return redirect(reverse('projectlist', kwargs={'client_id':projectobj.clientobj.id}))


@login_required
def tasklist(request, project_id):
    projectobj = get_object_or_404(models.Project, pk=project_id)
    page_header = "List Of Tasks For Project: "+projectobj.name
    if projectobj.owner != request.user:
        return HttpResponseForbidden()
    task_list = models.Task.objects.filter(owner=request.user, project=projectobj)
    return render(request, 'tasklist.html', {'page_header':page_header,'project_id':project_id, 'task_list':task_list})

@login_required
def tasknew(request, project_id):
    projectobj = get_object_or_404(models.Project, pk=project_id)
    page_header = "New Task For Project "+projectobj.name
    if request.method == 'POST':
        form = forms.TaskForm(request.POST)
        if form.is_valid():
            form.instance.owner = request.user
            form.instance.project = projectobj
            form.save()
            return redirect(reverse('tasklist', kwargs={'project_id':projectobj.id}))
    else:
        form = forms.TaskForm()
    return render(request, 'taskpage.html', {'page_header':page_header, 'form':form})


@login_required
def taskedit(request, task_id):
    taskobj = get_object_or_404(models.Task, pk=task_id)
    page_header = "Edit Task: "+taskobj.name
    if taskobj.owner != request.user:
        return HttpResponseForbidden()
    if request.method == 'POST':
        form = forms.TaskForm(request.POST , instance=taskobj)
        if form.is_valid():
            form.save()
            return redirect(reverse('tasklist', kwargs={'project_id':taskobj.projectobj.id}))
    else:
        form = forms.TaskForm(instance=taskobj)
    return render(request, 'taskpage.html', {'page_header':page_header,'form':form})


@login_required
def taskdelete(request, task_id):
    taskobj = get_object_or_404(models.Task, pk=task_id)
    timeentryCount = models.TimeEntry.objects.filter(task = taskobj).count()
    if timeentryCount == 0:
        taskobj.delete()
        return redirect(reverse('tasklist', kwargs={'project_id':taskobj.projectobj.id}))
    return redirect(reverse('tasklist', kwargs={'project_id':taskobj.projectobj.id}))


@login_required
def taskdetail(request, task_id):
    taskobj = get_object_or_404(models.Task, pk=task_id)
    if taskobj.owner != request.user:
        return HttpResponseForbidden()
    time_entry_list = models.TimeEntry.objects.filter(owner=request.user, task=taskobj)
    return render(request, 'taskdetail.html', {'task_id':task_id, 'taskobj':taskobj, 'time_entry_list':time_entry_list})

@login_required
def timerentry(request, task_id):
    taskobj = get_object_or_404(models.Task, pk=task_id)
    if taskobj.owner != request.user:
        return HttpResponseForbidden()
    return render(request, 'timerentry.html', {'task_id':task_id, 'taskobj':taskobj})



def get_authorization_url():
    flow = google_auth_oauthlib.flow.Flow.from_client_config(
        client_config=CLIENT_CONFIG,
        scopes=SCOPES)
    flow.redirect_uri = reduri
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

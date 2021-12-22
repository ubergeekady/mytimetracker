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
from string import Template
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from . import forms
from . import models
from datetime import datetime,date, timedelta
import os
import pytz
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
    IST = pytz.timezone('Asia/Kolkata')
    today = datetime.now(IST).date()
    time_entry_list = models.TimeEntry.objects.filter(owner=request.user, start_time__date = today)
    total_secs_today = 0 
    for entry in time_entry_list:
        total_secs_today += ((entry.durationminutes*60)+entry.durationseconds)
    today_time = convert(total_secs_today)
    today_productivity = (total_secs_today/(24*60*60))*100

    yesterday = today - timedelta(days=1)
    time_entry_list = models.TimeEntry.objects.filter(owner=request.user, start_time__date = yesterday)
    total_secs_yesterday = 0 
    for entry in time_entry_list:
        total_secs_yesterday += ((entry.durationminutes*60)+entry.durationseconds)
    yesterday_time = convert(total_secs_yesterday)
    yesterday_productivity = (total_secs_yesterday/(24*60*60))*100
    return render(request, 'dashboard.html', {
        'today_time':today_time,
        'today_productivity':'{:.2f}%'.format(today_productivity),
        'yesterday_time':yesterday_time,
        'yesterday_productivity':'{:.2f}%'.format(yesterday_productivity)
    })

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
    total_sec = 0 
    dict_list = []    
    for entry in time_entry_list:
        my_dict = {}
        my_dict['client'] = entry.taskobj.projectobj.clientobj.name
        my_dict['project'] = entry.taskobj.projectobj.name           
        my_dict['task'] = entry.taskobj.name
        my_dict['startTime'] = entry.start_time
        my_dict['endTime'] = entry.end_time
        my_dict['minutes'] = entry.durationminutes
        my_dict['seconds'] = entry.durationseconds
        my_dict['duration_string'] = str(entry.durationminutes) + " M: "+ str(entry.durationseconds) +" S"
        total_sec += ((entry.durationminutes*60)+entry.durationseconds)
        dict_list.append(my_dict)
    hours, mins, secs = convert(total_sec)
    try:
        total_duration = (taskobj.durationhours*60*60)+(taskobj.durationminutes*60)
        progress = (total_sec/total_duration)*100
    except:
        progress=0
    done = "{} Hours : {} Minutes : {} Seconds".format(hours, mins, secs)
    progress_percentage="{:.2f}".format(progress)
    return render(request, 'taskdetail.html', {'task_id':task_id, 'taskobj':taskobj, 'done':done, 'progress':progress_percentage, 'time_entry_list':time_entry_list})

@login_required
def timeentry(request, task_id):
    taskobj = get_object_or_404(models.Task, pk=task_id)
    if taskobj.owner != request.user:
        return HttpResponseForbidden()
    return render(request, 'timeentry.html', {'task_id':task_id, 'taskobj':taskobj})

@login_required
def newtimeentry(request):
    taskId = request.GET.get('taskId', None)
    startTime = request.GET.get('startTime', None)
    endTime = request.GET.get('endTime', None)
    startTime= datetime.strptime(startTime, '%d/%m/%Y, %H:%M:%S')
    endTime= datetime.strptime(endTime, '%d/%m/%Y, %H:%M:%S')
    difference = endTime-startTime
    seconds = difference.seconds
    min, sec = divmod(seconds, 60)
    hour, min = divmod(min, 60)
    taskobj = get_object_or_404(models.Task, pk=taskId)
    mod = models.TimeEntry.objects.create(start_time=startTime, end_time=endTime, 
                                durationminutes=min, durationseconds=sec,
                                task=taskobj, owner=request.user)
    mod.save()
    return redirect("%s?al=1" % reverse('taskdetail', kwargs={'task_id':taskId}))

@login_required
def timeentrydelete(request, timeentry_id):
    timeentryobj = get_object_or_404(models.TimeEntry, pk=timeentry_id)
    taskid = timeentryobj.taskobj.id
    if timeentryobj.owner != request.user:
        return HttpResponseForbidden()
    timeentryobj.delete()
    return redirect(reverse('taskdetail', kwargs={'task_id':taskid}))

def report(request):
    row_template = """
            <tr>
                <td>$client</td>
                <td>$project</td>
                <td>$task</td>
                <td>$starttime</td>
                <td>$endtime</td>
                <td>$minutes</td>
                <td>$seconds</td>
                <td>$duration</td>
            </tr>
        """
    t = Template(row_template)
    IST = pytz.timezone('Asia/Kolkata')
    today = datetime.now(IST).date()
    yesterday = today - timedelta(days=1)
    user_list = models.User.objects.filter(is_staff=False)
    total_sec = 0 
    dict_list = []
    for user in user_list:
        time_entries = models.TimeEntry.objects.filter(start_time__date = yesterday, owner=user)
        for entry in time_entries:
            my_dict = {}
            my_dict['client'] = entry.taskobj.projectobj.clientobj.name
            my_dict['project'] = entry.taskobj.projectobj.name           
            my_dict['task'] = entry.taskobj.name
            my_dict['startTime'] = entry.start_time
            my_dict['endTime'] = entry.end_time
            my_dict['minutes'] = entry.durationminutes
            my_dict['seconds'] = entry.durationseconds
            my_dict['duration_string'] = str(entry.durationminutes) + " M: "+ str(entry.durationseconds) +" S"
            total_sec += ((entry.durationminutes*60)+entry.durationseconds)
            dict_list.append(my_dict)
        secs = total_sec % 60
        mins = int((total_sec - secs)/60)
        hours = int((mins - (mins%60))/60)
        productivity = (total_sec/(24*60*60))*100
        table_header =  t.substitute(client='Client', project="Project", task="Task", 
                                starttime="Start Time", endtime="End Time",
                            minutes="Minutes", seconds="Seconds", duration="duration_string")
        table_str = "<table>"+table_header
        for item in dict_list:
            row_str = t.substitute(client=item['client'], project=item['project'], task=item['task'], 
                                starttime=item['startTime'], endtime=item['endTime'],
                            minutes=item['minutes'], seconds=item['seconds'], duration=item['duration_string'])
            table_str += row_str
        table_str += "</table>"
        if productivity <20:
            performance="Miserable"
        if productivity <40 and productivity>20:
            performance="PassMarks"
        if productivity <60 and productivity>40:
            performance="Good"
        if productivity>40:
            performance="Excellent"
        subject = "You worked {}H, {}M, {}S yesterday. Your productivity was {:.2f}%. {}".format(hours, mins, secs, productivity, performance)
        msgtxt = Mail(
            from_email='adysingh1989coursera@gmail.com',
            to_emails=user.email,
            subject=subject,
            html_content=table_str)
        try:
            sg = SendGridAPIClient('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')
            response = sg.send(msgtxt)
            print(response.status_code)
            print(response.body)
            print(response.headers)
        except Exception as e:
            print(e)   
    return HttpResponse("None")     
    

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

def convert(seconds):
    seconds = seconds % (24 * 3600)
    hour = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60
    return "%d:%02d:%02d" % (hour, minutes, seconds)

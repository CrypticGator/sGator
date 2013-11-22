from __future__ import division
from django.contrib.auth.models import User
from django.db.models import Sum
from django.http import Http404
from django.http import HttpResponse
from django.shortcuts import render,redirect
from django.core.urlresolvers import reverse
from django.contrib import messages
from course.models import Course
from django.template import Context, loader
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.contrib.sessions.backends.db import SessionStore
import datetime
from random import *
from django.views.decorators.csrf import csrf_exempt   
from pyquery import PyQuery
import string
import json
import algorithm
import itertools
import random


def setCount(c,request):
    request.session['tcount'] = c

def generateLinks(results):  #generate links for campus map view
    tempstrings = list()
    needed = ['name','lday','dday','ltime', 'dtime', 'lbuild', 'dbuild']
    tempstring = ''
    for course in results:
        for field, val in course:
            if field in needed:
                if (len(val) > 0) :
                    tempstring = tempstring + val +','
                    
        templist = tempstring.split(',')
        print templist
        x = len(templist) - 1
        y = 0
        while(x >=0):
            tempstrings.insert(x,templist[y])
            x = x-1
            y = y+1
            
        tempstring = tempstring + ';'
        
    print ''.join(tempstrings)
    
    return '0'

def insert_space(string, integer):
    return string[0:integer] + ' ' + string[integer:]

def home(request):
    return render(request, "home.html")

@csrf_exempt  
def generateSchedule(request):
    context = RequestContext(request)
    genAgain = False
    if request.user.is_authenticated():
        if request.is_ajax():  #Justin's Toast
            courses = request.raw_post_data
            request.user.get_profile().courses.append(courses)
            return HttpResponse(courses)
        else:

            if 'tcount' not in request.session:
                    setCount(0,request)
            if 'templ' not in request.session:
                     request.session['templ'] = list()
            if request.POST.get('more'):
                if 'tcount' not in request.session:
                    setCount(0,request)
                else: 
                    setCount(int(request.session['tcount'] + 1),request)
                genAgain = True

            tcourses = list()
            templist = list()
            generated = False
            if request.POST.get('clear'):
                del request.user.get_profile().cursc[0:len(request.user.get_profile().cursc)]  #CLEAR temporary list of schedules generated
                del request.user.get_profile().courses[0:len(request.user.get_profile().courses)] #If generated, the temporary courses are removed from the table and the User object
                request.session['tcount'] = 0
            courses = request.user.get_profile().courses
            courseO = list() # list of courses based on given ID for courses to be generated
            names = list()
            for i in courses:
                courseO.append(Course.objects.get(id__exact = i))
                if Course.objects.get(id__exact = i).name not in names:
                    names.append(Course.objects.get(id__exact = i).name)
                    
            namesF = list()
            for n in names:
                tlist = list()
                for c in courseO:
                    if c.name == n:
                        tlist.append(c)
                namesF.append(tlist)
            numFoundCourses = len(namesF)            
            print "NAMES "+str(namesF) # all temp courses sorted by course name
          
            if request.POST.get('Generate') or genAgain:
                if request.POST.get('numc'):
                    try:
                        numc = (request.POST.get('numc'))
                    except: numc = 20
                else: numc = 20
                #print numc
                generated = True
                #START READING COMMENTS HERE
                tcourses = algorithm.get_results(request.user.get_profile().courses)   #temporary courses chosen added to queue per user not to be lost after refresh, IGNORE THIS
                if len(tcourses) > 0:
                    if numc > len(namesF): # Where numc is number of courses put in by user
                        numc = len(namesF) # namesF is the list of lists
                    #results = algorithm.generate_schedules(tlist,numc)  #ORIGINAL CALL TO ALGORITHM get rid of this, replace with call to input_subset
                    results = control_algo(namesF,request,numc)
                    
                    for i in range(0,len(results)):
                        templist.insert(i,(results[i]))# for each schedule, get correct formatting for template tags, schedule1 ->templist(1) and so on....
                            #Need t oinsert formatdisplay() method for front end for posible new schedule list type
                    request.user.get_profile().cursc.insert(0,templist)  #place in current user schedule (temporary)

                else:
                    templist = request.user.get_profile().cursc      #hold value on refresh
            else:
                if generated:  #temporary IF, may have bug where more than 1 schedule will not appear-> here because if you click generate more than once, it will keep adding to schedule
                    for s in request.user.get_profile().cursc:
                        for v in s:
                            templist.append(v)
                    generated = false
                else:
                    if len(request.user.get_profile().cursc) > 0:
                        templist = request.user.get_profile().cursc[0]                   
            #print templist  
            cmap = list()
            '''
            if len(templist) > 0:
                for s in templist:
                    cmap.append(generateLinks(s))
                #print cmap
            '''


            print "TCOUNT"+str(request.session['tcount'])
            return render_to_response('schedule.html', {"courses": courseO,"results": templist,"cmaps": cmap,"totalC":numFoundCourses,}, context_instance=context)
        
    else:
        return render_to_response('nsi.html', context_instance=context)
  
    
def profile(request):
    context = RequestContext(request)
    user_profile = request.user.get_profile()#profile object passed to template - can also be manipulated
    if request.user.is_authenticated():
        return render_to_response("profile.html",{"uprofile": user_profile,},context_instance=context)  # to be edited when more stuff is added to profile page
    else:
        return render_to_response('nsi.html', context_instance=context)

def static_page(page, title):
    return lambda request: render(request, page, {"title": title})  #Pages that don't need authentication

def search(request):
    context = RequestContext(request)
    iquery = request.GET.get('q')
    query = iquery.strip()
    criteria = request.GET.get('DEPT')
    #print query + str(len(query))
    if criteria != "":
        resultsF = Course.objects.filter(dept__exact = criteria)
        
    else:
        
        if len(query) == 3 or ((len(query) == 8 or len(query) == 9) and ' ' in query):
            resultsF = Course.objects.filter(name__icontains = query)
        elif (not query.isalpha()) and (len(query) == 7 or len(query) == 8):
            tquery = insert_space(query,3)
            resultsF = Course.objects.filter(name__icontains = tquery)
        elif len(query) == 4:
            resultsF = Course.objects.filter(section__icontains = iquery)
        elif len(query) == 2:
            return render_to_response('nrf.html', context_instance=context)  
        elif len(query) > 1:

            if ' ' in query:
                index = query.find(' ')
                tfname = query[index+1:]
                tlname = query[0:index]
                resultsF = Course.objects.filter(cinst__icontains = tlname).filter(cinst__icontains = tfname)
            else:
                resultsF = Course.objects.filter(cinst__icontains = query)
                
            
        else:
            return render_to_response('nrf.html', context_instance=context)  #temporary no results found page
                                          
    size = len(resultsF)    
    if size < 1:
        return render_to_response('nrf.html', context_instance=context)

    
            
    return render_to_response('courses.html', {"results": resultsF,"size": size}, context_instance=context)

def control_algo(inputs, request, numc):
    templist = request.session['templ'] #Session templist to be changed in this method
    outputs = templist[:] # Get the leftover elements from last time
    course_combo = itertools.cycle(itertools.product(*inputs))
    while len(outputs) < 4:
        # actually generate results for this combo 
        list_IDs = list(course.id for course in next(course_combo))
        results = algorithm.generate_schedules(list_IDs,numc)
        outputs.extend(results)
    # At this point, len(outputs) must be 4 or greater
    templist = outputs[5:len(outputs)] # save the leftover elements
    outputs = outputs[0:5]
    request.session['templ'] = templist  # Save templist back to session cookie
    print outputs
    return outputs


@csrf_exempt 
def pasth(request):
    context = RequestContext(request)
    if request.user.is_authenticated(): 
        data = request.POST.get('test')
        results = list()
        pq = PyQuery(data)
        for c in pq('td'):
            results.append(pq(c).text())
            #to be parsed and added to Schedule Model of User Profile Model when created
        return render_to_response('pasth.html', {"results": results,}, context_instance=context)

    else:
        return render_to_response('nsi.html', context_instance=context)

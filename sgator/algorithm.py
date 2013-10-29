from course.models import Course as DB_Course
from sgator.models import Schedule

#Courses = [] # This is where we would get the list of Strings for the user's requested courses
#Results = [] # We will query the database to fill this list with each section for each course in Courses

def get_results(Courses):
    Results = []
    for course in Courses:
        course.replace(" ","") # Remove any spaces
        if course.isdigit(): # If a course entry has numbers, the user is requesting any section
            Results += list(DB_Course.objects.filter(id = course))
        else: # If a course entry is just numbers, the user is requesting a specific section
            Results += list(DB_Course.objects.filter(name__icontains = course)) # where section.name is the string name, ie "CEN3031"
    # At this point we should have a list of Courses in Jordan format
    for i in range(len(Results)):
        # split Results[i]/lday into list by ' 's, build list containing dictionary elements
        lecture_days = (c for c in Results[i].lday if c is not " ")
        lecture_time = Results[i].ltime
        discussion_days = (c for c in Results[i].dday if c is not " ")
        discussion_time = Results[i].dtime
        times = [{'day': day, 'time': time} for day, time in zip(lecture_days, lecture_time)] + [{'day': day, 'time': time} for day, time in zip(discussion_days, discussion_time)]
        discussion_flag = 0 # Set a flag equal to 1 if the section is a discussion
        if (Results[i].lday = '') 
            discussion_flag = 1
        Results[i] = (Results[i], times, discussion_flag)
    # At this point, Results contains all the sections of all the courses the user requested
    return Results

# example use: if( overlaps( Results[0], Results[1] )
def overlaps(class1, class2):
    return any(t==t2 for t in class1[1] for t2 in class2[1])

# example use: if( samecourse( Results[0], Results[1] )
# Returns True if both classes are the same course by name
def samecourse(class1, class2):
    return (class1[0].name == class2[0].name)

# Returns true if both classes are discussions or both are lectures
def both_dl(class1, class2):
    return class1[2] == class2[2]

#for i in range(1,len(Results)):
#    # add every section from Results that match Courses_[i], if they don't overlap
#    schedule = Schedule.__init__()
#    schedule.add(Results(i))
#    for j in range(1,len(Results)):
#        schedule.add(Results(j))
#    Possible_Schedules[i] = schedule

def generate_schedules(Results):
    Possible_Schedules = []
    for i in range(len(Results)):
        schedule = Schedule.__init__()
        schedule.add(Results[i][0])
        courses_in_schedule = 1
        for j in range(i,len(Results)):
            if (!overlaps( Results[courses_in_schedule-1][0], Results[j][0] )):
                if (!samecourse( Results[courses_in_schedule-1][0], Results[j][0] )):
                    if (!both_dl( Results[courses_in_schedule-1][0], Results[j][0] )):
                        schedule.add(Results[j][0])
                        courses_in_schedule += 1
                # If the two are the same course and they don't overlap, that
                # means we have two possible schedule, so make two schedules
                # out of them
                else 
                    if (!both_dl( Results[courses_in_schedule-1][0], Results[j][0] )):
                        


        Possible_Schedules.append(schedule)

    return Possible_Schedules

#def generate_schedules_helper(schedule,Results,i):
#    if i == len(Results): # base case
#        return schedule
#    else:
#        for j in range(1,len(Results)): # recursive case
#            schedule2 = Schedule.__init__(schedule)
#            # only make a new schedule if there is no conflict
#            if (not overlaps(Results[i],Results[j])) and (not samecourse(Results[i],Results[j])):
#                schedule2.add(Results[j][0])
#                generate_schedules_helper(schedule2,j)

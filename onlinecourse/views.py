from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views import generic
from django.contrib.auth import login, logout, authenticate
from .models import Course, Enrollment, Question, Choice, Submission

# --- Original Project Views ---
class CourseListView(generic.ListView):
    model = Course
    template_name = 'onlinecourse/course_list_bootstrap.html'
    context_object_name = 'course_list'

class CourseDetailView(generic.DetailView):
    model = Course
    template_name = 'onlinecourse/course_details_bootstrap.html'

def enroll(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    Enrollment.objects.create(user=request.user, course=course)
    return HttpResponseRedirect(reverse('onlinecourse:course_details', args=(course.id,)))

def registration_request(request):
    return render(request, 'onlinecourse/user_registration_bootstrap.html')

def login_request(request):
    return render(request, 'onlinecourse/user_login_bootstrap.html')

def logout_request(request):
    logout(request)
    return redirect('onlinecourse:index')

# --- New Assessment Views ---
def submit(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    user = request.user
    enrollment = Enrollment.objects.filter(user=user, course=course).first()
    submission = Submission.objects.create(enrollment=enrollment)
    choices = extract_answers(request)
    submission.choices.set(choices)
    submission_id = submission.id
    return HttpResponseRedirect(reverse('onlinecourse:exam_result', args=(course_id, submission_id,)))

def extract_answers(request):
    submitted_answers = []
    for key in request.POST:
        if key.startswith('choice_'):
            value = request.POST[key]
            choice_id = int(value)
            submitted_answers.append(choice_id)
    return submitted_answers

def show_exam_result(request, course_id, submission_id):
    context = {}
    course = get_object_or_404(Course, pk=course_id)
    submission = Submission.objects.get(id=submission_id)
    choices = submission.choices.all()
    total_score = 0
    questions = course.question_set.all()
    
    for question in questions:
        correct_choices = question.choice_set.filter(is_correct=True)
        selected_choices = choices.filter(question=question)
        if set(correct_choices) == set(selected_choices):
            total_score += question.grade
            
    context['course'] = course
    context['grade'] = total_score
    context['choices'] = choices
    return render(request, 'onlinecourse/exam_result_bootstrap.html', context)
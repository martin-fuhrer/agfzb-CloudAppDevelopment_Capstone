from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
# from .models import related models
# from .restapis import related methods
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from datetime import datetime
from .models import CarModel
from .restapis import get_dealers_from_cf, get_dealer_reviews_from_cf, store_review
import logging
import json

# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.
def about(request):
    return render(request, 'djangoapp/about.html')

def contact(request):
    return render(request, 'djangoapp/contact.html')

# Create a `login_request` view to handle sign in request
def login_request(request):
    context = {}
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['psw']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('djangoapp:index')
        else:
            context['message'] = "Invalid username or password."
            return render(request, 'djangoapp/login.html', context)
    else:
        return render(request, 'djangoapp/login.html', context)

# Create a `logout_request` view to handle sign out request
def logout_request(request):
    logout(request)
    return redirect('djangoapp:index')

# Create a `registration_request` view to handle sign up request
def registration_request(request):
    context = {}
    if request.method == 'GET':
        return render(request, 'djangoapp/registration.html', context)
    elif request.method == 'POST':
        # Check if user exists
        username = request.POST['username']
        password = request.POST['psw']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        user_exist = False
        try:
            User.objects.get(username=username)
            user_exist = True
        except:
            logger.error("New user")
        if not user_exist:
            user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name,
                                            password=password)
            login(request, user)
            return redirect("djangoapp:index")
        else:
            context['message'] = "User already exists."
            return render(request, 'djangoapp/registration.html', context)

# Update the `get_dealerships` view to render the index page with a list of dealerships
def get_dealerships(request):
    context = {}
    if request.method == "GET":
        url = "https://5bde1960.us-south.apigw.appdomain.cloud/api/dealership"
        # Get dealers from the URL
        dealerships = get_dealers_from_cf(url)
        # Concat all dealer's short name
        # dealer_names = ' '.join([dealer.short_name for dealer in dealerships])
        # Return a list of dealer short name
        # return HttpResponse(dealer_names)
        context['dealerships'] = dealerships
    return render(request, 'djangoapp/index.html', context)


# Create a `get_dealer_details` view to render the reviews of a dealer
# def get_dealer_details(request, dealer_id):
# ...
def get_dealer_details(request, dealer_id):
    context = {}
    if request.method == "GET":
        url = "https://5bde1960.us-south.apigw.appdomain.cloud/api/review"
        reviews = get_dealer_reviews_from_cf(url)
        # Concat all dealer's short name
        # dealer_names = ' '.join([dealer.short_name for dealer in dealerships])
        # Return a list of dealer short name
        # return HttpResponse(dealer_names)
        context['reviews'] = filter(lambda x: x.dealership == dealer_id, reviews)
        context['dealer_id'] = dealer_id
        context['dealer'] = get_dealer_detail_infos(dealer_id)
    return render(request, 'djangoapp/dealer_details.html', context)


# Create a `add_review` view to submit a review
# def add_review(request, dealer_id):
# ...
def add_review(request, dealer_id):
    if request.method == "GET":
        context = {}
        context['dealer_id'] = dealer_id
        context['dealer'] = get_dealer_detail_infos(dealer_id)
        context['cars'] = CarModel.objects.all()
        return render(request, 'djangoapp/add_review.html', context)
    if request.method == "POST":
        url = "https://5bde1960.us-south.apigw.appdomain.cloud/api/review-post"
        payload = {}
        payload['name'] = request.POST['username']
        payload['dealership'] = dealer_id
        payload['review'] = request.POST['review']
        payload['purchase'] = request.POST['purchase']
        payload['purchase_date'] = request.POST['purchase_date']
        car = CarModel.objects.get(id = request.POST['car'])
        if car:
            payload['car_make'] = car.make.name
            payload['car_model'] = car.name
            payload['car_year'] = car.year.strftime("%Y")
        store_review(url, payload)
    return redirect('djangoapp:dealer_details', dealer_id = dealer_id)


def get_dealer_detail_infos(dealer_id):
    url = "https://5bde1960.us-south.apigw.appdomain.cloud/api/dealership"
    dealerships = get_dealers_from_cf(url)
    return next(filter(lambda x: x.id == dealer_id, dealerships))

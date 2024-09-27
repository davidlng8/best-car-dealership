# Uncomment the required imports before adding the code

#from django.shortcuts import render
#from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
#from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import logout
#from django.contrib import messages
#from datetime import datetime

from django.http import JsonResponse
from django.contrib.auth import login, authenticate
import logging
import json
from django.views.decorators.csrf import csrf_exempt
from .populate import initiate
from .models import CarMake, CarModel
from .restapis import analyze_review_sentiments, get_request, post_review


# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.
def get_cars(request):
    count = CarMake.objects.filter().count()
    print(count)
    if(count == 0):
        initiate()
    car_models = CarModel.objects.select_related('car_make')
    cars = []
    for car_model in car_models:
        cars.append({
            "CarModel": car_model.name, 
            "CarMake": car_model.car_make.name, 
            "color": car_model.car_make.color
        })
    return JsonResponse({"CarModels":cars})

# Create a `login_request` view to handle sign in request
@csrf_exempt
def login_user(request):
    # Get username and password from request.POST dictionary
    data = json.loads(request.body)
    username = data['userName']
    password = data['password']
    # Try to check if provide credential can be authenticated
    user = authenticate(username=username, password=password)
    data = {"userName": username}
    if user is not None:
        # If user is valid, call login method to login current user
        login(request, user)
        data = {"userName": username, "status": "Authenticated"}
    return JsonResponse(data)

# Create a `logout_request` view to handle sign out request
def logout_request(request):
    logout(request)
    data = {"userName":""}
    return JsonResponse(data)

def does_username_exist(userName):
    try:
        # Check if user already exists
        User.objects.get(username=userName)
        return True
    except:
        # If not, simply log this is a new user
        logger.debug("{} is new user".format(userName))
    return False

# Create a `registration` view to handle sign up request
@csrf_exempt
def registration(request):
    # Get user details from request
    userData = json.loads(request.body)
    firstName = userData['firstName']
    lastName = userData['lastName']
    email = userData['email']
    userName = userData['userName']
    # TODO: Add encoding for password. Do not store in plain text
    password = userData['password']
    
    # To check if the user already exists
    username_exist = does_username_exist(userName)

    # If it is a new user
    if not username_exist:
        # Create user in auth_user table
        user = User.objects.create_user(
            username=userName, 
            first_name=firstName, 
            last_name=lastName,
            password=password, 
            email=email
        )
        # Login the user and redirect to list page
        login(request, user)
        data = {"userName":userName,"status":"Authenticated"}
        return JsonResponse(data)
    else :
        data = {"userName":userName,"error":"Already Registered"}
        return JsonResponse(data)

def return_response(data = {}, request = None, status=200):
    if status != 200 and request is not None:
        print(request)
    return JsonResponse({'status': status} | data)

# Update the `get_dealerships` view to render 
# the index page with a list of dealerships
def get_dealerships(request, state='all'):
    endpoint = '/fetchDealers'
    if state.lower() != 'all':
        # Append the state if necessary
        endpoint = f'{endpoint}/{state}'
    dealerships = get_request(endpoint)
    if dealerships != None:
        return return_response({'dealers' : dealerships})
    return return_response(
        {"message": "Unable to get dealership info"}, 
        request, 
        500
    )

def is_non_floating_point(value):
    try:
        if isinstance(value, str):
            value = value.strip()
            if not value:
                return False
            value = int(value)
        # Check if the value is an integer type
        return isinstance(value, int)
    except ValueError:
        # If it can't be converted to an integer, 
        # it's not a non-floating point number
        return False

# Create a `get_dealer_reviews` view to render the reviews of a dealer
def get_dealer_reviews(request,dealer_id):
    data_values = {"message": "Bad request"}
    if dealer_id is None or not is_non_floating_point(dealer_id):
        return return_response(data_values, request, 400)

    reviews = get_request(f'/fetchReviews/dealer/{dealer_id}')
    for review_detail in reviews:
        response = analyze_review_sentiments(review_detail['review'])
        print(response)
        review_detail['sentiment'] = response['sentiment']
    return return_response({'reviews': reviews})
    

# Create a `get_dealer_details` view to render the dealer details
def get_dealer_details(request, dealer_id):
    if dealer_id is None or not is_non_floating_point(dealer_id):
        return JsonResponse({"status": 400, "message": "Bad request"})
    dealer = get_request(f'/fetchDealer/{dealer_id}')
    if dealer != None:
        return return_response({'dealer': dealer})
    return JsonResponse(
        {"status": 500, "message": "Unable to get dealer info"}
    )

# Create a `add_review` view to submit a review
def add_review(request):
    if(request.user.is_anonymous == False):
        data = json.loads(request.body)
        try:
            post_review(data)
            return return_response({})
        except:
            return return_response(
                {'message': 'Error posting a review'}, 
                request, 
                401
            )
    else:
        return return_response({"message":"Unauthorized"}, request, 403)

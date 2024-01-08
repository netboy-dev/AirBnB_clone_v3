app.py


#!/usr/bin/python3

'''

Createw Flask app; and register the blueprint app_views to Flask instance app.

'''


from os import getenv

from flask import Flask, jsonify

from flask_cors import CORS

from models import storage

from api.v1.views import app_views


app = Flask(__name__)


# enable CORS and allow for origins:

CORS(app, resources={r'/api/v1/*': {'origins': '0.0.0.0'}})


app.register_blueprint(app_views)

app.url_map.strict_slashes = False



@app.teardown_appcontext

def teardown_engine(exception):

    '''

    Removes the current SQLAlchemy Session object after each request.

    '''

    storage.close()



# Error handlers for expected app behavior:

@app.errorhandler(404)

def not_found(error):

    '''

    Return errmsg `Not Found`.

    '''

    response = {'error': 'Not found'}

    return jsonify(response), 404



if __name__ == '__main__':

    HOST = getenv('HBNB_API_HOST', '0.0.0.0')

    PORT = int(getenv('HBNB_API_PORT', 5000))

    app.run(host=HOST, port=PORT, threaded=True)


api/v1/views/__init__.py


#!/usr/bin/python3

'''

Creates a Blueprint instance with `url_prefix` set to `/api/v1`.

'''



from flask import Blueprint


app_views = Blueprint('app_views', __name__, url_prefix='/api/v1')


from api.v1.views.index import *

from api.v1.views.states import *

from api.v1.views.cities import *

from api.v1.views.amenities import *

from api.v1.views.users import *

from api.v1.views.places import *

from api.v1.views.places_reviews import *

from api.v1.views.places_amenities import *


api/v1/views/amenities.py


#!/usr/bin/python3

'''

Creates a view for Amenity objects - handles all default RESTful API actions.

'''


# Import necessary modules

from flask import abort, jsonify, request

from models.amenity import Amenity

from api.v1.views import app_views

from models import storage



# Route for retrieving all Amenity objects

@app_views.route('/amenities', methods=['GET'], strict_slashes=False)

def get_all_amenities():

    '''Retrieves the list of all Amenity objects'''

    # Get all Amenity objects from the storage

    amenities = storage.all(Amenity).values()

    # Convert objects to dictionaries and jsonify the list

    return jsonify([amenity.to_dict() for amenity in amenities])



# Route for retrieving a specific Amenity object by ID

@app_views.route('/amenities/<amenity_id>',

                 methods=['GET'], strict_slashes=False)

def get_amenity(amenity_id):

    '''Retrieves an Amenity object'''

    # Get the Amenity object with the given ID from the storage

    amenity = storage.get(Amenity, amenity_id)

    if amenity:

        # Return the Amenity object in JSON format

        return jsonify(amenity.to_dict())

    else:

        # Return 404 error if the Amenity object is not found

        abort(404)



# Route for deleting a specific Amenity object by ID

@app_views.route('/amenities/<amenity_id>', methods=['DELETE'])

def delete_amenity(amenity_id):

    '''Deletes an Amenity object'''

    # Get the Amenity object with the given ID from the storage

    amenity = storage.get(Amenity, amenity_id)

    if amenity:

        # Delete the Amenity object from the storage and save changes

        storage.delete(amenity)

        storage.save()

        # Return an empty JSON with 200 status code

        return jsonify({}), 200

    else:

        # Return 404 error if the Amenity object is not found

        abort(404)



# Route for creating a new Amenity object

@app_views.route('/amenities', methods=['POST'], strict_slashes=False)

def create_amenity():

    '''Creates an Amenity object'''

    if not request.get_json():

        # Return 400 error if the request data is not in JSON format

        abort(400, 'Not a JSON')


    # Get the JSON data from the request

    data = request.get_json()

    if 'name' not in data:

        # Return 400 error if 'name' key is missing in the JSON data

        abort(400, 'Missing name')


    # Create a new Amenity object with the JSON data

    amenity = Amenity(**data)

    # Save the Amenity object to the storage

    amenity.save()

    # Return the newly created Amenity

    #   object in JSON format with 201 status code

    return jsonify(amenity.to_dict()), 201



# Route for updating an existing Amenity object by ID

@app_views.route('/amenities/<amenity_id>', methods=['PUT'],

                 strict_slashes=False)

def update_amenity(amenity_id):

    '''Updates an Amenity object'''

    # Get the Amenity object with the given ID from the storage

    amenity = storage.get(Amenity, amenity_id)

    if amenity:

        # Return 400 error if the request data is not in JSON format

        if not request.get_json():

            abort(400, 'Not a JSON')


        # Get the JSON data from the request

        data = request.get_json()

        ignore_keys = ['id', 'created_at', 'updated_at']

        # Update the attributes of the Amenity object with the JSON data

        for key, value in data.items():

            if key not in ignore_keys:

                setattr(amenity, key, value)


        # Save the updated Amenity object to the storage

        amenity.save()

        # Return the updated Amenity object in JSON format with 200 status code

        return jsonify(amenity.to_dict()), 200

    else:

        # Return 404 error if the Amenity object is not found

        abort(404)



# Error Handlers:

@app_views.errorhandler(404)

def not_found(error):

    '''Returns 404: Not Found'''

    # Return a JSON response for 404 error

    response = {'error': 'Not found'}

    return jsonify(response), 404



@app_views.errorhandler(400)

def bad_request(error):

    '''Return Bad Request message for illegal requests to the API.'''

    # Return a JSON response for 400 error

    response = {'error': 'Bad Request'}

    return jsonify(response), 400


api/v1/views/cities.py


#!/usr/bin/python3

'''

Create a new view for City objects - handles all default RESTful API actions.

'''


# Import necessary modules

from flask import abort, jsonify, request

# Import the State and City models

from models.state import State

from models.city import City

from api.v1.views import app_views

from models import storage



# Route for retrieving all City objects of a specific State

@app_views.route('/states/<state_id>/cities', methods=['GET'],

                 strict_slashes=False)

def get_cities_by_state(state_id):

    '''

    Retrieves the list of all City objects of a State.

    '''

    # Get the State object with the given ID from the storage

    state = storage.get(State, state_id)

    if not state:

        # Return 404 error if the State object is not found

        abort(404)


    # Get all City objects associated with

    #   the State and convert them to dictionaries

    cities = [city.to_dict() for city in state.cities]

    return jsonify(cities)



# Route for retrieving a specific City object by ID

@app_views.route('/cities/<city_id>', methods=['GET'], strict_slashes=False)

def get_city(city_id):

    '''

    Retrieves a City object.

    '''

    # Get the City object with the given ID from the storage

    city = storage.get(City, city_id)

    if city:

        # Return the City object in JSON format

        return jsonify(city.to_dict())

    else:

        # Return 404 error if the City object is not found

        abort(404)



# Route for deleting a specific City object by ID

@app_views.route('/cities/<city_id>', methods=['DELETE'])

def delete_city(city_id):

    '''

    Deletes a City object.

    '''

    # Get the City object with the given ID from the storage

    city = storage.get(City, city_id)

    if city:

        # Delete the City object from the storage and save changes

        storage.delete(city)

        storage.save()

        # Return an empty JSON with 200 status code

        return jsonify({}), 200

    else:

        # Return 404 error if the City object is not found

        abort(404)



# Route for creating a new City object under a specific State

@app_views.route('/states/<state_id>/cities', methods=['POST'],

                 strict_slashes=False)

def create_city(state_id):

    '''

    Creates a City object.

    '''

    # Get the State object with the given ID from the storage

    state = storage.get(State, state_id)

    if not state:

        # Return 404 error if the State object is not found

        abort(404)


    # Check if the request data is in JSON format

    if not request.get_json():

        # Return 400 error if the request data is not in JSON format

        abort(400, 'Not a JSON')


    # Get the JSON data from the request

    data = request.get_json()

    if 'name' not in data:

        # Return 400 error if 'name' key is missing in the JSON data

        abort(400, 'Missing name')


    # Assign the 'state_id' key in the JSON data

    data['state_id'] = state_id

    # Create a new City object with the JSON data

    city = City(**data)

    # Save the City object to the storage

    city.save()

    # Return the newly created City object in JSON format with 201 status code

    return jsonify(city.to_dict()), 201



# Route for updating an existing City object by ID

@app_views.route('/cities/<city_id>', methods=['PUT'], strict_slashes=False)

def update_city(city_id):

    '''

    Updates a City object.

    '''

    # Get the City object with the given ID from the storage

    city = storage.get(City, city_id)

    if city:

        # Check if the request data is in JSON format

        if not request.get_json():

            # Return 400 error if the request data is not in JSON format

            abort(400, 'Not a JSON')


        # Get the JSON data from the request

        data = request.get_json()

        ignore_keys = ['id', 'state_id', 'created_at', 'updated_at']

        # Update the attributes of the City object with the JSON data

        for key, value in data.items():

            if key not in ignore_keys:

                setattr(city, key, value)


        # Save the updated City object to the storage

        city.save()

        # Return the updated City object in JSON format with 200 status code

        return jsonify(city.to_dict()), 200

    else:

        # Return 404 error if the City object is not found

        abort(404)



# Error Handlers:

@app_views.errorhandler(404)

def not_found(error):

    '''

    404: Not Found.

    '''

    # Return a JSON response for 404 error

    return jsonify({'error': 'Not found'}), 404



@app_views.errorhandler(400)

def bad_request(error):

    '''

    Return Bad Request message for illegal requests to API.

    '''

    # Return a JSON response for 400 error

    return jsonify({'error': 'Bad Request'}), 400


api/v1/views/index.py


#!/usr/bin/python3

'''

Create a route `/status` on the object app_views.

'''



from flask import jsonify

from api.v1.views import app_views

from models import storage



@app_views.route('/status', methods=['GET'])

def api_status():

    '''

    Returns a JSON response for RESTful API health.

    '''

    response = {'status': 'OK'}

    return jsonify(response)



@app_views.route('/stats', methods=['GET'])

def get_stats():

    '''

    Retrieves the number of each objects by type.

    '''

    stats = {

        'amenities': storage.count('Amenity'),

        'cities': storage.count('City'),

        'places': storage.count('Place'),

        'reviews': storage.count('Review'),

        'states': storage.count('State'),

        'users': storage.count('User')

    }

    return jsonify(stats)



api/v1/views/places.py


#!/usr/bin/python3

'''

Create a view for Place objects - handles all default RESTful API actions

'''


# Import necessary modules

from flask import abort, jsonify, request

# Import the required models

from models.city import City

from models.place import Place

from models.state import State

from models.user import User

from models.amenity import Amenity

from api.v1.views import app_views

from models import storage



# Route for retrieving all Place objects of a City

@app_views.route('/cities/<city_id>/places', methods=['GET'],

                 strict_slashes=False)

def get_places_by_city(city_id):

    '''

    Retrieves the list of all Place objects of a City

    '''

    # Get the City object with the given ID from the storage

    city = storage.get(City, city_id)

    if not city:

        # Return 404 error if the City object is not found

        abort(404)


    # Get all Place objects of the City and convert them to dictionaries

    places = [place.to_dict() for place in city.places]

    return jsonify(places)



# Route for retrieving a specific Place object by ID

@app_views.route('/places/<place_id>', methods=['GET'],

                 strict_slashes=False)

def get_place(place_id):

    '''

    Retrieves a Place object

    '''

    # Get the Place object with the given ID from the storage

    place = storage.get(Place, place_id)

    if place:

        # Return the Place object in JSON format

        return jsonify(place.to_dict())

    else:

        # Return 404 error if the Place object is not found

        abort(404)



# Route for deleting a specific Place object by ID

@app_views.route('/places/<place_id>', methods=['DELETE'])

def delete_place(place_id):

    '''

    Deletes a Place object

    '''

    # Get the Place object with the given ID from the storage

    place = storage.get(Place, place_id)

    if place:

        # Delete the Place object from the storage and save changes

        storage.delete(place)

        storage.save()

        # Return an empty JSON with 200 status code

        return jsonify({}), 200

    else:

        # Return 404 error if the Place object is not found

        abort(404)



# Route for creating a new Place object

@app_views.route('/cities/<city_id>/places', methods=['POST'],

                 strict_slashes=False)

def create_place(city_id):

    '''

    Creates a Place object

    '''

    # Get the City object with the given ID from the storage

    city = storage.get(City, city_id)

    if not city:

        # Return 404 error if the City object is not found

        abort(404)


    # Check if the request data is in JSON format

    if not request.get_json():

        # Return 400 error if the request data is not in JSON format

        abort(400, 'Not a JSON')


    # Get the JSON data from the request

    data = request.get_json()

    if 'user_id' not in data:

        # Return 400 error if 'user_id' key is missing in the JSON data

        abort(400, 'Missing user_id')

    if 'name' not in data:

        # Return 400 error if 'name' key is missing in the JSON data

        abort(400, 'Missing name')


    # Get the User object with the given user_id from the storage

    user = storage.get(User, data['user_id'])

    if not user:

        # Return 404 error if the User object is not found

        abort(404)


    # Assign the city_id to the JSON data

    data['city_id'] = city_id

    # Create a new Place object with the JSON data

    place = Place(**data)

    # Save the Place object to the storage

    place.save()

    # Return the newly created Place object in JSON format with 201 status

    return jsonify(place.to_dict()), 201



# Route for updating an existing Place object by ID

@app_views.route('/places/<place_id>', methods=['PUT'], strict_slashes=False)

def update_place(place_id):

    '''

    Updates a Place object

    '''

    # Get the Place object with the given ID from the storage

    place = storage.get(Place, place_id)

    if place:

        # Check if the request data is in JSON format

        if not request.get_json():

            # Return 400 error if the request data is not in JSON format

            abort(400, 'Not a JSON')


        # Get the JSON data from the request

        data = request.get_json()

        ignore_keys = ['id', 'user_id', 'city_id', 'created_at', 'updated_at']

        # Update the attributes of the Place object with the JSON data

        for key, value in data.items():

            if key not in ignore_keys:

                setattr(place, key, value)


        # Save the updated Place object to the storage

        place.save()

        # Return the updated Place object in JSON format with 200 status code

        return jsonify(place.to_dict()), 200

    else:

        # Return 404 error if the Place object is not found

        abort(404)



# Error Handlers:

@app_views.errorhandler(404)

def not_found(error):

    '''

    Returns 404: Not Found

    '''

    # Return a JSON response for 404 error

    response = {'error': 'Not found'}

    return jsonify(response), 404



@app_views.errorhandler(400)

def bad_request(error):

    '''

    Return Bad Request message for illegal requests to the API

    '''

    # Return a JSON response for 400 error

    response = {'error': 'Bad Request'}

    return jsonify(response), 400



# New endpoint: POST /api/v1/places_search

@app_views.route('/places_search', methods=['POST'], strict_slashes=False)

def places_search():

    """

    Retrieves Place objects based on the provided JSON search criteria

    """


    # Check if the request contains valid JSON

    if request.get_json() is None:

        abort(400, description="Not a JSON")


    # Extract data from the JSON request body

    data = request.get_json()


    if data and len(data):

        states = data.get('states', None)

        cities = data.get('cities', None)

        amenities = data.get('amenities', None)


    # If no criteria provided, retrieve all places

    if not data or not len(data) or (

            not states and

            not cities and

            not amenities):

        places = storage.all(Place).values()

        list_places = []

        for place in places:

            list_places.append(place.to_dict())

        return jsonify(list_places)


    list_places = []


    # Filter and retrieve places based on states criteria

    if states:

        states_obj = [storage.get(State, s_id) for s_id in states]

        for state in states_obj:

            if state:

                for city in state.cities:

                    if city:

                        for place in city.places:

                            list_places.append(place)


    # Filter and retrieve places based on cities criteria

    if cities:

        city_obj = [storage.get(City, c_id) for c_id in cities]

        for city in city_obj:

            if city:

                for place in city.places:

                    if place not in list_places:

                        list_places.append(place)


    # Filter places based on amenities criteria

    if amenities:

        if not list_places:

            list_places = storage.all(Place).values()

        amenities_obj = [storage.get(Amenity, a_id) for a_id in amenities]


        list_places = [place for place in list_places

                       if all([am in place.amenities

                               for am in amenities_obj])]


    # Prepare the final list of places for response

    places = []

    for p in list_places:

        d = p.to_dict()

        d.pop('amenities', None)

        places.append(d)


    # Return the list of places in JSON format

    return jsonify(places)


api/v1/views/places_amenities.py


#!/usr/bin/python3

""" objects that handle all default RestFul API actions for Place - Amenity """



from models.place import Place

from models.amenity import Amenity

from models import storage

from api.v1.views import app_views

from os import environ

from flask import abort, jsonify, make_response, request

from flasgger.utils import swag_from



@app_views.route('places/<place_id>/amenities', methods=['GET'],

                 strict_slashes=False)

@swag_from('documentation/place_amenity/get_places_amenities.yml',

           methods=['GET'])

def get_place_amenities(place_id):

    """

    Retrieves the list of all Amenity objects of a Place

    """

    place = storage.get(Place, place_id)


    if not place:

        abort(404)


    if environ.get('HBNB_TYPE_STORAGE') == "db":

        amenities = [amenity.to_dict() for amenity in place.amenities]

    else:

        amenities = [storage.get(Amenity, amenity_id).to_dict()

                     for amenity_id in place.amenity_ids]


    return jsonify(amenities)



@app_views.route('/places/<place_id>/amenities/<amenity_id>',

                 methods=['DELETE'], strict_slashes=False)

@swag_from('documentation/place_amenity/delete_place_amenities.yml',

           methods=['DELETE'])

def delete_place_amenity(place_id, amenity_id):

    """

    Deletes a Amenity object of a Place

    """

    place = storage.get(Place, place_id)


    if not place:

        abort(404)


    amenity = storage.get(Amenity, amenity_id)


    if not amenity:

        abort(404)


    if environ.get('HBNB_TYPE_STORAGE') == "db":

        if amenity not in place.amenities:

            abort(404)

        place.amenities.remove(amenity)

    else:

        if amenity_id not in place.amenity_ids:

            abort(404)

        place.amenity_ids.remove(amenity_id)


    storage.save()

    return make_response(jsonify({}), 200)



@app_views.route('/places/<place_id>/amenities/<amenity_id>', methods=['POST'],

                 strict_slashes=False)

@swag_from('documentation/place_amenity/post_place_amenities.yml',

           methods=['POST'])

def post_place_amenity(place_id, amenity_id):

    """

    Link a Amenity object to a Place

    """

    place = storage.get(Place, place_id)


    if not place:

        abort(404)


    amenity = storage.get(Amenity, amenity_id)


    if not amenity:

        abort(404)


    if environ.get('HBNB_TYPE_STORAGE') == "db":

        if amenity in place.amenities:

            return make_response(jsonify(amenity.to_dict()), 200)

        else:

            place.amenities.append(amenity)

    else:

        if amenity_id in place.amenity_ids:

            return make_response(jsonify(amenity.to_dict()), 200)

        else:

            place.amenity_ids.append(amenity_id)


    storage.save()

    return make_response(jsonify(amenity.to_dict()), 201)


api/v1/views/places_reviews.py


#!/usr/bin/python3

'''

Create a new view for Review objects - handles all default RESTful API

'''


# Import necessary modules

from flask import abort, jsonify, request

from models.place import Place

from models.review import Review

from models.user import User

from api.v1.views import app_views

from models import storage



# Route for retrieving all Review objects of a Place

@app_views.route('/places/<place_id>/reviews', methods=['GET'],

                 strict_slashes=False)

def get_reviews_by_place(place_id):

    '''

    Retrieves the list of all Review objects of a Place

    '''

    # Get the Place object with the given ID from the storage

    place = storage.get(Place, place_id)

    if not place:

        # Return 404 error if the Place object is not found

        abort(404)


    # Get all Review objects of the Place and convert them to dictionaries

    reviews = [review.to_dict() for review in place.reviews]

    return jsonify(reviews)



# Route for retrieving a specific Review object by ID

@app_views.route('/reviews/<review_id>', methods=['GET'],

                 strict_slashes=False)

def get_review(review_id):

    '''

    Retrieves a Review object

    '''

    # Get the Review object with the given ID from the storage

    review = storage.get(Review, review_id)

    if review:

        # Return the Review object in JSON format

        return jsonify(review.to_dict())

    else:

        # Return 404 error if the Review object is not found

        abort(404)



# Route for deleting a specific Review object by ID

@app_views.route('/reviews/<review_id>', methods=['DELETE'])

def delete_review(review_id):

    '''

    Deletes a Review object

    '''

    # Get the Review object with the given ID from the storage

    review = storage.get(Review, review_id)

    if review:

        # Delete the Review object from the storage and save changes

        storage.delete(review)

        storage.save()

        # Return an empty JSON with 200 status code

        return jsonify({}), 200

    else:

        # Return 404 error if the Review object is not found

        abort(404)



# Route for creating a new Review object

@app_views.route('/places/<place_id>/reviews', methods=['POST'],

                 strict_slashes=False)

def create_review(place_id):

    '''

    Creates a Review object

    '''

    # Get the Place object with the given ID from the storage

    place = storage.get(Place, place_id)

    if not place:

        # Return 404 error if the Place object is not found

        abort(404)


    # Check if the request data is in JSON format

    if not request.get_json():

        # Return 400 error if the request data is not in JSON format

        abort(400, 'Not a JSON')


    # Get the JSON data from the request

    data = request.get_json()

    if 'user_id' not in data:

        # Return 400 error if 'user_id' key is missing in the JSON data

        abort(400, 'Missing user_id')

    if 'text' not in data:

        # Return 400 error if 'text' key is missing in the JSON data

        abort(400, 'Missing text')


    # Get the User object with the given user_id from the storage

    user = storage.get(User, data['user_id'])

    if not user:

        # Return 404 error if the User object is not found

        abort(404)


    # Assign the place_id to the JSON data

    data['place_id'] = place_id

    # Create a new Review object with the JSON data

    review = Review(**data)

    # Save the Review object to the storage

    review.save()

    # Return the newly created Review object in JSON format with 201 status

    return jsonify(review.to_dict()), 201



# Route for updating an existing Review object by ID

@app_views.route('/reviews/<review_id>', methods=['PUT'], strict_slashes=False)

def update_review(review_id):

    '''

    Updates a Review object

    '''

    # Get the Review object with the given ID from the storage

    review = storage.get(Review, review_id)

    if review:

        # Check if the request data is in JSON format

        if not request.get_json():

            # Return 400 error if the request data is not in JSON format

            abort(400, 'Not a JSON')


        # Get the JSON data from the request

        data = request.get_json()

        ignore_keys = ['id', 'user_id', 'place_id', 'created_at', 'updated_at']

        # Update the attributes of the Review object with the JSON data

        for key, value in data.items():

            if key not in ignore_keys:

                setattr(review, key, value)


        # Save the updated Review object to the storage

        review.save()

        # Return the updated Review object in JSON format with 200 status code

        return jsonify(review.to_dict()), 200

    else:

        # Return 404 error if the Review object is not found

        abort(404)



# Error Handlers:

@app_views.errorhandler(404)

def not_found(error):

    '''

    Returns 404: Not Found

    '''

    # Return a JSON response for 404 error

    response = {'error': 'Not found'}

    return jsonify(response), 404



@app_views.errorhandler(400)

def bad_request(error):

    '''

    Return Bad Request message for illegal requests to the API

    '''

    # Return a JSON response for 400 error

    response = {'error': 'Bad Request'}

    return jsonify(response), 400


api/v1/views/states.py


#!/usr/bin/python3

"""

Create a new view for State objects - handles all default RESTful API actions.

"""


# Import necessary modules

from flask import abort, jsonify, request

from models.state import State

from api.v1.views import app_views

from models import storage


# Route for retrieving all State objects

@app_views.route('/states', methods=['GET'], strict_slashes=False)

def get_all_states():

    """

    Retrieves the list of all State objects.

    """

    # Get all State objects from the storage

    states = storage.all(State).values()

    # Convert objects to dictionaries and jsonify the list

    state_list = [state.to_dict() for state in states]

    return jsonify(state_list)


# Route for retrieving a specific State object by ID

@app_views.route('/states/<state_id>', methods=['GET'], strict_slashes=False)

def get_state(state_id):

    """

    Retrieves a State object.

    """

    # Get the State object with the given ID from the storage

    state = storage.get(State, state_id)

    if state:

        # Return the State object in JSON format

        return jsonify(state.to_dict())

    else:

        # Return 404 error if the State object is not found

        abort(404)


# Route for deleting a specific State object by ID

@app_views.route('/states/<state_id>', methods=['DELETE'])

def delete_state(state_id):

    """

    Deletes a State object.

    """

    # Get the State object with the given ID from the storage

    state = storage.get(State, state_id)

    if state:

        # Delete the State object from the storage and save changes

        storage.delete(state)

        storage.save()

        # Return an empty JSON with 200 status code

        return jsonify({}), 200

    else:

        # Return 404 error if the State object is not found

        abort(404)


# Route for creating a new State object

@app_views.route('/states', methods=['POST'], strict_slashes=False)

def create_state():

    """

    Creates a State object.

    """

    if not request.get_json():

        # Return 400 error if the request data is not in JSON format

        abort(400, 'Not a JSON')


    # Get the JSON data from the request

    kwargs = request.get_json()

    if 'name' not in kwargs:

        # Return 400 error if 'name' key is missing in the JSON data

        abort(400, 'Missing name')


    # Create a new State object with the JSON data

    state = State(**kwargs)

    # Save the State object to the storage

    state.save()

    # Return the newly created State object in JSON format with 201 status code

    return jsonify(state.to_dict()), 201


# Route for updating an existing State object by ID

@app_views.route('/states/<state_id>', methods=['PUT'], strict_slashes=False)

def update_state(state_id):

    """

    Updates a State object.

    """

    # Get the State object with the given ID from the storage

    state = storage.get(State, state_id)

    if state:

        if not request.get_json():

            # Return 400 error if the request data is not in JSON format

            abort(400, 'Not a JSON')


        # Get the JSON data from the request

        data = request.get_json()

        ignore_keys = ['id', 'created_at', 'updated_at']

        # Update the attributes of the State object with the JSON data

        for key, value in data.items():

            if key not in ignore_keys:

                setattr(state, key, value)


        # Save the updated State object to the storage

        state.save()

        # Return the updated State object in JSON format with 200 status code

        return jsonify(state.to_dict()), 200

    else:

        # Return 404 error if the State object is not found

        abort(404)


# Error Handlers:


@app_views.errorhandler(404)

def not_found(error):

    """

    Raises a 404 error.

    """

    # Return a JSON response for 404 error

    response = {'error': 'Not found'}

    return jsonify(response), 404


@app_views.errorhandler(400)

def bad_request(error):

    """

    Returns a Bad Request message for illegal requests to the API.

    """

    # Return a JSON response for 400 error

    response = {'error': 'Bad Request'}

    return jsonify(response), 400



api/v1/views/users.py


#!/usr/bin/python3

'''

Create a new view for User objects - handles all default RESTful API actions

'''


# Import necessary modules

from flask import abort, jsonify, request

# Import the User model

from models.user import User

from api.v1.views import app_views

from models import storage



# Route for retrieving all User objects

@app_views.route('/users', methods=['GET'], strict_slashes=False)

def get_all_users():

    '''

    retrieves the list of all User objects

    '''

    # Get all User objects from the storage and convert them to dictionaries

    users = storage.all(User).values()

    return jsonify([user.to_dict() for user in users])



# Route for retrieving a specific User object by ID

@app_views.route('/users/<user_id>', methods=['GET'], strict_slashes=False)

def get_user(user_id):

    '''

    Retrieves a User object

    '''

    # Get the User object with the given ID from the storage

    user = storage.get(User, user_id)

    if user:

        # Return the User object in JSON format

        return jsonify(user.to_dict())

    else:

        # Return 404 error if the User object is not found

        abort(404)



# Route for deleting a specific User object by ID

@app_views.route('/users/<user_id>', methods=['DELETE'])

def delete_user(user_id):

    '''

    Deletes a User object

    '''

    # Get the User object with the given ID from the storage

    user = storage.get(User, user_id)

    if user:

        # Delete the User object from the storage and save changes

        storage.delete(user)

        storage.save()

        # Return an empty JSON with 200 status code

        return jsonify({}), 200

    else:

        # Return 404 error if the User object is not found

        abort(404)



# Route for creating a new User object

@app_views.route('/users', methods=['POST'], strict_slashes=False)

def create_user():

    '''

    Creates a User object

    '''

    # Check if the request data is in JSON format

    if not request.get_json():

        # Return 400 error if the request data is not in JSON format

        abort(400, 'Not a JSON')


    # Get the JSON data from the request

    data = request.get_json()

    if 'email' not in data:

        # Return 400 error if 'email' key is missing in the JSON data

        abort(400, 'Missing email')

    if 'password' not in data:

        # Return 400 error if 'password' key is missing in the JSON data

        abort(400, 'Missing password')


    # Create a new User object with the JSON data

    user = User(**data)

    # Save the User object to the storage

    user.save()

    # Return the newly created User object in JSON format with 201 status code

    return jsonify(user.to_dict()), 201



# Route for updating an existing User object by ID

@app_views.route('/users/<user_id>', methods=['PUT'], strict_slashes=False)

def update_user(user_id):

    '''

    Updates a User object

    '''

    # Get the User object with the given ID from the storage

    user = storage.get(User, user_id)

    if user:

        # Check if the request data is in JSON format

        if not request.get_json():

            # Return 400 error if the request data is not in JSON format

            abort(400, 'Not a JSON')


        # Get the JSON data from the request

        data = request.get_json()

        ignore_keys = ['id', 'email', 'created_at', 'updated_at']

        # Update the attributes of the User object with the JSON data

        for key, value in data.items():

            if key not in ignore_keys:

                setattr(user, key, value)


        # Save the updated User object to the storage

        user.save()

        # Return the updated User object in JSON format with 200 status code

        return jsonify(user.to_dict()), 200

    else:

        # Return 404 error if the User object is not found

        abort(404)



# Error Handlers:

@app_views.errorhandler(404)

def not_found(error):

    '''

    Returns 404: Not Found

    '''

    # Return a JSON response for 404 error

    response = {'error': 'Not found'}

    return jsonify(response), 404



@app_views.errorhandler(400)

def bad_request(error):

    '''

    Return Bad Request message for illegal requests to the API

    '''

    # Return a JSON response for 400 error

    response = {'error': 'Bad Request'}

    return jsonify(response), 400


models/user.py


#!/usr/bin/python3

""" holds class User"""

import models

from models.base_model import BaseModel, Base

from os import getenv

import sqlalchemy

from sqlalchemy import Column, String

from sqlalchemy.orm import relationship

import hashlib



class User(BaseModel, Base):

    """Representation of a user """

    if models.storage_t == 'db':

        __tablename__ = 'users'

        email = Column(String(128), nullable=False)

        password = Column(String(128), nullable=False)

        first_name = Column(String(128), nullable=True)

        last_name = Column(String(128), nullable=True)

        places = relationship("Place", backref="user")

        reviews = relationship("Review", backref="user")

    else:

        email = ""

        password = ""

        first_name = ""

        last_name = ""


    def __init__(self, *args, **kwargs):

        """

            instantiates user object

        """

        if kwargs:

            pwd = kwargs.pop('password', None)

            if pwd:

                # Hash the password using MD5

                secure = hashlib.md5()

                secure.update(pwd.encode("utf-8"))

                secure_password = secure.hexdigest()

                kwargs['password'] = secure_password

        super().__init__(*args, **kwargs)




models/base_model.py


#!/usr/bin/python3

"""

Contains class BaseModel

"""


from sqlalchemy.ext.declarative import declarative_base

from datetime import datetime

import models

from os import getenv

import sqlalchemy

from sqlalchemy import Column, String, DateTime

import uuid

import hashlib


time = "%Y-%m-%dT%H:%M:%S.%f"


if models.storage_t == "db":

    Base = declarative_base()

else:

    Base = object



class BaseModel:

    """The BaseModel class from which future classes will be derived"""

    if models.storage_t == "db":

        id = Column(String(60), primary_key=True)

        created_at = Column(DateTime, default=datetime.utcnow)

        updated_at = Column(DateTime, default=datetime.utcnow)


    def __init__(self, *args, **kwargs):

        """Initialization of the base model"""

        if kwargs:

            for key, value in kwargs.items():

                if key != "__class__":

                    setattr(self, key, value)

            if kwargs.get("created_at", None) and type(self.created_at) is str:

                self.created_at = datetime.strptime(kwargs["created_at"], time)

            else:

                self.created_at = datetime.utcnow()

            if kwargs.get("updated_at", None) and type(self.updated_at) is str:

                self.updated_at = datetime.strptime(kwargs["updated_at"], time)

            else:

                self.updated_at = datetime.utcnow()

            if kwargs.get("id", None) is None:

                self.id = str(uuid.uuid4())

        else:

            self.id = str(uuid.uuid4())

            self.created_at = datetime.utcnow()

            self.updated_at = self.created_at


    def __str__(self):

        """String representation of the BaseModel class"""

        return "[{:s}] ({:s}) {}".format(self.__class__.__name__, self.id,

                                         self.__dict__)


    def save(self):

        """updates the attribute 'updated_at' with the current datetime"""

        self.updated_at = datetime.utcnow()

        models.storage.new(self)

        models.storage.save()


    def to_dict(self, save_fs=None):

        """returns a dictionary containing all keys/values of the instance"""

        new_dict = self.__dict__.copy()

        if "created_at" in new_dict:

            new_dict["created_at"] = new_dict["created_at"].strftime(time)

        if "updated_at" in new_dict:

            new_dict["updated_at"] = new_dict["updated_at"].strftime(time)

        new_dict["__class__"] = self.__class__.__name__

        if "_sa_instance_state" in new_dict:

            del new_dict["_sa_instance_state"]


        # Hash the password to MD5 value if it exists

        if save_fs is None:

            if "password" in new_dict:

                del new_dict["password"]


        return new_dict


    def delete(self):

        """delete the current instance from the storage"""

        models.storage.delete(self)



models/engine/db_storage.py


#!/usr/bin/python3

"""

Contains the class DBStorage

"""


import models

from models.amenity import Amenity

from models.base_model import BaseModel, Base

from models.city import City

from models.place import Place

from models.review import Review

from models.state import State

from models.user import User

from os import getenv

import sqlalchemy

from sqlalchemy import create_engine

from sqlalchemy.orm import scoped_session, sessionmaker


classes = {"Amenity": Amenity, "City": City,

           "Place": Place, "Review": Review, "State": State, "User": User}



class DBStorage:

    """interaacts with the MySQL database"""

    __engine = None

    __session = None


    def __init__(self):

        """Instantiate a DBStorage object"""

        HBNB_MYSQL_USER = getenv('HBNB_MYSQL_USER')

        HBNB_MYSQL_PWD = getenv('HBNB_MYSQL_PWD')

        HBNB_MYSQL_HOST = getenv('HBNB_MYSQL_HOST')

        HBNB_MYSQL_DB = getenv('HBNB_MYSQL_DB')

        HBNB_ENV = getenv('HBNB_ENV')

        self.__engine = create_engine('mysql+mysqldb://{}:{}@{}/{}'.

                                      format(HBNB_MYSQL_USER,

                                             HBNB_MYSQL_PWD,

                                             HBNB_MYSQL_HOST,

                                             HBNB_MYSQL_DB))

        if HBNB_ENV == "test":

            Base.metadata.drop_all(self.__engine)


    def all(self, cls=None):

        """query on the current database session"""

        new_dict = {}

        for clss in classes:

            if cls is None or cls is classes[clss] or cls is clss:

                objs = self.__session.query(classes[clss]).all()

                for obj in objs:

                    key = obj.__class__.__name__ + '.' + obj.id

                    new_dict[key] = obj

        return (new_dict)


    def new(self, obj):

        """add the object to the current database session"""

        self.__session.add(obj)


    def save(self):

        """commit all changes of the current database session"""

        self.__session.commit()


    def delete(self, obj=None):

        """delete from the current database session obj if not None"""

        if obj is not None:

            self.__session.delete(obj)


    def reload(self):

        """reloads data from the database"""

        Base.metadata.create_all(self.__engine)

        sess_factory = sessionmaker(bind=self.__engine, expire_on_commit=False)

        Session = scoped_session(sess_factory)

        self.__session = Session


    def close(self):

        """call remove() method on the private session attribute"""

        self.__session.remove()


    def get(self, cls, id):

        '''get:

        retrieve an object from the file storage by class and id.

        '''

        if cls in classes.values() and id and type(id) == str:

            d_obj = self.all(cls)

            for key, value in d_obj.items():

                if key.split(".")[1] == id:

                    return value

        return None


    def count(self, cls=None):

        '''count:

        count the number of objects in storage matching the given class.

        '''

        data = self.all(cls)

        if cls in classes.values():

            data = self.all(cls)

        return len(data)



models/engine/file_storage.py



#!/usr/bin/python3

"""

Contains the FileStorage class

"""


import json

import models

from models.amenity import Amenity

from models.base_model import BaseModel

from models.city import City

from models.place import Place

from models.review import Review

from models.state import State

from models.user import User

from hashlib import md5


classes = {"Amenity": Amenity, "BaseModel": BaseModel, "City": City,

           "Place": Place, "Review": Review, "State": State, "User": User}



class FileStorage:

    """serializes instances to a JSON file & deserializes back to instances"""


    # string - path to the JSON file

    __file_path = "file.json"

    # dictionary - empty but will store all objects by <class name>.id

    __objects = {}


    def all(self, cls=None):

        """returns the dictionary __objects"""

        if cls is not None:

            new_dict = {}

            for key, value in self.__objects.items():

                if cls == value.__class__ or cls == value.__class__.__name__:

                    new_dict[key] = value

            return new_dict

        return self.__objects


    def new(self, obj):

        """sets in __objects the obj with key <obj class name>.id"""

        if obj is not None:

            key = obj.__class__.__name__ + "." + obj.id

            self.__objects[key] = obj


    def save(self):

        """serializes __objects to the JSON file (path: __file_path)"""

        json_objects = {}

        for key in self.__objects:

            if key == "password":

                json_objects[key].decode()

            json_objects[key] = self.__objects[key].to_dict(save_fs=1)

        with open(self.__file_path, 'w') as f:

            json.dump(json_objects, f)


    def reload(self):

        """deserializes the JSON file to __objects"""

        try:

            with open(self.__file_path, 'r') as f:

                jo = json.load(f)

            for key in jo:

                self.__objects[key] = classes[jo[key]["__class__"]](**jo[key])

        except:

            pass


    def delete(self, obj=None):

        """delete obj from __objects if it’s inside"""

        if obj is not None:

            key = obj.__class__.__name__ + '.' + obj.id

            if key in self.__objects:

                del self.__objects[key]


    def close(self):

        """call reload() method for deserializing the JSON file to objects"""

        self.reload()


    def get(self, cls, id):

        """

        Returns the object based on the class name and its ID, or

        None if not found

        """

        if cls not in classes.values():

            return None


        all_cls = models.storage.all(cls)

        for value in all_cls.values():

            if (value.id == id):

                return value


        return None


    def count(self, cls=None):

        """

        count the number of objects in storage

        """

        all_class = classes.values()


        if not cls:

            count = 0

            for clas in all_class:

                count += len(models.storage.all(clas).values())

        else:

            count = len(models.storage.all(cls).values())


        return count



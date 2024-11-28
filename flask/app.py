from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
import bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_cors import CORS  # Import CORS
import re
from datetime import datetime, timedelta, timezone
from garminconnect import Garmin, GarminConnectConnectionError, GarminConnectTooManyRequestsError
import os
import pickle
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from base64 import b64encode, b64decode
import time, random
import pytz
from bson.objectid import ObjectId
# Initialize the Flask app and setup MongoDB connection
app = Flask(__name__)

CORS(app, resources={r"/*": {"origins": "http://localhost:5173"}})

# Flask config for MongoDB
app.config["MONGO_URI"] = "change later"
mongo = PyMongo(app)

# JWT config
app.config["JWT_SECRET_KEY"] = "your-secret-key"  # Change this in production!
jwt = JWTManager(app)

KEY = b64decode(os.getenv('ENCRYPTION_KEY'))

# AES Encryption settings
def encrypt_data(data):
    """Encrypt the session data."""
    IV = os.urandom(16)  # Generate a random IV for each encryption
    cipher = AES.new(KEY, AES.MODE_CBC, IV)
    data_bytes = pickle.dumps(data)  # Convert object to bytes
    encrypted_data = cipher.encrypt(pad(data_bytes, AES.block_size))  # Pad and encrypt
    # Prepend IV to the encrypted data and base64 encode it for storage
    return b64encode(IV + encrypted_data).decode('utf-8')

def decrypt_data(encrypted_data):
    """Decrypt the session data."""
    encrypted_data_bytes = b64decode(encrypted_data)
    IV = encrypted_data_bytes[:16]  # Extract the IV from the beginning
    encrypted_data = encrypted_data_bytes[16:]  # The rest is the encrypted data
    cipher = AES.new(KEY, AES.MODE_CBC, IV)
    decrypted_data = unpad(cipher.decrypt(encrypted_data), AES.block_size)
    # #print("decrypted_data: ", decrypted_data)
    return pickle.loads(decrypted_data)  # Convert bytes back to object

# Helper function to validate email format
def is_valid_email(email):
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(email_regex, email) is not None

# Helper function to generate a unique activity ID
def generate_activity_id(existing_ids):
    """
    Generates a unique activity ID similar to Garmin's format.
    
    :param existing_ids: A set of already existing activity IDs.
    :return: A unique numeric activity ID.
    """
    while True:
        # Use the current timestamp for uniqueness and randomness for additional entropy
        base_id = int(time.time())  # Convert to milliseconds since epoch
        random_part = random.randint(1000, 9999)  # Add a random component for entropy
        activity_id = int(f"{base_id}{random_part}")
        
        if activity_id not in existing_ids:
            return activity_id

# Register API Endpoint (POST /register)
@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")
    
    # Input validation
    if not username or not email or not password:
        return jsonify({"message": "Missing required fields"}), 400

    if not is_valid_email(email):
        return jsonify({"message": "Invalid email format"}), 400

    # Check if the email or username already exists
    existing_user = mongo.db.users.find_one({"email": email})
    if existing_user:
        return jsonify({"message": "Email already exists"}), 400
    
    # Hash the password
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    # Insert user into MongoDB
    mongo.db.users.insert_one({
        "username": username,
        "email": email,
        "password": hashed_password
    })

    return jsonify({"message": "User registered successfully!"}), 201


# Login API Endpoint (POST /login)
@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    
    username = data.get("username")
    password = data.get("password")
    
    # Input validation
    if not username or not password:
        return jsonify({"message": "Missing username or password"}), 400
    
    # Find the user in MongoDB
    user = mongo.db.users.find_one({"username": username})
    if not user:
        return jsonify({"message": "User not found"}), 404
    
    # Check if password is correct
    if not bcrypt.checkpw(password.encode('utf-8'), user["password"]):
        return jsonify({"message": "Invalid credentials"}), 401
    
    mongo.db.users.update_one(
        {"username": username},
        {"$set": {"last_logged_in": datetime.now(tz=timezone.utc)}}
    )
    # Create JWT token
    access_token = create_access_token(identity=user["email"], expires_delta=timedelta(days=7) ) # Set token expiration to 7 days)

    return jsonify({"message": "Login successful", "access_token": access_token})


# Protected API Endpoint (Example: /profile) - Requires JWT authentication
@app.route("/profile", methods=["GET"])
@jwt_required()
def profile():

    current_user_email = get_jwt_identity()
    # Fetch the user's profile info (excluding password)
    user = mongo.db.users.find_one({"email": current_user_email}, {"password": 0})
    
    if not user:
        return jsonify({"message": "User not found"}), 404
    
    last_synced_garmin = user.get("last_synced_garmin")

    return jsonify({"authenticated": True, "username": user["username"], "last_synced_garmin": last_synced_garmin})


@app.route("/login_garmin", methods=["POST"])
@jwt_required()
def login_garmin():
    data = request.json

    current_user_email = get_jwt_identity()
    user = mongo.db.users.find_one({"email": current_user_email}, {"password": 0})

    if not user:
        return jsonify({"message": "You have been logged out of FitVerse."}), 404

    garmin_email = data.get("email")
    garmin_password = data.get("password")

    if not garmin_email or not garmin_password:
        return jsonify({"message": "Garmin email and password are required."}), 400
    
    try:
        # Authenticate with Garmin
        client = Garmin(garmin_email, garmin_password)
        client.login()

        # Encrypt session data before storing it
        encrypted_session_data = encrypt_data(client)
        
        # Store the encrypted session data in MongoDB
        mongo.db.users.update_one(
            {"email": current_user_email},
            {
                "$set": {
                    "garmin_email": garmin_email,
                    "garmin_session_data": encrypted_session_data,  # Store encrypted data
                    "last_synced_garmin": "first_sync"
                }
            },
            upsert=True
        )

        return jsonify({"message": "Successfully connected to Garmin and session saved."}), 200

    except (GarminConnectConnectionError, GarminConnectTooManyRequestsError) as e:
        return jsonify({"message": f"Garmin login error: {e}"}), 400

    except Exception as e:
        return jsonify({"message": f"An unexpected error occurred: {str(e)}"}), 500


@app.route("/get_activities_from_date", methods=['GET', 'POST'])
@jwt_required()
def get_activities_from_date():
    # Get the JWT identity, which is the current user's email
    current_user_email = get_jwt_identity()
    
    force = request.json.get("force")

    # Retrieve the user from the database to get the user_id
    user = mongo.db.users.find_one({"email": current_user_email}, {"password": 0})
    if not user:
        return jsonify({"msg": "User not found"}), 404

    user_id = user.get("_id")
    
    encrypted_garmin = user.get("garmin_session_data")
    
    if encrypted_garmin:
        garmin = decrypt_data(encrypted_garmin)
    else:
        return jsonify({"message": f"User has no Garmin link saved"}), 202
    
    
    syncDate = user.get('last_synced_garmin')
    if (not syncDate == 'first_sync'):
        syncDate = syncDate.replace(tzinfo=timezone.utc)
    if not syncDate or force:
        syncDate = datetime.now(tz=timezone.utc) - timedelta(weeks=52)

        
    if syncDate - datetime.now(tz=timezone.utc) < timedelta(days=1) and not force:
        return jsonify({"message": f"We have synced with Garmin in the last 24 hours. Skipping automatic sync."}), 201
    
    activities = garmin.get_activities_by_date(syncDate)
    
    #print(len(activities))


    for activity in activities:
        # Map the required fields to the new simplified structure
        activity_data = {
            'user_id': user_id,
            'activityId': activity.get('activityId'),
            'activityName': activity.get('activityName'),
            'startTimeLocal': activity.get('startTimeLocal'),
            'startTimeGMT': activity.get('startTimeGMT'),
            'activityType': activity.get('activityType', {}).get('typeKey', ''),
            'distance': activity.get('distance'),
            'duration': activity.get('duration'),
            'elapsedDuration': activity.get('elapsedDuration'),
            'movingDuration': activity.get('movingDuration'),
            'elevationGain': activity.get('elevationGain'),
            'elevationLoss': activity.get('elevationLoss'),
            'averageSpeed': activity.get('averageSpeed'),
            'maxSpeed': activity.get('maxSpeed'),
            'calories': activity.get('calories'),
            'bmrCalories': activity.get('bmrCalories'),
            'averageHR': activity.get('averageHR'),
            'maxHR': activity.get('maxHR'),
            'averageRunningCadenceInStepsPerMinute': activity.get('averageRunningCadenceInStepsPerMinute'),
            'maxRunningCadenceInStepsPerMinute': activity.get('maxRunningCadenceInStepsPerMinute'),
            'steps': activity.get('steps'),
            'avgPower': activity.get('avgPower'),
            'maxPower': activity.get('maxPower'),
            'normPower': activity.get('normPower'),
            'avgVerticalOscillation': activity.get('avgVerticalOscillation'),
            'avgGroundContactTime': activity.get('avgGroundContactTime'),
            'avgStrideLength': activity.get('avgStrideLength'),
            'avgVerticalRatio': activity.get('avgVerticalRatio'),
            'minElevation': activity.get('minElevation'),
            'maxElevation': activity.get('maxElevation'),
            'maxDoubleCadence': activity.get('maxDoubleCadence'),
            'summarizedDiveInfo': activity.get('summarizedDiveInfo', {}),
            'maxVerticalSpeed': activity.get('maxVerticalSpeed'),
            'locationName': activity.get('locationName'),
            'moderateIntensityMinutes': activity.get('moderateIntensityMinutes'),
            'vigorousIntensityMinutes': activity.get('vigorousIntensityMinutes'),
            'fastestSplit_1000': activity.get('fastestSplit_1000'),
            'fastestSplit_1609': activity.get('fastestSplit_1609'),
            'fastestSplit_5000': activity.get('fastestSplit_5000'),
            'pr': activity.get('pr'),
            'manualActivity': activity.get('manualActivity')
        }
        
        existing_activity = mongo.db.activities.find_one({
            "user_id": user_id,
            "activityId": activity.get('activityId')
        })
        
        activityType = activity.get("activityType").get('typeKey')
        print(activityType)
        if activityType:
            acceptable_activity = "running" in activityType.lower() or "cycling" in activityType.lower() or "swimming" in activityType.lower()
        else:
            acceptable_activity = False
            
        if existing_activity or not acceptable_activity:
            continue
        mongo.db.activities.insert_one(activity_data)
    
    mongo.db.users.update_one(
        {"email": current_user_email},
        {"$set": {"last_synced_garmin": datetime.now(tz=timezone.utc)}}
    )
    
    return jsonify({"message": f"Successfully saved {len(activities)} activities from Garmin."}), 200

@app.route("/fetch_user_activities", methods=['GET'])
@jwt_required()
def fetch_user_activities():
    current_user_email = get_jwt_identity()
    
    # Retrieve the user from the database to get the user_id
    user = mongo.db.users.find_one({"email": current_user_email}, {"password": 0})
    
    user_id = user.get("_id")
    pipeline = [
        {"$match": {"user_id": user_id}},
        {"$project": {
            "_id": {"$toString": "$_id"},
            "user_id": {"$toString": "$user_id"},
            "activityId": 1,
            "activityName": 1,
            "startTimeLocal": 1,
            "startTimeGMT": 1,
            "activityType": 1,
            "distance": 1,
            "duration": 1,
            "elapsedDuration": 1,
            "movingDuration": 1,
            "elevationGain": 1,
            "elevationLoss": 1,
            "averageSpeed": 1,
            "maxSpeed": 1,
            "calories": 1,
            "bmrCalories": 1,
            "averageHR": 1,
            "maxHR": 1,
            "averageRunningCadenceInStepsPerMinute": 1,
            "maxRunningCadenceInStepsPerMinute": 1,
            "steps": 1,
            "avgPower": 1,
            "maxPower": 1,
            "normPower": 1,
            "avgVerticalOscillation": 1,
            "avgGroundContactTime": 1,
            "avgStrideLength": 1,
            "avgVerticalRatio": 1,
            "minElevation": 1,
            "maxElevation": 1,
            "maxDoubleCadence": 1,
            "summarizedDiveInfo": 1,
            "maxVerticalSpeed": 1,
            "locationName": 1,
            "moderateIntensityMinutes": 1,
            "vigorousIntensityMinutes": 1,
            "fastestSplit_1000": 1,
            "fastestSplit_1609": 1,
            "fastestSplit_5000": 1,
            "pr": 1,
            "manualActivity": 1,
            "workoutTemplate": 1,
            "workoutData": 1
        }}
    ]

    
    user_activities = list(mongo.db.activities.aggregate(pipeline))
    #print(user_activities)
    if len(user_activities) != 0: 
        user_activities.sort(key=lambda x: datetime.strptime(x["startTimeLocal"], "%Y-%m-%d %H:%M:%S"), reverse=True)
        return jsonify({"activities": user_activities[0:8]}), 200
    else:
        return jsonify({"message": "This user has no activities"}), 201
    

@app.route("/fetch_user_activities_last_week_by_category", methods=['GET'])
@jwt_required()
def fetch_user_activities_last_week_by_category():
    current_user_email = get_jwt_identity()
    user = mongo.db.users.find_one({"email": current_user_email}, {"password": 0})
    user_id = user.get("_id")
    
    # Calculate the dates for the past 7 days
    today = datetime.now().date()
    last_week_dates = [(today - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(7)]
    
    # Define activity type mapping logic
    def categorize_activity(activity_name):
        if 'running' in activity_name.lower():
            return 'running'
        elif 'cycling' in activity_name.lower():
            return 'cycling'
        elif 'swimming' in activity_name.lower():
            return 'swimming'
        elif 'strength' in activity_name.lower():
            return 'strength'
        return None  # Exclude activities that do not match any category

    pipeline = [
        {"$match": {"user_id": user_id}},
        {"$project": {
            "activityType": 1,
            "startTimeLocal": 1,
            "duration": 1,
            "distance": 1,
            "calories": 1
        }},
        {"$match": {"startTimeLocal": {"$gte": (today - timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S")}}}
    ]
    
    activities = list(mongo.db.activities.aggregate(pipeline))
    
    # Initialize categorized data with all dates and empty categories
    categorized_data = {
        date: {category: [] for category in ["running", "cycling", "swimming", "strength"]}
        for date in last_week_dates
    }

    # Process activities and categorize them by date and type
    for activity in activities:
        category = categorize_activity(activity["activityType"])
        if category:
            # Extract the date from `startTimeLocal`
            activity_date = datetime.strptime(activity["startTimeLocal"], "%Y-%m-%d %H:%M:%S").date().strftime("%Y-%m-%d")
            if activity_date in categorized_data:
                categorized_data[activity_date][category].append({
                    "duration": activity.get("duration", 0),
                    "distance": activity.get("distance", 0),
                    "calories": activity.get("calories", 0)
                })
    
    return jsonify({"activities": categorized_data})


@app.route("/add_activity", methods=['POST'])
@jwt_required()
def add_activity():
    data = request.get_json()
    current_user_email = get_jwt_identity()
    user = mongo.db.users.find_one({"email": current_user_email}, {"password": 0})
    user_id = user.get("_id")
    
    # Required fields
    name = data.get("name")
    activityType = data.get("type")
    distance = data.get("distance")
    duration = data.get("duration")
    
    # Optional fields
    averageHR = data.get("averageHR")
    maxHR = data.get("maxHR")
    maxSpeed = data.get("maxSpeed")
    calories = data.get("calories")
    
    if activityType == "Run":
        db_type = "running"
    elif activityType == "Swim":
        db_type = "swimming"
    else:
        db_type = activityType.lower()
    
    timeLocal = datetime.now() - timedelta(seconds=duration)
    timeGMT = datetime.now(pytz.utc) - timedelta(seconds=duration)
    
    local_time_str = timeLocal.strftime("%Y-%m-%d %H:%M:%S")
    gmt_time_str = timeGMT.strftime("%Y-%m-%d %H:%M:%S")
    
    print(local_time_str, gmt_time_str)
    
    existing_query = mongo.db.activities.find({"user_id": user_id}, {"_id": 0, "activity_id": 1})
    existing_ids = [doc.get('activityId') for doc in existing_query if 'activityId' in doc]
    
    activity_id = generate_activity_id(existing_ids)
    # Map the required fields to the new simplified structure
    activity_data = {
        'user_id': user_id,
        'activityId': activity_id,
        'activityName': name,
        'startTimeLocal': local_time_str,
        'startTimeGMT': gmt_time_str,
        'activityType': db_type,
        'distance': distance,
        'duration': duration,
        'averageSpeed': distance / duration,
        'maxSpeed': maxSpeed,
        'calories': calories,
        'averageHR': averageHR,
        'maxHR': maxHR,
        'manualActivity': True
    }
    
    try:
        mongo.db.activities.insert_one(activity_data)
        return jsonify({"message": "Successfully added an activity to the database"}), 200
    except Exception as e:
        return jsonify({"message": "Something went wrong trying to write to the database: " + e}), 499
        
@app.route("/edit_activity", methods=['POST'])
@jwt_required()
def edit_activity():
    from bson.json_util import dumps

    data = request.get_json()
    current_user_email = get_jwt_identity()
    user = mongo.db.users.find_one({"email": current_user_email}, {"password": 0})
    user_id = user.get("_id")
    
    name = data.get("name")
    activityType = data.get("type")
    distance = data.get("distance")
    duration = data.get("duration")
    activity_id = data.get("activity_id")
    
    averageHR = data.get("averageHR")
    maxHR = data.get("maxHR")
    maxSpeed = data.get("maxSpeed")
    calories = data.get("calories")
    
    # Optional fields
    workoutData = data.get("workoutData")
    if (workoutData):
        workoutData["user_id"] = str(user_id)
    workoutTemplate = data.get("workoutTemplate")
    
    if activityType == "Run":
        db_type = "running"
    elif activityType == "Swim":
        db_type = "swimming"
    else:
        db_type = activityType.lower()
    
    # Prepare the update object
    update_data = {
        'activityName': name,
        'activityType': db_type,
        'distance': distance,
        'duration': duration,
        'averageSpeed': distance / duration if distance and duration else None,
        'maxSpeed': maxSpeed,
        'calories': calories,
        'averageHR': averageHR,
        'maxHR': maxHR,
    }
    
    # Add optional fields to the update object
    if workoutData:
        update_data['workoutData'] = workoutData
    if workoutTemplate:
        update_data['workoutTemplate'] = workoutTemplate
        
    try:
        mongo.db.activities.update_one(
            {"user_id": ObjectId(user_id), "activityId": activity_id},
            {"$set": update_data},
            upsert=True
        )
        
        return jsonify({
            "message": "Successfully edited an activity in the database",
        }), 200

    except Exception as e:
        return jsonify({"message": f"Something went wrong while writing to the database: {str(e)}"}), 499

@app.route("/delete_activity", methods=['POST'])
@jwt_required()
def delete_activity():
    data = request.get_json()
    current_user_email = get_jwt_identity()
    user = mongo.db.users.find_one({"email": current_user_email}, {"password": 0})
    user_id = user.get("_id")
    activity_id = data.get("activity_id")
    
    try:
        mongo.db.activities.delete_one( {"user_id": user_id, "activityId": activity_id} )
        return jsonify({"message": "Successfully removed an activity from the database"}), 200
    except Exception as e:
        return jsonify({"message": "Something went wrong trying to delete an activity: " + e}), 499


@app.route('/get_nutrition', methods=['GET'])
def get_nutrition():
    try:
        # Get query parameters
        search_query = request.args.get('search', '')  # Default to an empty string if no search
        start_index = int(request.args.get('start_index', 0))  # Default to 0 if not provided
        limit = int(request.args.get('limit', 20))  # Default to 20 items per fetch

        # Define the aggregation pipeline
        pipeline = [
            # Match documents based on the search query
            {
                "$match": {
                    "name": {"$regex": search_query, "$options": "i"}  # Case-insensitive search
                }
            },
            # Add a field to calculate the length of the name field
            {
                "$addFields": {
                    "nameLength": {"$strLenCP": "$name"}  # String length considering Unicode code points
                }
            },
            # Sort by the length of the name
            {
                "$sort": {"nameLength": 1}  # Ascending order
            },
            # Skip and limit for pagination
            {
                "$skip": start_index
            },
            {
                "$limit": limit
            },
            # Remove the temporary nameLength field
            {
                "$unset": "nameLength"
            }
        ]

        # Perform the aggregation query
        items_collection = mongo.db.nutrition  # Assumes the collection is named 'nutrition'
        items = list(items_collection.aggregate(pipeline))

        # Include necessary fields in the response
        result = [
            {
                "_id": str(item["_id"]),
                "name": item["name"],
                "carbs": item.get("carbs", 0),
                "fats": item.get("total_fat", 0),
                "proteins": item.get("protein", 0),
                "sugars": item.get("sugar", 0),
                "calories": item.get("calories", 0),
                # Add more fields if needed
            }
            for item in items
        ]

        return jsonify({
            "data": result,
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/add_meal', methods=['POST'])
@jwt_required()
def add_meal():
    try:
        # Get the current user's email from the JWT token
        current_user_email = get_jwt_identity()
        user = mongo.db.users.find_one({"email": current_user_email}, {"password": 0})
        
        if not user:
            return jsonify({"error": "User not found"}), 404

        user_id = user.get("_id")

        # Parse incoming JSON data
        data = request.get_json()

        # Validate required fields
        name = data.get("name")
        selected_items = data.get("selectedItems")
        total_macros = data.get("totalMacros")

        if not name or not isinstance(selected_items, list) or not total_macros:
            return jsonify({"error": "Missing required fields: name, selectedItems, or totalMacros"}), 400

        required_macros = ["carbs", "fats", "proteins", "sugars", "calories"]
        if not all(macro in total_macros for macro in required_macros):
            return jsonify({"error": f"totalMacros must include {required_macros}"}), 400

        meal_entry = {
            "user_id": user_id,
            "name": name,
            "selectedItems": selected_items,
            "totalMacros": total_macros,
            "created_at": datetime.now(tz=timezone.utc)
        }

        result = mongo.db.meals.insert_one(meal_entry)

        # Return a success response
        return jsonify({
            "message": "Meal added successfully",
            "meal_id": str(result.inserted_id)
        }), 200

    except Exception as e:
        # Handle unexpected errors
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500


@app.route("/fetch_user_meals", methods=['GET'])
@jwt_required()
def fetch_user_meals():
    try:
        # Get the current user's email from the JWT token
        current_user_email = get_jwt_identity()

        # Retrieve the user from the database to get the user_id
        user = mongo.db.users.find_one({"email": current_user_email}, {"password": 0})

        if not user:
            return jsonify({"message": "User not found"}), 404

        user_id = user.get("_id")

        # Get query parameters
        search_query = request.args.get('search', '')  # Optional search query (defaults to empty string)
        start_index = int(request.args.get('start_index', 0))  # Default to 0
        limit = int(request.args.get('limit', 50))  # Default limit of 50 meals

        # Define the aggregation pipeline
        pipeline = [
            # Match documents based on user_id and optional search query
            {
                "$match": {
                    "user_id": user_id,
                    **({"name": {"$regex": search_query, "$options": "i"}} if search_query else {})
                }
            },
            # Sort meals by created_at in descending order (most recent first)
            {"$sort": {"created_at": -1}},
            # Skip and limit for pagination
            {"$skip": start_index},
            {"$limit": limit},
            # Project the fields to include in the response
            {
                "$project": {
                    "_id": {"$toString": "$_id"},
                    "user_id": {"$toString": "$user_id"},
                    "name": 1,
                    "selectedItems": 1,
                    "created_at": 1
                }
            }
        ]

        # Perform the aggregation query
        meals = list(mongo.db.meals.aggregate(pipeline))

        return jsonify({"meals": meals}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/edit_meal", methods=['POST'])
@jwt_required()
def edit_meal():
    data = request.get_json()
    current_user_email = get_jwt_identity()
    
    # Fetch user details from the database
    user = mongo.db.users.find_one({"email": current_user_email}, {"password": 0})
    user_id = user.get("_id")
    
    # Extract meal data from the request body
    name = data.get("name")
    meal_id = data.get("meal_id")
    total_macros = data.get("totalMacros")  # This contains carbs, fats, proteins, sugars, calories
    selected_items = data.get("selectedItems")  # List of selected items for the meal
    
    # Prepare total macros data
    macros = {
        'carbs': total_macros.get('carbs'),
        'fats': total_macros.get('fats'),
        'proteins': total_macros.get('proteins'),
        'sugars': total_macros.get('sugars'),
        'calories': total_macros.get('calories')
    }
    
    try:
        # Update the meal record in the database
        mongo.db.meals.update_one(
            {"user_id": ObjectId(user_id), "_id": ObjectId(meal_id)},
            {
                "$set": {
                    'name': name,
                    'totalMacros': macros,
                    'selectedItems': selected_items
                }
            },
            upsert=True
        )

        return jsonify({"message": "Successfully edited the meal in the database"}), 200

    except Exception as e:
        return jsonify({"message": f"Something went wrong trying to write to the database: {str(e)}"}), 499



@app.route("/fetch_meals_last_week", methods=["GET"])
@jwt_required()
def fetch_meals_last_week():
    # Authenticate user
    current_user_email = get_jwt_identity()
    user = mongo.db.users.find_one({"email": current_user_email}, {"password": 0})
    user_id = user.get("_id")

    # Date range: last 7 days
    today = datetime.now(timezone.utc)
    
    #print(today)

    # Calculate last week’s start date in UTC
    last_week_start = today - timedelta(days=7)
    
    # MongoDB aggregation pipeline
    pipeline = [
        {
            "$match": {
                "user_id": ObjectId(user_id),
                "created_at": {"$gte": last_week_start, "$lte": today},
            }
        },
        {
            "$addFields": {
                "totalMacros.carbs": {"$convert": {"input": "$totalMacros.carbs", "to": "double", "onError": 0}},
                "totalMacros.fats": {"$convert": {"input": "$totalMacros.fats", "to": "double", "onError": 0}},
                "totalMacros.proteins": {"$convert": {"input": "$totalMacros.proteins", "to": "double", "onError": 0}},
                "totalMacros.sugars": {"$convert": {"input": "$totalMacros.sugars", "to": "double", "onError": 0}},
                "totalMacros.calories": {"$convert": {"input": "$totalMacros.calories", "to": "double", "onError": 0}},
            }
        },
        {
            "$project": {
                "day": {"$dateToString": {"format": "%Y-%m-%d", "date": "$created_at"}},
                "totalMacros": 1,
            }
        },
        {
            "$group": {
                "_id": "$day",
                "total_carbs": {"$sum": "$totalMacros.carbs"},
                "total_fats": {"$sum": "$totalMacros.fats"},
                "total_proteins": {"$sum": "$totalMacros.proteins"},
                "total_sugars": {"$sum": "$totalMacros.sugars"},
                "total_calories": {"$sum": "$totalMacros.calories"},
            }
        },
        {
            "$project": {
                "day": "$_id",
                "total_carbs": 1,
                "total_fats": 1,
                "total_proteins": 1,
                "total_sugars": 1,
                "total_calories": 1,
            }
        },
        {"$sort": {"day": 1}},
    ]

    # Execute aggregation
    results = list(mongo.db.meals.aggregate(pipeline))
    #print("results", results)

    # Prepare results in a consistent format for 7 days
    meals_by_day = {result["day"]: result for result in results}

    # Fill in missing days
    complete_results = []
    for i in range(7):
        day = (last_week_start + timedelta(days=i+1)).strftime("%Y-%m-%d")
        complete_results.append(
            meals_by_day.get(
                day,
                {
                    "day": day,
                    "total_carbs": 0,
                    "total_fats": 0,
                    "total_proteins": 0,
                    "total_sugars": 0,
                    "total_calories": 0,
                },
            )
        )
        
    #print("after tho??", complete_results)
        
    return jsonify({"meals_by_day": complete_results})


@app.route("/delete_meal", methods=['POST'])
@jwt_required()
def delete_meal():
    data = request.get_json()
    current_user_email = get_jwt_identity()
    user = mongo.db.users.find_one({"email": current_user_email}, {"password": 0})
    user_id = user.get("_id")
    meal_id = data.get("_id")
    
    #print(user_id, meal_id)
    try:
        #print("Find any first?", mongo.db.meals.find_one( {"user_id": user_id, "_id": ObjectId(meal_id)} ))
        mongo.db.meals.delete_one( {"user_id": user_id, "_id": ObjectId(meal_id)} )
        #print("Find any?", mongo.db.meals.find_one( {"user_id": user_id, "_id": ObjectId(meal_id)} ))
        return jsonify({"message": "Successfully removed an activity from the database"}), 200
    except Exception as e:
        return jsonify({"message": "Something went wrong trying to delete an activity: " + e}), 499

@app.route("/fetch_nutrition_summary", methods=["POST"])
@jwt_required()
def fetch_nutrition_summary():
    # Authenticate user
    current_user_email = get_jwt_identity()
    user = mongo.db.users.find_one({"email": current_user_email}, {"password": 0})
    user_id = user.get("_id")

    # Get query parameter for granularity: "day" or "week"
    granularity = request.get_json().get("granularity", "day").lower()
    if granularity not in ["day", "week"]:
        return jsonify({"error": "Invalid granularity. Must be 'day' or 'week'"}), 400

    # Current date in UTC
    today = datetime.now(timezone.utc)

    if granularity == "day":
        # Last 14 days
        start_date = today - timedelta(days=14)
    elif granularity == "week":
        # Last 14 weeks
        start_date = today - timedelta(weeks=14)

    # MongoDB aggregation pipeline
    pipeline = [
        {
            "$match": {
                "user_id": ObjectId(user_id),
                "created_at": {"$gte": start_date, "$lte": today},
            }
        },
        {
            "$addFields": {
                "totalMacros.carbs": {"$convert": {"input": "$totalMacros.carbs", "to": "double", "onError": 0}},
                "totalMacros.fats": {"$convert": {"input": "$totalMacros.fats", "to": "double", "onError": 0}},
                "totalMacros.proteins": {"$convert": {"input": "$totalMacros.proteins", "to": "double", "onError": 0}},
                "totalMacros.sugars": {"$convert": {"input": "$totalMacros.sugars", "to": "double", "onError": 0}},
                "totalMacros.calories": {"$convert": {"input": "$totalMacros.calories", "to": "double", "onError": 0}},
            }
        },
        {
            "$project": {
                "day": {"$dateToString": {"format": "%Y-%m-%d", "date": "$created_at"}},
                "totalMacros": 1,
            }
        },
        {
            "$group": {
                "_id": "$day",
                "total_carbs": {"$sum": "$totalMacros.carbs"},
                "total_fats": {"$sum": "$totalMacros.fats"},
                "total_proteins": {"$sum": "$totalMacros.proteins"},
                "total_sugars": {"$sum": "$totalMacros.sugars"},
                "total_calories": {"$sum": "$totalMacros.calories"},
            }
        },
        {
            "$sort": {"_id": 1}
        }
    ]

    # Execute aggregation
    results = list(mongo.db.meals.aggregate(pipeline))

    # Prepare results for either daily or weekly granularity
    if granularity == "day":
        # Fill in missing days for the last 14 days
        meals_by_day = {result["_id"]: result for result in results}
        complete_results = []
        for i in range(14):
            day = (start_date + timedelta(days=i+1)).strftime("%Y-%m-%d")
            complete_results.append(
                meals_by_day.get(
                    day,
                    {
                        "day": day,
                        "total_carbs": 0,
                        "total_fats": 0,
                        "total_proteins": 0,
                        "total_sugars": 0,
                        "total_calories": 0,
                    },
                )
            )

            # Ensure `day` is consistent in all records
            if "_id" in complete_results[-1]:
                complete_results[-1]["day"] = complete_results[-1].pop("_id")
    elif granularity == "week":
        # Identify the start date of the current week
        today = today.replace(hour=0, minute=0, second=0, microsecond=0)
        week_start = today - timedelta(days=today.weekday())  # Start of the current week (Monday)

        # Prepare results for the last 14 weeks
        meals_by_week = []
        for i in range(15):
            # Calculate the start and end dates of the current week
            current_week_start = week_start - timedelta(weeks=i)
            current_week_end = current_week_start + timedelta(days=6)

            # Adjust both the start and end date by one day forward
            current_week_start = current_week_start + timedelta(days=1)
            current_week_end = current_week_end + timedelta(days=1)

            # Filter the results within the current week
            week_data = [
                result
                for result in results
                if current_week_start.strftime("%Y-%m-%d") <= result["_id"] <= current_week_end.strftime("%Y-%m-%d")
            ]

            # Calculate averages for the week
            if week_data:
                total_days = len(week_data)
                week_totals = {
                    "total_carbs": sum(day["total_carbs"] for day in week_data) / total_days,
                    "total_fats": sum(day["total_fats"] for day in week_data) / total_days,
                    "total_proteins": sum(day["total_proteins"] for day in week_data) / total_days,
                    "total_sugars": sum(day["total_sugars"] for day in week_data) / total_days,
                    "total_calories": sum(day["total_calories"] for day in week_data) / total_days,
                }
            else:
                week_totals = {
                    "total_carbs": 0,
                    "total_fats": 0,
                    "total_proteins": 0,
                    "total_sugars": 0,
                    "total_calories": 0,
                }
                
            week_label = f"{current_week_start.strftime('%m/%d')}-{current_week_end.strftime('%m/%d')}"

            # Append the week result with the formatted 'week' field
            meals_by_week.append({
                "week": week_label,
                **week_totals,
            })

        # Sort results in ascending order of `week_start`
        complete_results = sorted(meals_by_week, key=lambda x: x["week"])[0:14]

    #print(complete_results)

    return jsonify({"nutrition_summary": complete_results}), 200


@app.route('/get_exercises', methods=['GET'])
def get_exercises():
    try:
        # Get query parameters
        search_query = request.args.get('search', '')  # Default to an empty string if no search
        start_index = int(request.args.get('start_index', 0))  # Default to 0 if not provided
        limit = int(request.args.get('limit', 20))  # Default to 20 items per fetch

        # Define the aggregation pipeline
        pipeline = [
            # Match documents based on the search query
            {
                "$match": {
                    "title": {"$regex": search_query, "$options": "i"}  # Case-insensitive search
                }
            },
            # Add a field to calculate the length of the title field
            {
                "$addFields": {
                    "titleLength": {"$strLenCP": "$title"}  # String length considering Unicode code points
                }
            },
            # Sort by the length of the title
            {
                "$sort": {"titleLength": 1}  # Ascending order
            },
            # Skip and limit for pagination
            {
                "$skip": start_index
            },
            {
                "$limit": limit
            },
            # Remove the temporary titleLength field
            {
                "$unset": "titleLength"
            }
        ]

        # Perform the aggregation query
        exercises_collection = mongo.db.exercises
        items = list(exercises_collection.aggregate(pipeline))

        # Include necessary fields in the response
        result = [
            {
                "_id": str(item["_id"]),
                "title": item["title"],
                "desc": item.get("desc", ""),
                "type": item.get("type", ""),
                "body_part": item.get("body_part", ""),
                "equipment": item.get("equipment", ""),
                "level": item.get("level", ""),
                # Add more fields if needed
            }
            for item in items
        ]

        return jsonify({
            "data": result,
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/fetch_paginated_activities", methods=['GET'])
@jwt_required()
def fetch_paginated_activities():
    try:
        current_user_email = get_jwt_identity()

        # Retrieve the user from the database to get the user_id
        user = mongo.db.users.find_one({"email": current_user_email}, {"password": 0})
        if not user:
            return jsonify({"error": "User not found"}), 404

        user_id = user.get("_id")

        # Query parameters
        #print("hello???????????????", request.args)
        search_query = request.args.get('search', '')  # Default to an empty string if no search
        start_index = int(request.args.get('start_index', 0))  # Default to 0 if not provided
        limit = int(request.args.get('limit', 20))  # Default to 20 items per fetch

        pipeline = [
            # Match the user_id and optional search query
            {
                "$match": {
                    "user_id": ObjectId(user_id),
                    **({"activityName": {"$regex": search_query, "$options": "i"}} if search_query else {})  # Case-insensitive search
                }
            },
            # Project only the required fields
            {
                "$project": {
                        "_id": {"$toString": "$_id"},
                        "user_id": {"$toString": "$user_id"},
                        "activityId": 1,
                        "activityName": 1,
                        "startTimeLocal": 1,
                        "startTimeGMT": 1,
                        "activityType": 1,
                        "distance": 1,
                        "duration": 1,
                        "elapsedDuration": 1,
                        "movingDuration": 1,
                        "elevationGain": 1,
                        "elevationLoss": 1,
                        "averageSpeed": 1,
                        "maxSpeed": 1,
                        "calories": 1,
                        "bmrCalories": 1,
                        "averageHR": 1,
                        "maxHR": 1,
                        "averageRunningCadenceInStepsPerMinute": 1,
                        "maxRunningCadenceInStepsPerMinute": 1,
                        "steps": 1,
                        "avgPower": 1,
                        "maxPower": 1,
                        "normPower": 1,
                        "avgVerticalOscillation": 1,
                        "avgGroundContactTime": 1,
                        "avgStrideLength": 1,
                        "avgVerticalRatio": 1,
                        "minElevation": 1,
                        "maxElevation": 1,
                        "maxDoubleCadence": 1,
                        "summarizedDiveInfo": 1,
                        "maxVerticalSpeed": 1,
                        "locationName": 1,
                        "moderateIntensityMinutes": 1,
                        "vigorousIntensityMinutes": 1,
                        "fastestSplit_1000": 1,
                        "fastestSplit_1609": 1,
                        "fastestSplit_5000": 1,
                        "pr": 1,
                        "manualActivity": 1,
                        "workoutTemplate": 1,
                        "workoutData": 1
                }
            },
            # Sort by the most recent activity
            {
                "$sort": {"startTimeLocal": -1}
            },
            # Skip for pagination
            {
                "$skip": start_index
            },
            # Limit the number of results
            {
                "$limit": limit
            }
        ]

        activities_collection = mongo.db.activities
        user_activities = list(activities_collection.aggregate(pipeline))
        
        #print(user_activities)
        if not user_activities:
            return jsonify({"message": "No activities found"}), 200

        return jsonify({"activities": user_activities}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/get_activity_details", methods=['POST'])
@jwt_required()
def get_activity_details():

    current_user_email = get_jwt_identity()
    

    # Retrieve the user from the database to get the user_id
    user = mongo.db.users.find_one({"email": current_user_email}, {"password": 0})
    if not user:
        return jsonify({"msg": "User not found"}), 404
    
    encrypted_garmin = user.get("garmin_session_data")
    
    if encrypted_garmin:
        garmin = decrypt_data(encrypted_garmin)
    else:
        return jsonify({"message": f"User has no Garmin link saved"}), 202
    
    
    activity_id = request.get_json().get("activityId")
    # Fetch activity details using the GarminConnect function
    activity_details = garmin.get_activity_details(activity_id)
    
    # Extract the relevant data: metricDescriptors, activityDetailMetrics, and sumElapsedDuration
    metric_descriptors = activity_details.get('metricDescriptors', [])
    activity_detail_metrics = activity_details.get('activityDetailMetrics', [])
    
    # Prepare the response data
    response_data = {
        'activityId': activity_id,
        'activityTime': [],
        'metrics': []
    }
    
    #print(metric_descriptors)
    
    # Go through each time series data point
    for i in range(len(activity_detail_metrics)):
        metrics = activity_detail_metrics[i]['metrics']
        
        # For each metric, collect its values across all timestamps
        for descriptor in metric_descriptors:
            metric_key = descriptor['key']
            metric_index = descriptor['metricsIndex']
            
            we_dont_care = ("duration" in metric_key.lower() or "timestamp" in metric_key.lower()  
                            or "longitude" in metric_key.lower() or "latitude" in metric_key.lower()
                            or "battery" in metric_key.lower() or "sum" in metric_key.lower()) and not (metric_key == 'sumDuration')
            if (we_dont_care):
                continue
            # Ensure that this metric exists in the current entry
            if metric_index < len(metrics):
                metric_value = metrics[metric_index]
                
                # Add this metric to the response data, if not already added
                
                if metric_key == 'sumDuration':
                    response_data['activityTime'].append(metric_value)
                elif metric_key not in [m['key'] for m in response_data['metrics']]:
                    response_data['metrics'].append({
                        'key': metric_key,
                        'unit': descriptor['unit']['key'],
                        'values': [metric_value]
                    })
                else:
                    # If this metric already exists, append the value for this timestamp
                    for metric in response_data['metrics']:
                        if metric['key'] == metric_key:
                            metric['values'].append(metric_value)
                            break

    # Return the structured response as JSON
    return jsonify(response_data)

@app.route("/get_activity_splits", methods=['POST'])
@jwt_required()
def get_activity_splits():
    current_user_email = get_jwt_identity()

    # Retrieve the user from the database to get the user_id
    user = mongo.db.users.find_one({"email": current_user_email}, {"password": 0})
    if not user:
        return jsonify({"msg": "User not found"}), 404
    
    encrypted_garmin = user.get("garmin_session_data")
    
    if encrypted_garmin:
        garmin = decrypt_data(encrypted_garmin)
    else:
        return jsonify({"message": f"User has no Garmin link saved"}), 202

    # Get the activity ID from the request payload
    activity_id = request.get_json().get("activityId")
    if not activity_id:
        return jsonify({"msg": "Activity ID is required"}), 400

    try:
        # Fetch activity splits using GarminConnect
        splits = garmin.get_activity_splits(activity_id)
    except Exception as e:
        return jsonify({"msg": f"Failed to fetch splits: {str(e)}"}), 500

    # Organize the data for the chart
        # Categories (x-axis)
    categories = []
    
    # Initialize series
    duration_series = {"name": "Duration (seconds)", "data": []}
    distance_series = {"name": "Distance (meters)", "data": []}
    calories_series = {"name": "Calories Burned", "data": []}
    avg_speed_series = {"name": "Average Speed (m/s)", "data": []}
    
    # Process each lap
    for lap in splits.get("lapDTOs", []):
        categories.append(lap.get("lapIndex"))
        duration_series["data"].append(lap.get("duration"))
        distance_series["data"].append(lap.get("distance"))
        calories_series["data"].append(lap.get("calories"))
        avg_speed_series["data"].append(lap.get("averageSpeed"))
    
    # Combine the series
    series = [duration_series, distance_series, calories_series, avg_speed_series]
    
    organized_data = {
        "categories": categories,
        "series": series
    }

    return jsonify({"activityId": activity_id, "splits": organized_data})

@app.route('/add_template', methods=['POST'])
@jwt_required()
def add_template():
    try:
        # Get the current user's email from the JWT token
        current_user_email = get_jwt_identity()
        user = mongo.db.users.find_one({"email": current_user_email}, {"password": 0})
        
        if not user:
            return jsonify({"error": "User not found"}), 404

        user_id = user.get("_id")

        # Parse incoming JSON data
        data = request.get_json()

        # Validate required fields
        name = data.get("name")
        selected_items = data.get("selectedItems")

        template_entry = {
            "user_id": user_id,
            "name": name,
            "selectedItems": selected_items,
        }
        
        if not (name == '' or name == None):
            result = mongo.db.workout_templates.insert_one(template_entry)

        # Return a success response
        return jsonify({
            "message": "Workout added successfully",
            "workout_id": str(result.inserted_id),
            "user_id": str(user_id)
        }), 200

    except Exception as e:
        # Handle unexpected errors
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@app.route("/edit_template", methods=['POST'])
@jwt_required()
def edit_template():
    data = request.get_json()
    current_user_email = get_jwt_identity()
    
    # Fetch user details from the database
    user = mongo.db.users.find_one({"email": current_user_email}, {"password": 0})
    user_id = user.get("_id")
    
    # Extract meal data from the request body
    name = data.get("name")
    workout_id = data.get("meal_id")
    selected_items = data.get("selectedItems")  # List of selected items for the meal
    
    
    try:
        # Update the meal record in the database
        mongo.db.workout_template.update_one(
            {"user_id": ObjectId(user_id), "_id": ObjectId(workout_id)},
            {
                "$set": {
                    'name': name,
                    'selectedItems': selected_items
                }
            },
            upsert=True
        )

        return jsonify({"message": "Successfully edited the workout in the database"}), 200

    except Exception as e:
        return jsonify({"message": f"Something went wrong trying to write to the database: {str(e)}"}), 499

@app.route('/fetch_user_workout_templates', methods=['GET'])
@jwt_required()
def fetch_user_workout_templates():
    current_user_email = get_jwt_identity()
    
    # Retrieve the user from the database to get the user_id
    user = mongo.db.users.find_one({"email": current_user_email}, {"password": 0})
    user_id = user.get("_id")
    
    # Get query parameters
    search_query = request.args.get('search', '')  # Default to empty string if no search query
    start_index = int(request.args.get('start_index', 0))  # Default to 0 if not provided
    limit = int(request.args.get('limit', 20))  # Default to 20 items per fetch
    
    # Define the query
    query = {"user_id": user_id}
    if search_query:
        query["name"] = {"$regex": search_query, "$options": "i"}  # Case-insensitive search on name
    
    # Find matching workout templates
    workout_templates = mongo.db.workout_templates.find(query).skip(start_index).limit(limit)
    
    # Prepare the result to include only necessary fields
    result = [
        {
            "_id": str(template["_id"]),
            "user_id": str(template["user_id"]),
            "name": template["name"],
            "selectedItems": template.get("selectedItems", [])
        }
        for template in workout_templates
    ]
    
    # print(result)
    
    return jsonify({"workout_templates": result})

@app.route("/fetch_user_activities_by_category_options", methods=['POST'])
@jwt_required()
def fetch_user_activities_by_category_options():
    current_user_email = get_jwt_identity()
    user = mongo.db.users.find_one({"email": current_user_email}, {"password": 0})
    user_id = user.get("_id")

    # Get granularity parameter
    granularity = request.get_json().get("granularity", "days").lower()
    if granularity not in ["days", "weeks", "months"]:
        return jsonify({"error": "Invalid granularity. Must be 'days', 'weeks', or 'months'"}), 400

    # Calculate the date ranges
    today = datetime.now().date()

    if granularity == "days":
        date_range = [today - timedelta(days=i) for i in range(14)]  # Keep as datetime objects for sorting
        match_start_date = (today - timedelta(days=14)).strftime("%Y-%m-%d %H:%M:%S")
    elif granularity == "weeks":
        # Calculate the start and end dates for the last 14 weeks
        weeks = []
        for i in range(14):
            week_start = today - timedelta(days=today.weekday() + i * 7)
            week_end = week_start + timedelta(days=6)
            weeks.append((week_start, week_end))
        match_start_date = weeks[-1][0].strftime("%Y-%m-%d %H:%M:%S")
    elif granularity == "months":
        # Calculate the start of the current month and 12 months back
        months = []
        for i in range(12):
            month_start = (today.replace(day=1) - timedelta(days=i * 30)).replace(day=1)
            next_month_start = (month_start + timedelta(days=31)).replace(day=1)
            months.append((month_start, next_month_start - timedelta(days=1)))
        match_start_date = months[-1][0].strftime("%Y-%m-%d %H:%M:%S")

    # Define activity type mapping logic
    def categorize_activity(activity_name):
        if 'running' in activity_name.lower():
            return 'running'
        elif 'cycling' in activity_name.lower():
            return 'cycling'
        elif 'swimming' in activity_name.lower():
            return 'swimming'
        elif 'strength' in activity_name.lower():
            return 'strength'
        return None

    # MongoDB aggregation pipeline
    pipeline = [
        {"$match": {"user_id": user_id}},
        {"$project": {
            "activityType": 1,
            "startTimeLocal": 1,
            "duration": 1,
            "distance": 1,
            "calories": 1
        }},
        {"$match": {"startTimeLocal": {"$gte": match_start_date}}}
    ]

    activities = list(mongo.db.activities.aggregate(pipeline))

    if granularity == "days":
        # Sort the date_range by date (keeping as datetime objects)
        date_range = sorted(date_range)
        categorized_data = {
            date.strftime("%m/%d"): {category: {"count": 0, "activities": []} for category in ["running", "cycling", "swimming", "strength"]}
            for date in date_range
        }

        for activity in activities:
            category = categorize_activity(activity["activityType"])
            if category:
                activity_date = datetime.strptime(activity["startTimeLocal"], "%Y-%m-%d %H:%M:%S").date()
                activity_date_str = activity_date.strftime("%m/%d")
                if activity_date_str in categorized_data:
                    categorized_data[activity_date_str][category]["count"] += 1
                    categorized_data[activity_date_str][category]["activities"].append({
                        "duration": activity.get("duration", 0),
                        "distance": activity.get("distance", 0),
                        "calories": activity.get("calories", 0)
                    })

    elif granularity == "weeks":
        # Sort the weeks by week_start date
        weeks.sort(key=lambda x: x[0])  # Sort by the start date of the week
        categorized_data = {
            f"{week_start.strftime('%m/%d')} - {week_end.strftime('%m/%d')}": {category: {"count": 0, "activities": []} for category in ["running", "cycling", "swimming", "strength"]}
            for week_start, week_end in weeks
        }

        for activity in activities:
            category = categorize_activity(activity["activityType"])
            if category:
                activity_date = datetime.strptime(activity["startTimeLocal"], "%Y-%m-%d %H:%M:%S").date()
                for week_start, week_end in weeks:
                    if week_start <= activity_date <= week_end:
                        week_label = f"{week_start.strftime('%m/%d')} - {week_end.strftime('%m/%d')}"
                        categorized_data[week_label][category]["count"] += 1
                        categorized_data[week_label][category]["activities"].append({
                            "duration": activity.get("duration", 0),
                            "distance": activity.get("distance", 0),
                            "calories": activity.get("calories", 0)
                        })
                        break

    elif granularity == "months":
        # Sort the months by month_start date
        months.sort(key=lambda x: x[0])  # Sort by the start date of the month
        categorized_data = {
            f"{month_start.strftime('%m/%y')}": {category: {"count": 0, "activities": []} for category in ["running", "cycling", "swimming", "strength"]}
            for month_start, _ in months
        }

        for activity in activities:
            category = categorize_activity(activity["activityType"])
            if category:
                activity_date = datetime.strptime(activity["startTimeLocal"], "%Y-%m-%d %H:%M:%S").date()
                for month_start, month_end in months:
                    if month_start <= activity_date <= month_end:
                        month_label = month_start.strftime('%m/%y')
                        categorized_data[month_label][category]["count"] += 1
                        categorized_data[month_label][category]["activities"].append({
                            "duration": activity.get("duration", 0),
                            "distance": activity.get("distance", 0),
                            "calories": activity.get("calories", 0)
                        })
                        break
                    
    print(categorized_data)
    return jsonify({"activities": categorized_data})




@app.route("/get_garmin_stats_options", methods=['POST'])
@jwt_required()
def get_garmin_stats_options():
    current_user_email = get_jwt_identity()
    user = mongo.db.users.find_one({"email": current_user_email}, {"password": 0})
    user_id = user.get("_id")

    # Get granularity parameter from the request
    granularity = request.get_json().get("granularity", "days").lower()
    if granularity not in ["days", "weeks", "months"]:
        return jsonify({"error": "Invalid granularity. Must be 'days', 'weeks', or 'months'"}), 400

    # Calculate the date ranges
    today = datetime.now().date()

    if granularity == "days":
        date_range = [today - timedelta(days=i) for i in range(14)]  # 14 days of data
        match_start_date = (today - timedelta(days=14)).strftime("%Y-%m-%d")
    elif granularity == "weeks":
        weeks = []
        for i in range(14):
            week_start = today - timedelta(days=today.weekday() + i * 7)
            week_end = week_start + timedelta(days=6)
            weeks.append((week_start, week_end))
        match_start_date = weeks[-1][0].strftime("%Y-%m-%d")
    elif granularity == "months":
        months = []
        for i in range(12):
            month_start = (today.replace(day=1) - timedelta(days=i * 30)).replace(day=1)
            next_month_start = (month_start + timedelta(days=31)).replace(day=1)
            months.append((month_start, next_month_start - timedelta(days=1)))
        match_start_date = months[-1][0].strftime("%Y-%m-%d")

    # Retrieve Garmin data using the Garmin Connect API
    encrypted_garmin = user.get("garmin_session_data")
    if encrypted_garmin:
        garmin = decrypt_data(encrypted_garmin)  # Decrypt session data
    else:
        return jsonify({"message": "User has no Garmin link saved"}), 202

    # Get daily stats from Garmin based on date ranges
    start_date = datetime.strptime(match_start_date, "%Y-%m-%d").date()
    end_date = today

    # Fetch data using Garmin's `get_daily_stats`
    daily_stats = garmin.get_daily_steps(start_date, end_date)

    # Prepare the response data
    categorized_data = {}

    if granularity == "days":
        # Organize data by day
        for stat in daily_stats:
            date = stat.get("calendarDate")
            activity_date = datetime.strptime(date, "%Y-%m-%d").date()
            activity_date_str = activity_date.strftime("%m/%d")
            total_steps = stat.get("totalSteps", 0) or 0  # Default to 0 if None
            total_distance = stat.get("totalDistance", 0) or 0  # Default to 0 if None

            if activity_date_str not in categorized_data:
                categorized_data[activity_date_str] = {"totalSteps": 0, "totalDistance": 0}

            # Add the steps and distance (defaulting None to 0)
            categorized_data[activity_date_str]["totalSteps"] += total_steps
            categorized_data[activity_date_str]["totalDistance"] += total_distance

    elif granularity == "weeks":
        # Organize data by week
        weeks = []
        for i in range(14):
            week_start = today - timedelta(days=today.weekday() + i * 7)
            week_end = week_start + timedelta(days=6)
            weeks.append((week_start, week_end))

        for week_start, week_end in weeks:
            week_label = f"{week_start.strftime('%m/%d')} - {week_end.strftime('%m/%d')}"
            categorized_data[week_label] = {"totalSteps": 0, "totalDistance": 0}

            for stat in daily_stats:
                date = datetime.strptime(stat.get("calendarDate"), "%Y-%m-%d").date()
                if week_start <= date <= week_end:
                    total_steps = stat.get("totalSteps", 0) or 0
                    total_distance = stat.get("totalDistance", 0) or 0
                    categorized_data[week_label]["totalSteps"] += total_steps
                    categorized_data[week_label]["totalDistance"] += total_distance

    elif granularity == "months":
        # Organize data by month
        months = []
        for i in range(12):
            month_start = (today.replace(day=1) - timedelta(days=i * 30)).replace(day=1)
            next_month_start = (month_start + timedelta(days=31)).replace(day=1)
            months.append((month_start, next_month_start - timedelta(days=1)))

        for month_start, month_end in months:
            month_label = month_start.strftime('%m/%y')
            categorized_data[month_label] = {"totalSteps": 0, "totalDistance": 0}

            for stat in daily_stats:
                date = datetime.strptime(stat.get("calendarDate"), "%Y-%m-%d").date()
                if month_start <= date <= month_end:
                    total_steps = stat.get("totalSteps", 0) or 0
                    total_distance = stat.get("totalDistance", 0) or 0
                    categorized_data[month_label]["totalSteps"] += total_steps
                    categorized_data[month_label]["totalDistance"] += total_distance

    return jsonify(categorized_data), 200



if __name__ == "__main__":
    #print("Running Flask app")
    app.run(debug=True)

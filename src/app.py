from datetime import timedelta
from flask import Flask, request, jsonify
from flask_migrate import Migrate
from models import db, Users, Pets, Veterinarians, Vaccines, Appointment, Prescriptions
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, get_jwt_identity, jwt_required
from flask_bcrypt import Bcrypt 
import datetime
from datetime import date
from operator import itemgetter

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///mibasededatos.db"
app.config["JWT_SECRET_KEY"] = "ULTRA_SECRET_PASSWORD"
app.config["SECRET_KEY"] = "SECRET_WORD"

#expires_jwt = timedelta()

db.init_app(app)
CORS(app)
migrate = Migrate(app, db)
jwt = JWTManager(app)
bcrypt = Bcrypt(app)


with app.app_context():
    db.create_all()

#GET METHOD
@app.route('/', methods=['GET'])
@jwt_required()
def home():
    users = Users.query.all()
    users = list(map(lambda user: user.serialize(), users))
    
    return jsonify({
        "data": users,
        "status": 'success'
    }),200
   
#REGISTER POST METHOD

@app.route("/register", methods=["POST"])
def register():
  get_email_from_body = request.json.get("emailAddress")
  get_rut_from_body = request.json.get("rut")
  print(get_email_from_body)
  usuario = Users()
  existing_user = Users.query.filter_by(email=get_email_from_body).first()
  if existing_user is not None:
    return jsonify({
      "msg":"User already exists"
    })
  else:
    usuario.name = request.json.get("name")
    usuario.rut = request.json.get("rut")
    usuario.email = request.json.get("emailAddress")
    usuario.address = request.json.get("address")
    password = request.json.get("password")
    #crypt password 
    passwordHash = bcrypt.generate_password_hash(password)
    usuario.password = passwordHash
    usuario.phone_number = request.json.get("phone")

    db.session.add(usuario)
    db.session.commit()

  return jsonify({
    "msg":"User created"
  }) , 201

  #return f"User created", 201

#LOGIN POST METHOD

@app.route("/login", methods=["POST"])
def login():
  login_email = request.json.get("email")
  password = request.json.get("password")
  user = Users.query.filter_by(email=login_email).first()
  

  if user is not None:
   if bcrypt.check_password_hash(user.password, password):
   ## token = create_access_token(identity = login_email, expires_delta = expires_jwt)
    expire = datetime.timedelta(days=3)
    token = create_access_token(identity = user.id, expires_delta=expire)

    role = ""
    role_auth = Veterinarians.query.filter_by(user_id = user.id).first()
    if role_auth == None:
       role = "user"
    else:
       role = "veterinarian"

    return jsonify({
      "token": token,
      "status": "success",
      "role": role,
      "user" : user.serialize(),
      "msg":"Login accepted"
    }) , 201
   else:
    return jsonify({
     "msg":"Invalid email or password"
   }), 401
  else:
    return jsonify({
     "msg":"Invalid email or password"
   }), 401
  
  

@app.route('/vet/calendar', methods=['GET'])
def getAppointmentsPreview():
    appointments = Appointment.query.all()
    appointments = list(map(lambda appointment: appointment.serialize(), appointments))
    filter_data_appointments = []
    for i in range(len(appointments)):
      temp_dict = {}
      weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
      weekdays_abbreviated = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]
      months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]

      vet_temp = Veterinarians.query.filter_by(id=appointments[i]["vet_id"]).first()
      vet = Users.query.filter_by(id=vet_temp.user_id).first()
      temp_dict["vet_id"] = vet_temp.id
      temp_dict["veterinarian"] = vet.name

      temp_dict["type_of_visit"] = appointments[i]["type_of_visit"]

      pet = Pets.query.filter_by(id=appointments[i]["pet_id"]).first()
      temp_dict["species"] = pet.species
      temp_dict["breed"] = pet.breed

      temp_dict["time"] = appointments[i]["time"]
      temp_dict["full_date"] = appointments[i]["date"]
      temp_dict["date_day"] = date.fromisoformat(appointments[i]["date"]).day
      temp_dict["date_month"] = date.fromisoformat(appointments[i]["date"]).month
      temp_dict["date_year"] = date.fromisoformat(appointments[i]["date"]).year
      temp_dict["weekday"] = weekdays[date.fromisoformat(appointments[i]["date"]).isoweekday()]
      temp_dict["weekday_abbreviated"] = weekdays_abbreviated[date.fromisoformat(appointments[i]["date"]).isoweekday()]
      temp_dict["month_name"] = months[date.fromisoformat(appointments[i]["date"]).month-1]
      temp_dict["appointment_id"] = appointments[i]["appointment_id"]

      temp_dict["pet_id"] = appointments[i]["pet_id"]
      pet = Pets.query.filter_by(id=appointments[i]["pet_id"]).first()
      temp_dict["pet_name"] = pet.name

      temp_dict["owner_id"] = appointments[i]["user_id"]
      user = Users.query.filter_by(id=appointments[i]["user_id"]).first()
      temp_dict["owner_name"] = user.name
      temp_dict["frontend_element_type"] = "card"
      
      filter_data_appointments.append(temp_dict) 

    filter_data_appointments = sorted(filter_data_appointments, key=itemgetter("full_date"))

    filter_data_vets = []
    vets_filter_query = Veterinarians.query.all()
    vets_filter_query = list(map(lambda vet: vet.serialize(), vets_filter_query))
    for i in range(len(vets_filter_query)):
       temp_dict = {}
       temp_dict["vet_id"] = vets_filter_query[i]["vet_id"]
       user_temp = Users.query.filter_by(id = vets_filter_query[i]["user_id"]).first()
       temp_dict["vet_name"] = user_temp.name
       filter_data_vets.append(temp_dict)

    filter_data_pets = []
    pets_filter_query = Pets.query.all()
    pets_filter_query = list(map(lambda pet: pet.serialize(), pets_filter_query))
    for i in range(len(pets_filter_query)):
       temp_dict = {}
       temp_dict["pet_id"] = pets_filter_query[i]["pet_id"]
       temp_dict["pet_name"] = pets_filter_query[i]["name"]
       filter_data_pets.append(temp_dict)

    filter_data_owners = []
    owners_filter_query = Users.query.all()
    owners_filter_query = list(map(lambda owner: owner.serialize(), owners_filter_query))
    for i in range(len(owners_filter_query)):
       temp_dict = {}
       temp_dict["owner_id"] = owners_filter_query[i]["user_id"]
       temp_dict["owner_name"] = owners_filter_query[i]["name"]
       filter_data_owners.append(temp_dict)

    return jsonify({
        "appointments_data": filter_data_appointments,
        "filter_data_vets": filter_data_vets,
        "filter_data_pets": filter_data_pets,
        "filter_data_owners": filter_data_owners,
        "status": 'success'
    }),200


@app.route('/vet/clinical-record-preview', methods=['GET'])
def getClinicalRecordsPreview():
   pet = Pets.query.order_by(Pets.id.desc()).first()
   owner = Users.query.filter_by(id=pet.user_id).first()
   pet_sterilized = 0
   if (pet.sterilized):
      pet_sterilized = "Sterilized"
   else:
      pet_sterilized = "Not sterilized"
  
   values = {
    "name": pet.name,
    "species": pet.species,
    "date_of_birth": pet.date_of_birth,
    "age": pet.age,
    "color": pet.color,
    "owner": owner.name,
    "sterilized": pet_sterilized,
    "weight": str(pet.weight),
    "breed": pet.breed,
    "allergies": pet.allergies,
    "image": pet.image
   }

   return jsonify({
        "data": values,
        "status": 'success'
    }),200

@app.route('/vet/clinical-records', methods=['GET'])
def getClinicalRecords():
    pets = Pets.query.all()
    pets = list(map(lambda pet: pet.serialize(), pets))
    keys = ["pet_id", "image", "name", "species", "age", "color", "owner"]
    values = []
    for i in range(len(pets)):
      temp_dict = {}
      temp_values = []

      temp_values.append(pets[i]["pet_id"])
      temp_values.append(pets[i]["image"])
      temp_values.append(pets[i]["name"])
      temp_values.append(pets[i]["species"])
      temp_values.append(pets[i]["age"])
      temp_values.append(pets[i]["color"])

      owner = Users.query.filter_by(id=pets[i]["user_id"]).first()
      temp_values.append(owner.name)
      
      for i in range(len(temp_values)):
         temp_dict[keys[i]] = temp_values[i]
         
      values.append(temp_dict)

    return jsonify({
        "data": values,
        "status": 'success'
    }),200


#CLINICAL RECORDS SPECIFIC

@app.route('/vet/clinical-records-specific/<int:id>', methods = ["GET"])
def getClinicalRecordsSpecific(id):
  pet_specific = Pets.query.filter_by(id=id).first()
  if pet_specific is not None:
     return jsonify(pet_specific.serialize()),200
  else:
     return jsonify({"error":"pet no found"}),404



@app.route("/vet/calendar/create-appointment", methods=["GET", "POST"])
def createAppointment():

  if request.method == "GET":
     veterinarians_query = Veterinarians.query.all()
     veterinarians_query = list(map(lambda veterinarian: veterinarian.serialize(), veterinarians_query))
     veterinarians = []
     for i in range(len(veterinarians_query)):
        temp_dict = {}
        temp_dict["vet_id"] = veterinarians_query[i]["vet_id"]

        vet_name = Users.query.filter_by(id = veterinarians_query[i]["user_id"]).first()
        temp_dict["name"] = vet_name.name

        veterinarians.append(temp_dict)
      
     print("vet: ", veterinarians)
     pets_query = Pets.query.all()
     pets_query = list(map(lambda pet: pet.serialize(), pets_query))
     pets = []
     for i in range(len(pets_query)):
        temp_dict = {}
        temp_dict["name"] = pets_query[i]["name"]
        temp_dict["pet_id"] = pets_query[i]["pet_id"]
        
        pets.append(temp_dict)

     return jsonify({
        "vet_info": veterinarians,
        "pet_info": pets}
      ), 200

  elif request.method == "POST":
    appointment = Appointment()
    
    day = request.json["appointmentData"].get("day")
    month = request.json["appointmentData"].get("month")
    year = request.json["appointmentData"].get("year")
    date_ISO = str(year) + "-" + month + "-" + day
    appointment.date = date_ISO
    appointment.time = request.json["appointmentData"].get("time")
    appointment.vet_id = request.json["appointmentData"].get("vetID")
    pet_temp = Pets.query.filter_by(id = request.json["appointmentData"].get("petID")).first()
    appointment.user_id = pet_temp.user_id
    appointment.pet_id = request.json["appointmentData"].get("petID")
    appointment.comments = request.json["appointmentData"].get("comments")
    appointment.type_of_visit = request.json["appointmentData"].get("typeOfVisit")
    appointment.payment_status = 0

    db.session.add(appointment)
    db.session.commit()

    return jsonify({
      "msg": "Appointment created",
      "status": "ok"}
    ), 201


@app.route('/user', methods=['GET'])
@jwt_required()
def getUserFrontPageData():
   
   current_user_id = get_jwt_identity()
   user = Users.query.filter_by(id=current_user_id).first()
   pets_query = Pets.query.filter_by(user_id = user.id)
   pets_query = list(map(lambda pet: pet.serialize(), pets_query))
   appointments_query = Appointment.query.filter_by(user_id = user.id)
   appointments_query = list(map(lambda appointment: appointment.serialize(), appointments_query))
   
   pets = []
   for i in range(len(pets_query)):
      temp_dict = {}

      temp_dict["name"] = pets_query[i]["name"]
      temp_dict["species"] = pets_query[i]["species"]
      temp_dict["age"] = pets_query[i]["age"]
      temp_dict["pet_id"] = pets_query[i]["pet_id"]
      temp_dict["image"] = pets_query[i]["image"]

      pets.append(temp_dict)
      
   user_data = {}
   user_data["id"] = user.id
   user_data["name"] = user.name  

   appointments = []
   for i in range(len(appointments_query)):
      temp_dict = {}

      temp_dict["date"] = appointments_query[i]["date"] 
      temp_dict["time"] = appointments_query[i]["time"]

      temp_vet = Veterinarians.query.filter_by(id=appointments_query[i]["vet_id"]).first()
      temp_user = Users.query.filter_by(id=temp_vet.user_id).first()
      temp_dict["veterinarian"] = temp_user.name

      temp_dict["type_of_visit"] = appointments_query[i]["type_of_visit"]

      temp_pet = Pets.query.filter_by(id = appointments_query[i]["pet_id"]).first()
      temp_dict["species"] = temp_pet.species
      temp_dict["pet_name"] = temp_pet.name

      appointments.append(temp_dict)


   return jsonify({
      "pets_data": pets,
      "user_data": user_data,
      "appointments_data": appointments
   }), 200

#USER PET LISTED


@app.route('/user/pets', methods = ["GET"])
@jwt_required()
def getUserPetListed():
  user_id = get_jwt_identity()
  userpet_listed = Pets.query.filter_by(user_id=user_id).all()
  userpet_listed = list(map(lambda pet: pet.serialize(), userpet_listed))
  

  if userpet_listed is not None:
     return jsonify(userpet_listed),200
  else:
     return jsonify({"error":"pet no found"}),404


#TEST ENDPOINTS BELOW

@app.route('/postman/calendar', methods=['GET'])
def getAppointmentsPostman():
    appointments = Appointment.query.all()
    appointments = list(map(lambda appointment: appointment.serialize(), appointments))
    pets = Pets.query.all()
    pets = list(map(lambda pet: pet.serialize(), pets))

    
    return jsonify({
        "data": pets,
        "status": 'success'
    }),200

@app.route('/postman/update-appointment', methods=['PUT'])
def updateAppointmentPostman():
   appointment = Appointment.query.get(request.json.get("app_id"))
   appointment.date = request.json.get("date")
   db.session.commit()
   return jsonify("Appointment updated"), 200

@app.route("/postman/create-vet", methods=["POST"])
def createVetPostman():
  veterinarian = Veterinarians()

  veterinarian.user_id = request.json.get("user_id")
  veterinarian.specialty = request.json.get("specialty")
  veterinarian.position = request.json.get("position")

  db.session.add(veterinarian)
  db.session.commit()

  return f"Veterinarian created", 201

@app.route('/postman/consult-veterinarians', methods=['GET'])
def getVeterinariansPostman():
    veterinarians = Veterinarians.query.all()
    veterinarians = list(map(lambda veterinarian: veterinarian.serialize(), veterinarians))
    
    return jsonify({
        "data": veterinarians,
        "status": 'success'
    }),200

@app.route("/postman/create-pet", methods=["POST"])
def createPetPostman():
  pet = Pets()

  pet.user_id = request.json.get("user_id")
  pet.image = request.json.get("image")
  pet.name = request.json.get("name")
  pet.species = request.json.get("species")
  pet.date_of_birth = request.json.get("date_of_birth")
  pet.age = request.json.get("age")
  pet.color = request.json.get("color")
  pet.sterilized = request.json.get("sterilized")
  pet.weight = request.json.get("weight") #IMPORTANT!! fix weigth spelling on database (also change usuario model to user)
  pet.height = request.json.get("height")
  pet.breed = request.json.get("breed")
  pet.allergies = request.json.get("allergies")
  pet.aditional_info = request.json.get("aditional_info")
  pet.doctor_notes = request.json.get("doctor_notes")
  pet.status = request.json.get("status")

  db.session.add(pet)
  db.session.commit()

  return f"Pet created", 201

@app.route('/postman/consult-pets', methods=['GET'])
def getPetsPostman():
    pets = Pets.query.all()
    pets = list(map(lambda pet: pet.serialize(), pets))
    
    return jsonify({
        "data": pets,
        "status": 'success'
    }),200


# this only runs if `$ python src/app.py` is executed
if __name__ == "__main__":
  app.run(host="localhost", port=5007, debug=True)


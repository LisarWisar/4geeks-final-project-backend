from flask import Flask, request, jsonify
from flask_migrate import Migrate
from models import db, Users, Pets, Veterinarians, Vaccines, Appointment, Prescriptions
from flask_cors import CORS
import datetime
from datetime import date

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///mibasededatos.db"
CORS(app)

db.init_app(app)
migrate = Migrate(app, db)

with app.app_context():
    db.create_all()

#GET METHOD
@app.route('/', methods=['GET'])
def home():
    users = Users.query.all()
    users = list(map(lambda user: user.serialize_1(), users))
    
    return jsonify({
        "data": users,
        "status": 'success'
    }),200
   
#REGISTER POST METHOD

@app.route("/register", methods=["POST"])
def register():
  get_email_from_body = request.json.get("email")
  get_rut_from_body = request.json.get("rut")
  usuario = Users()
  existing_user = Users.query.filter_by(email=get_email_from_body, rut=get_rut_from_body).first()
  if existing_user is not None:
    return "User already exists"
  else:
    usuario.name = request.json.get("name")
    usuario.rut = request.json.get("rut")
    usuario.email = request.json.get("email")
    usuario.address = request.json.get("address")
    usuario.password = request.json.get("password")
    usuario.phone_number = request.json.get("phone_number")

    db.session.add(usuario)
    db.session.commit()

  return f"User created", 201

  #return f"User created", 201

#LOGIN POST METHOD

@app.route("/login", methods=["POST"])
def login():
  login_email = request.json.get("email")
  login_password = request.json.get("password")
  user = Users.query.filter_by(email=login_email).first()
  if user is not None:
    if user.password == login_password:
      return jsonify("Login accepted"), 200
    else:
      return jsonify("Invalid email or password"), 401
  else:
    return jsonify("Invalid email or password"), 401
  
@app.route("/vet/calendar/create-appointment", methods=["POST"])
def createAppointment():
  appointment = Appointment()

  appointment.date = request.json.get("date")
  appointment.time = request.json.get("time")
  appointment.vet_id = request.json.get("vet_id")
  appointment.user_id = request.json.get("user_id")
  appointment.pet_id = request.json.get("pet_id")
  appointment.comments = request.json.get("comments")
  appointment.type_of_visit = request.json.get("type_of_visit")
  appointment.payment_status = request.json.get("payment_status")

  db.session.add(appointment)
  db.session.commit()

  return f"Appointment created", 201

@app.route('/vet/calendar', methods=['GET'])
def getAppointmentsPreview():
    appointments = Appointment.query.all()
    appointments = list(map(lambda appointment: appointment.serialize_5(), appointments))
    keys = ["veterinarian", "type_of_visit", "species", "breed", "time", "day"]
    values = []
    for i in range(len(appointments)):
      temp_dict = {}
      temp_values = []

      vet_temp = Veterinarians.query.filter_by(id=appointments[i]["vet_id"]).first()
      vet = Users.query.filter_by(id=vet_temp.user_id).first()
      temp_values.append(vet.name)

      temp_values.append(appointments[i]["type_of_visit"])

      pet = Pets.query.filter_by(id=appointments[i]["pet_id"]).first()
      temp_values.append(pet.species)
      temp_values.append(pet.breed)

      temp_values.append(appointments[i]["time"]) 

      temp_values.append(appointments[i]["date"])
      
      for i in range(len(temp_values)):
         temp_dict[keys[i]] = temp_values[i]
         
      values.append(temp_dict)

    return jsonify({
        "data": values,
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
    pets = list(map(lambda pet: pet.serialize_2(), pets))
    keys = ["image", "name", "species", "age", "color", "owner"]
    values = []
    for i in range(len(pets)):
      temp_dict = {}
      temp_values = []

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

   

#TEST ENDPOINTS BELOW



@app.route('/postman/calendar', methods=['GET'])
def getAppointmentsPostman():
    appointments = Appointment.query.all()
    appointments = list(map(lambda appointment: appointment.serialize_5(), appointments))
    pets = Pets.query.all()
    pets = list(map(lambda pet: pet.serialize_2(), pets))

    
    return jsonify({
        "data": pets,
        "status": 'success'
    }),200

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
    veterinarians = list(map(lambda veterinarian: veterinarian.serialize_3(), veterinarians))
    
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
    pets = list(map(lambda pet: pet.serialize_2(), pets))
    
    return jsonify({
        "data": pets,
        "status": 'success'
    }),200


# this only runs if `$ python src/app.py` is executed
if __name__ == "__main__":
  app.run(host="localhost", port=5007, debug=True)


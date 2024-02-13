from flask import Flask, request, jsonify
from flask_migrate import Migrate
from models import db, Usuario, Pets, Veterinarians, Vaccines, Appointment, Prescriptions
from flask_cors import CORS, cross_origin

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
    users = Usuario.query.all()
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
  usuario = Usuario()
  existing_user = Usuario.query.filter_by(email=get_email_from_body, rut=get_rut_from_body).first()
  if existing_user is not None:
    return "User already exists"
  else:
    usuario.name = request.json.get("name")
    usuario.rut = request.json.get("rut")
    usuario.email = request.json.get("email")
    usuario.address = request.json.get("address")
    usuario.password = request.json.get("password")
    usuario.phone_number = request.json.get("phone_number")



  return f"User created", 201

#LOGIN POST METHOD

@app.route("/login", methods=["POST"])
def login():
  login_email = request.json.get("email")
  login_password = request.json.get("password")
  user = Usuario.query.filter_by(email=login_email).first()
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
def getAppointments():
    appointments = Appointment.query.all()
    appointments = list(map(lambda appointment: appointment.serialize_5(), appointments))
    #pets = Pets.query_all()
    #veterinarians = Veterinarians.query.all()
    #users = Usuario.query.all()

    return jsonify({
        "data": appointments,
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

#@app.route("/vet/calendar", methods=["GET"])
#def vetFrontView():
#  #add verification
#  if request.method =="GET":
#    rows = Appointment.query.all()
#    column_keys = Appointment.__table__.columns.keys()
#    rows_dic_temp = {}
#    rows_dic = []
#    for row in rows:
#      for col in column_keys:
#          rows_dic_temp[col] = getattr(row, col)
#      rows_dic.append(rows_dic_temp)
#      rows_dic_temp= {}
#    appointments = []
#
#    for row in range(len(rows_dic)):
#      new_appointment = {
#        "date": rows_dic[row]["date"],
#        "time": rows_dic[row]["time"],
#        #"vet_name": db.session.query(Usuario.name).filter_by(id=db.session.query(Veterinarians.user_id).filter_by(id=rows_dic[row]["vet_id"]).first()).first(),
#        #"user_name": Usuario.query.filter_by(id=1).first()["name"],
#        "comments": rows_dic[row]["comments"],
#        "type_of_visit": rows_dic[row]["type_of_visit"],
#        "payment_status": rows_dic[row]["payment_status"]
#      }
#      appointments.append(new_appointment)
#    numero_test = 1
#    test = Usuario.query.filter_by(id=numero_test).first()
#    print("test :", test)
#  return jsonify(appointments)

@app.route("/postman/create-vet", methods=["POST"])
def createVetPostman():
  veterinarian = Veterinarians()

  veterinarian.user_id = request.json.get("user_id")
  veterinarian.specialty = request.json.get("specialty")
  veterinarian.position = request.json.get("position")

  db.session.add(veterinarian)
  db.session.commit()

  return f"Veterinarian created", 201

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
  pet.weigth = request.json.get("weigth") #IMPORTANT!! fix weigth spelling on database (also change usuario model to user)
  pet.height = request.json.get("height")
  pet.breed = request.json.get("breed")
  pet.allergies = request.json.get("allergies")
  pet.aditional_info = request.json.get("aditional_info")
  pet.doctor_notes = request.json.get("doctor_notes")
  pet.status = request.json.get("status")

  db.session.add(pet)
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


# this only runs if `$ python src/app.py` is executed
if __name__ == "__main__":
  app.run(host="localhost", port=5007, debug=True)


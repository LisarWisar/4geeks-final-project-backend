from datetime import timedelta
from flask import Flask, request, jsonify
from flask_migrate import Migrate
from models import db, Usuario, Pets, Veterinarians, Vaccines, Appointment, Prescriptions
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, get_jwt_identity, jwt_required
from flask_bcrypt import Bcrypt 


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
    users = Usuario.query.all()
    users = list(map(lambda user: user.serialize_1(), users))
    
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
  usuario = Usuario()
  existing_user = Usuario.query.filter_by(email=get_email_from_body).first()
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

#LOGIN POST METHOD

@app.route("/login", methods=["POST"])
def login():
  login_email = request.json.get("email")
  password = request.json.get("password")
  user = Usuario.query.filter_by(email=login_email).first()
  if user is not None:
   if bcrypt.check_password_hash(user.password, password):
   ## token = create_access_token(identity = login_email, expires_delta = expires_jwt)
    token = create_access_token(identity = login_email)
   
    return jsonify({
      "token": token,
      "status": "success",
      "user" : user.serialize_1(),
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
  
  
# this only runs if `$ python src/app.py` is executed
if __name__ == "__main__":
  app.run(host="localhost", port=5007, debug=True)

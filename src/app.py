from flask import Flask, request, jsonify
from flask_migrate import Migrate
from models import db, Usuario, Pets, Veterinarians, Vaccines, Appointment, Prescriptions
from flask_cors import CORS


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///mibasededatos.db"

db.init_app(app)
migrate = Migrate(app, db)
CORS(app)

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

    db.session.add(usuario)
    db.session.commit()

  return f"User created", 201

#LOGIN POST METHOD

@app.route("/login", methods=["POST"])
def login():
  login_email = request.json.get("email")
  login_password = request.json.get("password")
  user = Usuario.query.filter_by(email=login_email).first()
  if user is not None:
    if user.password == login_password:
      return f"Login accepted", 201
    else:
      return f"Invalid email or password", 401
  else:
    return f"Invalid email or password", 401


# this only runs if `$ python src/app.py` is executed
if __name__ == "__main__":
  app.run(host="localhost", port=5007, debug=True)

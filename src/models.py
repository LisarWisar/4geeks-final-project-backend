from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Usuario(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(50), nullable=False)
    rut = db.Column(db.String(50), nullable=False)
    address = db.Column(db.String(50), nullable=False)
    phone_number = db.Column(db.String(50), nullable=False)

    def serialize_1(self):
        return {
        'user_id': self.id,
        'name': self.name,
        'email': self.email,
        'rut': self.rut,
        'address': self.address
        }

    
class Pets(db.Model):
    __tablename__ = 'pets'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    image = db.Column(db.String(200))
    name = db.Column(db.String(250), nullable=False)
    species = db.Column(db.String(250), unique=False)
    date_of_birth = db.Column(db.String(200), nullable=False)
    age = db.Column(db.Integer)
    color = db.Column(db.String(50))
    sterilized = db.Column(db.Boolean)
    weigth = db.Column(db.Float)
    height = db.Column(db.Float)
    breed = db.Column(db.String(200))
    allergies = db.Column(db.String(200))
    aditional_info = db.Column(db.String(200))
    doctor_notes = db.Column(db.String(200))
    status = db.Column(db.Boolean)

    def serialize_2(self):
        return {
        'pet_id':self.id,
        'user_id':self.user_id,
        'image':self.image,
        'name':self.name,
        'species':self.species,
        'date_of_birth' : self.date_of_birth,
        'age':self.age,
        'color':self.color,
        'sterilized':self.sterilized,
        'weigth':self.weigth,
        'height':self.height,
        'breed':self.breed,
        'allergies':self.allergies,
        'aditional_info':self.aditional_info,
        'doctor_notes':self.doctor_notes,
        'status':self.status
    }
    
class Veterinarians(db.Model):
    __tablename__ = 'veterinarians'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    specialty = db.Column(db.Integer, nullable=False)
    position = db.Column(db.Integer, unique=False)

    def serialize_3(self):
        return {
        'vet_id':self.id,
        'user_id':self.user_id,
        'specialty':self.specialty,
        'position':self.position
        }
    
class Vaccines(db.Model):
    __tablename__ = 'vaccines'
    id = db.Column(db.Integer, primary_key=True)
    pet_id = db.Column(db.Integer, db.ForeignKey("pets.id"))
    vet_id = db.Column(db.Integer, db.ForeignKey("veterinarians.id"))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    appointment_id = db.Column(db.Integer, db.ForeignKey("appointment.id"))
    dose = db.Column(db.Integer)
    type_of_vaccine = db.Column(db.String(200))
    lote = db.Column(db.String(200))

    def serialize_4(self):
        return {
        'vac_id':self.id,
        'pet_id':self.pet_id,
        'vet_id':self.vet_id,
        'user_id':self.user_id,
        'appointment':self.appointment_id,
        'dose' : self.dose,
        'type_of_vaccine':self.type_of_vaccine,
        'lote':self.lote
        }
    
class Appointment(db.Model):
    __tablename__ = 'appointment'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(200))
    time = db.Column(db.String(200))
    vet_id = db.Column(db.Integer, db.ForeignKey("veterinarians.id"))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    pet_id = db.Column(db.Integer, db.ForeignKey("pets.id"))
    comments = db.Column(db.String(200))
    type_of_visit = db.Column(db.String(200))
    payment_status = db.Column(db.Integer, nullable=False)


    def serialize_5(self):
        return {
        'appointment_id':self.id,
        'date':self.date,
        'time':self.time,
        'vet_id':self.vet_id,
        'user_id':self.user_id,
        'pet_id' : self.pet_id,
        'comments':self.comments,
        'type_of_visit':self.type_of_visit,
        'payments_status':self.payment_status
        }

class Prescriptions(db.Model):
    __tablename__ = 'prescriptions'
    id = db.Column(db.Integer, primary_key=True)
    appointment_id = db.Column(db.Integer, db.ForeignKey("appointment.id"))
    image = db.Column(db.String(200))
    content = db.Column(db.String(200))

    def serialize_6(self):
        return {
        'prescription_id':self.id,
        'appointment_id':self.appointment_id,
        'image':self.image,
        'content':self.content
        }


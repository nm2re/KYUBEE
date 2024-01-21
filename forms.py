

import uuid
db = SQLAlchemy()

class Test(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=str(uuid.uuid4()), unique=True)
    
    
    
new_record = Test()  
db.session.add(new_record)

inserted_uuid = new_record.id
print("Inserted UUID:", inserted_uuid)
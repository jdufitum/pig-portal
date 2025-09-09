from datetime import date
from sqlmodel import Session
from app.db.session import engine, init_db
from app.models.pig import Pig, Sex, Litter, WeightRecord

def run():
	init_db()
	with Session(engine) as session:
		litter = Litter(code="LIT-001", farrowing_date=date(2024,1,1))
		session.add(litter)
		session.flush()
		p1 = Pig(ear_tag="E100", sex=Sex.MALE, breed="Duroc", birth_date=date(2024,1,1), litter_id=litter.id)
		p2 = Pig(ear_tag="E101", sex=Sex.FEMALE, breed="Landrace", birth_date=date(2024,1,1), litter_id=litter.id)
		session.add(p1)
		session.add(p2)
		session.flush()
		session.add(WeightRecord(pig_id=p1.id, recorded_on=date(2024,2,1), weight_kg=25))
		session.add(WeightRecord(pig_id=p2.id, recorded_on=date(2024,2,1), weight_kg=23))
		session.commit()
		print("Seeded demo data")

if __name__ == "__main__":
	run()
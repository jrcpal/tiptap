from models import db, connect_db, User, SavedBeer, RatedBeer
from app import app 

db.drop_all()
db.create_all()

users = [
    User(username="Bot", password="$2b$12$n8N0Qs5KOL2FDtCdRnk6JO.4lapepYdA3FQsDTMW.WQerXVDUe/X6", first_name="Robo")
]

db.session.add_all(users)
db.session.commit()


beers = [
    SavedBeer(user_id=1, beer_id="zTTWa2", name="Robo Beer", description="beer for robots", ibu=69, abv=5, style="Probot Lager", style_description="Won't gunk up the cogs.")
]

db.session.add_all(beers)
db.session.commit()

ratings = [
    RatedBeer(user_id=1, beer_id="c4f2KE", name="Her second beer", description="Robo loves beer", ibu=0, abv=666, style="Chocolate Stout", style_description="Chocolate is delicious and so are stouts", rating=5, notes="Beep Boop Love Beer" )
]

db.session.add_all(ratings)
db.session.commit()
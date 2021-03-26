from flask import Flask, render_template, redirect, session, flash, request, jsonify
import requests, json, random, os
#from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User, SavedBeer, RatedBeer
from survey import beer_survey as survey
from forms import RegisterForm, LoginForm, DeleteForm
from sqlalchemy.exc import IntegrityError



app = Flask(__name__)


app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get('DATABASE_URL', "postgres:///tiptapbeer")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "needtochangethis123!"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False


connect_db(app)
db.create_all()


CURR_USER_KEY = "curr_user"
BASE_URI = "https://sandbox-api.brewerydb.com/v2"
API_KEY = "key=00e5f08fc31d4f272660c804487c1b7c"
RESPONSES_KEY = "responses"

failsafe_beer = {
"id": "zTTWa2",
"name": "Dat Basic Beer",
"description": "This isn't a real beer. This is the beer you get because you played with the quiz and picked something like oh I want a fruity stout with a ton of IBU. Very funny.",
"abv": "20.5", "ibu": "1000",
"style": {
"id": 164, "name": "Hybrid/Weird",
"description": "Now and then, a mean-spirited bill falls in love with the funny Hops Alligator Ale. An Octoberfest defined by the Strohs finds much coolness with a Budweiser Select. Most people believe that a St. Pauli Girl has a change of heart about a fried Keystone light, but they need to remember how secretly another Imperial Stout inside the Brewers Reserve procrastinates. The shot near a steam engine can be kind to a financial Fosters. A miller is pissed.."
}
}



@app.errorhandler(404)
def page_not_found(e):
    """Show 404 NOT FOUND page."""
    return render_template('404.html'), 404


@app.route('/')
def home_page():

    if "username" in session:
       username = session['username']
    
       return render_template('index.html', survey=survey, username=username)

    return render_template('index.html', survey=survey)

@app.route('/glossary')
def show_glossary():

    if "username" in session:
        username = session['username']
        return render_template('glossary.html', username=username)
    
    else:
        return render_template('glossary.html')


###### LOGIN/REGISTER/LOGOUT ######

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Register a user: produce form and handle form submission."""

    if "username" in session:
        return redirect(f"/users/{session['username']}")

    form = RegisterForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        first_name = form.first_name.data

        user = User.register(username, password, first_name)

        db.session.commit()
        session['username'] = user.username

        # if survey results has been stored, commit to database once user has registered
        if "result" in session:
            data = session["result"]
            # avoid blank beer description data from session data   
            if "description" not in data:
                data["description"] = "N/A"
                
            new_saved_beer = SavedBeer(user_id=user.id, beer_id=data["id"], name=data["name"], description=data["description"], ibu=data["ibu"], abv=data["abv"], style=data["style"]["name"], style_description=data["style"]["description"])
            db.session.add(new_saved_beer)
            db.session.commit()
            return redirect(f"/users/{user.username}")

        return redirect(f"/users/{user.username}")

    else:
        return render_template("users/register.html", form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Produce login form or handle login."""

    if "username" in session:
        return redirect(f"/users/{session['username']}")

    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = User.authenticate(username, password) 

        # <User> or False
        if user:
            session['username'] = user.username

            # if survey result has been stored, commit to database once user has logged in
            if "result" in session:
                data = session["result"]
                
                if "description" not in data:
                    data["description"] = "N/A"
                
                new_saved_beer = SavedBeer(user_id=user.id, beer_id=data["id"], name=data["name"], description=data["description"], ibu=data["ibu"], abv=data["abv"], style=data["style"]["name"], style_description=data["style"]["description"] )
                db.session.add(new_saved_beer)
                db.session.commit()
                return redirect(f"/users/{user.username}")

            else:
                return redirect(f"/users/{user.username}")

        else:
            form.username.errors = ["Invalid username/password."]
            return render_template("users/login.html", form=form)

    return render_template("users/login.html", form=form)

@app.route("/logout")
def logout():
    """Logout route."""

    session.pop("username")
    return redirect("/")


@app.route("/users/<username>")
def show_user(username):
    """Example page for logged-in-users."""

    if "username" not in session:
        flash("Please login first!", "danger")
        return redirect('/')
    else:
        username = session["username"]
        user = User.query.filter_by(username=username).first()
        return render_template("users/show.html", user=user)

  


###### SURVEY #####

@app.route("/begin", methods=["POST"])
def start_survey():
    """Clear the session of responses."""

    session[RESPONSES_KEY] = []

    return redirect("/questions/0")


@app.route("/answer", methods=["POST"])
def handle_question():
    """Save response and redirect to next question."""

    # get the response choice
    choice = request.form['answer']

    # add this response to the session
    responses = session[RESPONSES_KEY]
    responses.append(choice)
    session[RESPONSES_KEY] = responses

    if (len(responses) == len(survey.questions)):
        # They've answered all the questions! Thank them.
        return redirect("/result")

    else:
        return redirect(f"/questions/{len(responses)}")


@app.route("/questions/<int:qid>")
def show_question(qid):

    """Display current question."""
    responses = session.get(RESPONSES_KEY)

    if (responses is None):
        # trying to access question page too soon
        return redirect("/")

    if (len(responses) == len(survey.questions)):
        # They've answered all the questions! Thank them.
        return redirect("/result")

    if (len(responses) != qid):
        # Trying to access questions out of order.
        flash(f"Invalid question id: {qid}.")
        return redirect(f"/questions/{len(responses)}")

    question = survey.questions[qid]

    if "username" in session:
        username = session['username']
        return render_template(
        "question.html", question_num=qid, question=question, username=username)

    else:
        return render_template(
        "question.html", question_num=qid, question=question)


@app.route("/result")
def show_result():
    """Survey complete. Show result page."""

    if "username" in session:
        username = session['username']
        #user = User.query.filter_by(username=username).first()

    responses = session.get(RESPONSES_KEY)

    # HERE IT IS, the API request
    resp = requests.get(f"{BASE_URI}/search?q={responses[0]}&{responses[1]}&{API_KEY}")
    beer = resp.json()
    beer_string = json.dumps(beer)
    beer_data = json.loads(beer_string)

    # filter out beers that don't contain IBU information
    beer_results = []
    for beer in beer_data["data"]:
        if "ibu" in beer:
            beer_results.append(beer)
    
    #Filter beer results depending on level of IBU
    if responses[2] == "No bitter taste":
        beer_results = [beer for beer in beer_results if float(beer["ibu"]) < 26]
       
    if responses[2] == "Mild or noticeable bitterness":
        beer_results = [beer for beer in beer_results if float(beer["ibu"]) > 25 and float(beer["ibu"]) < 75]  
       
    if responses[2] == "Strong bitterness":
        beer_results = [beer for beer in beer_results if float(beer["ibu"]) > 75]
        
    #select one random beer from filtered results
    if len(beer_results) > 0:
        random_filtered_beer = random.choice(beer_results)
    else: 
        random_filtered_beer = failsafe_beer

    #return beers that match the same category as the selected beer 
    matching_beers = [beer for beer in beer_results if beer["style"]["id"] == random_filtered_beer["style"]["id"] and beer["name"] != random_filtered_beer["name"]]


    # save the beer to session if user not logged in/registered
    if "username" not in session:
        session["result"] = random_filtered_beer
        
        return render_template("result.html", beer=random_filtered_beer, matching_beers=matching_beers, responses=responses )
    
    else:
        return render_template("result.html", beer=random_filtered_beer, matching_beers=matching_beers, responses=responses, username=username )



###### SAVE / RATE BEER  ######

@app.route("/save-beer", methods=['GET','POST'])
def save_beer():
    """Store beer result in database for user's saved beer list"""

    if "username" in session:
        username = session['username']
        user = User.query.filter_by(username=username).first()
    
        userId = user.id
        beer_id = request.form.get("beer_id")
        name = request.form.get("name")
        description = request.form.get("description")
        ibu = request.form.get("ibu") or "N/A"
        abv = request.form.get("abv")
        style = request.form.get("style")
        style_description = request.form.get("style_description")

        new_saved_beer = SavedBeer(user_id=userId, beer_id=beer_id, name=name, description=description, ibu=ibu, abv=abv, style=style, style_description=style_description )
        db.session.add(new_saved_beer)
        db.session.commit()
        flash('This beer has been saved!', 'success')

        return redirect(f"/users/{username}")
    
    else:
        return redirect("/login")



@app.route("/rate-beer", methods=['GET','POST'])
def rate_beer():

    #Remove saved beer from saved beer db and add beer information to rated beer db

    if "username" in session:
        username = session['username']
        user = User.query.filter_by(username=username).first()
    
    beer_id = request.form["data"]
    rating = request.form["rating"]
    notes = request.form["notes"]

    beer = SavedBeer.query.filter_by(beer_id=beer_id).first()

    if beer:
        userId = user.id
        beer_id = beer.beer_id
        name = beer.name
        description = beer.description
        ibu = beer.ibu
        abv = beer.abv
        style = beer.style
        style_description = beer.style_description
    
        new_rated_beer = RatedBeer(user_id=userId, beer_id=beer_id, name=name, description=description, ibu=ibu, abv=abv, style=style, style_description=style_description, rating=rating, notes=notes )
        db.session.add(new_rated_beer)
        db.session.commit()

        return redirect(f"/beer/{beer.id}")

    else:
        # update already rated beer information in ratings db 
        ratedBeer = RatedBeer.query.filter_by(beer_id=beer_id).first()
        ratedBeer.rating = rating
        ratedBeer.notes = notes 
        db.session.commit()
        return redirect(f"/users/{username}")


@app.route('/beer/<int:id>', methods=["GET", "DELETE"])
def remove_saved_beer(id):
    """Delete beer from saved beer list if it's been rated"""

    if "username" in session:
        username = session['username']

    beer = SavedBeer.query.get_or_404(id)
    if beer:
        db.session.delete(beer)
        db.session.commit()
        return redirect(f"/users/{username}")

    else:
        return redirect(f"/users/{username}")




@app.route('/beer/<int:id>/delete', methods=["GET", "DELETE"])
def delete_saved_beer(id):
    """Delete beer from saved beer list if user clicks delete button"""

    if "username" in session:
        username = session['username']

    beer = SavedBeer.query.get_or_404(id)
    db.session.delete(beer)
    db.session.commit()
    return redirect(f"/users/{username}")



@app.route('/rating/<int:id>/delete', methods=["GET", "DELETE"])
def delete_rated_beer(id):
    """Delete rating from ratings list if user clicks delete button"""

    if "username" in session:
        username = session['username']

    rated_beer = RatedBeer.query.get_or_404(id)
    db.session.delete(rated_beer)
    db.session.commit()
    return redirect(f"/users/{username}")
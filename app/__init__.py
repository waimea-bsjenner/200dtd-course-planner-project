#===========================================================
# YOUR PROJECT TITLE HERE
# YOUR NAME HERE
#-----------------------------------------------------------
# BRIEF DESCRIPTION OF YOUR PROJECT HERE
#===========================================================

from flask import Flask, render_template, request, flash, redirect
import html

from app.helpers.session import init_session
from app.helpers.db      import connect_db
from app.helpers.errors  import init_error, not_found_error
from app.helpers.logging import init_logging
from app.helpers.time    import init_datetime, utc_timestamp, utc_timestamp_now


# Create the app
app = Flask(__name__)

# Configure app
init_session(app)   # Setup a session for messages, etc.
init_logging(app)   # Log requests
init_error(app)     # Handle errors and exceptions
init_datetime(app)  # Handle UTC dates in timestamps


#-----------------------------------------------------------
# Home page route
#-----------------------------------------------------------
@app.get("/")
def index():
    with connect_db() as client:
        sql = "SELECT * from classes"
        params=[]
        result = client.execute(sql, params)
        classes = result.rows
        return render_template("pages/home.jinja", classes=classes)


#-----------------------------------------------------------
# About page route
#-----------------------------------------------------------
@app.get("/about/")
def about():
    return render_template("pages/about.jinja")


#-----------------------------------------------------------
# class page route - Show details of a single class
#-----------------------------------------------------------
@app.get("/class/<int:id>")
def show_class(id):
    with connect_db() as client:
        # Get all the things from the DB
        sql = "SELECT * FROM topics where class_id=? ORDER BY done ASC"
        params = [id]
        result = client.execute(sql, params)
        topics = result.rows

        sql2 = "SELECT * FROM classes where id=?"
        result2 = client.execute(sql2,params)
        clas = result2.rows[0]

        # And show them on the page
        return render_template("pages/class.jinja", topics=topics, clas=clas)


#-----------------------------------------------------------
# Topic page - show details of a single topic
#-----------------------------------------------------------
@app.get("/topic/<int:id>")
def show_topic(id):
    with connect_db() as client:
        # Get the thing details from the DB
        sql = "SELECT * FROM steps WHERE topic_id=?"
        params = [id]
        result = client.execute(sql, params)
        steps = result.rows

        sql2 = "SELECT * from topics WHERE id=?"
        result2 = client.execute(sql2,params)
        topic = result2.rows[0]

        return render_template("pages/topic.jinja", steps=steps, topic=topic)

#-----------------------------------------------------------
# Step page - show details of a single step
#-----------------------------------------------------------
@app.get("/step/<int:id>")
def show_step(id):
    with connect_db() as client:
        # Get the thing details from the DB
        sql = "SELECT * FROM steps WHERE id=?"
        params = [id]
        result = client.execute(sql, params)

        # Did we get a result?
        if result.rows:
            # yes, so show it on the page
            step = result.rows[0]
            return render_template("pages/step.jinja", step=step)

        else:
            # No, so show error
            return not_found_error()


#-----------------------------------------------------------
# Route for adding a thing, using data posted from a form
#-----------------------------------------------------------
@app.post("/add")
def add_a_thing():
    # Get the data from the form
    name  = request.form.get("name")
    price = request.form.get("price")

    # Sanitise the text inputs
    name = html.escape(name)

    with connect_db() as client:
        # Add the thing to the DB
        sql = "INSERT INTO things (name, price) VALUES (?, ?)"
        params = [name, price]
        client.execute(sql, params)

        # Go back to the home page
        flash(f"Thing '{name}' added", "success")
        return redirect("/things")


#-----------------------------------------------------------
# Route for deleting a thing, Id given in the route
#-----------------------------------------------------------
@app.get("/delete/<int:id>")
def delete_a_thing(id):
    with connect_db() as client:
        # Delete the thing from the DB
        sql = "DELETE FROM things WHERE id=?"
        params = [id]
        client.execute(sql, params)

        # Go back to the home page
        flash("Thing deleted", "success")
        return redirect("/things")



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
# New Class page
#-----------------------------------------------------------
@app.get("/newClassForm")
def newClassForm():
    return render_template("pages/newClassForm.jinja")

#-----------------------------------------------------------
# New Topic page
#-----------------------------------------------------------
@app.get("/newTopicForm")
def newTopicForm():
    return render_template("pages/newTopicForm.jinja")


#-----------------------------------------------------------
# Route for adding a topic, using date posted from a form
#-----------------------------------------------------------
@app.post("/addTopic")
def add_a_topic():
    # Get the data from the form
    name = request.form.get("name")
    class_id = request.form.get("class_id")
    internal = request.form.get("internal")
    external = request.form.get("external")
    
#-----------------------------------------------------------
# Route for adding a class, using data posted from a form
#-----------------------------------------------------------
@app.post("/addClass")
def add_a_class():
    # Get the data from the form
    name = request.form.get("name")
    size = request.form.get("size")
    year = request.form.get("year")

    # Sanitise the text inputs
    name = html.escape(name)

    with connect_db() as client:
        # Add the thing to the DB
        sql = "INSERT INTO classes (name, size, year) VALUES (?, ?, ?)"
        params = [name, size, year]
        client.execute(sql, params)

        # Go back to the home page
        flash(f"Thing '{name}' added", "success")
        return redirect("/")


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



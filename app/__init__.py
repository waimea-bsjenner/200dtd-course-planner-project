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
# About page route
#-----------------------------------------------------------
@app.get("/about/")
def about():
    return render_template("pages/about.jinja")

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
        sql2 = "SELECT * from topics"
        result2 = client.execute(sql2, params)
        topics = result2.rows
        sql3 = "SELECT * from steps"
        result3 = client.execute(sql3, params)
        steps = result3.rows
        return render_template("pages/home.jinja", classes=classes, topics=topics, steps=steps)
    

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
    with connect_db() as client:
        sql = "SELECT * from classes"
        params=[]
        result = client.execute(sql, params)
        classes = result.rows
    return render_template("pages/newTopicForm.jinja", classes=classes)

#-----------------------------------------------------------
# New Step page
#-----------------------------------------------------------
@app.get("/newStepForm")
def newStepForm():
    with connect_db() as client:
        sql = "SELECT * from topics"
        params=[]
        result = client.execute(sql,params)
        topics = result.rows
    return render_template("pages/newStepForm.jinja", topics=topics)

#-----------------------------------------------------------
# Update Class page
#-----------------------------------------------------------
@app.get("/updateClassForm/<int:id>")
def updateClassForm(id):
    with connect_db() as client:
        sql = "SELECT * from classes WHERE id=?"
        params = [id]
        result=client.execute(sql, params)
        clas=result.rows[0]
    return render_template("pages/updateClassForm.jinja", clas=clas)


#-----------------------------------------------------------
# Update Topic page
#-----------------------------------------------------------
@app.get("/updateTopicForm/<int:id>")
def updateTopicForm(id):
    with connect_db() as client:
        sql = "SELECT * from topics where id=?"
        params = [id]
        result = client.execute(sql, params)
        topic = result.rows[0]
        sql2 = "SELECT * from classes"
        params2 = []
        result=client.execute(sql, params)
        classes = result.rows
    return render_template("pages/updateTopicForm.jinja", topic=topic, classes=classes)

#-----------------------------------------------------------
# Update Step page
#-----------------------------------------------------------
@app.get("/updateStepForm/<int:id>")
def updateStepForm(id):
    with connect_db() as client:
        sql = "SELECT * from steps where id=?"
        params = [id]
        result = client.execute(sql, params)
        step = result.rows[0]
    return render_template("pages/updateStepForm.jinja", step=step)

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
    description = request.form.get("description")
    credits = request.form.get("credits")
    standard_number = request.form.get("standard_number")

    name = html.escape(name)
    description = html.escape(description)

    with connect_db() as client:
        sql = "INSERT INTO topics (name, class_id, external, internal, description, credits, standard_number) VALUES (?, ?, ?, ?, ?, ?, ?)"
        params = [name, class_id, internal, external, description, credits, standard_number]
        client.execute(sql, params)

        flash(f"Topic '{name}' added", "success")
        return redirect("/")
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
        flash(f"Class '{name}' added", "success")
        return redirect("/")
    
#-----------------------------------------------------------
# Route for adding a step, using date posted from a form
#-----------------------------------------------------------
@app.post("/addStep")
def add_a_step():
    name = request.form.get("name")
    topic_id = request.form.get("topic_id")
    notes = request.form.get("notes")
    url1 = request.form.get("url1")
    url2 = request.form.get("url2")
    url3 = request.form.get("url3")
    
    name = html.escape(name)
    notes = html.escape(notes)
    url1 = html.escape(url1)
    url2 = html.escape(url2)
    url3 = html.escape(url3)
    with connect_db() as client:
        sql = "INSERT INTO steps (name, topic_id, notes, url1, url2, url3) VALUES (?, ?, ?, ?, ?, ?)"
        params = [name, topic_id, notes, url1, url2, url3]
        client.execute(sql, params)

        flash(f"Step '{name}' added", "Success")
        return redirect("/")
    

#-----------------------------------------------------------
# Route for updating a class, Id given in the route
#-----------------------------------------------------------
@app.post("/updateClass/<int:id>")
def update_a_class(id):
    name = request.form.get("name")
    size = request.form.get("size")
    year = request.form.get("year")

    name = html.escape(name)
    with connect_db() as client:
        sql = "UPDATE classes SET name=?, size=?, year=? WHERE id=?"
        params = [name, size, year, id]
        client.execute(sql, params)
        flash("Class updated", "success")
        return redirect("/")    

#-----------------------------------------------------------
# Route for updating a Topic, Id given in the route
#-----------------------------------------------------------
@app.post("/updateTopic/<int:id>")
def update_a_topic(id):
    name = request.form.get("name")
    class_id = request.form.get("class_id")
    external = request.form.get("external")
    internal = request.form.get("internal")
    description = request.form.get("description")
    credits = request.form.get("credits")
    standard_number = request.form.get("standard_number")

    name = html.escape(name)
    description = html.escape(description)
    with connect_db() as client:
        sql = "UPDATE classes SET name=?, class_id=?, external=?, internal=?, description=?, credits=?, standard_number=? WHERE id=?"
        params = [name, class_id, external, internal, description, credits, standard_number, id]
        client.execute(sql, params)
        flash("Class updated", "success")
        return redirect("/")    

#-----------------------------------------------------------
# Route for updating a Step, Id given in the route
#-----------------------------------------------------------
@app.post("/updateClass/<int:id>")
def update_a_step(id):
    name = request.form.get("name")
    topic_id = request.form.get("topic_id")
    notes = request.form.get("notes")
    url1 = request.form.get("url1")
    url2 = request.form.get("url2")
    url3 = request.form.get("url3")


    name = html.escape(name)
    notes = html.escape(notes)
    url1 = html.escape(url1)
    url2 = html.escape(url2)
    url3 = html.escape(url3)

    with connect_db() as client:
        sql = "UPDATE classes SET name=?, topic_id=?, notes=?, url1=?, url2=?, url3=? WHERE id=?"
        params = [name, topic_id, notes, url1, url2, url3, id]
        client.execute(sql, params)
        flash("Class updated", "success")
        return redirect("/")
    
    
#-----------------------------------------------------------
#
#-----------------------------------------------------------
#-----------------------------------------------------------
# Route for deleting a class, Id given in the route
#-----------------------------------------------------------
@app.get("/deleteClass/<int:id>")
def delete_a_class(id):
    with connect_db() as client:
        # Delete the thing from the DB
        sql = "DELETE FROM classes WHERE id=?"
        params = [id]
        client.execute(sql, params)

        # Go back to the home page
        flash("Class deleted", "success")
        return redirect("/")

#-----------------------------------------------------------
# Route for deleting a topic, Id given in the route
#-----------------------------------------------------------
@app.get("/deleteTopic/<int:id>")
def delete_a_topic(id):
    with connect_db() as client:
        # Delete the thing from the DB
        sql = "DELETE FROM topics WHERE id=?"
        params = [id]
        client.execute(sql, params)

        # Go back to the home page
        flash("Topic deleted", "success")
        return redirect("/")

#-----------------------------------------------------------
# Route for deleting a step, Id given in the route
#-----------------------------------------------------------
@app.get("/deleteStep/<int:id>")
def delete_a_step(id):
    with connect_db() as client:
        # Delete the thing from the DB
        sql = "DELETE FROM steps WHERE id=?"
        params = [id]
        client.execute(sql, params)

        # Go back to the home page
        flash("Step deleted", "success")
        return redirect("/")



from flask import Flask, render_template, request, redirect, url_for, jsonify
from uuid import uuid4
from flask import jsonify
from flask_bcrypt import Bcrypt

app = Flask(__name__)
bcrypt = Bcrypt(app)

# In a real app, you'd use a database to store event data.
events = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/create_event', methods=['POST'])
def create_event():
    title = request.form.get('title')
    description = request.form.get('description')
    time = request.form.get('time')
    location = request.form.get('location')
    plain_password = request.form.get('password')
    password_hash = bcrypt.generate_password_hash(plain_password).decode('utf-8')


    # Generate a unique ID for the event
    event_id = str(uuid4())
    
    events[event_id] = {
        'title': title,
        'description': description,
        'time': time,
        'location': location,
        'password': password_hash  # Save the password here
    }

    # Generate the full URL for the event
    event_url = request.url_root[:-1] + url_for('event_page', event_id=event_id)

    # Pass the event URL to the template that shows it to the user
    return render_template('event_created.html', event_url=event_url)

@app.route('/event/<event_id>')
def event_page(event_id):
    event = events.get(event_id)
    if event:
        # Pass the event_id to the template
        return render_template('event.html', event=event, event_id=event_id)
    else:
        return 'Event not found', 404

@app.route('/event/edit/<event_id>', methods=['GET', 'POST'])
def edit_event(event_id):
    event = events.get(event_id)
    if not event:
        return jsonify({'status': 'error', 'message': 'Event not found'}), 404
    
    if request.method == 'POST':
        plain_password = request.form.get('password')

        if bcrypt.check_password_hash(event['password'], plain_password):
            # Update the event with the data submitted in the form
            event['title'] = request.form.get('title')
            event['description'] = request.form.get('description')
            event['time'] = request.form.get('time')
            event['location'] = request.form.get('location')

            return jsonify({'status': 'success', 'message': 'Event updated successfully.'})
        else:
            return jsonify({'status': 'error', 'message': 'Incorrect password. Please try again.'})
    
    # Render the edit page as before for GET requests
    return render_template('edit_event.html', event=event, event_id=event_id)

@app.route('/events', methods=['GET'])
def list_events():
    # Return a JSON list of all the event details
    return jsonify(list(events.values()))

if __name__ == "__main__":
    app.run(debug=True)
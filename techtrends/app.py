import sqlite3

from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash
from werkzeug.exceptions import abort
import logging
import os
import sys

# Function to get a database connection.
# This function connects to database with the name database.db & also return the updated number of connections made with the database.

connection_request = 0

def get_db_connection():
    global connection_request
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    connection_request += 1
    return connection

# Function to get a post using its ID
def get_post(post_id):
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    connection.close()
    return post

# Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'

# Define the main route of the web application 
@app.route('/')
def index():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    return render_template('index.html', posts=posts)

# Define how each individual article is rendered 
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    if post is None:
        # >>> Step 1: Best Practices For Application Deployment / Logs | A non-existing article is accessed and a 404 page is returned. <<< Required Action
        logging.info('A non-existing article is accessed.')
        return render_template('404.html'), 404
    else:
        # >>> Step 1: Best Practices For Application Deployment / Logs | An existing article is retrieved. The title of the article should be recorded in the log line. <<< Required Action
        logging.info('Article "{title}" retrieved!'.format(title=post['title']))
        return render_template('post.html', post=post)

# Define the About Us page
@app.route('/about')
def about():
    # >>> Step 1: Best Practices For Application Deployment / Logs | The "About Us" page is retrieved. <<< Required Action
    logging.info('The "About Us" page is retrieved.')
    return render_template('about.html')

# Define the post creation functionality 
@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            connection = get_db_connection()
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                         (title, content))
            connection.commit()
            connection.close()
            # >>> Step 1: Best Practices For Application Deployment / Logs | A new article is created. The title of the new article should be recorded in the logline. <<< Required Action
            logging.info('Article "{title}" created!'.format(title=title))
            return redirect(url_for('index'))

    return render_template('create.html')

# >>> Step 1: Best Practices For Application Deployment / Healthcheck Endpoint <<< Required Action
@app.route('/healthz')
def status():
    if os.path.exists('database.db'):
        return jsonify({"result": "OK - healthy"})
    else:
        return jsonify({"result": "Error - Missing {}".format('database.db')}), 500

# >>> Step 1: Best Practices For Application Deployment / Metrics Endpoint <<< Required Action
@app.route('/metrics')
def metrics():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    #Considering The /metrics endpoint response should NOT be hardcoded.
    count_post = len(posts)
    response = app.response_class(
            response=json.dumps({"status":"success","code":0,"data":{"db_connection_count": connection_request, "post_count": count_post}}), #Considering The /metrics endpoint response should NOT be hardcoded.
            status=200,
            mimetype='application/json'
    )

    return response

# >>> Step 1: Best Practices For Application Deployment / Logs | Defining function for logging multiple events <<< Required Action
def initialize_logger():

    log_level = os.getenv("LOGLEVEL", "DEBUG").upper()
    log_level = (
        getattr(logging, log_level)
        if log_level in ["CRITICAL", "DEBUG", "ERROR", "INFO", "WARNING",]
        else logging.DEBUG
    )

    format = logging.Formatter('%(levelname)s:%(name)s:%(asctime)s, %(message)s')

    handler_stdout = logging.StreamHandler(sys.stdout)
    handler_stdout.setFormatter(format)
    app.logger.addHandler(handler_stdout)
    handler_stderr = logging.StreamHandler(sys.stderr)

    logging.basicConfig(
                format='%(levelname)s:%(name)s:%(asctime)s, %(message)s',
                level=log_level,
                handlers=[
                    handler_stdout, handler_stderr,
                ]
    )

# start the application on port 3111
if __name__ == "__main__":
    initialize_logger()
    
    app.run(host='0.0.0.0', port='3111')
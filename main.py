from flask import Flask, render_template, request, redirect, url_for, session
from pymongo import MongoClient
from bson.objectid import ObjectId

app = Flask(__name__)
app.secret_key = "supersecretkey"

# MongoDB connection
client = MongoClient("mongodb://localhost:27017/")
db = client.recipe_management


@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if db.users.find_one({'username': username}):
            return render_template('register.html', error="Username already exists!")
        db.users.insert_one({'username': username, 'password': password})
        session['username'] = username
        return redirect(url_for('dashboard'))
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = db.users.find_one({'username': username, 'password': password})
        if user and user['password'] == password:
            session['username'] = username
            return redirect(url_for('dashboard'))
        return "Invalid credentials!"
    return render_template('login.html')


@app.route('/dashboard')
def dashboard():
    # if 'username' not in session:
    #     return redirect(url_for('login'))
    # recipes = db.recipes.find({'username': session['username']})
    return render_template('dashboard.html')


@app.route('/add_recipe', methods=['GET', 'POST'])
def add_recipe():
    if 'username' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        # Collecting form data
        recipe = {
            'name': request.form['name'],
            'description': request.form['description'],
            'ingredients': request.form['ingredients'],
            'instructions': request.form['instructions'],
            'username': session['username']  # Assuming the user is logged in and the session contains the username
        }

        # Insert the new recipe into the MongoDB database
        db.recipes.insert_one(recipe)

        # Render a success page with a message and a button
        return render_template('recipe_added.html')

    return render_template('add_recipe.html')


@app.route('/edit_recipe/<id>', methods=['GET', 'POST'])
def edit_recipe(id):
    if 'username' not in session:
        return redirect(url_for('login'))
    recipe = db.recipes.find_one({'_id': ObjectId(id), 'username': session['username']})
    if request.method == 'POST':
        recipe_name = request.form['recipe_name']
        ingredients = request.form['ingredients']
        instructions = request.form['instructions']
        db.recipes.update_one(
            {'_id': ObjectId(id)},
            {'$set': {
                'recipe_name': recipe_name,
                'ingredients': ingredients,
                'instructions': instructions
            }}
        )
        return redirect(url_for('dashboard'))
    return render_template('edit_recipe.html', recipe=recipe)


@app.route('/delete_recipe/<id>')
def delete_recipe(id):
    if 'username' not in session:
        return redirect(url_for('login'))
    db.recipes.delete_one({'_id': ObjectId(id), 'username': session['username']})
    return redirect(url_for('dashboard'))


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)

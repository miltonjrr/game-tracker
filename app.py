import os
from flask import Flask, render_template, request, redirect, url_for
from models import db, Game

app = Flask(__name__)

# Configure database - uses Render's environment variable
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', '').replace('postgres://', 'postgresql://')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Initialize database tables
with app.app_context():
    db.create_all()

# Optional: For local testing only (remove before deploying to Render)
LOCAL_DEVELOPMENT = False  # Set to False when deploying
if LOCAL_DEVELOPMENT:
    @app.before_request
    def restrict_by_ip():
        ALLOWED_IPS = ["191.241.132.114", "127.0.0.1"]
        client_ip = request.remote_addr
        if client_ip not in ALLOWED_IPS:
            abort(403, description=f"Access denied. Your IP ({client_ip}) is not whitelisted.")

@app.route('/')
def index():
    games = Game.query.all()
    return render_template('index.html', games=games)

@app.route('/add', methods=['GET', 'POST'])
def add_game():
    if request.method == 'POST':
        title = request.form['title']
        status = request.form['status']
        new_game = Game(title=title, status=status)
        db.session.add(new_game)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('add_game.html')

@app.route('/update/<int:game_id>', methods=['POST'])
def update_game(game_id):
    game = Game.query.get(game_id)
    game.status = request.form['status']
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/delete/<int:game_id>', methods=['POST'])
def delete_game(game_id):
    game = Game.query.get_or_404(game_id)
    db.session.delete(game)
    db.session.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)

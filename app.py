from flask import (Flask, request, session, g, redirect, url_for, abort,
        render_template, flash)
import sqlite3
from contextlib import closing

DATABASE = '/tmp/flaskr.db'
SECRET_KEY = 'development key'

app = Flask(__name__)
app.config.from_object(__name__)

def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql') as f:
            db.cursor().executescript(f.read())
        db.commit()

def connect_db():
    return sqlite3.connect(app.config['DATABASE'])

@app.before_request
def before_request():
    g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
    g.db.close()

@app.route('/')
def index():
    cur = g.db.execute("""select id, forename, surname, email, phone
            from entries""")
    people = [ {
        'id': row[0],
        'forename': row[1],
        'surname': row[2],
        'email': row[3],
        'phone': row[4],
        } for row in cur.fetchall() ]
    return render_template('index.html', people=people)

@app.route('/new', endpoint='new', methods=['GET', 'POST'])
@app.route('/edit/<id>', methods=['GET', 'POST'])
def edit(id = None):
    if request.form:
        valid = True
        if not request.form['forename']:
            valid = False
            flash('Must enter first name')
        if not request.form['surname']:
            valid = False
            flash('Must enter last name')
        if not request.form['phone']:
            valid = False
            flash('Must enter phone')
        if not request.form['email']:
            valid = False
            flash('Must enter email')
        if valid:
            if not id:
                g.db.execute("""insert into entries(forename, surname, email, phone)
                        values(?, ?, ?, ?)""", [
                            request.form['forename'],
                            request.form['surname'],
                            request.form['email'],
                            request.form['phone'],
                            ])
            else:
                g.db.execute("""update entries set forename=?, surname=?, email=?,
                        phone=? where id=?""", [
                            request.form['forename'],
                            request.form['surname'],
                            request.form['email'],
                            request.form['phone'],
                            id,
                            ])
            g.db.commit()
            return redirect(url_for('index'))
        else:
            person = request.form
    else:
        if id:
            row = g.db.execute("""select forename, surname, email, phone
                    from entries where id=?""", [ id ]).fetchone()
            person = { 'forename': row[0],
                    'surname': row[1],
                    'email': row[2],
                    'phone': row[3],
                    }

    return render_template('edit.html', person=person)


@app.route('/delete/<id>')
def delete(id):
    g.db.execute('delete from entries where id=?', [ id ])
    g.db.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)

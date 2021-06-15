from flask import Flask, render_template, request, redirect, flash, abort
import sqlite3



app = Flask(__name__)


@app.route('/')
def hello():
    conn = get_db_connection()
    sms = conn.execute('SELECT * FROM sms').fetchall()
    email = conn.execute('SELECT * FROM email').fetchall()
    conn.close()
    return render_template('index.html', sms=sms, email=email )

@app.route('/gallary')
def gallary():
    return render_template('gallary.html')

@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']

        if not name :
            flash('Name  is required!')
        else:
            conn = get_db_connection()
            conn.execute('INSERT INTO email (name, email) VALUES (?, ?)',
                         (name, email))
            conn.commit()
            conn.close()
            return redirect(url_for('index'))

    return render_template('create.html')


@app.route('/create_sms', methods=('GET', 'POST'))
def create_sms ():
    if request.method == 'POST':
        name   = request.form['name']
        number = request.form['number']

        if not name:
            flash('Name is required!') 
        else:
            conn = get_db_connection()
            conn.execute('INSERT INTO sms (name,phone   VALUES (?, ?)',
                         (name, number))
            conn.commit()
            conn.close()
            return redirect(url_for('index'))

    return render_template('create.html')

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn


@app.route('/<int:id>/<what>/delete', methods=('POST',))
def delete(id,what):
    
    conn = get_db_connection()
    if what is 'sms':
    	post = get_sms(id)
    	conn.execute('DELETE FROM sms WHERE id = ?', (id,))
    else:
    	post = get_mail(id)
    	conn.execute('DELETE FROM email WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    flash('"{}" was successfully deleted!'.format(post['name  ']))
    return redirect(url_for('index'))


def get_sms(post_id):
    conn = get_db_connection()
    post = conn.execute('SELECT * FROM sms WHERE id = ?',
                        (post_id,)).fetchone()
    conn.close()
    if post is None:
        abort(404)
    return post

def get_mail(post_id):
    conn = get_db_connection()
    post = conn.execute('SELECT * FROM email WHERE id = ?',
                        (post_id,)).fetchone()
    conn.close()
    if post is None:
        abort(404)
    return post

@app.route('/<int:post_id>')
def post(post_id):
    post = get_sms(post_id)
    return render_template('post.html', post=post)

@app.route('/mail/<int:post_id>')
def mail(post_id):
    post = get_mail(post_id)
    return render_template('post.html', mail=post)


@app.route('/<int:id>/<what>/edit', methods=('GET', 'POST'))
def edit(id, what): 
	if what== 'sms':
		post = get_sms(id)
	else:
		post = get_mail(id)
	if request.method == 'POST':
	    title = request.form['title']
	    content = request.form['content']

	    if not title:
	        flash('Title is required!')
	    else:
	        conn = get_db_connection()
	        if what is 'sms':
	        	conn.execute('UPDATE sms SET name = ?, phone = ?'
	                     ' WHERE id = ?',
	                     (title, content, id))
	        else:
	        	conn.execute('UPDATE email SET name = ?, email= ?'
	                     ' WHERE id = ?',
	                     (title, content, id))
	        conn.commit()
	        conn.close()
	        return redirect(url_for('index'))

	return render_template('edit.html', post=post, what=what )
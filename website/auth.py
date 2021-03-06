from tabnanny import check
from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User, Music
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user

auth = Blueprint('auth', __name__)

@auth.route('/')
#@login_required
def nav_to_main():
    return render_template("main-page.html", user=current_user)


@auth.route('/menu')
@login_required
def nav_to_menu():
    return render_template("menu.html", user=current_user)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                login_user(user, remember=True)
                return redirect(url_for('auth.nav_to_menu'))
            else:
                flash('Incorrect password, try again.', category='error')
        else:
            flash('Email does not exist.', category='error')

    return render_template("login.html", user=current_user)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


@auth.route('/delete-account')
@login_required
def delete_account():
    db.session.delete(current_user)
    db.session.commit()
    flash('Account deleted.', category='success')

    logout_user()
    return redirect(url_for('auth.login'))


@auth.route('/lead')
@login_required
def nav_to_lead():
    return render_template("lead.html", user=current_user)

@auth.route('/double-tenor')
@login_required
def nav_to_double_tenor():
    return render_template("double-tenor.html", user=current_user)


@auth.route('/double-second')
@login_required
def nav_to_double_second():
    return render_template("double-second.html", user=current_user)


@auth.route('/guitar-cello')
@login_required
def nav_to_guitar_cello():
    return render_template("guitar-cello.html", user=current_user)


@auth.route('/tenor-bass')
@login_required
def nav_to_tenor_bass():
    return render_template("tenor-bass.html", user=current_user)


@auth.route('/six-bass')
@login_required
def nav_to_six_bass():
    return render_template("six-bass.html", user=current_user)


@auth.route('/help')
@login_required
def nav_to_help():
    return render_template("help.html", user=current_user)


@auth.route('/settings')
@login_required
def nav_to_settings():
    return render_template("settings.html", user=current_user)


@auth.route('/drum-select')
@login_required
def nav_to_drum_select():
    return render_template("drum-select.html", user=current_user)


@auth.route('/add-music', methods=['GET', 'POST'])
@login_required
def add_music():
    if request.method == 'POST':
        title = request.form.get('title')
        composer = request.form.get('composer')
        genre = request.form.get('genre')
        description = request.form.get('description')
        pdf_link = request.form.get('pdf_link')
        audio_link = request.form.get('audio_link')

        if len(title) < 1:
            flash('You must enter a title.', category='error')
        else:
            new_sample = Music(title=title, composer=composer, genre=genre,
                               description=description, pdf_link=pdf_link,
                               audio_link=audio_link, user_id=current_user.id)
            db.session.add(new_sample)
            db.session.commit()
            return redirect(url_for('views.nav_to_music_library'))

    return render_template("add-music.html", user=current_user)


@auth.route('/edit-music/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_music(id):
    music = Music.query.get(id)
    if request.method == 'POST':
        title = request.form.get('title')
        composer = request.form.get('composer')
        genre = request.form.get('genre')
        description = request.form.get('description')
        pdf_link = request.form.get('pdf_link')
        audio_link = request.form.get('audio_link')

        if len(title) < 1:
            flash('You must enter a title.', category='error')
        else:
            music.set_title(title)
            music.set_composer(composer)
            music.set_genre(genre)
            music.set_description(description)
            music.set_pdf(pdf_link)
            music.set_audio(audio_link)
            db.session.commit()
            return redirect(url_for('views.nav_to_music_library'))

    return render_template("edit-music.html", user=current_user, music=music)

@auth.route('/change-user-permissions', methods=['GET', 'POST'])
@login_required
def change_permissions():
    if request.method == 'POST':
        email = request.form.get('email')
        admin_set = request.form.get('priv')

        user = User.query.filter_by(email=email).first()
        is_admin = True if admin_set == 'admin' else False

        if not user:
            flash('This email does not exist.', category='error')
        else:
            user.set_is_admin(is_admin)
            flash('User permissions updated!', category='success')
            return redirect(url_for('auth.change_settings'))

    return render_template("permissions.html", user=current_user)


@auth.route('/settings', methods=['GET', 'POST'])
def change_settings():
    if request.method == 'POST':
        background = request.form.get('background')
        drum_color = request.form.get('drum-color')

        current_user.set_background(background)
        current_user.set_drum_color(drum_color)
        flash('Design settings updated successfully!', category="success")
        return redirect(url_for('auth.change_settings'))

    return render_template("settings.html", user=current_user)
\

@auth.route('/update-account', methods=['GET', 'POST'])
def update_account():
    if request.method == 'POST':
        email = request.form.get('email')
        first_name = request.form.get('firstName')

        user = User.query.filter_by(email=email).first()
        if user and email != current_user.email:
            flash('Email already exists.', category='error')
        elif len(email) < 4:
            flash('Email must be greater than 3 characters.', category='error')
        elif len(first_name) < 2:
            flash('First name must be greater than 1 character.', category='error')
        else:
            current_user.set_email(email)
            current_user.set_first_name(first_name)
            flash('Account updated!', category='success')
            return redirect(url_for('auth.change_settings'))

    return render_template("update-account.html", user=current_user)


@auth.route('/change-password', methods=['GET', 'POST'])
def change_password():
    if request.method == 'POST':
        old_password = request.form.get('old')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        if not check_password_hash(current_user.password, old_password):
            flash('Current password is incorrect, try again.', category='error')
        elif password1 != password2:
            flash('New passwords don\'t match.', category='error')
        elif len(password1) < 7:
            flash('New password must be at least 7 characters.', category='error')
        else:
            current_user.set_password(generate_password_hash(password1, method='sha256'))
            flash('Password changed!', category='success')
            return redirect(url_for('auth.change_settings'))

    return render_template("change-password.html", user=current_user)


@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        first_name = request.form.get('firstName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already exists.', category='error')
        elif len(email) < 4:
            flash('Email must be greater than 3 characters.', category='error')
        elif len(first_name) < 2:
            flash('First name must be greater than 1 character.', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match.', category='error')
        elif len(password1) < 7:
            flash('Password must be at least 7 characters.', category='error')
        else:
            admin = True if db.session.query(User).count() == 0 else False
            new_user = User(email=email, first_name=first_name, password=generate_password_hash(
                password1, method='sha256'), is_admin=admin)
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash('Account created!', category='success')
            return redirect(url_for('auth.nav_to_menu'))

    return render_template("sign_up.html", user=current_user)
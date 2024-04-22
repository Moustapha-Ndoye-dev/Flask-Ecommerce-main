from flask import Blueprint, render_template, flash, redirect
from .forms import LoginForm, SignUpForm, PasswordChangeForm
from .models import Customer
from . import db
from flask_login import login_user, login_required, logout_user

auth = Blueprint('auth', __name__)

@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    form = SignUpForm()
    if form.validate_on_submit():
        email = form.email.data
        username = form.username.data
        password1 = form.password1.data
        password2 = form.password2.data

        # Vérifier si l'adresse e-mail existe déjà
        existing_user = Customer.query.filter_by(email=email).first()
        if existing_user:
            flash('L\'adresse e-mail existe déjà !')
            return redirect('/sign-up')

        if password1 == password2:
            new_customer = Customer()
            new_customer.email = email
            new_customer.username = username
            new_customer.password = password2

            try:
                db.session.add(new_customer)
                db.session.commit()
                flash('Compte créé avec succès, vous pouvez maintenant vous connecter')
                return redirect('/login')
            except Exception as e:
                print(e)
                flash('Compte non créé !!')

        else:
            flash('Les mots de passe ne correspondent pas')

    return render_template('signup.html', form=form)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        customer = Customer.query.filter_by(email=email).first()

        if customer:
            if customer.verify_password(password=password):
                login_user(customer)
                return redirect('/')
            else:
                flash('E-mail ou mot de passe incorrect')

        else:
            flash('Le compte n\'existe pas, veuillez vous inscrire')

    return render_template('login.html', form=form)

@auth.route('/logout', methods=['GET', 'POST'])
@login_required
def log_out():
    logout_user()
    return redirect('/')

@auth.route('/profile/<int:customer_id>')
@login_required
def profile(customer_id):
    customer = Customer.query.get(customer_id)
    return render_template('profile.html', customer=customer)

@auth.route('/change-password/<int:customer_id>', methods=['GET', 'POST'])
@login_required
def change_password(customer_id):
    form = PasswordChangeForm()
    customer = Customer.query.get(customer_id)
    if form.validate_on_submit():
        current_password = form.current_password.data
        new_password = form.new_password.data
        confirm_new_password = form.confirm_new_password.data

        if customer.verify_password(current_password):
            if new_password == confirm_new_password:
                customer.password = confirm_new_password
                db.session.commit()
                flash('Mot de passe mis à jour avec succès')
                return redirect(f'/profile/{customer.id}')
            else:
                flash('Les nouveaux mots de passe ne correspondent pas !!')

        else:
            flash('Le mot de passe actuel est incorrect')

    return render_template('change_password.html', form=form)

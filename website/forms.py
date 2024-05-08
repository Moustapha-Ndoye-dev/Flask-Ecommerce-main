from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, FloatField, PasswordField, EmailField, BooleanField, SubmitField, SelectField
from wtforms.validators import DataRequired, length, NumberRange
from flask_wtf.file import FileField, FileRequired


class SignUpForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired()])
    username = StringField('nom', validators=[DataRequired(), length(min=2)])
    password1 = PasswordField('mot de passe', validators=[DataRequired(), length(min=6)])
    password2 = PasswordField('Confirmer le mot de passe', validators=[DataRequired(), length(min=6)])
    submit = SubmitField('Sinscrire')


class LoginForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired()])
    password = PasswordField('mot de paasse', validators=[DataRequired()])
    submit = SubmitField('Se connecter')


class PasswordChangeForm(FlaskForm):
    current_password = PasswordField('mot de passe actuel', validators=[DataRequired(), length(min=6)])
    new_password = PasswordField('Nouveau mot de passe', validators=[DataRequired(), length(min=6)])
    confirm_new_password = PasswordField('Confirmer lenouveau mot de passe', validators=[DataRequired(), length(min=6)])
    change_password = SubmitField('Changer le mot de passe')


class ShopItemsForm(FlaskForm):
    product_name = StringField('Nom du produit', validators=[DataRequired()])
    category = SelectField('Catégorie', coerce=int, validators=[DataRequired()])
    current_price = FloatField('Prix actuel', validators=[DataRequired()])
    previous_price = FloatField('Ancien Prix', validators=[DataRequired()])
    in_stock = IntegerField('Quantité', validators=[DataRequired(), NumberRange(min=0)])
    product_picture = FileField('Photo du produit',validators=[FileRequired()])
    flash_sale = BooleanField('Vente flash')
    add_product = SubmitField('Ajouter le produit')
    update_product = SubmitField('Mise à jour')
    

class OrderForm(FlaskForm):
    order_status = SelectField('Statut de la commande', choices=[('En attente', 'En attente'), ('Acceptée', 'Acceptée'),
                                                        ('En cours de livraison', 'En cours de livraison'),
                                                        ('Livré', 'Livré'), ('Annulé', 'Annulé')])

    update = SubmitField('Statut Mis a jour')


class CategoryForm(FlaskForm):
    name = StringField('Nom de la catégorie', validators=[DataRequired(), length(min=2, max=100)])
    submit = SubmitField('Ajouter la catégorie')




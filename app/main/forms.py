from app import db
from app.models import User, Item
from flask_wtf import FlaskForm
from flask import request
from wtforms import Form, StringField, PasswordField, BooleanField, SubmitField, SelectField, DecimalField, IntegerField, FormField, FieldList, FileField,FloatField,TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, Length, NumberRange,InputRequired, EqualTo
import phonenumbers


class AddProduct(FlaskForm):
    name = StringField('Name')
    description = TextAreaField('Description')
    category = StringField('Category')
    image = FileField('Image')
    category    = SelectField('User Type', choices=[('Printers', 'Printers'), ('Electronics', 'Electronics'), ('Laptops', 'Laptops'), ('Power', 'Power')])
    submit   = SubmitField('Add')

class SearchForm(FlaskForm):
	searched = StringField("Searched", validators=[DataRequired()])
	submit = SubmitField("Submit")

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])

    password = PasswordField('Password', validators=[DataRequired()])
    usertype = SelectField('User Type', choices=[('Vendor', 'Vendor'), ('Customer', 'Customer')])
    remember = BooleanField('Remember Me')
    submit   = SubmitField('Sign In')

class SalesForm(FlaskForm):
    amount = FloatField('Sales Amount: ', [InputRequired()])
    discount = FloatField('Discount Amount: ', [InputRequired()])
    customer = IntegerField("Customer's Account ID: ", [InputRequired()])
    submit = SubmitField('Transfer')  

class RegistrationForm(FlaskForm):
    username    = StringField('Username', validators=[
        DataRequired(),
        Length(min=3, max=32, message="Username must be between 3 and 32 characters.")])

    email       = StringField('Email', validators=[
        DataRequired(), 
        Email(message="Invalid email address.")])

    phone       = StringField('Phone Number', validators=[DataRequired()])
    address     = StringField('Address', validators=[DataRequired()])
    firstname   = StringField('First Name', validators=[DataRequired()])
    lastname    = StringField('Last Name', validators=[DataRequired()])
    usertype    = SelectField('User Type', choices=[('Vendor', 'Vendor'), ('Customer', 'Customer')])
    password    = PasswordField('Password', validators=[DataRequired()])
    password2   = PasswordField('Verify Password', validators=[DataRequired(), EqualTo('password')])
    
    submit      = SubmitField('Sign Up')

    #local field validators
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('That username is taken.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('An account using that email already exists.')


class AddToCartForm(FlaskForm):
    submit = SubmitField('Add to Cart')

class QuantityEntryForm(FlaskForm):
    quantity = IntegerField(validators=[DataRequired()])

    def validate_quantity(self, quantity):
        if quantity.data < 0:
            raise ValidationError('Invalid quantity.')

class CartQuantitiesForm(FlaskForm):
    quantities = FieldList(FormField(QuantityEntryForm), min_entries=1)
    submit = SubmitField('Done')



#addItem to Inventory form
class ItemForm(FlaskForm):
    name        = StringField('Name',validators=[DataRequired()])
    price       = DecimalField('Price',validators=[
        DataRequired(), 
        NumberRange(min=0.01, message="Must have a positive price.")])
    description = StringField('Description',validators=[
        DataRequired(), 
        Length(max=300)])
    stock       = IntegerField('Stock',validators=[
        DataRequired(), 
        NumberRange(min=1, message="Must have stock.")])
    image = FileField('Image')
    submit      = SubmitField('Submit',validators=[DataRequired()])


class WithdrawForm(FlaskForm):

    amount = FloatField('Withdraw Amount: ', [InputRequired()])
    withdraw = SubmitField('Withdraw Amount')

class DepositForm(FlaskForm):

    amount = FloatField('Deposit Amount: ', [InputRequired()])
    deposit = SubmitField('Deposit Amount')

class TransferForm(FlaskForm):

    account_id = IntegerField("Recipient's Account ID: ", [InputRequired()])
    amount = FloatField('Transfer Amount: ', [InputRequired()])
    password = PasswordField('Account password: ', [InputRequired()])
    transfer = SubmitField('Transfer Amount')
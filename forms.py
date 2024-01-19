from flask_wtf import FlaskForm
# from wtforms import validators
from wtforms.fields.simple import SubmitField, PasswordField, StringField
from wtforms.validators import DataRequired, Email, EqualTo, Length


class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()],render_kw={"placeholder": "Email"})
    password = PasswordField('Password', validators=[DataRequired(), Length(min=5, max=20)],render_kw={"placeholder": "Password"})
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')],render_kw={"placeholder": "Confirm Password"})

    register_field = SubmitField('Register') 


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()],render_kw={"placeholder": "Email"})
    password = PasswordField('Password', validators=[DataRequired(), Length(min=5, max=20)],render_kw={"placeholder": "Password"})

    login_field = SubmitField('Login')

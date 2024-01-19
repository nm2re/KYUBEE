from flask_bcrypt import Bcrypt
from flask import Flask, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user
from flask import render_template
from wtforms import ValidationError
from flask_wtf import FlaskForm
# from wtforms import validators
from wtforms.fields.simple import SubmitField, PasswordField, StringField
from wtforms.validators import DataRequired, Email, EqualTo, Length



app = Flask(__name__)
# -----------------------CONFIG--------------------------
app.config['SECRET_KEY'] = 'e728db02b86faeb0c569febd00886d06'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
# -----------------------INSTANCES-----------------------

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)




login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(id):
    return student_login.query.get(int(id))



# -----------------------DATABASE-----------------------   
class student_login(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    # f_name = db.Column(db.String(80), nullable=False)
    # l_name = db.Column(db.String(80), nullable=False)
    # department = db.Column(db.String(90), nullable=False)
    email = db.Column(db.String(80), nullable=False)
    password = db.Column(db.String(90), nullable=False)
    cookie = db.Column(db.String(90), nullable=False)


# class teacher_login(db.Model, UserMixin):
#     id = db.Column(db.Integer, primary_key=True)
#     f_name = db.Column(db.String(80), nullable=False)
#     l_name = db.Column(db.String(80), nullable=False)
#     department = db.Column(db.String(90), nullable=False)
#     email = db.Column(db.String(80), nullable=False)
#     password = db.Column(db.String(90), nullable=False)
#     cookie = db.Column(db.String(90), nullable=False)


class question_papers(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teacher_login.id'))
    date_created = db.Column(db.Date, nullable=False)


class questions(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    details = db.Column(db.String(90), nullable=False)
    qp_id = db.Column(db.Integer, db.ForeignKey('question_papers.id'))


class department(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(90), nullable=False)
    teacher_count = db.Column(db.Integer, nullable=False)


class notes(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(90), nullable=False)
    teacher_count = db.Column(db.Integer, nullable=False)





#------------------------FORMS-----------------------------
class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()],render_kw={"placeholder": "Email"})
    password = PasswordField('Password', validators=[DataRequired(), Length(min=5, max=20)],render_kw={"placeholder": "Password"})
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')],render_kw={"placeholder": "Confirm Password"})

    def validate_email(self, email):
        existing_user_email = student_login.query.filter_by(
            email=email.data).first()
        if existing_user_email:
            raise ValidationError(
                'That email already exists. Please choose a different one.')
            
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()],render_kw={"placeholder": "Email"})
    password = PasswordField('Password', validators=[DataRequired(), Length(min=5, max=20)],render_kw={"placeholder": "Password"})
    login_field = StringField('Login')




# ------------------------------ROUTES-------------------------------------
@app.route('/home',methods=['GET','POST'])
@login_required
def homepage():
    return render_template('dashboard.html')


@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = student_login.query.filter_by(email=form.email.data).first()
        if user:
            if bcrypt.check_password_hash(user.password,form.password.data):
                login_user(user)
                return redirect(url_for('homepage'))
    return render_template('login.html', form=form)


@app.route('/logout',methods=['GET','POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))



@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = student_login(email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html', form=form)




# main
if __name__ == '__main__':
    app.run(debug=True)

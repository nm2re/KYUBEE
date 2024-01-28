# import uuid
# from flask_bcrypt import Bcrypt
# from flask import Flask, redirect, url_for, request, flash
# from flask_sqlalchemy import SQLAlchemy
# from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user
# from flask import render_template
# import validators
# from wtforms import IntegerField, RadioField, ValidationError
# from flask_wtf import FlaskForm
# # from wtforms import validators
# from wtforms.fields.simple import SubmitField, PasswordField, StringField
# from wtforms.validators import DataRequired, Email, EqualTo, Length
# from flask_migrate import Migrate

# app = Flask(__name__)
# # -----------------------CONFIG--------------------------
# app.config['SECRET_KEY'] = 'e728db02b86faeb0c569febd00886d06'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
# # -----------------------INSTANCES-----------------------

# db = SQLAlchemy(app)
# migrate = Migrate(app, db)
# bcrypt = Bcrypt(app)

# login_manager = LoginManager()
# login_manager.init_app(app)
# login_manager.login_view = 'login'


# @login_manager.user_loader
# def load_user(id):
#     student_user = student_login.query.get(id)
#     teacher_user = teacher_login.query.get(id)
#     if student_user:
#         return student_user
#     elif teacher_user:
#         return teacher_user
#     # else:
#     #     None


# # -----------------------DATABASE-----------------------
# class student_login(db.Model, UserMixin):
#     ID = db.Column(db.String(36), primary_key=True, default=str(uuid.uuid4()), unique=True)
#     EMAIL = db.Column(db.String(80), nullable=False)
#     PASSWORD = db.Column(db.String(90), nullable=False)

#     def get_id(self):
#         return str(self.ID)  # Since ID field name is not id


# class teacher_login(db.Model, UserMixin):
#     ID = db.Column(db.String(36), primary_key=True, default=str(uuid.uuid4()), unique=True)
#     EMAIL = db.Column(db.String(80), nullable=False)
#     PASSWORD = db.Column(db.String(90), nullable=False)

#     def get_id(self):
#         return str(self.ID)


# class students(db.Model, UserMixin):
#     STUDENT_ID = db.Column(db.String(36), primary_key=True, default=str(uuid.uuid4()), unique=True)
#     STUDENT_EMAIL = db.Column(db.String(80), nullable=False)
#     FIRST_NAME = db.Column(db.String(80))
#     LAST_NAME = db.Column(db.String(80))
#     DEPARTMENT_ID = db.Column(db.Integer, db.ForeignKey('department.DEPARTMENT_ID'))
#     PHONE_NUMBER = db.Column(db.Integer)


# class teachers(db.Model, UserMixin):
#     TEACHER_ID = db.Column(db.String(36), primary_key=True, default=str(uuid.uuid4()), unique=True)
#     TEACHER_EMAIL = db.Column(db.String(80), nullable=False)
#     FIRST_NAME = db.Column(db.String(80))
#     LAST_NAME = db.Column(db.String(80))
#     DEPARTMENT_ID = db.Column(db.Integer, db.ForeignKey('department.DEPARTMENT_ID'))
#     PHONE_NUMBER = db.Column(db.Integer)


# class question_papers(db.Model, UserMixin):
#     QP_ID = db.Column(db.String(36), primary_key=True, default=str(uuid.uuid4()), unique=True)
#     TEACHER_ID = db.Column(db.Integer, db.ForeignKey('teachers.TEACHER_ID'))
#     FILE_TYPE = db.Column(db.String(10), nullable=False)
#     DATE_CREATED = db.Column(db.Date, nullable=False)


# class questions(db.Model, UserMixin):
#     Q_ID = db.Column(db.Integer, primary_key=True)
#     Q_DETAILS = db.Column(db.String(90), nullable=False)
#     Q_TAGS = db.Column(db.JSON,nullable=False)
#     QP_ID = db.Column(db.Integer, db.ForeignKey('question_papers.QP_ID'))


# class department(db.Model, UserMixin):
#     DEPARTMENT_ID = db.Column(db.Integer, primary_key=True)
#     DEPARTMENT_NAME = db.Column(db.String(90), nullable=False)
#     TEACHER_COUNT = db.Column(db.Integer, nullable=False)


# class notes(db.Model, UserMixin):
#     NOTE_ID = db.Column(db.String(36), primary_key=True, default=str(uuid.uuid4()), unique=True)
#     NOTE_NAME = db.Column(db.String(90), nullable=False)
#     TEACHER_ID = db.Column(db.Integer, db.ForeignKey('teachers.TEACHER_ID'))
#     DEPARTMENT_ID = db.Column(db.Integer, db.ForeignKey('department.DEPARTMENT_ID'))
#     DATE_ADDED = db.Column(db.Date,nullable=False)


# # ------------------------FORMS-----------------------------
# class RegistrationForm(FlaskForm):
#     email = StringField('Email', validators=[DataRequired(), Email()], render_kw={"placeholder": "Email"})
#     password = PasswordField('Password', validators=[DataRequired(), Length(min=5, max=20)],
#                              render_kw={"placeholder": "Password"})
#     confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')],
#                                      render_kw={"placeholder": "Confirm Password"})

#     # options = RadioField('Options',choices=[('option1','option2')])

#     def validate_email(self, email):
#         existing_student_email = student_login.query.filter_by(
#             EMAIL=email.data).first()

#         existing_teacher_email = teacher_login.query.filter_by(
#             EMAIL=email.data).first()

#         if existing_student_email or existing_teacher_email:
#             flash('This email already exists')
#             raise ValidationError(
#                 'That email already exists. Please choose a different one.')


# class LoginForm(FlaskForm):
#     email = StringField('Email', validators=[DataRequired(), Email()], render_kw={"placeholder": "Email"})
#     password = PasswordField('Password', validators=[DataRequired(), Length(min=5, max=20)],
#                              render_kw={"placeholder": "Password"})
#     login_field = StringField('Login')


# class ProfileForm(FlaskForm):
#     # username = StringField('Username', validators=[DataRequired(), Length(min=2, max=10)],render_kw={"placeholder": "Username"})
#     first_name = StringField('First Name', validators=[DataRequired(), Length(min=2, max=10)],
#                              render_kw={"placeholder": "First Name"})
#     last_name = StringField('Last Name', validators=[DataRequired(), Length(min=2, max=10)],
#                             render_kw={"placeholder": "Last Name"})
#     department = StringField('Department', validators=[DataRequired(), Length(min=3, max=15)],
#                              render_kw={"placeholder": "Department"})
#     phone_number = IntegerField('Telephone', validators=[DataRequired()], render_kw={"placeholder": "Phone Number"})


# # ------------------------------ROUTES-------------------------------------
# @app.route('/dashboard/<string:user_type>/<string:user_id>', methods=['GET', 'POST'])
# @login_required
# def dashboard(user_type, user_id):
#     if user_type == 'Student':
#         logged_user = student_login.query.get(user_id)
#     elif user_type == 'Teacher':
#         logged_user = teacher_login.query.get(user_id)

#     if logged_user:
#         flash(f"Email: {logged_user.EMAIL}", 'info')
#     else:
#         flash('User not found', 'error')

#     return render_template('dashboard.html', user_type=user_type, user_id=user_id)


# @app.route('/studentprofile/<login_uuid>', methods=['GET', 'POST'])
# def student_profile(login_uuid):
#     form = ProfileForm()
#     print(login_uuid)

#     if form.validate_on_submit():
        
#         db.session.query(students).filter_by(STUDENT_ID=login_uuid).update({"FIRST_NAME": form.first_name.data, "LAST_NAME": form.last_name.data,"DEPARTMENT_ID": form.department.data, "PHONE_NUMBER": form.phone_number.data})
        
#         db.session.commit()
#         return redirect(url_for('login'))
#     else:
#         print('hello')
#         print(form.errors)
#     return render_template('studentprofile.html', form=form, login_uuid=login_uuid)


# @app.route('/teacherprofile', methods=['GET', 'POST'])
# def teacher_profile():
#     form = ProfileForm()

#     if form.validate_on_submit():
#         user = teachers(FIRST_NAME=form.first_name.data, LAST_NAME=form.last_name.data, DEPARTMENT_ID=form.department.data,
#                         PHONE_NUMBER=form.phone_number.data)
#         if user:
#             db.session.add(user)
#             db.session.commit()
#             return redirect(url_for('login'))
#     return render_template('teacherprofile.html', form=form)


# @app.route('/')
# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     form = LoginForm()
#     if form.validate_on_submit():

#         # selected_user = request.form.get('users')
#         # print(selected_user)

#         # if selected_user == 'Student':
#         student_user = student_login.query.filter_by(EMAIL=form.email.data).first()
#         if student_user:
#             if bcrypt.check_password_hash(student_user.PASSWORD, form.password.data):
#                 login_user(student_user)
#                 return redirect(url_for('dashboard', user_type='Student', user_id=student_user.ID))
#     # elif selected_user == 'Teacher':
#         else:
#             teacher_user = teacher_login.query.filter_by(EMAIL=form.email.data).first()
#             if bcrypt.check_password_hash(teacher_user.PASSWORD, form.password.data):
#                 login_user(teacher_user)
#                 return redirect(url_for('dashboard', user_type='Teacher', user_id=teacher_user.ID))
#     return render_template('login.html', form=form)


# @app.route('/logout', methods=['GET', 'POST'])
# @login_required
# def logout():
#     logout_user()
#     return redirect(url_for('login'))


# @app.route('/register', methods=['GET', 'POST'])
# def register():
#     form = RegistrationForm()

#     if form.validate_on_submit():
#         selected_user = request.form.get('users')
#         hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')

#         print(f"---{selected_user}-------")
#         print(request.form)
#         if selected_user == "Student":
            
#             login_uuid = str(uuid.uuid4())
#             user = student_login(ID=login_uuid,EMAIL=form.email.data, PASSWORD=hashed_password)
#             db.session.add(user)
            
#             user_details = students(STUDENT_ID=login_uuid,STUDENT_EMAIL = form.email.data)
#             db.session.add(user_details)
#             db.session.commit()
#             return redirect(url_for('student_profile',login_uuid=login_uuid))

#         elif selected_user == "Teacher":
#             user = teacher_login(EMAIL=form.email.data, PASSWORD=hashed_password)
#             db.session.add(user)
#             db.session.commit()
#             return redirect(url_for('teacher_profile'))
#         else:
#             print(form.errors)

#     return render_template('register.html', form=form)


# # main
# if __name__ == '__main__':
#     app.run(debug=True)

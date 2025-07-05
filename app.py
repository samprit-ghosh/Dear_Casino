from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta, date
from pytz import timezone
from dateutil.relativedelta import relativedelta
import bcrypt
import requests
import re



# Create a timezone-aware UTC datetime


# Load environment variables from .env file
load_dotenv()

# Create a Flask app
app = Flask(__name__)

# app.secret_key = '0df660dd7e2503a4'

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
global_array = [10, "Apple", 20, "Banana", 30, "Cherry"]

@app.context_processor
def inject_globals():
    return dict(global_array=global_array)

# Nagaland Satta -> 10 Slots -> 10:20-7:20 (1 hr)
# Dear Fatafat -> 8 Slots -> 10:30-9:00 (1.5 hr)

# 10:00 AM
# 11:00 AM
# 12:00 PM
# 01:00 PM
# 02:00 PM
# 03:00 PM
# 04:00 PM
# 05:00 PM
# 06:00 PM
# 07:00 PM
# db.create_all()


class Nagaland_Result(db.Model):
    __tablename__ = "nagaland"
    id = db.Column(db.Integer, primary_key=True)
    
    # 10 columns for 1-digit results
    slot1_digit = db.Column(db.String(1), nullable=True)
    slot2_digit = db.Column(db.String(1), nullable=True)
    slot3_digit = db.Column(db.String(1), nullable=True)
    slot4_digit = db.Column(db.String(1), nullable=True)
    slot5_digit = db.Column(db.String(1), nullable=True)
    slot6_digit = db.Column(db.String(1), nullable=True)
    slot7_digit = db.Column(db.String(1), nullable=True)
    slot8_digit = db.Column(db.String(1), nullable=True)
    slot9_digit = db.Column(db.String(1), nullable=True)
    slot10_digit = db.Column(db.String(1), nullable=True)
    
    # 10 columns for 3-digit results
    slot1_number = db.Column(db.String(3), nullable=True)
    slot2_number = db.Column(db.String(3), nullable=True)
    slot3_number = db.Column(db.String(3), nullable=True)
    slot4_number = db.Column(db.String(3), nullable=True)
    slot5_number = db.Column(db.String(3), nullable=True)
    slot6_number = db.Column(db.String(3), nullable=True)
    slot7_number = db.Column(db.String(3), nullable=True)
    slot8_number = db.Column(db.String(3), nullable=True)
    slot9_number = db.Column(db.String(3), nullable=True)
    slot10_number = db.Column(db.String(3), nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.now(timezone("Asia/Kolkata")))
    
    # Helper method to get formatted date string
    def get_formatted_date(self):
        return self.created_at.strftime('%d-%b-%Y(%a)')
        
    # Helper method to check if date matches a specific day
    def is_same_day(self, target_date):
        return (self.created_at.year == target_date.year and 
                self.created_at.month == target_date.month and 
                self.created_at.day == target_date.day)


class Fatafat_Result(db.Model):
    __tablename__ = "fatafat"
    id = db.Column(db.Integer, primary_key=True)
    
    # 8 columns for 1-digit results
    slot1_digit = db.Column(db.String(1), nullable=True)
    slot2_digit = db.Column(db.String(1), nullable=True)
    slot3_digit = db.Column(db.String(1), nullable=True)
    slot4_digit = db.Column(db.String(1), nullable=True)
    slot5_digit = db.Column(db.String(1), nullable=True)
    slot6_digit = db.Column(db.String(1), nullable=True)
    slot7_digit = db.Column(db.String(1), nullable=True)
    slot8_digit = db.Column(db.String(1), nullable=True)
    
    # 8 columns for 3-digit results
    slot1_number = db.Column(db.String(3), nullable=True)
    slot2_number = db.Column(db.String(3), nullable=True)
    slot3_number = db.Column(db.String(3), nullable=True)
    slot4_number = db.Column(db.String(3), nullable=True)
    slot5_number = db.Column(db.String(3), nullable=True)
    slot6_number = db.Column(db.String(3), nullable=True)
    slot7_number = db.Column(db.String(3), nullable=True)
    slot8_number = db.Column(db.String(3), nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.now(timezone("Asia/Kolkata")))
    
    # Helper method to get formatted date string
    def get_formatted_date(self):
        return self.created_at.strftime('%d-%b-%Y(%a)')
    
    # Helper method to check if date matches a specific day
    def is_same_day(self, target_date):
        return (self.created_at.year == target_date.year and 
                self.created_at.month == target_date.month and 
                self.created_at.day == target_date.day)


class MarqueeText(db.Model):
    __tablename__ = "marquee_text"
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(500), nullable=False, default="Welcome to our site!")
    is_active = db.Column(db.Boolean, default=True)
    scroll_speed = db.Column(db.Integer, default=6)  # HTML marquee scrollamount value
    created_at = db.Column(db.DateTime, default=datetime.now(timezone("Asia/Kolkata")))
    updated_at = db.Column(db.DateTime, default=datetime.now(timezone("Asia/Kolkata")), onupdate=datetime.now(timezone("Asia/Kolkata")))
    
    @classmethod
    def get_active(cls):
        return cls.query.filter_by(is_active=True).first()


# Get the admin password from the environment variable
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD')


# @app.route('/delete_old_results', methods=['POST'])
# def delete_old_results():
#     old_results = datetime.now(timezone("Asia/Kolkata")) - relativedelta(months=2)
#     old_results = old_results.strftime('%d-%m-%Y')
#     old_results = Result.query.filter(Result.date.like(f"%{old_results}%")).all()
        
#     if old_results:
#         for data in old_results:
#             db.session.delete(data)
#         db.session.commit()

@app.route('/delete_old_results', methods=['GET', 'POST'])
def delete_old_results():
    # Calculate the date cutoffs
    now = datetime.now(timezone("Asia/Kolkata"))
    cutoff_1 = now - relativedelta(months=1)
    cutoff_2 = now - relativedelta(months=2)
    cutoff_3 = now - relativedelta(months=3)
    cutoff_4 = now - relativedelta(months=4)
    cutoff_5 = now - relativedelta(months=5)
    cutoff_6 = now - relativedelta(months=6)

    # Query records older than the cutoff dates
    old_results_1 = Nagaland_Result.query.filter(Nagaland_Result.created_at < cutoff_1).all()
    old_results_2 = Nagaland_Result.query.filter(Nagaland_Result.created_at < cutoff_2).all()
    old_results_3 = Nagaland_Result.query.filter(Nagaland_Result.created_at < cutoff_3).all()
    old_results_4 = Nagaland_Result.query.filter(Nagaland_Result.created_at < cutoff_4).all()
    old_results_5 = Nagaland_Result.query.filter(Nagaland_Result.created_at < cutoff_5).all()
    old_results_6 = Nagaland_Result.query.filter(Nagaland_Result.created_at < cutoff_6).all()

    # Delete the old records
    if old_results_1:
        for data in old_results_1:
            db.session.delete(data)
        db.session.commit()

    if old_results_2:
        for data in old_results_2:
            db.session.delete(data)
        db.session.commit()

    if old_results_3:
        for data in old_results_3:
            db.session.delete(data)
        db.session.commit()

    if old_results_4:
        for data in old_results_4:
            db.session.delete(data)
        db.session.commit()

    if old_results_5:
        for data in old_results_5:
            db.session.delete(data)
        db.session.commit()

    if old_results_6:
        for data in old_results_6:
            db.session.delete(data)
        db.session.commit()

    # Similarly update for Extra table queries using date field - not changing yet
    cutoff_1_str = cutoff_1.strftime('%b-%Y')
    cutoff_2_str = cutoff_2.strftime('%b-%Y')  
    cutoff_3_str = cutoff_3.strftime('%b-%Y')
    cutoff_4_str = cutoff_4.strftime('%b-%Y')
    cutoff_5_str = cutoff_5.strftime('%b-%Y')
    cutoff_6_str = cutoff_6.strftime('%b-%Y')

    # old_extras_1 = Extra.query.filter(Extra.date.like(f"%{cutoff_1_str}%")).all()
    # old_extras_2 = Extra.query.filter(Extra.date.like(f"%{cutoff_2_str}%")).all()
    # old_extras_3 = Extra.query.filter(Extra.date.like(f"%{cutoff_3_str}%")).all()
    # old_extras_4 = Extra.query.filter(Extra.date.like(f"%{cutoff_4_str}%")).all()
    # old_extras_5 = Extra.query.filter(Extra.date.like(f"%{cutoff_5_str}%")).all()
    # old_extras_6 = Extra.query.filter(Extra.date.like(f"%{cutoff_6_str}%")).all()

    # # Delete the old records
    # if old_extras_1:
    #     for data in old_extras_1:
    #         db.session.delete(data)
    #     db.session.commit()

    # if old_extras_2:
    #     for data in old_extras_2:
    #         db.session.delete(data)
    #     db.session.commit()

    # if old_extras_3:
    #     for data in old_extras_3:
    #         db.session.delete(data)
    #     db.session.commit()

    # if old_extras_4:
    #     for data in old_extras_4:
    #         db.session.delete(data)
    #     db.session.commit()

    # if old_extras_5:
    #     for data in old_extras_5:
    #         db.session.delete(data)
    #     db.session.commit()

    # if old_extras_6:
    #     for data in old_extras_6:
    #         db.session.delete(data)
    #     db.session.commit()

    return redirect(url_for('home'))



@app.route("/")
def home():
    results = Nagaland_Result.query.order_by(Nagaland_Result.created_at.desc()).all()

    now = datetime.now(timezone("Asia/Kolkata"))
    
    # Get today's data
    # Get start and end of today
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = now.replace(hour=23, minute=59, second=59, microsecond=999999)
    
    daily_data = Nagaland_Result.query.filter(
        Nagaland_Result.created_at >= today_start,
        Nagaland_Result.created_at <= today_end
    ).first()
    
    # daily_extra = Extra.query.filter_by(date=now.strftime('%d-%b-%Y(%a)')).first()

    # Matka Results (last 7 days)
    g_matka_results = []
    for i in range(7):
        day = now - relativedelta(days=i)
        day_start = day.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        result = Nagaland_Result.query.filter(
            Nagaland_Result.created_at >= day_start,
            Nagaland_Result.created_at <= day_end
        ).first()
        g_matka_results.append(result)

    # Night Results (last 7 days)
    g_night_results = []
    for i in range(7):
        day = now - relativedelta(days=i)
        formatted_day = day.strftime('%d-%b-%Y(%a)')
        # result = Extra.query.filter_by(date=formatted_day).first()
        g_night_results.append(result)

    # Slot times
    start_time = {f'slot{i}': now.replace(hour=9+i, minute=0, second=0, microsecond=0) for i in range(1, 11)}
    end_time = {f'slot{i}': now.replace(hour=9+i, minute=55, second=0, microsecond=0) for i in range(1, 11)}

    # Get active marquee text
    active_marquee = MarqueeText.get_active()  








    return render_template('index.html',
                          g_matka_results=g_matka_results,
                          g_night_results=g_night_results,
                       
                          results=results,
                        #   extra=daily_extra,
                          now=now,
                          start_time=start_time,
                          end_time=end_time,
                          daily_data=daily_data,
                          active_marquee=active_marquee,
                          title="Fastest and Live Online Goa Satta Result only at goasatta.in")


def check_password(plain_password: str, hashed_password: str) -> bool:
    # Compare the plain password with the hashed password
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))




@app.route("/admin_auth", methods=['GET', 'POST'])
def admin_auth():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if not password:
            flash("Password is required")
            return redirect(url_for('admin_auth'))
        
        if username == "admin" and check_password(password, ADMIN_PASSWORD):
            session['admin'] = True
            return redirect(url_for('admin'))
        else:
            flash("Invalid Password. Try Again!!!")
            return redirect(url_for('admin_auth')) 
    return render_template('login.html', title="Admin Login")


@app.route("/admin")
def admin():
    if 'admin' in session:
        now = datetime.now(timezone("Asia/Kolkata"))
        
        # Get today's data
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = now.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        daily_data_nagaland = Nagaland_Result.query.filter(
            Nagaland_Result.created_at >= today_start,
            Nagaland_Result.created_at <= today_end
        ).first()

        daily_data_fatafat = Fatafat_Result.query.filter(
            Fatafat_Result.created_at >= today_start,
            Fatafat_Result.created_at <= today_end
        ).first()

        marquee_texts = MarqueeText.query.order_by(MarqueeText.created_at.desc()).all()

        return render_template('admin.html', daily_data_nagaland=daily_data_nagaland, daily_data_fatafat=daily_data_fatafat, title="Admin Panel", marquee_texts=marquee_texts)
    return redirect(url_for('admin_auth'))
    

@app.route('/add_nagaland', methods=['POST'])
def add_nagaland():
    now = datetime.now(timezone("Asia/Kolkata"))
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = now.replace(hour=23, minute=59, second=59, microsecond=999999)
    
    daily_data = Nagaland_Result.query.filter(
        Nagaland_Result.created_at >= today_start,
        Nagaland_Result.created_at <= today_end
    ).first()

    if not daily_data:
        # Create a new record - the created_at will have default value
        daily_data = Nagaland_Result()

    slot = request.form['slots']
    value_digit = request.form['one_digit']
    value_number = request.form['three_digit']

    if slot == '1':
        daily_data.slot1_digit = value_digit
        daily_data.slot1_number = value_number
    elif slot == '2':
        daily_data.slot2_digit = value_digit
        daily_data.slot2_number = value_number
    elif slot == '3':
        daily_data.slot3_digit = value_digit
        daily_data.slot3_number = value_number
    elif slot == '4':
        daily_data.slot4_digit = value_digit
        daily_data.slot4_number = value_number
    elif slot == '5':
        daily_data.slot5_digit = value_digit
        daily_data.slot5_number = value_number
    elif slot == '6':
        daily_data.slot6_digit = value_digit
        daily_data.slot6_number = value_number
    elif slot == '7':
        daily_data.slot7_digit = value_digit
        daily_data.slot7_number = value_number
    elif slot == '8':
        daily_data.slot8_digit = value_digit
        daily_data.slot8_number = value_number
    elif slot == '9':
        daily_data.slot9_digit = value_digit
        daily_data.slot9_number = value_number
    elif slot == '10':
        daily_data.slot10_digit = value_digit
        daily_data.slot10_number = value_number

    db.session.add(daily_data)
    db.session.commit()
    return redirect('/admin')


@app.route('/add_fatafat', methods=['POST'])
def add_fatafat():
    now = datetime.now(timezone("Asia/Kolkata"))
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = now.replace(hour=23, minute=59, second=59, microsecond=999999)
    
    daily_data = Fatafat_Result.query.filter(
        Fatafat_Result.created_at >= today_start,
        Fatafat_Result.created_at <= today_end
    ).first()

    if not daily_data:
        # Create a new record - the created_at will have default value
        daily_data = Fatafat_Result()

    slot = request.form['slots']
    value_digit = request.form['one_digit']
    value_number = request.form['three_digit']

    if slot == '1':
        daily_data.slot1_digit = value_digit
        daily_data.slot1_number = value_number
    elif slot == '2':
        daily_data.slot2_digit = value_digit
        daily_data.slot2_number = value_number
    elif slot == '3':
        daily_data.slot3_digit = value_digit
        daily_data.slot3_number = value_number
    elif slot == '4':
        daily_data.slot4_digit = value_digit
        daily_data.slot4_number = value_number
    elif slot == '5':
        daily_data.slot5_digit = value_digit
        daily_data.slot5_number = value_number
    elif slot == '6':
        daily_data.slot6_digit = value_digit
        daily_data.slot6_number = value_number
    elif slot == '7':
        daily_data.slot7_digit = value_digit
        daily_data.slot7_number = value_number
    elif slot == '8':
        daily_data.slot8_digit = value_digit
        daily_data.slot8_number = value_number

    db.session.add(daily_data)
    db.session.commit()
    return redirect('/admin')


@app.route('/update/<game>/<int:slot>', methods=['GET', 'POST'])
def update(game, slot):
    if 'admin' in session:
        now = datetime.now(timezone("Asia/Kolkata"))
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = now.replace(hour=23, minute=59, second=59, microsecond=999999)

        if game == "nagaland":
            daily_data = Nagaland_Result.query.filter(
                Nagaland_Result.created_at >= today_start,
                Nagaland_Result.created_at <= today_end
            ).first()
        
        elif game == "fatafat":
            daily_data = Fatafat_Result.query.filter(
                Fatafat_Result.created_at >= today_start,
                Fatafat_Result.created_at <= today_end
            ).first()

        slot_digit = f'slot{slot}_digit'
        slot_number = f'slot{slot}_number'

        one = getattr(daily_data, slot_digit)
        three = getattr(daily_data, slot_number)

        if request.method=='POST':
            oneDigi = request.form['oneDigi']
            threeDigi = request.form['threeDigi']
            setattr(daily_data, slot_digit, oneDigi)
            setattr(daily_data, slot_number, threeDigi)
            db.session.commit()
            return redirect('/admin')
        return render_template('update.html', game=game, one = one, three = three, slot=slot, title="Edit Result")
    return redirect(url_for('admin_auth'))


@app.route('/delete/<game>/<int:slot>', methods=['GET', 'POST'])
def delete(game, slot):
    if 'admin' in session:
        now = datetime.now(timezone("Asia/Kolkata"))
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = now.replace(hour=23, minute=59, second=59, microsecond=999999)

        if game == "nagaland":
            daily_data = Nagaland_Result.query.filter(
                Nagaland_Result.created_at >= today_start,
                Nagaland_Result.created_at <= today_end
            ).first()
        elif game == "fatafat":
            daily_data = Fatafat_Result.query.filter(
                Fatafat_Result.created_at >= today_start,
                Fatafat_Result.created_at <= today_end
            ).first()

        slot_digit = f'slot{slot}_digit'
        slot_number = f'slot{slot}_number'

        setattr(daily_data, slot_digit, None)
        setattr(daily_data, slot_number, None)
        db.session.commit()
        return redirect('/admin')
    return redirect(url_for('admin_auth'))


@app.route('/add_marquee', methods=['POST'])
def add_marquee():
    if 'admin' in session:
        if request.method == 'POST':
            marquee_text = request.form['marquee_text']
            print(marquee_text)
            if not marquee_text:
                flash("Marquee text cannot be empty")
                return redirect(url_for('admin_marquee'))
            new_marquee = MarqueeText(content=marquee_text, is_active=True)
            db.session.add(new_marquee)
            db.session.commit()
        return redirect('/admin')
    return redirect(url_for('admin_auth'))



@app.route('/update/marquee/<int:id>', methods=['GET', 'POST'])
def update_marquee(id):
    if 'admin' in session:
        marquee_to_update = MarqueeText.query.filter(MarqueeText.id == id).first()
        if request.method=='POST':
            updated_marquee_text = request.form['marquee_text']
            updated_marquee_status = request.form['marquee_status']
            marquee_to_update.content = updated_marquee_text
            if updated_marquee_status == "Enable":
                marquee_to_update.is_active = True
            elif updated_marquee_status == "Disable":
                marquee_to_update.is_active = False
            db.session.commit()
            return redirect('/admin')
        return render_template('update_marquee.html', title="Edit Marquee", marquee_to_update=marquee_to_update, status=marquee_to_update.is_active)
    return redirect(url_for('admin_auth'))


@app.route('/delete/marquee/<int:id>', methods=['GET', 'POST'])
def delete_marquee(id):
    if 'admin' in session:
        marquee_to_delete = MarqueeText.query.filter(MarqueeText.id == id).first()
        if marquee_to_delete:
            db.session.delete(marquee_to_delete)
            db.session.commit()
        return redirect('/admin')
    return redirect(url_for('admin_auth'))


@app.route('/admin_logout')
def logout():
    session.pop('admin', None)
    return redirect(url_for('admin_auth'))


@app.route("/admin/marquee", methods=['GET', 'POST'])
def admin_marquee():
    if 'admin' not in session:
        return redirect(url_for('admin_auth'))
        
    marquee_texts = MarqueeText.query.order_by(MarqueeText.created_at.desc()).all()
    active_marquee = MarqueeText.get_active()
    
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'add':
            content = request.form.get('content')
            speed = request.form.get('speed', 6, type=int)
            
            # If no active marquee exists, make this one active
            is_active = True if not active_marquee else False
            
            new_marquee = MarqueeText()
            new_marquee.content = content
            new_marquee.scroll_speed = speed
            new_marquee.is_active = is_active
            
            db.session.add(new_marquee)
            db.session.commit()
            flash("New marquee text added successfully!")
            return redirect(url_for('admin_marquee'))
            
        elif action == 'update':
            marquee_id = request.form.get('id', type=int)
            marquee = MarqueeText.query.get(marquee_id)
            
            if marquee:
                marquee.content = request.form.get('content')
                marquee.scroll_speed = request.form.get('speed', 6, type=int)
                db.session.commit()
                flash("Marquee updated successfully!")
            
            return redirect(url_for('admin_marquee'))
            
        elif action == 'set_active':
            marquee_id = request.form.get('id', type=int)
            
            # First, deactivate all marquees
            all_marquees = MarqueeText.query.all()
            for m in all_marquees:
                m.is_active = False
            
            # Then activate the selected one
            marquee = MarqueeText.query.get(marquee_id)
            if marquee:
                marquee.is_active = True
                flash("Marquee set as active!")
                
            db.session.commit()
            return redirect(url_for('admin_marquee'))
            
        elif action == 'delete':
            marquee_id = request.form.get('id', type=int)
            marquee = MarqueeText.query.get(marquee_id)
            
            if marquee:
                db.session.delete(marquee)
                db.session.commit()
                flash("Marquee deleted!")
                
            return redirect(url_for('admin_marquee'))
    
    return render_template('admin_marquee.html', marquee_texts=marquee_texts, active_marquee=active_marquee, title="Manage Marquee Text")


@app.route("/about")
def about():
    return render_template('about.html', title="About Us")

@app.route("/text")
def text():
    
    results = Nagaland_Result.query.order_by(Nagaland_Result.id.desc()).all()

    now = datetime.now(timezone("Asia/Kolkata"))

    # Get today's data
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = now.replace(hour=23, minute=59, second=59, microsecond=999999)
    
    daily_data = Nagaland_Result.query.filter(
        Nagaland_Result.created_at >= today_start,
        Nagaland_Result.created_at <= today_end
    ).first()
    
    # daily_extra = Extra.query.filter_by(date=now.strftime('%d-%b-%Y(%a)')).first()

    start_time = {
    'slot1' : now.replace(hour=10, minute=0, second=0, microsecond=0),
    'slot2' : now.replace(hour=11, minute=0, second=0, microsecond=0),
    'slot3' : now.replace(hour=12, minute=0, second=0, microsecond=0),
    'slot4' : now.replace(hour=13, minute=0, second=0, microsecond=0),
    'slot5' : now.replace(hour=14, minute=0, second=0, microsecond=0),
    'slot6' : now.replace(hour=15, minute=0, second=0, microsecond=0),
    'slot7' : now.replace(hour=16, minute=0, second=0, microsecond=0),
    'slot8' : now.replace(hour=17, minute=0, second=0, microsecond=0),
    'slot9' : now.replace(hour=18, minute=0, second=0, microsecond=0),
    'slot10' : now.replace(hour=19, minute=0, second=0, microsecond=0)
    }

    end_time = {
    'slot1' : now.replace(hour=10, minute=55, second=0, microsecond=0),
    'slot2' : now.replace(hour=11, minute=55, second=0, microsecond=0),
    'slot3' : now.replace(hour=12, minute=55, second=0, microsecond=0),
    'slot4' : now.replace(hour=13, minute=55, second=0, microsecond=0),
    'slot5' : now.replace(hour=14, minute=55, second=0, microsecond=0),
    'slot6' : now.replace(hour=15, minute=55, second=0, microsecond=0),
    'slot7' : now.replace(hour=16, minute=55, second=0, microsecond=0),
    'slot8' : now.replace(hour=17, minute=55, second=0, microsecond=0),
    'slot9' : now.replace(hour=18, minute=55, second=0, microsecond=0),
    'slot10' : now.replace(hour=19, minute=55, second=0, microsecond=0),
    }

    return render_template('text.html', 
                           
        results=results, now=now, start_time=start_time, end_time=end_time, daily_data=daily_data, title="Fastest and Live Online Goa Satta Result only at goasatta.in")




# @app.route("/online")
# def online():
#     return render_template('online.html', title="Play Online")

@app.route("/contact")
def contact():
    return render_template('Contact.html', title="Contact Us")

@app.route("/old")
def old():
      matka_results = Nagaland_Result.query.order_by(Nagaland_Result.created_at.desc()).limit(31).all()
    #   night_results = Extra.query.order_by(Extra.id.desc()).limit(31).all()
      return render_template('old.html', matka_results=matka_results, title="Old Result")
if __name__ == '__main__':
    app.run(debug=True)
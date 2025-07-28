from flask import Flask, render_template, request, redirect, url_for, session, flash, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta, date
from pytz import timezone
from dateutil.relativedelta import relativedelta
import bcrypt
import requests
import re
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

# Create a Flask app
app = Flask(__name__)

# App configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)

db = SQLAlchemy(app)

# Global variables
global_array = [10, "Apple", 20, "Banana", 30, "Cherry"]
months_for_old_results = 3
days_for_results = 7
to_months_delete_results = 4
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD')

# Context processors
@app.context_processor
def inject_globals():
    return dict(
        global_array=global_array,
        now=datetime.now(timezone("Asia/Kolkata"))
    )

# Models (same as before)
class Nagaland_Result(db.Model):
    __tablename__ = "nagaland"
    id = db.Column(db.Integer, primary_key=True)
    
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
    
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone("Asia/Kolkata")))
    
    def get_formatted_date(self):
        return self.created_at.strftime('%d-%b-%Y(%a)')
        
    def is_same_day(self, target_date):
        return (self.created_at.year == target_date.year and 
                self.created_at.month == target_date.month and 
                self.created_at.day == target_date.day)

class Fatafat_Result(db.Model):
    __tablename__ = "fatafat"
    id = db.Column(db.Integer, primary_key=True)
    
    slot1_digit = db.Column(db.String(1), nullable=True)
    slot2_digit = db.Column(db.String(1), nullable=True)
    slot3_digit = db.Column(db.String(1), nullable=True)
    slot4_digit = db.Column(db.String(1), nullable=True)
    slot5_digit = db.Column(db.String(1), nullable=True)
    slot6_digit = db.Column(db.String(1), nullable=True)
    slot7_digit = db.Column(db.String(1), nullable=True)
    slot8_digit = db.Column(db.String(1), nullable=True)
    
    slot1_number = db.Column(db.String(3), nullable=True)
    slot2_number = db.Column(db.String(3), nullable=True)
    slot3_number = db.Column(db.String(3), nullable=True)
    slot4_number = db.Column(db.String(3), nullable=True)
    slot5_number = db.Column(db.String(3), nullable=True)
    slot6_number = db.Column(db.String(3), nullable=True)
    slot7_number = db.Column(db.String(3), nullable=True)
    slot8_number = db.Column(db.String(3), nullable=True)
    
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone("Asia/Kolkata")))
    
    def get_formatted_date(self):
        return self.created_at.strftime('%d-%b-%Y(%a)')
    
    def is_same_day(self, target_date):
        return (self.created_at.year == target_date.year and 
                self.created_at.month == target_date.month and 
                self.created_at.day == target_date.day)

class MarqueeText(db.Model):
    __tablename__ = "marquee_text"
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(500), nullable=False, default="Welcome to our site!")
    is_active = db.Column(db.Boolean, default=True)
    scroll_speed = db.Column(db.Integer, default=6)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone("Asia/Kolkata")))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone("Asia/Kolkata")), 
                         onupdate=lambda: datetime.now(timezone("Asia/Kolkata")))
    
    @classmethod
    def get_active(cls):
        return cls.query.filter_by(is_active=True).all()

# Helper functions
def get_current_datetime():
    return datetime.now(timezone("Asia/Kolkata"))

def get_today_range():
    now = get_current_datetime()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = now.replace(hour=23, minute=59, second=59, microsecond=999999)
    return today_start, today_end

def check_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def get_current_fatafat_slot(now=None):
    if not now:
        now = get_current_datetime()
    slot_start = now.replace(hour=10, minute=30, second=0, microsecond=0)
    for i in range(8):
        start = slot_start + timedelta(hours=i, minutes=i*30)
        end = start + timedelta(hours=1, minutes=30)
        show_until = start + timedelta(minutes=40)
        if start <= now < end:
            return {
                "slot_num": i + 1,
                "show_result": now < show_until
            }
    return None

def get_current_nagaland_slot(now=None):
    if not now:
        now = get_current_datetime()
    slot_start = now.replace(hour=10, minute=20, second=0, microsecond=0)
    for i in range(10):
        start = slot_start + timedelta(hours=i)
        end = start + timedelta(hours=1)
        show_until = start + timedelta(minutes=40)
        if start <= now < end:
            return {
                "slot_num": i + 1,
                "show_result": now < show_until
            }
    return None

# Routes
@app.route('/googlee5a35d73d550fdce.html')
def google_verification():
    return send_from_directory(os.path.abspath('.'), 'googlee5a35d73d550fdce.html')

@app.route('/robots.txt')
def robots_txt():
    return send_from_directory('static', 'robots.txt')

@app.route("/")
def home():
    try:
        now = get_current_datetime()
        today_start, today_end = get_today_range()
        
        # Get Nagaland data
        nagaland_slots_info = get_current_nagaland_slot(now)
        nagaland_daily = Nagaland_Result.query.filter(
            Nagaland_Result.created_at >= today_start,
            Nagaland_Result.created_at <= today_end
        ).first()
        
        slot_num = nagaland_slots_info["slot_num"] if nagaland_slots_info else 1
        show_nagaland_result = nagaland_slots_info["show_result"] if nagaland_slots_info else False
        nagaland_digit = getattr(nagaland_daily, f"slot{slot_num}_digit", "-") if nagaland_daily else "-"
        nagaland_number = getattr(nagaland_daily, f"slot{slot_num}_number", "---") if nagaland_daily else "---"
        
        # Get Fatafat data
        fatafat_slots_info = get_current_fatafat_slot(now)
        fatafat_daily = Fatafat_Result.query.filter(
            Fatafat_Result.created_at >= today_start,
            Fatafat_Result.created_at <= today_end
        ).first()
        
        slot_num = fatafat_slots_info["slot_num"] if fatafat_slots_info else 1
        show_fatafat_result = fatafat_slots_info["show_result"] if fatafat_slots_info else False
        fatafat_digit = getattr(fatafat_daily, f"slot{slot_num}_digit", "-") if fatafat_daily else "-"
        fatafat_number = getattr(fatafat_daily, f"slot{slot_num}_number", "---") if fatafat_daily else "---"
        
        # Get recent results
        g_nagaland_results = []
        g_fatafat_results = []
        
        for i in range(days_for_results):
            day = now - relativedelta(days=i)
            day_start = day.replace(hour=0, minute=0, second=0, microsecond=0)
            day_end = day.replace(hour=23, minute=59, second=59, microsecond=999999)
            
            nag_result = Nagaland_Result.query.filter(
                Nagaland_Result.created_at >= day_start,
                Nagaland_Result.created_at <= day_end
            ).first()
            g_nagaland_results.append(nag_result)
            
            fat_result = Fatafat_Result.query.filter(
                Fatafat_Result.created_at >= day_start,
                Fatafat_Result.created_at <= day_end
            ).first()
            g_fatafat_results.append(fat_result)
        
        # Get active marquees
        active_marquees = MarqueeText.get_active()
        
        return render_template('index.html',
                            nagaland_digit=nagaland_digit,
                            nagaland_number=nagaland_number,
                            show_nagaland_result=show_nagaland_result,
                            g_nagaland_results=g_nagaland_results,
                            fatafat_digit=fatafat_digit,
                            fatafat_number=fatafat_number,
                            show_fatafat_result=show_fatafat_result,
                            g_fatafat_results=g_fatafat_results,
                            active_marquees=active_marquees,
                            title="Fastest and Live Online Goa Satta Result")
    
    except Exception as e:
        logger.error(f"Error in home route: {str(e)}")
        flash("An error occurred while loading the page. Please try again.", "error")
        return redirect(url_for('home'))

@app.route("/admin_auth", methods=['GET', 'POST'])
def admin_auth():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if not password:
            flash("Password is required", "error")
            return redirect(url_for('admin_auth'))
        
        if username == "Dearcasino" and check_password(password, ADMIN_PASSWORD):
            session['admin'] = True
            session.permanent = True
            return redirect(url_for('admin'))
        else:
            flash("Invalid Password. Try Again!!!", "error")
            return redirect(url_for('admin_auth')) 
    return render_template('login.html', title="Admin Login")

@app.route("/admin")
def admin():
    if 'admin' not in session:
        return redirect(url_for('admin_auth'))
    
    try:
        now = get_current_datetime()
        today_start, today_end = get_today_range()
        
        daily_data_nagaland = Nagaland_Result.query.filter(
            Nagaland_Result.created_at >= today_start,
            Nagaland_Result.created_at <= today_end
        ).first()

        daily_data_fatafat = Fatafat_Result.query.filter(
            Fatafat_Result.created_at >= today_start,
            Fatafat_Result.created_at <= today_end
        ).first()

        marquee_texts = MarqueeText.query.order_by(MarqueeText.created_at.desc()).all()

        return render_template('admin.html', 
                            daily_data_nagaland=daily_data_nagaland, 
                            daily_data_fatafat=daily_data_fatafat, 
                            title="Admin Panel", 
                            marquee_texts=marquee_texts)
    except Exception as e:
        logger.error(f"Error in admin route: {str(e)}")
        flash("An error occurred while accessing admin panel", "error")
        return redirect(url_for('admin_auth'))

@app.route('/add_nagaland', methods=['POST'])
def add_nagaland():
    if 'admin' not in session:
        return redirect(url_for('admin_auth'))
    
    try:
        now = get_current_datetime()
        today_start, today_end = get_today_range()
        
        daily_data = Nagaland_Result.query.filter(
            Nagaland_Result.created_at >= today_start,
            Nagaland_Result.created_at <= today_end
        ).first()

        if not daily_data:
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
        flash("Nagaland result added successfully!", "success")
    except Exception as e:
        logger.error(f"Error adding Nagaland result: {str(e)}")
        db.session.rollback()
        flash("Failed to add Nagaland result", "error")
    
    return redirect('/admin')

@app.route('/add_fatafat', methods=['POST'])
def add_fatafat():
    if 'admin' not in session:
        return redirect(url_for('admin_auth'))
    
    try:
        now = get_current_datetime()
        today_start, today_end = get_today_range()
        
        daily_data = Fatafat_Result.query.filter(
            Fatafat_Result.created_at >= today_start,
            Fatafat_Result.created_at <= today_end
        ).first()

        if not daily_data:
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
        flash("Fatafat result added successfully!", "success")
    except Exception as e:
        logger.error(f"Error adding Fatafat result: {str(e)}")
        db.session.rollback()
        flash("Failed to add Fatafat result", "error")
    
    return redirect('/admin')

@app.route('/update/<game>/<int:slot>', methods=['GET', 'POST'])
def update(game, slot):
    if 'admin' not in session:
        return redirect(url_for('admin_auth'))
    
    try:
        now = get_current_datetime()
        today_start, today_end = get_today_range()

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
        else:
            flash("Invalid game type", "error")
            return redirect('/admin')

        slot_digit = f'slot{slot}_digit'
        slot_number = f'slot{slot}_number'

        one = getattr(daily_data, slot_digit, None)
        three = getattr(daily_data, slot_number, None)

        if request.method == 'POST':
            oneDigi = request.form['oneDigi']
            threeDigi = request.form['threeDigi']
            setattr(daily_data, slot_digit, oneDigi)
            setattr(daily_data, slot_number, threeDigi)
            db.session.commit()
            flash(f"{game.capitalize()} result updated successfully!", "success")
            return redirect('/admin')
        
        return render_template('update.html', game=game, one=one, three=three, slot=slot, title="Edit Result")
    
    except Exception as e:
        logger.error(f"Error updating {game} slot {slot}: {str(e)}")
        flash(f"Failed to update {game} result", "error")
        return redirect('/admin')

@app.route('/delete/<game>/<int:slot>', methods=['GET', 'POST'])
def delete(game, slot):
    if 'admin' not in session:
        return redirect(url_for('admin_auth'))
    
    try:
        now = get_current_datetime()
        today_start, today_end = get_today_range()

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
        else:
            flash("Invalid game type", "error")
            return redirect('/admin')

        slot_digit = f'slot{slot}_digit'
        slot_number = f'slot{slot}_number'

        setattr(daily_data, slot_digit, None)
        setattr(daily_data, slot_number, None)
        db.session.commit()
        flash(f"{game.capitalize()} slot {slot} result deleted successfully!", "success")
    except Exception as e:
        logger.error(f"Error deleting {game} slot {slot}: {str(e)}")
        db.session.rollback()
        flash(f"Failed to delete {game} result", "error")
    
    return redirect('/admin')

@app.route('/add_marquee', methods=['POST'])
def add_marquee():
    if 'admin' not in session:
        return redirect(url_for('admin_auth'))
    
    try:
        marquee_text = request.form['marquee_text']
        if not marquee_text:
            flash("Marquee text cannot be empty", "error")
            return redirect('/admin')
        
        # If no active marquee exists, make this one active
        is_active = not MarqueeText.query.filter_by(is_active=True).first()
        
        new_marquee = MarqueeText(
            content=marquee_text,
            is_active=is_active
        )
        db.session.add(new_marquee)
        db.session.commit()
        flash("Marquee text added successfully!", "success")
    except Exception as e:
        logger.error(f"Error adding marquee: {str(e)}")
        db.session.rollback()
        flash("Failed to add marquee text", "error")
    
    return redirect('/admin')

@app.route('/update/marquee/<int:id>', methods=['GET', 'POST'])
def update_marquee(id):
    if 'admin' not in session:
        return redirect(url_for('admin_auth'))
    
    try:
        marquee_to_update = MarqueeText.query.get_or_404(id)
        
        if request.method == 'POST':
            updated_marquee_text = request.form['marquee_text']
            updated_marquee_status = request.form.get('marquee_status', 'Disable')
            
            marquee_to_update.content = updated_marquee_text
            marquee_to_update.is_active = updated_marquee_status == "Enable"
            marquee_to_update.updated_at = get_current_datetime()
            
            db.session.commit()
            flash("Marquee updated successfully!", "success")
            return redirect('/admin')
        
        status = "Enable" if marquee_to_update.is_active else "Disable"
        return render_template('update_marquee.html', 
                            title="Edit Marquee", 
                            marquee_to_update=marquee_to_update, 
                            status=status)
    
    except Exception as e:
        logger.error(f"Error updating marquee {id}: {str(e)}")
        flash("Failed to update marquee", "error")
        return redirect('/admin')

@app.route('/delete/marquee/<int:id>', methods=['GET', 'POST'])
def delete_marquee(id):
    if 'admin' not in session:
        return redirect(url_for('admin_auth'))
    
    try:
        marquee_to_delete = MarqueeText.query.get_or_404(id)
        db.session.delete(marquee_to_delete)
        db.session.commit()
        flash("Marquee text deleted successfully!", "success")
    except Exception as e:
        logger.error(f"Error deleting marquee {id}: {str(e)}")
        db.session.rollback()
        flash("Failed to delete marquee text", "error")
    
    return redirect('/admin')

@app.route('/admin_logout')
def logout():
    session.pop('admin', None)
    flash("You have been logged out successfully", "success")
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
            is_active = not active_marquee
            
            new_marquee = MarqueeText(
                content=content,
                scroll_speed=speed,
                is_active=is_active
            )
            
            db.session.add(new_marquee)
            db.session.commit()
            flash("New marquee text added successfully!", "success")
            return redirect(url_for('admin_marquee'))
            
        elif action == 'update':
            marquee_id = request.form.get('id', type=int)
            marquee = MarqueeText.query.get(marquee_id)
            
            if marquee:
                marquee.content = request.form.get('content')
                marquee.scroll_speed = request.form.get('speed', 6, type=int)
                marquee.updated_at = get_current_datetime()
                db.session.commit()
                flash("Marquee updated successfully!", "success")
            
            return redirect(url_for('admin_marquee'))
            
        elif action == 'set_active':
            marquee_id = request.form.get('id', type=int)
            
            # First, deactivate all marquees
            MarqueeText.query.update({'is_active': False})
            
            # Then activate the selected one
            marquee = MarqueeText.query.get(marquee_id)
            if marquee:
                marquee.is_active = True
                marquee.updated_at = get_current_datetime()
                flash("Marquee set as active!", "success")
                
            db.session.commit()
            return redirect(url_for('admin_marquee'))
            
        elif action == 'delete':
            marquee_id = request.form.get('id', type=int)
            marquee = MarqueeText.query.get(marquee_id)
            
            if marquee:
                db.session.delete(marquee)
                db.session.commit()
                flash("Marquee deleted!", "success")
                
            return redirect(url_for('admin_marquee'))
    
    return render_template('admin_marquee.html', 
                        marquee_texts=marquee_texts, 
                        active_marquee=active_marquee, 
                        title="Manage Marquee Text")

@app.route("/about")
def about():
    return render_template('about.html', title="About Us")

@app.route("/text")
def text():
    try:
        now = get_current_datetime()
        today_start, today_end = get_today_range()
        
        results = Nagaland_Result.query.order_by(Nagaland_Result.id.desc()).all()
        daily_data = Nagaland_Result.query.filter(
            Nagaland_Result.created_at >= today_start,
            Nagaland_Result.created_at <= today_end
        ).first()

        start_time = {
            'slot1': now.replace(hour=10, minute=0, second=0, microsecond=0),
            'slot2': now.replace(hour=11, minute=0, second=0, microsecond=0),
            'slot3': now.replace(hour=12, minute=0, second=0, microsecond=0),
            'slot4': now.replace(hour=13, minute=0, second=0, microsecond=0),
            'slot5': now.replace(hour=14, minute=0, second=0, microsecond=0),
            'slot6': now.replace(hour=15, minute=0, second=0, microsecond=0),
            'slot7': now.replace(hour=16, minute=0, second=0, microsecond=0),
            'slot8': now.replace(hour=17, minute=0, second=0, microsecond=0),
            'slot9': now.replace(hour=18, minute=0, second=0, microsecond=0),
            'slot10': now.replace(hour=19, minute=0, second=0, microsecond=0)
        }

        end_time = {
            'slot1': now.replace(hour=10, minute=55, second=0, microsecond=0),
            'slot2': now.replace(hour=11, minute=55, second=0, microsecond=0),
            'slot3': now.replace(hour=12, minute=55, second=0, microsecond=0),
            'slot4': now.replace(hour=13, minute=55, second=0, microsecond=0),
            'slot5': now.replace(hour=14, minute=55, second=0, microsecond=0),
            'slot6': now.replace(hour=15, minute=55, second=0, microsecond=0),
            'slot7': now.replace(hour=16, minute=55, second=0, microsecond=0),
            'slot8': now.replace(hour=17, minute=55, second=0, microsecond=0),
            'slot9': now.replace(hour=18, minute=55, second=0, microsecond=0),
            'slot10': now.replace(hour=19, minute=55, second=0, microsecond=0)
        }

        return render_template('text.html', 
                            results=results, 
                            now=now, 
                            start_time=start_time, 
                            end_time=end_time, 
                            daily_data=daily_data, 
                            title="Nagaland Results")
    
    except Exception as e:
        logger.error(f"Error in text route: {str(e)}")
        flash("An error occurred while loading results", "error")
        return redirect(url_for('home'))

@app.route("/contact")
def contact():
    return render_template('Contact.html', title="Contact Us")

@app.route("/old_nagaland")
def old_nagaland():
    try:
        now = get_current_datetime()
        months_ago = now - relativedelta(months=months_for_old_results)
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        
        nagaland_results = Nagaland_Result.query.filter(
            Nagaland_Result.created_at >= months_ago,
            Nagaland_Result.created_at < today_start
        ).order_by(Nagaland_Result.created_at.desc()).all()
        
        return render_template('old.html', 
                            flag=True,  
                            results=nagaland_results, 
                            title="Old Nagaland Results")
    
    except Exception as e:
        logger.error(f"Error in old_nagaland route: {str(e)}")
        flash("An error occurred while loading old results", "error")
        return redirect(url_for('home'))

@app.route("/old_fatafat")
def old_fatafat():
    try:
        now = get_current_datetime()
        months_ago = now - relativedelta(months=months_for_old_results)
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        
        fatafat_results = Fatafat_Result.query.filter(
            Fatafat_Result.created_at >= months_ago,
            Fatafat_Result.created_at < today_start
        ).order_by(Fatafat_Result.created_at.desc()).all()
        
        return render_template('old.html', 
                            flag=False,  
                            results=fatafat_results, 
                            title="Old Fatafat Results")
    
    except Exception as e:
        logger.error(f"Error in old_fatafat route: {str(e)}")
        flash("An error occurred while loading old results", "error")
        return redirect(url_for('home'))

@app.route('/delete_old_results', methods=['GET', 'POST'])
def delete_old_results():
    if 'admin' not in session:
        return redirect(url_for('admin_auth'))
    
    try:
        now = get_current_datetime()
        cutoff = now - relativedelta(months=to_months_delete_results)

        # Delete Nagaland_Result older than specified months
        old_nagaland = Nagaland_Result.query.filter(
            Nagaland_Result.created_at < cutoff
        ).all()
        for data in old_nagaland:
            db.session.delete(data)

        # Delete Fatafat_Result older than specified months
        old_fatafat = Fatafat_Result.query.filter(
            Fatafat_Result.created_at < cutoff
        ).all()
        for data in old_fatafat:
            db.session.delete(data)

        db.session.commit()
        flash(f"All results older than {to_months_delete_results} months have been deleted.", "success")
    except Exception as e:
        logger.error(f"Error deleting old results: {str(e)}")
        db.session.rollback()
        flash("Failed to delete old results", "error")
    
    return redirect(url_for('admin'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
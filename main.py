from flask import Flask, render_template, request, session, redirect, jsonify, flash, url_for
from model.user_model import user
from flask_mailman import Mail ,EmailMessage
import os


obj = user()
#import user_controller as user_controller

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['MAIL_SERVER'] = 'smtp.fastmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'sanwalsangwall.com'
app.config['MAIL_PASSWORD'] = 'your_fastmail_app_password'  # ya normal password if allowed


@app.route('/')
def main():
    return render_template('base1.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/login_validation', methods=['POST'])
def user_login():
    return obj.user_validation()

@app.route('/dashboard')
def main_dashboard():
    if 'user_id' in session:
        return render_template('dashboard.html') # Fixed typo in session key
    else:
        return redirect('/login')
    
@app.route('/bus_location')  # Fixed typo in route name
def bus_location():  # Fixed typo in function name
    # Example: Replace with real-time data from your database
    buses = [
        {
            'name': 'Bus 12',
            'eta': 5,
            'location': 'Main Street',
            'destination': 'Central Campus',
            'lat': 31.5204,
            'lng': 74.3587
        },
        {
            'name': 'Bus 8',
            'eta': 10,
            'location': 'Elm Avenue',
            'destination': 'North Gate',
            'lat': 31.5300,
            'lng': 74.3500
        }
    ]
    return render_template('live.html', buses=buses)

@app.route('/schedules')
def bus_schedules():
    stops = obj.get_stops()
    #print(stops)
    return render_template('schedule.html' , stops = stops)

from model.user_model import user as UserModel
@app.route('/setting', methods=['GET', 'POST'])
def setting():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        theme = request.form.get('theme')
        email = 'email' in request.form
        notifications = 'notifications' in request.form

        # Verify user
        user_obj = UserModel()
        user_valid = False
        user_id = None
        try:
            user_obj.cursor.execute("SELECT idusers, password FROM users WHERE username = %s", (username,))
            result = user_obj.cursor.fetchone()
            user_obj.cursor.fetchall()  # <- ✅ Clear the result set if any leftover

            if result and user_obj.verify_password(result[1], password):
              user_valid = True
              user_id = result[0]
              
        except Exception as e:
            flash(f"❌ Error verifying user: {str(e)}", "error")
            return redirect(url_for('setting'))

        # ✅ Save theme and settings in session
        session['theme'] = theme
        session['email'] = email
        session['notifications'] = notifications

        # ✅ Save notifications flag in database
        try:
            user_obj.cursor.execute(
                "UPDATE users SET notify_enabled = %s  WHERE idusers = %s",
                (1 if notifications else 0, user_id)
            )
            user_obj.conn.commit()
        except Exception as e:
            flash(f"❌ Error saving to database: {str(e)}", "error")
            return redirect(url_for('setting'))

        flash("✅ Settings saved successfully!", "success")
        return redirect(url_for('setting'))

    return render_template('setting.html', theme=session.get('theme', 'light'))




@app.route('/notifications')
def bus_notification():
    results = obj.get_noti()
    return render_template('noti.html' , results=results)

@app.route('/bus_messages')
def bus_messages():
    return render_template('send_messages.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect('/')

@app.route('/admin_cpanel' , methods=['GET','POST'])
def admin_cpanel():
    if request.method == 'POST':
        return obj.admin_validation()
    
    return render_template('cpanel.html')

def get_users():
    return obj.get_users()

def total_buses():
    return obj.total_buses()


def total_routes():
    return obj.total_routes()

def u_management():
    return obj.u_management()

def r_management():
    return obj.r_management()
def s_management():
    return obj.s_management()

@app.route('/admin_dashboard')
def admin_dashboard():
    users =get_users()
    buses = total_buses()
    routes = total_routes()
    info = u_management()
    r_info = r_management()
    stops = s_management()
    if 'admin_id' in session:
        return render_template('admin.html',users = users,buses = buses,routes = routes ,info = info ,r_info = r_info,stops=stops)
    else:
        return redirect('/admin_cpanel')
@app.route('/admin_logout')
def admin_logout():
    session.pop('admin_id', None)
    return redirect('/admin_cpanel')

@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    if request.method == 'POST':
        if 'admin_id' not in session:
            flash("❌ Unauthorized access. Please login first.", "error")
            return redirect('/admin_cpanel')
        
        try:
            return obj.add_user()
        except Exception as e:
            flash(f"❌ Error: {str(e)}", "error")
            return redirect(url_for('add_user'))

    return render_template('add_user.html')

@app.route('/update_user',methods=['GET','POST'])
def update_user():
    if request.method == 'POST':
        if 'admin_id' not in session:
            flash("❌ Unauthorized access. Please login first.", "error")
            return redirect('/admin_cpanel')
        
        try:
            return obj.update_user()
        except Exception as e:
            flash(f"❌ Error: {str(e)}", "error")
            return redirect(url_for('update_user'))

    return render_template('update_users.html')

@app.route('/delete_user',methods=['GET','POST'])
def delete_user():
    if request.method == 'POST':
        if 'admin_id' not in session:
            flash("❌ Unauthorized access. Please login first.", "error")
            return redirect('/admin_cpanel')
        
        try:
            return obj.delete_user()
        except Exception as e:
            flash(f"❌ Error: {str(e)}", "error")
            return redirect(url_for('delete_user'))

    return render_template('delete_user.html')


            

@app.route('/add_bus',methods=['GET','POST'])
def add_bus():
    if request.method == 'POST':
        if 'admin_id' not in session:
            return jsonify({"error": "Unauthorized access"}), 403  # Prevent unauthorized access
        try:
            result = obj.add_bus()  # Assuming this function handles bus creation
            return jsonify({"success": "Bus added successfully", "data": result}), 201
        except Exception as e:
            return jsonify({"error": str(e)}), 400  # Catch and return errors
        
    return render_template('add_bus.html')

@app.route('/update_bus',methods=['GET','POST'])
def update_bus():
    if request.method == 'POST':
        if 'admin_id' not in session:
            return jsonify({"error": "Unauthorized access"}), 403
        try:
            return obj.update_bus()
        except Exception as e:
            return jsonify({"error": str(e)}), 400
    return render_template('update_bus.html')

@app.route('/delete_bus',methods=['GET','POST'])
def delete_bus():
    if request.method == 'POST':
        if 'admin_id' not in session:
            return jsonify({"error": "Unauthorized access"}), 403
        try:
            return obj.delete_bus()
        except Exception as e:
            return jsonify({"error": str(e)}), 400
    return render_template('delete_bus.html')


@app.route('/add_stop',methods=['GET','POST'])
def add_stop():
    if request.method == 'POST':
        if 'admin_id' not in session:
            return jsonify({"error": "Unauthorized access"}), 403  # Prevent unauthorized access

        try:
            result = obj.add_stop()  # Assuming this function handles user creation
            return jsonify({"success": "User added successfully", "data": result}), 201
        except Exception as e:
            return jsonify({"error": str(e)}), 400  # Catch and return errors

    return render_template('add_stops.html')  # Show form for adding user

@app.route('/update_stop',methods=['GET','POST'])
def update_stop():
    if request.method == 'POST':
        if 'admin_id' not in session:
            return jsonify({"error": "Unauthorized access"}), 403
        try:
            return obj.update_stop()
        except Exception as e:
            return jsonify({"error": str(e)}), 400
    return render_template('update_stops.html')

@app.route('/delete_stop',methods=['GET','POST'])
def delete_stop():
    if request.method == 'POST':
        if 'admin_id' not in session:
            return jsonify({"error": "Unauthorized access"}), 403
        try:
            return obj.delete_stop()
        except Exception as e:
            return jsonify({"error": str(e)}), 400
    return render_template('delete_stop.html')


@app.route('/send_message',methods=['GET','POST'])
def send_message():
    if request.method == 'POST':
        if 'admin_id' not in session:
            return jsonify({"error": "Unauthorized access"}), 403
        try:
            return obj.send_messages()
        except Exception as e:
            return jsonify({"error": str(e)}), 400
    return render_template('send_messages.html')

def get_stop():
    return obj.get_stops()

def get_notification():
    return obj.get_noti()
             
if __name__ == '__main__':
    app.run(debug=True)
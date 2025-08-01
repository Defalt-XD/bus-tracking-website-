from flask import request,render_template,jsonify,redirect,session,url_for,flash
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
import bcrypt
class user:
    def __init__(self):
        try:
            self.conn = mysql.connector.connect(host='localhost ', database='data', user='root', password='root') 
            self.cursor = self.conn.cursor()
            print('Connected to database')
        except mysql.connector.Error as e:
            print(e)
              
    def user_validation(self):
        try:
            user_id = request.form.get("std_id")
            password = request.form.get("password")       
            self.cursor.execute( "SELECT password FROM users WHERE idusers = %s ",(user_id,))
            result = self.cursor.fetchone()
            
            if result and self.verify_password(result[0], password):
                session['user_id'] = result[0]
                return redirect('/dashboard')
            else:
                flash("❌ Login failed. Invalid Student ID or password.", "error")
                return redirect('/login')
        except mysql.connector.Error as e:
            flash(f"❌ Database error: {str(e)}", "error")
            return redirect('/login')
    def admin_validation(self):
        try:
            username = request.form.get("username")
            password = request.form.get("password")    
            self.cursor.execute("SELECT password FROM admin WHERE username =%s AND password = %s",(username, password))
            result = self.cursor.fetchone()
            
            if not result:
                session.pop('admin_id', None)  # Clear any existing session
                flash("❌ Login failed. Invalid username or password.", "error")
                return redirect('/admin_cpanel')
            
            # Clear any existing messages before setting success
            session.pop('_flashes', None)
            session['admin_id'] = result[0]
            return redirect('/admin_dashboard')

        except mysql.connector.Error as e:
            return jsonify({"error": str(e)}), 500
        
        

    def hash_password(self,password):
     return generate_password_hash(password)

    def verify_password(self,stored_hash, provided_password):
      return check_password_hash(stored_hash, provided_password)
    def add_user(self):
      try:
        # Get form data
        std_id = request.form.get("std_id")
        email = request.form.get("email")
        username = request.form.get("username")
        password = request.form.get("password")

        if not std_id or not username or not password:
            flash("❌ All fields are required!", "error")
            return redirect(url_for('add_user'))
        
        # Check if user already exists
        self.cursor.execute("SELECT idusers FROM users WHERE idusers = %s", (std_id,))
        if self.cursor.fetchone():
            flash("❌ Student ID already exists!", "error")
            return redirect(url_for('add_user'))
        
        # Encrypt the password
        hashed_password = self.hash_password(password)

        # Insert into database
        self.cursor.execute(
            "INSERT INTO users (idusers,email, username, password) VALUES (%s,%s, %s, %s)", 
            (std_id,email, username, hashed_password)
        )
        self.conn.commit()
        
        flash("✅ User added successfully!", "success")
        return redirect(url_for('add_user'))

      except ValueError as e:
        return jsonify({"error": str(e)}), 400

      except ValueError as e:  # Handle duplicate std_id errors
        return jsonify({"error": "Student ID already exists"}), 409
    
    def add_bus(self):
        number = request.form.get("bus_number")
        capacity = request.form.get("capacity")
        start_pt = request.form.get("starting_point")
        end_pt = request.form.get("destination_point")
        
        if not number or not capacity or not start_pt or not end_pt:
            flash("❌ All fields are required!", "error")
            return redirect(url_for('add_bus'))
        try:
            # Check if bus already exists
            self.cursor.execute("SELECT bus_number FROM buses WHERE bus_number = %s", (number,))
            if self.cursor.fetchone():
                flash("❌ Bus number already exists!", "error")
                return redirect(url_for('add_bus'))
            self.cursor.execute("INSERT INTO buses (bus_number, capacity, start_route, end_route) VALUES (%s, %s, %s, %s)", (number, capacity, start_pt, end_pt))
            self.conn.commit()
            flash("✅ Bus added successfully!", "success")
            return redirect(url_for('add_bus'))
        except Exception as e:
            flash(f"❌ Error: {str(e)}", "error")
            return redirect(url_for('add_bus'))

    def update_bus(self):
        try:
            bus_number = request.form.get("bus_number")
            capacity = request.form.get("capacity")
            start_pt = request.form.get("starting_point")
            end_pt = request.form.get("destination_point")
            if not bus_number or not capacity or not start_pt or not end_pt:
                flash("❌ All fields are required!", "error")
                return redirect(url_for('update_bus'))
            self.cursor.execute("SELECT bus_number FROM buses WHERE bus_number = %s", (bus_number,))
            if not self.cursor.fetchone():
                flash("❌ Bus not found!", "error")
                return redirect(url_for('update_bus'))
            self.cursor.execute("UPDATE buses SET capacity = %s, start_route = %s, end_route = %s WHERE bus_number = %s", (capacity, start_pt, end_pt, bus_number))
            self.conn.commit()
            flash("✅ Bus updated successfully!", "success")
            return redirect(url_for('update_bus'))
        except Exception as e:
            flash(f"❌ Error: {str(e)}", "error")
            return redirect(url_for('update_bus'))

    def delete_bus(self):
        try:
            bus_number = request.form.get("bus_number")
            if not bus_number:
                flash("❌ Bus number is required!", "error")
                return redirect(url_for('delete_bus'))
            self.cursor.execute("SELECT bus_number FROM buses WHERE bus_number = %s", (bus_number,))
            if not self.cursor.fetchone():
                flash("❌ Bus not found!", "error")
                return redirect(url_for('delete_bus'))
            self.cursor.execute("DELETE FROM buses WHERE bus_number = %s", (bus_number,))
            self.conn.commit()
            flash("✅ Bus deleted successfully!", "success")
            return redirect(url_for('delete_bus'))
        except Exception as e:
            flash(f"❌ Error: {str(e)}", "error")
            return redirect(url_for('delete_bus'))

    def get_users(self):
        try:
            self.cursor.execute("SELECT COUNT(*) FROM users")  
            total_users = self.cursor.fetchone()[0]
            
            
            return total_users
        
        except ValueError as e:
            return jsonify({"error": str(e)}), 400
    
    def total_buses(self):
        try:
            self.cursor.execute("SELECT COUNT(*) FROM buses")  
            total_buses = self.cursor.fetchone()[0]
            
            
            return total_buses
        
        except ValueError as e:
            return jsonify({"error": str(e)}), 400
    
    def total_routes(self):
        try:
            self.cursor.execute("SELECT COUNT(DISTINCT CONCAT(start_route, ' -> ', end_route)) AS total_routes FROM buses;")  
            total_routes = self.cursor.fetchone()[0]
            
            
            return total_routes
        
        except ValueError as e:
            return jsonify({"error": str(e)}), 400
        
    
    def u_management(self):
        try:
            self.cursor.execute("SELECT idusers ,username FROM users")  
            user_info = self.cursor.fetchall()
            
            
            return user_info
        
        except ValueError as e:
            return jsonify({"error": str(e)}), 400
        
    def r_management(self):
        try:
            self.cursor.execute("SELECT bus_number ,capacity, start_route,end_route FROM buses")  
            user_info = self.cursor.fetchall()
            
            
            return user_info
        
        except ValueError as e:
            return jsonify({"error": str(e)}), 400
        
    def s_management(self):
        try:
            self.cursor.execute("SELECT bus_number ,stop_1,stop_2,stop_3,stop_4 FROM stops")  
            stops_info = self.cursor.fetchall()
            
            
            return stops_info
        
        except ValueError as e:
            return jsonify({"error": str(e)}), 400
        
    def add_stop(self):
        bus_number = request.form.get('bus_number')
        start_time = request.form.get('start_time')
        stop_1 = request.form.get('stop1')
        stop_2 = request.form.get('stop2')
        stop_3 = request.form.get('stop3')
        stop_4 = request.form.get('stop4')
        end_time = request.form.get('end_time')
        if not bus_number or not stop_1 or not stop_2 or not stop_3 or not stop_4:
            flash("❌ All fields are required!", "error")
            return redirect(url_for('add_stop'))
        try:
            self.cursor.execute("SELECT bus_number FROM stops WHERE bus_number = %s", (bus_number,))
            if self.cursor.fetchone():
                flash("❌ Route for this bus already exists!", "error")
                return redirect(url_for('add_stop'))
            self.cursor.execute("INSERT INTO stops (bus_number,starting_time, stop_1, stop_2, stop_3, stop_4 ,end_time) VALUES (%s,%s, %s, %s, %s, %s,%s)", (bus_number,start_time, stop_1, stop_2, stop_3, stop_4,end_time))
            self.conn.commit()
            flash("✅ Route added successfully!", "success")
            return redirect(url_for('add_stop'))
        except Exception as e:
            flash(f"❌ Error: {str(e)}", "error")
            return redirect(url_for('add_stop'))

    def update_stop(self):
        try:
            bus_number = request.form.get("bus_number")
            stop_1 = request.form.get("stop1")
            stop_2 = request.form.get("stop2")
            stop_3 = request.form.get("stop3")
            stop_4 = request.form.get("stop4")
            if not bus_number or not stop_1 or not stop_2 or not stop_3 or not stop_4:
                flash("❌ All fields are required!", "error")
                return redirect(url_for('update_stop'))
            self.cursor.execute("SELECT bus_number FROM stops WHERE bus_number = %s", (bus_number,))
            if not self.cursor.fetchone():
                flash("❌ Route not found!", "error")
                return redirect(url_for('update_stop'))
            self.cursor.execute("UPDATE stops SET stop_1 = %s, stop_2 = %s, stop_3 = %s, stop_4 = %s WHERE bus_number = %s", (stop_1, stop_2, stop_3, stop_4, bus_number))
            self.conn.commit()
            flash("✅ Route updated successfully!", "success")
            return redirect(url_for('update_stop'))
        except Exception as e:
            flash(f"❌ Error: {str(e)}", "error")
            return redirect(url_for('update_stop'))

    def delete_stop(self):
        try:
            bus_number = request.form.get("bus_number")
            if not bus_number:
                flash("❌ Bus number is required!", "error")
                return redirect(url_for('delete_stop'))
            self.cursor.execute("SELECT bus_number FROM stops WHERE bus_number = %s", (bus_number,))
            if not self.cursor.fetchone():
                flash("❌ Route not found!", "error")
                return redirect(url_for('delete_stop'))
            self.cursor.execute("DELETE FROM stops WHERE bus_number = %s", (bus_number,))
            self.conn.commit()
            flash("✅ Route deleted successfully!", "success")
            return redirect(url_for('delete_stop'))
        except Exception as e:
            flash(f"❌ Error: {str(e)}", "error")
            return redirect(url_for('delete_stop'))
        
    def send_messages(self):
        try:
            recipient = request.form.get("recipient")
            tittle = request.form.get("subject")
            message = request.form.get("message")
            if not recipient or not tittle or not message:
                flash("❌ All fields are required!", "error")
                return redirect(url_for('send_message'))
            # Assuming you have a table to store messages
            self.cursor.execute("INSERT INTO messages (recipient,tittle,message) VALUES (%s,%s, %s)", (recipient,tittle, message))
            self.conn.commit()
            flash("✅ Message sent successfully!", "success")
            # Send email to users who enabled notifications
            self.send_email(tittle, tittle, message)
            return redirect(url_for('send_message'))
        except Exception as e:
            flash(f"❌ Error: {str(e)}", "error")
            return redirect(url_for('send_message'))

    def send_email(self, tittle, subject, body):
        # Import here to avoid circular import
        from flask_mailman import EmailMessage
        from flask import current_app
        # Get emails of users who enabled notifications
        self.cursor.execute("SELECT email FROM users WHERE notify_enabled = 1")
        emails = [row[0] for row in self.cursor.fetchall()]
        for email in emails:
            msg = EmailMessage(
                subject=f"📢 {tittle}: {subject}",
                body=body,
                from_email=current_app.config['MAIL_USERNAME'],
                to=[email]
            )
            msg.send()
        
    def get_stops(self):
        try:
            self.cursor.execute("SELECT bus_number,starting_time, stop_1, stop_2, stop_3, stop_4,end_time FROM stops")  
            stops_info = self.cursor.fetchall()
            return stops_info
        except ValueError as e:
            return jsonify({"error": str(e)}), 400
        
    def get_noti(self):
        try:
            self.cursor.execute("SELECT * FROM messages")  
            notifications = self.cursor.fetchall()
            return notifications
        except ValueError as e:
            return jsonify({"error": str(e)}), 400

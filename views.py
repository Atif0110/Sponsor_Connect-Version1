from flask import flash, redirect, render_template, request, session, url_for, current_app as app
from models import db, Sponsor, Influencer, AdRequest, Campaign
from datetime import datetime
from functools import wraps
import os

def confirm_sponsor(view_function):
    @wraps(view_function)
    def decorated_function(*args, **kwargs):
        if 's_name' and 's_id' in session:
            return view_function(*args, **kwargs)
        else:
            flash('Sponser login required!')
            return redirect(url_for('sponsor_login'))
    return decorated_function

def confirm_influencer(view_function):
    @wraps(view_function)
    def decorated_function(*args, **kwargs):
        if 'i_name' and 'i_id' in session:
            return view_function(*args, **kwargs)
        else:
            flash('Influencer login required!')
            return redirect(url_for('influencer_login'))
    return decorated_function

@app.route('/')
def main_home():
    return render_template('index.html')

@app.route('/admin/login', methods = ['GET','POST'])
def admin_login():
    if request.method == 'POST':
        password = request.form['password']
        if password == "admin2024":
            session['admin'] = True
            return redirect(url_for('admin_dashboard'))
        flash("Incorrect password!")
        return render_template('admin_login.html')
    return render_template('admin_login.html')

@app.route('/sponsor/register', methods = ['GET','POST'])
def sponsor_register():
    if request.method == 'POST':
        company_name = request.form['company_name']
        industry = request.form['industry']
        password = request.form['password']

        s = Sponsor.query.filter_by(company_name = company_name).first()
        if s:
            flash("Company already exists!")
            return render_template('sponsor_register.html')
        
        new_s = Sponsor(company_name = company_name, password = password, industry = industry)
        db.session.add(new_s)
        db.session.commit()

        s = Sponsor.query.filter_by(company_name = company_name).first()
        session['s_name'] = s.company_name
        session['s_id'] = s.id 
        flash("Registered successfully!")
        return redirect(url_for('sponsor_dashboard'))  
    return render_template('sponsor_register.html')

@app.route('/sponsor/login', methods = ['GET','POST'])
def sponsor_login():
    if request.method == 'POST':
        company_name = request.form['company_name']
        password = request.form['password']

        s = Sponsor.query.filter_by(company_name = company_name).first()
        if s:
            if s.password == password:
                session['s_name'] = s.company_name
                session['s_id'] = s.id 
                return redirect(url_for('sponsor_dashboard'))  
            flash("Incorrect password!")          
            return render_template("sponsor_login.html")
        flash("Company not found!")
        return render_template('sponsor_login.html')
    return render_template('sponsor_login.html')

@app.route('/influencer/register', methods = ['GET','POST'])
def influencer_register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        niche = request.form['niche']
        reach = request.form['reach']

        i = Influencer.query.filter_by(email = email).first()
        if i:
            flash("Email already exists!")
            return render_template('influencer_register.html')
        
        new_i = Influencer(name = name, email = email, password = password, niche = niche, reach = reach)
        db.session.add(new_i)
        db.session.commit()

        i = Influencer.query.filter_by(email = email).first()
        session['i_name'] = i.name
        session['i_id'] = i.id 
        flash("Registered successfully.")
        return redirect(url_for('influencer_dashboard'))  
    return render_template('influencer_register.html')

@app.route('/influencer/profile', methods = ['GET','POST'])
@confirm_influencer
def influencer_profile():
    id = session.get("i_id")
    i = Influencer.query.get(id)
    if not i:
        flash("Profile not found!")
        return redirect(url_for('influencer_dashboard')) 
     
    if request.method == 'POST':
        name = request.form['name']
        niche = request.form['niche']
        reach = request.form['reach']
        
        i.name = name
        i.niche = niche
        i.reach = reach

        db.session.commit()
        session['i_name'] = name
        flash("Profile updated.")
        return redirect(url_for('influencer_profile'))  
    return render_template('influencer_profile.html', profile = i)

@app.route('/influencer/login', methods = ['GET','POST'])
def influencer_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        i = Influencer.query.filter_by(email = email).first()
        if i:
            if i.password == password:
                session['i_name'] = i.name
                session['i_id'] = i.id 
                return redirect(url_for('influencer_dashboard'))  
            flash("Incorrect password!")          
            return render_template("influencer_login.html")
        flash("Email not found!")
        return render_template('influencer_login.html')
    return render_template('influencer_login.html')

@app.route('/admin/logout')
def admin_logout():
    session.pop("admin")
    return redirect(url_for('admin_login'))

@app.route('/sponsor/logout')
def sponsor_logout():
    session.pop("s_id")
    session.pop("s_name")
    return redirect(url_for('sponsor_login'))

@app.route('/influencer/logout')
def influencer_logout():
    session.pop("i_id")
    session.pop("i_name")
    return redirect(url_for('influencer_login'))

@app.route('/campaign/create', methods=['GET', 'POST'])
@confirm_sponsor
def campaign_create():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        start_date_s = request.form['start_date']
        end_date_s = request.form['end_date']
        budget = request.form['budget']
        visibility = request.form['visibility']

        start_date = datetime.strptime(start_date_s, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date_s, '%Y-%m-%d').date()

        new_c = Campaign(sponsor_id = session.get("s_id"), 
                        name = name, 
                        description = description,
                        start_date = start_date, 
                        end_date = end_date, 
                        budget = budget, 
                        visibility = visibility)

        db.session.add(new_c)
        db.session.commit()
        flash("Campaign added.")
        return redirect(url_for('sponsor_dashboard')) 

    return render_template('campaign_create.html', sponsor = session.get('s_name'))

@app.route('/campaign/update/<int:id>', methods=['GET', 'POST'])
@confirm_sponsor
def campaign_update(id):
    c = Campaign.query.get(id)
    if not c:
        flash("Campaign not found!")
        return redirect(url_for('sponser_dashboard'))      
        
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        start_date_s = request.form['start_date']
        end_date_s = request.form['end_date']
        budget = request.form['budget']

        start_date = datetime.strptime(start_date_s, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date_s, '%Y-%m-%d').date()

        c.name = name
        c.description = description
        c.start_date = start_date 
        c.end_date = end_date
        c.budget = budget

        db.session.commit()
        flash("Campaign updated.")
        return redirect(url_for('sponsor_dashboard')) 
    return render_template('campaign_update.html', sponsor = session.get('s_name'), campaign = c)

@app.route('/campaign/delete/<int:id>', methods=['GET', 'POST'])
@confirm_sponsor
def campaign_delete(id):
    c = Campaign.query.get(id)
    if not c:
        flash("Campaign not found!")
        return redirect(url_for('sponser_dashboard'))  

    db.session.delete(c)
    db.session.commit()
    flash("Campaign removed.")
    return redirect(url_for('sponsor_dashboard')) 
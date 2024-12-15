from flask import Flask, flash, redirect, render_template, request, session, url_for
from models import db, Sponsor, Influencer, AdRequest, Campaign, InfluencerRequest
from sqlalchemy import func
from datetime import datetime
from functools import wraps
import os

app = Flask(__name__, template_folder="templates")
basedir = os.path.abspath(os.path.dirname(__file__))

app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///" + os.path.join(basedir,"SponserConnect.sqlite3")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = "SponserConnect"

db.init_app(app)
app.app_context().push()

from views import *

@app.route('/campaign/<int:id>', methods=['GET', 'POST'])
@confirm_sponsor
def campaign(id):
    c = Campaign.query.get(id)
    if not c:
        flash("Campaign not found!")
        return redirect(url_for('sponsor_dashboard')) 
    requests = AdRequest.query.filter_by(campaign_id = id).all()
    return render_template('sponsor_campaign.html', campaign = c, sponsor = session.get('s_name'), requests = requests)


@app.route('/campaign/request/<int:id>', methods=['GET', 'POST'])
@confirm_sponsor
def campaign_request(id):
    c = Campaign.query.get(id)
    if not c:
        flash("Campaign not found!")
        return redirect(url_for('sponser_dashboard'))  
        
    if request.method == 'POST':
        influencer_id = request.form['influencer_id']
        message = request.form['message']
        requirements = request.form['requirements']
        payment_amount = request.form['payment_amount']

        new_r = AdRequest(campaign_id = id, influencer_id = influencer_id, message = message,
                          requirements = requirements, payment_amount = payment_amount)
        
        db.session.add(new_r)
        db.session.commit()
        flash("Ad requested.")
        return redirect(url_for('sponsor_dashboard'))
    influencers = Influencer.query.all() 
    return render_template('campaign_request.html', sponsor = session.get('s_name'), campaign = c, influencers = influencers)


@app.route('/request/update/<int:id>', methods=['GET', 'POST'])
@confirm_sponsor
def request_update(id):
    r = AdRequest.query.get(id)
    if not r:
        flash("Request not found!")
        return redirect(url_for('sponsor_dashboard'))
    cid = r.campaign_id 
    if r.status == 'Pending':
        flash("You cannot make changes now!")
        return redirect(url_for('campaign', id = cid)) 
    if request.method == 'POST':
        message = request.form['message']
        requirements = request.form['requirements']
        payment_amount = request.form['payment_amount']

        r.message = message
        r.requirements = requirements
        r.payment_amount = payment_amount

        db.session.commit()
        flash("Request updated.")
        return redirect(url_for('campaign', id = cid))
    return render_template('request_update.html', request = r, sponsor = session.get('s_name'))

@app.route('/request/delete/<int:id>', methods=['GET', 'POST'])
@confirm_sponsor
def request_delete(id):
    r = AdRequest.query.get(id)
    if not r:
        flash("Request not found!")
        return redirect(url_for('sponsor_dashboard')) 
    cid = r.campaign_id

    db.session.delete(r)
    db.session.commit()
    flash("Request deleted.")
    return redirect(url_for('campaign', id = cid)) 

@app.route('/request/accept/<int:id>')
@confirm_influencer
def request_accept(id):
    r = AdRequest.query.get(id)
    if not r:
        flash("Request not found!")
        return redirect(url_for('influencer_dashboard'))
    r.status = "Accepted"
    db.session.commit()
    flash("Request accepted.")
    return redirect(url_for('influencer_dashboard')) 

@app.route('/sponsor/request/accept/<int:id>')
@confirm_sponsor
def sponsor_request_accept(id):
    r = AdRequest.query.get(id)
    if not r:
        flash("Request not found!")
        return redirect(url_for('sponsor_dashboard'))
    
    r.status = "Accepted(self)"
    db.session.commit()
    flash("Request accepted.")
    return redirect(url_for('sponsor_dashboard')) 

@app.route('/sponsor/request/reject/<int:id>')
@confirm_sponsor
def sponsor_request_reject(id):
    r = AdRequest.query.get(id)
    if not r:
        flash("Request not found!")
        return redirect(url_for('sponsor_dashboard'))
    
    r.status = "Rejected(Self)"
    db.session.commit()
    flash("Request rejected.")
    return redirect(url_for('sponsor_dashboard'))

@app.route('/request/reject/<int:id>')
@confirm_influencer
def request_reject(id):
    r = AdRequest.query.get(id)
    if not r:
        flash("Request not found!")
        return redirect(url_for('influencer_dashboard'))
    r.status = "Rejected"
    db.session.commit()
    flash("Request rejected.")
    return redirect(url_for('influencer_dashboard')) 

@app.route('/request/negotiate/<int:id>', methods=['GET', 'POST'])
@confirm_influencer
def request_negotiate(id):
    r = AdRequest.query.get(id)
    if not r:
        flash("Request not found!")
        return redirect(url_for('influencer_dashboard'))
    if request.method == "POST":
        msg = request.form['msg']
        r.status = "Negotiated"
        r.negotiation = msg
        db.session.commit()
        flash("Negotiation submitted.")
        return redirect(url_for('influencer_dashboard'))
    return render_template('request_negotiate.html', request = r, influencer = session.get('i_name'))

@app.route('/request/complete/<int:id>', methods=['GET', 'POST'])
@confirm_influencer
def request_complete(id):
    r = AdRequest.query.get(id)
    if not r:
        flash("Request not found!")
        return redirect(url_for('influencer_dashboard'))
    
    r.status = 'Completed'
    db.session.commit()
    flash("Campaign completed.")
    return redirect(url_for('influencer_dashboard'))

@app.route('/influencer/campaign/request/<int:id>', methods=['GET', 'POST'])
@confirm_influencer
def influencer_campaign_request(id):
    c = Campaign.query.get(id)
    if not c or c.visibility != 'Public':
        flash("Campaign not found!")
        return redirect(url_for('influencer_dashboard'))  
    r = AdRequest.query.filter_by(influencer_id = session.get('i_id'), campaign_id = id).first()
    if r:
        flash("You have already requested for this campaign!")
        return redirect(url_for('influencer_dashboard'))    
      
    new_r = AdRequest(campaign_id = id, 
                      influencer_id = session.get('i_id'), 
                      message = "This is a public campaign.",
                      payment_amount = 0,
                      status = 'Self Requested',
                      requirements = "Everything required for the campaign.")
    db.session.add(new_r)
    db.session.commit()
    flash('Campaign requested.')
    return redirect(url_for('influencer_dashboard')) 
    
@app.route('/sponsor/dashboard')
@confirm_sponsor
def sponsor_dashboard():
    campaigns = Campaign.query.filter_by(sponsor_id = session.get("s_id")).all()
    return render_template("sponsor_dashboard.html", campaigns = campaigns, sponsor = session.get("s_name"))

@app.route('/influencer/dashboard')
@confirm_influencer
def influencer_dashboard():
    requests = AdRequest.query.filter_by(influencer_id = session.get("i_id")).all()
    campaigns = Campaign.query.filter_by(visibility = 'Public').all()
    return render_template("influencer_dashboard.html", requests = requests, campaigns = campaigns, influencer = session.get("i_name"), id = session.get("i_id"))

@app.route('/admin/dashboard')
def admin_dashboard():
    if 'admin' not in session:
        flash("Log in to continue!")
        return redirect(url_for("admin_login"))
    ts = Sponsor.query.count()
    ti = Influencer.query.count()
    campaigns = Campaign.query.all()
    return render_template("admin_dashboard.html", campaigns = campaigns, ts = ts, ti = ti, sponsor = session.get("s_name"))

@app.route('/campaign/flag/<int:id>')
def campaign_flag(id):
    if 'admin' not in session:
        flash("Log in to continue!")
        return redirect(url_for("admin_login"))
    
    c = Campaign.query.get(id)
    if not c:
        flash("Campaign not found!")
        return redirect(url_for('admin_dashboard')) 
    
    flag = c.flagged
    c.flagged = not flag
    db.session.commit()
    flash('Campaign profile updated.')
    return redirect(url_for('admin_dashboard')) 


if __name__ == '__main__':
  db.create_all()
  app.run(debug=True)
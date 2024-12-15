# SponsorConnect

SponsorConnect is a Flask-based web application that bridges sponsors and influencers to collaborate on advertising campaigns. This platform facilitates campaign management, ad requests, and influencer-sponsor interactions in an intuitive and streamlined way.

## Features

- **Admin Dashboard**: Manage campaigns, sponsors, and influencers.
- **Sponsor Features**:
  - Register and log in as a sponsor.
  - Create, update, and delete advertising campaigns.
  - Accept or reject ad requests from influencers.
  - View campaign-specific requests and negotiate terms.
- **Influencer Features**:
  - Register and log in as an influencer.
  - Browse public campaigns and submit requests to participate.
  - Negotiate terms, accept or reject sponsorship offers.
  - Update personal profile details.
- **Campaign Management**:
  - Public and private campaign visibility settings.
  - Budget allocation and timeline definition.
  - Flagging campaigns for admin review.
- **Ad Requests**:
  - Status updates: Pending, Accepted, Rejected, Negotiated, or Completed.
  - Dynamic negotiation and payment adjustments.

## Technologies Used

- **Backend**: Flask, SQLAlchemy
- **Database**: SQLite
- **Frontend**: Jinja2 templates
- **Other**: Session management for user authentication, Flash messages for user feedback

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/sponsorconnect.git
   cd sponsorconnect

   
**STEPS TO SETUP THE PROJECT**

1. **Set up a virtual environment:**

python -m venv venv
source venv/bin/activate  

2. **Install dependencies:**

pip install -r requirements.txt

3. **Initialize the database:**

python app.py

4. **Run the development server:**

python app.py

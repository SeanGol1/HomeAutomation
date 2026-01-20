import datetime
from flask import Blueprint, render_template, request, jsonify ,redirect
from requests import session
import website.functions as functions 
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build


google = Blueprint('google', __name__)



# Google

SCOPES = ['https://www.googleapis.com/auth/calendar']
CLIENT_SECRETS_FILE = "configs/google.json"

@google.route('/authorize' , methods=['GET','POST'])
def authorize():
    # redirect_uri = url_for('views.oauth2callback', _external=True)
    redirect_uri = 'https://415d19f830e7.ngrok-free.app/google/callback'
    print("🚀 Redirect URI being used:", redirect_uri)

    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        redirect_uri=redirect_uri)
    
    # auth_url, state = flow.authorization_url(access_type='offline', include_granted_scopes='true')

    auth_url, state = flow.authorization_url() 
    #        access_type='offline',
        #include_granted_scopes='true'

    session['state'] = state
    

    return redirect(auth_url)

@google.route('callback', methods=['GET','POST'])
def oauth2callback():
    redirect_uri = 'https://415d19f830e7.ngrok-free.app/google/callback'

    # state = session['state']
    # if not state: 
    #     return "Error"

    # print( 'State: ' + state)   
    
    # Rebuild the flow with the same state
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        # state=state,
        redirect_uri=redirect_uri
    )

    flow.fetch_token(authorization_response=request.url)

    credentials = flow.credentials

    # Save the credentials and device info in the session or database
    session['credentials'] = {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    }
    return redirect('/calendar')

@google.route('/calendar', methods=['GET','POST'])
def calendar():
    creds = Credentials(**session['credentials'])
    service = build('calendar', 'v3', credentials=creds)

    now = datetime.datetime.utcnow().isoformat() + 'Z'
    events_result = service.events().list(
        calendarId='primary', timeMin=now,
        maxResults=5, singleEvents=True,
        orderBy='startTime').execute()
    events = events_result.get('items', [])

    return render_template('calendar.html', events=events)


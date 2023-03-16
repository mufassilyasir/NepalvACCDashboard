from flask import Blueprint, redirect, url_for, request, session
from .models import Users, db
from flask_login import login_manager, login_user, LoginManager
from urllib.parse import urlparse

from dotenv import load_dotenv

import os
import requests
import urllib.parse as urlparse


auth = Blueprint("auth", __name__)
load_dotenv()


login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.init_app(auth)


@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))


VATSIM_ENDPOINT = os.getenv("VATSIM_ENDPOINT")
VATSIM_CLIENT_ID = os.getenv("VATSIM_CLIENT_ID")
VATSIM_CLIENT_SECRET = os.getenv("VATSIM_CLIENT_SECRET")
VATSIM_REDIRECT_URI = os.getenv("VATSIM_REDIRECT_URI")


@auth.route('/login')
def login():
    url = f"{VATSIM_ENDPOINT}/oauth/authorize"
    params = {
        "client_id": VATSIM_CLIENT_ID,
        "redirect_uri": VATSIM_REDIRECT_URI,
        "response_type": "code",
        "scope": "full_name vatsim_details email",
        "required_scopes": "vatsim_details email"
    }

    url_parse = urlparse.urlparse(url)
    query = url_parse.query
    url_dict = dict(urlparse.parse_qsl(query))
    url_dict.update(params)
    url_new_query = urlparse.urlencode(url_dict)
    url_parse = url_parse._replace(query=url_new_query)
    new_url = urlparse.urlunparse(url_parse)
    return redirect(new_url)


@auth.route('/login/callback')
def authorize():
    code = request.args.get("code")

    data = {
        'grant_type': 'authorization_code',
        'client_id': VATSIM_CLIENT_ID,
        'client_secret': VATSIM_CLIENT_SECRET,
        'redirect_uri': VATSIM_REDIRECT_URI,
        'code':  code

    }
    r = requests.post(f"{VATSIM_ENDPOINT}/oauth/token", data=data)
    try:
        token = r.json()['access_token']
    except KeyError:
        return "Error, missing token from VATSIM. Make sure you didn't access the link directly. If the issue persists contact the vACC Staff."
    headers = {
        'Authorization': f"Bearer {token}",
        'Accept': 'application/json'
    }

    r1 = requests.get(f"{VATSIM_ENDPOINT}/api/user", headers=headers)
    result = r1.json()
    if 'error' in result:
        return result

    try:
        name_first = result['data']['personal']['name_first']
    except KeyError:
        UseCID = "True"
        name_first = "None"
    else:
        UseCID = "False"
    finally:
        try:
            name_last = result['data']['personal']['name_last']
        except KeyError:
            name_last = "None"
        finally:
            try:
                name_full = result['data']['personal']['name_full']
            except KeyError:
                name_full = "None"
            finally:
                try:
                    rating_long = result['data']['vatsim']['rating']['long']
                except KeyError:
                    return "Error in fetching rating. Don't play with URL's"
                else:

                    try:
                        email = result['data']['personal']['email']
                    except KeyError:
                        return "Error in fetching email. Don't play with URL's"
                    else:

                        rating_short = result['data']['vatsim']['rating']['short']
                        pilot_short = result['data']['vatsim']['pilotrating']['short']
                        pilot_long = result['data']['vatsim']['pilotrating']['long']
                        division_id = result['data']['vatsim']['division']['id']
                        division_name = result['data']['vatsim']['division']['name']
                        region_id = result['data']['vatsim']['region']['id']
                        region_name = result['data']['vatsim']['region']['name']
                        subdivision_id = result['data']['vatsim']['subdivision']['id']
                        subdivision_name = result['data']['vatsim']['subdivision']['name']
                        cid = result['data']['cid']

                        found_CID = Users.query.filter_by(id=cid).first()
                        if found_CID:
                            user = Users.query.filter_by(id=cid).first()
                            user.NameFirst = name_first
                            user.NameLast = name_last
                            user.NameFull = name_full
                            user.Email = email
                            user.RatingLong = rating_long
                            user.RatingShort = rating_short
                            user.PilotShort = pilot_short
                            user.PilotLong = pilot_long
                            user.DivisionID = division_id
                            user.DivisionName = division_name
                            user.RegionID = region_id
                            user.RegionName = region_name
                            user.SubdivisionID = subdivision_id
                            user.SubdivisionName = subdivision_name
                            if UseCID:
                                user.UseCID = UseCID
                            db.session.commit()
                            print("Mufassil, member CID was found and their records were updated in our database.")
                            login_user(user, remember=True)
                            
                            try: 
                                if session["origin-nepal-vacc"]:
                                    pass
                            except KeyError:
                                return redirect(url_for("views.dashboard"))
                            else:
                                return redirect(session["origin-nepal-vacc"])

                        else:
                            if UseCID == "True":
                                User_add = Users(id=cid, NameFirst="None", NameLast="None", NameFull="None", Email=email, RatingLong=rating_long, RatingShort=rating_short, PilotShort=pilot_short, PilotLong=pilot_long,
                                                 DivisionID=division_id, DivisionName=division_name, RegionID=region_id, RegionName=region_name, SubdivisionID=subdivision_id, SubdivisionName=subdivision_name, UseCID=UseCID)
                            else:
                                User_add = Users(id=cid, NameFirst=name_first, NameLast=name_last, NameFull=name_full, Email=email, RatingLong=rating_long, RatingShort=rating_short, PilotShort=pilot_short, PilotLong=pilot_long,
                                                 DivisionID=division_id, DivisionName=division_name, RegionID=region_id, RegionName=region_name, SubdivisionID=subdivision_id, SubdivisionName=subdivision_name, UseCID="False")
                            db.session.add(User_add)
                            db.session.commit()
                            user = Users.query.filter_by(id=cid).first()
                            print("Mufassil, member CID was NOT found, and their records were updated in our database.")
                            login_user(user, remember=True)
                            return redirect(url_for("views.policy"))

from flask import Blueprint, render_template, redirect, abort, request, flash, url_for, session, jsonify
from flask_login import current_user
from datetime import datetime
from werkzeug.utils import secure_filename

from .models import SystemLog, Users, VATSIM, db, Extras, Events
from dotenv import load_dotenv
from .avatar import avatardownload
from .utils import updatename
from .emailfunc import send_email, post_discord_message

import os
import requests


views = Blueprint("views", __name__)
load_dotenv()
ZERO = os.getenv("ZERO")
ONE = os.getenv("ONE")
TWO = os.getenv("TWO")
THREE = os.getenv("THREE")
DIRECTOR = os.getenv("DIRECTOR")
DISCORD_ENDPOINT = os.getenv("DISCORD_ENDPOINT")
DISCORD_CHANNEL_ID = os.getenv("DISCORD_CHANNEL_ID")
DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
FILE_UPLOAD_EXTENSIONS = ["PNG", "JPG", "JPEG", "GIF"]


def allowedextensions(imagename):
    if not "." in imagename:
        return False

    extension = imagename.rsplit(".", 1)[1]

    if extension.upper() in FILE_UPLOAD_EXTENSIONS:
        return True
    else:
        return False


def allowed_image_size(imagesize):

    if int(imagesize) <= 2.0 * 1024 * 1024:
        return True
    else:
        return False


@views.route("/policy", strict_slashes=False)
def policy():
    if current_user.is_authenticated:
        query = Users.query.filter_by(id=current_user.id).first()
        if query.PrivacyPolicyAccept == "False":
            if query.UseCID == "False":
                name = query.NameFull
                name_first = query.NameFirst
                name_last = query.NameLast
                avatardownload(name_first, name_last, current_user.id)
            elif query.UseCID == "True":
                name = current_user.id
                name_first = "CID"
                name_last = "CID"
                avatardownload(name_first, name_last, current_user.id)

            user_avatar_path = f"/static/public/Initials/{current_user.id}.png"

            return render_template("privacypolicy.html", name=name, user_avatar_path=user_avatar_path)

        else:
            return redirect(url_for("views.dashboard"))

    else:
        return redirect(url_for("auth.login"))


@views.route("/policy/accept", methods=["GET", "POST"], strict_slashes=False)
def policyaccept():
    if current_user.is_authenticated:
        query = Users.query.filter_by(id=current_user.id).first()
        email = query.Email
        if query.UseCID == "False":
            name_first = query.NameFirst
        elif query.UseCID == "True":
            name_first = current_user.id

        if query.PrivacyPolicyAccept == "False":
            if request.method == "POST":
                email_opt_in = request.form.get("emailoptin")

                if email_opt_in == "1":
                    query.OptinEmails = "True"

                query.PrivacyPolicyAccept = "True"
                time_now = datetime.utcnow()
                system_log = SystemLog(action_by=current_user.id, action=f"Accepted privacy policy and sent welcome email to them.",
                                       timestamp=f"{time_now.strftime('%d-%m-%Y %H:%M:%S')} UTC")
                db.session.add(system_log)
                db.session.commit()
                send_email('Welcome To Nepal vACC Dashboard', 'no-reply@nepalvacc.com',
                           [email], None, None, render_template("/email/welcomeemail.html", name_first=name_first))

                
                try: 
                    if session["origin-nepal-vacc"]:
                        pass
                except KeyError:
                    return redirect(url_for("views.dashboard"))
                else:
                    return redirect(session["origin-nepal-vacc"])
        else:
            return redirect(url_for("views.dashboard"))

    else:
        return redirect(url_for("auth.login"))


@views.route("/policy/deny", methods=["GET", "POST"], strict_slashes=False)
def policydeny():
    if current_user.is_authenticated:
        query = Users.query.filter_by(id=current_user.id).first()
        if query.PrivacyPolicyAccept == "False":
            Users.query.filter_by(id=current_user.id).delete()
            time_now = datetime.utcnow()
            system_log = SystemLog(action_by=current_user.id, action=f"Denied privacy policy. Hence removed from database.",
                                   timestamp=f"{time_now.strftime('%d-%m-%Y %H:%M:%S')} UTC")
            db.session.add(system_log)
            db.session.commit()
            return redirect(url_for("logout"))

        else:
            return redirect(url_for("views.dashboard"))
    else:
        return redirect(url_for("auth.login"))




@views.route("", strict_slashes=False, methods=["POST", "GET"])
async def dashboard():
    if current_user.is_authenticated:
        query = Users.query.filter_by(id=current_user.id).first()
        if query.PrivacyPolicyAccept == "True":
            if current_user.has_role(THREE) == False:
                cid = current_user.id
                user = Users.query.filter_by(id=cid).first()

                if request.method == "POST":
                    group = request.form["group"]

                    if group == "1":
                        user.UseCID = "True"
                        time_now = datetime.utcnow()
                        system_log = SystemLog(action_by=current_user.id, action=f"Changed name through dashboard to use VATSIM CID only.",
                                               timestamp=f"{time_now.strftime('%d-%m-%Y %H:%M:%S')} UTC")
                        db.session.add(system_log)
                        db.session.commit()
                        query1 = Extras.query.filter_by(id=current_user.id).first()
                        if query1:
                            group = "1"
                            cid = current_user.id
                            user_id = query1.discord_user_id
                            name = "None"
                            updatename(user_id, name, cid, group)
                        flash("Name Change Successful!")
                        return redirect(url_for("views.dashboard"))

                    elif group == "2":
                        user.UseCID = "False"
                        user.UseFirst = "False"
                        time_now = datetime.utcnow()
                        system_log = SystemLog(action_by=current_user.id, action=f"Changed name through dashboard to use VATSIM Full Name.",
                                               timestamp=f"{time_now.strftime('%d-%m-%Y %H:%M:%S')} UTC")
                        db.session.add(system_log)
                        db.session.commit()
                        query1 = Extras.query.filter_by(id=current_user.id).first()
                        if query1:
                            group = "2"
                            cid = current_user.id
                            user_id = query1.discord_user_id
                            name = user.NameFull
                            updatename(user_id, name, cid, group)
                        flash("Name Change Successful!")
                        return redirect(url_for("views.dashboard"))

                    elif group == "3":
                        user.UseCID = "False"
                        user.UseFirst = "True"
                        time_now = datetime.utcnow()
                        system_log = SystemLog(action_by=current_user.id, action=f"Changed name through dashboard to use VATSIM First Name only.",
                                               timestamp=f"{time_now.strftime('%d-%m-%Y %H:%M:%S')} UTC")
                        db.session.add(system_log)
                        db.session.commit()
                        query1 = Extras.query.filter_by(id=current_user.id).first()
                        if query1:
                            group = "3"
                            cid = current_user.id
                            user_id = query1.discord_user_id
                            name = user.NameFirst
                            updatename(user_id, name, cid, group)
                        flash("Name Change Successful!")
                        return redirect(url_for("views.dashboard"))

                if user.UseCID == "False" and user.UseFirst == "False":
                    name = user.NameFull
                elif user.UseCID == "False" and user.UseFirst == "True":
                    name = user.NameFirst
                elif user.UseCID == "True":
                    name = cid

                if current_user.has_role(ZERO):
                    check_admin = "True"
                elif current_user.has_role(ONE):
                    check_admin = "True"
                elif current_user.has_role(TWO):
                    check_admin = "True"
                else:
                    check_admin = "False"


                fetch1 = VATSIM.query.filter_by(value=1).first()
                residents = fetch1.json_data

                fetch2 = VATSIM.query.filter_by(value=2).first()
                visitors = fetch2.json_data

                fetch3 = VATSIM.query.filter_by(value=3).first()
                solopeeps = fetch3.json_data

                fetch4 = VATSIM.query.filter_by(value=4).first()
                mentors = fetch4.json_data

                RatingLong = user.RatingLong
                RatingShort = user.RatingShort
                PilotShort = user.PilotShort
                PilotLong = user.PilotLong
                DivisionName = user.DivisionName
                RegionName = user.RegionName
                SubdivisionName = user.SubdivisionName

                if current_user.has_role(ONE):
                    staff_role = "vACC Staff"
                elif current_user.has_role(ZERO):
                    staff_role = "Server"
                elif current_user.has_role(TWO):
                    staff_role = "vACC Instructor/Mentor"
                else:
                    staff_role = "None"

                staff_position = user.StaffPosition

                if user.UseCID == "False" and user.NameFull != "None" and user.NameFirst != "None":
                    naming = user.NameFull
                    name_first = user.NameFirst
                    cid = current_user.id
                    UseCID = "False"

                elif user.UseCID == "True" and user.NameFull != "None" and user.NameFirst != "None":
                    naming = user.NameFull
                    name_first = user.NameFirst
                    cid = current_user.id
                    UseCID = "False"

                elif user.UseCID == "True" and user.NameFull == "None" and user.NameFirst == "None":
                    naming = "None"
                    name_first = "None"
                    cid = current_user.id
                    UseCID = "True"

                if query.user_own_upload == "True":
                    user_avatar_path = query.user_own_upload_link
                else:
                    user_avatar_path = f"/static/public/Initials/{cid}.png"

                query1 = Extras.query.filter_by(id=cid).first()
                if query1:
                    is_linked = query1.discord_link_data
                    is_member = query1.discord_server_data
                    is_discord_profile_allowed = query1.discord_profile_use
                    discord_profile_link = query1.discord_profile_link
                    return render_template("index.html", name=name, check_admin=check_admin, is_linked=is_linked, is_member=is_member, is_discord_profile_allowed=is_discord_profile_allowed, discord_profile_link=discord_profile_link, residents=residents, visitors=visitors, solopeeps=solopeeps, mentors=mentors, cid=cid, RegionName=RegionName, DivisionName=DivisionName, SubdivisionName=SubdivisionName, PilotLong=PilotLong, PilotShort=PilotShort, RatingLong=RatingLong, RatingShort=RatingShort, staff_position=staff_position, staff_role=staff_role, user_avatar_path=user_avatar_path, userUseCID=user.UseCID, OptinEmails=user.OptinEmails, naming=naming, name_first=name_first, UseCID=UseCID)
                else:
                    return render_template("index.html", name=name, check_admin=check_admin, is_linked="No", is_member="No", is_discord_profile_allowed="False", discord_profile_link="None", residents=residents, visitors=visitors, solopeeps=solopeeps, mentors=mentors, cid=cid, RegionName=RegionName, DivisionName=DivisionName, SubdivisionName=SubdivisionName, PilotLong=PilotLong, PilotShort=PilotShort, RatingLong=RatingLong, RatingShort=RatingShort, staff_position=staff_position, staff_role=staff_role, user_avatar_path=user_avatar_path, userUseCID=user.UseCID, OptinEmails=user.OptinEmails, naming=naming, name_first=name_first, UseCID=UseCID)

            else:
                abort(403)

        else:
            return redirect(url_for("views.policy"))

    elif current_user.is_anonymous:
        return redirect(url_for("auth.login"))


@views.route("/events", strict_slashes=False)
def eventsroute():
    if current_user.is_authenticated:
        query0 = Users.query.filter_by(id=current_user.id).first()
        if query0.PrivacyPolicyAccept == "True":
            if current_user.has_role(THREE) == False:

                event_list = []
                event_get = Events.query.all()
                for event in event_get:
                    if event.start_time != "None":

                        start_time = event.start_time[:-11]
                        end_time = event.end_time[:-11]
                        event_banner = event.event_banner
                        event_link = event.event_link
                        values = {
                            "start_time": start_time,
                            "end_time": end_time,
                            "event_banner": event_banner,
                            "event_link": event_link
                        }
                        event_list.append(values)

                cid = current_user.id
                if query0.UseCID == "False":
                    name = query0.NameFull
                elif query0.UseCID == "True":
                    name = cid

                if query0.UseCID == "False" and query0.UseFirst == "False":
                    name = query0.NameFull
                elif query0.UseCID == "False" and query0.UseFirst == "True":
                    name = query0.NameFirst
                elif query0.UseCID == "True":
                    name = cid

                query2 = Extras.query.filter_by(id=cid).first()

                if current_user.has_role(ZERO):
                    check_admin = "True"
                elif current_user.has_role(ONE):
                    check_admin = "True"
                elif current_user.has_role(TWO):
                    check_admin = "True"
                else:
                    check_admin = "False"

                fetch1 = VATSIM.query.filter_by(value=1).first()
                residents = fetch1.json_data

                fetch2 = VATSIM.query.filter_by(value=2).first()
                visitors = fetch2.json_data

                fetch3 = VATSIM.query.filter_by(value=3).first()
                solopeeps = fetch3.json_data

                fetch4 = VATSIM.query.filter_by(value=4).first()
                mentors = fetch4.json_data

                if query0.user_own_upload == "True":
                    user_avatar_path = query0.user_own_upload_link
                else:
                    user_avatar_path = f"/static/public/Initials/{cid}.png"

                if query2:
                    is_linked = query2.discord_link_data
                    is_member = query2.discord_server_data
                    is_discord_profile_allowed = query2.discord_profile_use
                    discord_profile_link = query2.discord_profile_link

                    if len(event_list) != 0:
                        return render_template("events.html", events=event_list, name=name, check_admin=check_admin, is_linked=is_linked, is_member=is_member, is_discord_profile_allowed=is_discord_profile_allowed, discord_profile_link=discord_profile_link, residents=residents, visitors=visitors, solopeeps=solopeeps, mentors=mentors, user_avatar_path=user_avatar_path, OptinEmails=query0.OptinEmails)
                    else:
                        return render_template("events.html", events="None", name=name, check_admin=check_admin, is_linked=is_linked, is_member=is_member, is_discord_profile_allowed=is_discord_profile_allowed, discord_profile_link=discord_profile_link, residents=residents, visitors=visitors, solopeeps=solopeeps, mentors=mentors, user_avatar_path=user_avatar_path, OptinEmails=query0.OptinEmails)

                else:
                    if len(event_list) != 0:
                        return render_template("events.html", events=event_list, name=name, check_admin=check_admin, is_linked="No", is_member="No", is_discord_profile_allowed="False", discord_profile_link="None", residents=residents, visitors=visitors, solopeeps=solopeeps, mentors=mentors, user_avatar_path=user_avatar_path, OptinEmails=query0.OptinEmails)
                    else:
                        return render_template("events.html", events="None", name=name, check_admin=check_admin, is_linked="No", is_member="No", is_discord_profile_allowed="False", discord_profile_link="None", residents=residents, visitors=visitors, solopeeps=solopeeps, mentors=mentors, user_avatar_path=user_avatar_path, OptinEmails=query0.OptinEmails)

            else:
                abort(403)
        else:
            return redirect(url_for("views.policy"))
    else:
        return redirect(url_for("auth.login"))


@views.route("/upload/avatar", methods=["POST"], strict_slashes=False)
def avataruploader():
    if current_user.is_authenticated:
        if current_user.has_role(THREE) == False:
            if request.method == "POST":
                if request.files:

                    if not allowed_image_size(request.cookies.get("imagesize")):
                        flash("Maximum avatar file size must be 2.0 MB.", category='error')
                        return redirect(url_for("views.dashboard"))

                    image = request.files['image']

                    if image.filename == "":
                        flash("To upload an avatar you should give file a name.", category='error')

                    elif not allowedextensions(image.filename):
                        flash("Avatar file extensions must be 'PNG', 'JPG', 'JPEG', 'GIF' extensions only.", category='error')

                    else:
                        path = f"{os.path.dirname(os.path.abspath(__file__))}/static/public/uploads/{current_user.id}"
                        if os.path.exists(path) == False:
                            os.chdir(f"{os.path.dirname(os.path.abspath(__file__))}/static/public/uploads")
                            os.makedirs(str(f"{current_user.id}"))

                        for files in os.listdir(path):
                            if files:
                                os.remove(
                                    f"{os.path.dirname(os.path.abspath(__file__))}/static/public/uploads/{current_user.id}/{files}")

                        saving_path = f"/static/public/uploads/{current_user.id}"
                        image.save(os.path.join(
                            f"{os.path.dirname(os.path.abspath(__file__))}/{saving_path}", secure_filename(image.filename)))
                        query = Users.query.filter_by(id=current_user.id).first()
                        query1 = Extras.query.filter_by(id=current_user.id).first()
                        time_now = datetime.utcnow()
                        add_to_system_log = SystemLog(
                            action_by= current_user.id, action = "Uploaded custom avatar", timestamp = f"{time_now.strftime('%d-%m-%Y %H:%M:%S')} UTC")
                        db.session.add(add_to_system_log)
                        if query1:
                            query1.discord_profile_use = "False"
                        query.user_own_upload = "True"
                        query.user_own_upload_link = os.path.join(saving_path, secure_filename(image.filename))

                        db.session.commit()
                        flash("Custom avatar uploaded!", category='success')

                    return redirect(url_for("views.dashboard"))
        else:
            abort(403)
    else:
        return redirect(url_for("auth.login"))


@views.route("/avatar/reset", methods=["POST"], strict_slashes=False)
def avatarreset():
    if current_user.is_authenticated:
        if current_user.has_role(THREE) == False:
            if request.method == "POST":
                value = request.form["resetavatar"]
                if value == "resetpls":
                    query = Users.query.filter_by(id=current_user.id).first()
                    query1 = Extras.query.filter_by(id=current_user.id).first()
                    if query1:
                        query1.discord_profile_use = "False"
                    query.user_own_upload = "False"
                    db.session.commit()
                    flash("Avatar set to default", category='success')
                    return redirect(url_for("views.dashboard"))

        else:
            abort(403)
    else:
        return redirect(url_for("auth.login"))


@views.route("/email-join", strict_slashes=False)
def emailjoin():
    if current_user.is_authenticated:
        query0 = Users.query.filter_by(id=current_user.id).first()
        if query0.PrivacyPolicyAccept == "True":
            if current_user.has_role(THREE) == False:
                query0.OptinEmails = "True"
                time_now = datetime.utcnow()
                system_log = SystemLog(action_by=current_user.id, action=f"Opted in the emails through dashboard",
                                       timestamp=f"{time_now.strftime('%d-%m-%Y %H:%M:%S')} UTC")
                db.session.add(system_log)
                db.session.commit()
                flash("Successfully opted in emails!")
                return redirect(url_for("views.dashboard"))
            else:
                abort(403)
        else:
            return redirect(url_for("views.policy"))
    else:
        return redirect(url_for("auth.login"))


@views.route("/email-leave", strict_slashes=False)
def emailleave():
    if current_user.is_authenticated:
        query0 = Users.query.filter_by(id=current_user.id).first()
        if query0.PrivacyPolicyAccept == "True":
            if current_user.has_role(THREE) == False:
                query0.OptinEmails = "False"
                time_now = datetime.utcnow()
                system_log = SystemLog(action_by=current_user.id, action=f"Opted out of the emails through dashboard",
                                       timestamp=f"{time_now.strftime('%d-%m-%Y %H:%M:%S')} UTC")
                db.session.add(system_log)
                db.session.commit()
                flash("Successfully opted out of emails!")
                return redirect(url_for("views.dashboard"))
            else:
                abort(403)
        else:
            return redirect(url_for("views.policy"))
    else:
        return redirect(url_for("auth.login"))


@views.route("/admin/mass/email", methods=["POST", "GET"], strict_slashes=False)
def massemail():
    if current_user.is_authenticated:
        if current_user.has_role(ZERO) or current_user.has_role(ONE):
            if request.method == "POST":
                group = request.form["group"]
                subject = request.form["subject"]
                body = request.form["emailbody"]
                reason = request.form["reason"]

                if len(subject) < 10:
                    flash("Nope, your subject is less than 10 characters. I won't send it!", category='error')
                elif len(body) < 10:
                    flash("Nope your body is less then 10 characters. I won't send it!", category='error')
                elif len(reason) < 10:
                    flash("Nope your reason is less then 10 characters. I won't send it!", category='error')
                else:

                    if group == "1":
                        mailing_group = "1 - (People Opted In Emails)"
                        mass_group_emails = []
                        users = Users.query.filter_by(OptinEmails="True").all()
                        for user in users:
                            mass_group_emails.append(user.Email)

                        send_email(subject, ('Nepal vACC Mass Email', 'mass-email@members.nepalvacc.com'), [
                                   'mass-email@members.nepalvacc.com'], mass_group_emails,None, render_template("/email/massemailtemp.html", reason=reason, body=body, subject=subject))

                    elif group == "2":
                        r = requests.get("https://hq.vatwa.net/api/vacc/NPL/resident")

                        mailing_group = "2 - Residents (Opted in emails)"
                        mass_group_emails = []
                        users_in_db = []
                        users_in_hq = []
                        for resident in r.json():
                            users_in_hq.append(int(resident['cid']))

                        users = Users.query.filter_by(OptinEmails="True").all()
                        for user in users:
                            users_in_db.append(user.id)

                        if len(set(users_in_hq).intersection(set(users_in_db))) > 0:
                            for ids in set(users_in_hq).intersection(set(users_in_db)):
                                for filter in Users.query.filter_by(id=ids).all():
                                    mass_group_emails.append(filter.Email)

                            send_email(subject, ('Nepal vACC Mass Email', 'mass-email@members.nepalvacc.com'), [
                                'mass-email@members.nepalvacc.com'], mass_group_emails, None, render_template("/email/massemailtemp.html", reason=reason, body=body, subject=subject))
                        else:
                            flash(
                                "Sorry couldn't find any ids. This might happen because VATWA HQ didn't return correct response. Error Line 696.", category='error')
                            return redirect(request.base_url)

                    elif group == "3":
                        r = requests.get("https://hq.vatwa.net/api/vacc/NPL/resident")

                        mailing_group = "3 - Residents (Everyone)"
                        mass_group_emails = []
                        users_in_db = []
                        users_in_hq = []

                        for resident in r.json():
                            users_in_hq.append(int(resident['cid']))

                        users = Users.query.all()
                        for user in users:
                            users_in_db.append(user.id)

                        if len(set(users_in_hq).intersection(set(users_in_db))) > 0:
                            for ids in set(users_in_hq).intersection(set(users_in_db)):
                                for filter in Users.query.filter_by(id=ids).all():
                                    mass_group_emails.append(filter.Email)

                            send_email(subject, ('Nepal vACC Mass Email', 'mass-email@members.nepalvacc.com'), [
                                'mass-email@members.nepalvacc.com'], mass_group_emails, None, render_template("/email/massemailtemp.html", reason=reason, body=body, subject=subject))
                        else:
                            flash(
                                "Sorry couldn't find any ids. This might happen because VATWA HQ didn't return correct response. Error Line 696.", category='error')
                            return redirect(request.base_url)

                    elif group == "4":
                        r = requests.get("https://hq.vatwa.net/api/vacc/NPL/visitor")

                        mailing_group = "4 - Visitors (Opted in emails)"
                        mass_group_emails = []
                        users_in_db = []
                        users_in_hq = []

                        for visitor in r.json():
                            users_in_hq.append(int(visitor['cid']))

                        users = Users.query.filter_by(OptinEmails="True").all()
                        for user in users:
                            users_in_db.append(user.id)

                        if len(set(users_in_hq).intersection(set(users_in_db))) > 0:
                            for ids in set(users_in_hq).intersection(set(users_in_db)):
                                for filter in Users.query.filter_by(id=ids).all():
                                    mass_group_emails.append(filter.Email)

                            send_email(subject, ('Nepal vACC Mass Email', 'mass-email@members.nepalvacc.com'), [
                                'mass-email@members.nepalvacc.com'], mass_group_emails, None, render_template("/email/massemailtemp.html", reason=reason, body=body, subject=subject))
                        else:
                            flash(
                                "Sorry couldn't find any ids. This might happen because VATWA HQ didn't return correct response. Error Line 696.", category='error')
                            return redirect(request.base_url)

                    elif group == "5":
                        r = requests.get("https://hq.vatwa.net/api/vacc/NPL/visitor")

                        mailing_group = "5 - Visitors (Everyone)"
                        mass_group_emails = []
                        users_in_db = []
                        users_in_hq = []

                        for visitor in r.json():
                            users_in_hq.append(int(visitor['cid']))

                        users = Users.query.all()
                        for user in users:
                            users_in_db.append(user.id)

                        if len(set(users_in_hq).intersection(set(users_in_db))) > 0:
                            for ids in set(users_in_hq).intersection(set(users_in_db)):
                                for filter in Users.query.filter_by(id=ids).all():
                                    mass_group_emails.append(filter.Email)

                            send_email(subject, ('Nepal vACC Mass Email', 'mass-email@members.nepalvacc.com'), [
                                'mass-email@members.nepalvacc.com'], mass_group_emails, None, render_template("/email/massemailtemp.html", reason=reason, body=body, subject=subject))
                        else:
                            flash(
                                "Sorry couldn't find any ids. This might happen because VATWA HQ didn't return correct response. Error Line 696.", category='error')
                            return redirect(request.base_url)
                    
                    
                    elif group == "6":
                        r = requests.get("https://hq.vatwa.net/api/vacc/NPL/staff")

                        mailing_group = "6 - Nepal vACC Staff (Everyone)"
                        mass_group_emails = []
                        users_in_db = []
                        users_in_hq = []

                        for staff in r.json():
                            users_in_hq.append(int(staff['cid']))

                        users = Users.query.all()
                        for user in users:
                            users_in_db.append(user.id)

                        if len(set(users_in_hq).intersection(set(users_in_db))) > 0:
                            for ids in set(users_in_hq).intersection(set(users_in_db)):
                                for filter in Users.query.filter_by(id=ids).all():
                                    mass_group_emails.append(filter.Email)

                            send_email(subject, ('Nepal vACC Mass Email', 'mass-email@members.nepalvacc.com'), [
                                'mass-email@members.nepalvacc.com'], mass_group_emails, None, render_template("/email/massemailtemp.html", reason=reason, body=body, subject=subject))
                        else:
                            flash(
                                "Sorry couldn't find any ids. This might happen because VATWA HQ didn't return correct response. Error Line 696.", category='error')
                            return redirect(request.base_url)


                    elif group == "7":
                        mailing_group = "7 - (Everyone)"
                        mass_group_emails = []
                        users = Users.query.all()
                        for user in users:
                            mass_group_emails.append(user.Email)

                        send_email(subject, ('Nepal vACC Mass Email', 'mass-email@members.nepalvacc.com'), [
                                   'mass-email@members.nepalvacc.com'], mass_group_emails, None, render_template("/email/massemailtemp.html", reason=reason, body=body, subject=subject))

                    query = Extras.query.filter_by(id=current_user.id).first()
                    if query:
                        user_id = query.discord_user_id
                    else:
                        user_id = "DISCORD ACCOUNT NOT LINKED :expressionless:?"

                    data = {
                        "content": f"<@{user_id}> Mass Emailed {len(mass_group_emails)} people on group **{mailing_group}**, with a reason **{reason}**"}

                    post_discord_message(data, DISCORD_BOT_TOKEN, DISCORD_ENDPOINT, DISCORD_CHANNEL_ID)

                    time_now = datetime.utcnow()
                    system_log = SystemLog(
                        action_by=current_user.id, action=f"Mass emailed {len(mass_group_emails)} people, with a reason {reason}", timestamp=f"{time_now.strftime('%d-%m-%Y %H:%M:%S')} UTC")
                    db.session.add(system_log)
                    db.session.commit()
                    flash("Mass Email Sent!", category='success')
                    return render_template("massemail.html")

            return render_template("massemail.html")

        else:
            abort(403)
    else:
        return redirect(url_for("auth.login"))


@views.route('/admin/vatsim/member-search', methods=['GET', 'POST'])
def vatsimmembersearch():
    if current_user.is_authenticated:
        if current_user.id == 10000006 or current_user.id == int(DIRECTOR):
            if request.method == "POST":
                cid = request.form['vatsim_id']
                reason = request.form['reason']
                if len(cid) < 5:
                    flash("CID must be greater than 5 numbers", category='error')
                    return redirect(url_for("views.vatsimmembersearch"))
                elif len(reason) < 4:
                    flash("Please enter reason", category='error')
                    return redirect(url_for("views.vatsimmembersearch"))

                

                headers = {"Authorization": "Token 4a97b61de2569b4988335d0d79b5006c0f15382e"}
                r = requests.get(f"https://api.vatsim.net/api/ratings/{cid}/", headers=headers)

                atc_ratings = {"0" : "Account Disabled", "-1" : "Inactive Account", "1" : "Pilot/Observer (OBS)", "2" : "Tower Trainee (S1)", "3" : "Tower Controller (S2)", "4" : "TMA Controller (S3)", "5" : "Enroute Controller (C1)", "7" : "Senior Enroute Controller (C3)", "8" : "Instructor (I1)", "10" : "Senior Instructor (I3)", "11" : "Supervisor (SUP)", "12" : "Administrator (ADM)"} 
                pilot_ratings = {"0" : "P0", "1" : "P1", "3" : "P2", "7" : "P3", "15" : "P4"}
                result = r.json()
                atc = atc_ratings[str(result['rating'])]
                pilot = pilot_ratings[str(result['pilotrating'])]
                result['rating'] = atc
                result['pilotrating'] = pilot
                add_log = SystemLog(action_by = current_user.id, action=f"Searched ID: {cid} with reason {reason}", timestamp = f"{datetime.utcnow().strftime('%d-%m-%Y %H:%M:%S')} UTC")
                db.session.add(add_log)
                db.session.commit()
                
                return render_template("searchmember.html", cid=result['id'], name=result['name_first'] + " "+ result['name_last'], email=result['email'],
                region=result['region'], division=result['division'], subdivision=result['subdivision'], country=result['country'], atcrating=result['rating'],
                pilotrating=result['pilotrating'], lastrating=result['lastratingchange'], regdate=result['reg_date'])
            return render_template("searchmember.html")
        else:
            abort(403)
from flask import Blueprint, redirect, url_for, request, session, flash, abort
from flask_login import current_user
from dotenv import load_dotenv
from .models import Users, db, Extras, SystemLog
from .utils import discordlogin, discordspeciallogin, getuser, getguilds, discordserverjoinlogin, refreshtoken, discordlogoutrequest, add_guild_member
from datetime import datetime
from .emailfunc import post_discord_message

import os

dis = Blueprint("dis", __name__)
load_dotenv()

DISCORD_ENDPOINT = os.getenv("DISCORD_ENDPOINT")
DISCORD_LINK_URI = os.getenv("DISCORD_LINK_URI")
DISCORD_SERVER_URI = os.getenv("DISCORD_SERVER_URI")
DISCORD_GUILD_ID = os.getenv("DISCORD_GUILD_ID")
DISCORD_ENDPOINT = os.getenv("DISCORD_ENDPOINT")
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
DISCORD_CHANNEL_ID = os.getenv("DISCORD_CHANNEL_ID")
DISCORD_SPECIAL_REDIRECT_URI = os.getenv("DISCORD_SPECIAL_REDIRECT_URI")
THREE = os.getenv("THREE")


@dis.route("/discord/link")
def oauth():
    if current_user.is_authenticated:
        query = Users.query.filter_by(id=current_user.id).first()
        if query.PrivacyPolicyAccept == "True":
            if current_user.has_role(THREE):
                abort(403)
            else:
                return redirect(DISCORD_LINK_URI)
        else:
            return redirect(url_for("views.policy"))
    else:
        return redirect(url_for("auth.login"))


@dis.route("/discord/link/callback")
def oauthcallback():
    if current_user.is_authenticated:
        query = Users.query.filter_by(id=current_user.id).first()
        if query.PrivacyPolicyAccept == "True":
            if current_user.has_role(THREE) == False:
                code = request.args.get("code")
                error = request.args.get("error")
                if error == None:
                    if code != None:
                        result = discordlogin(code)

                        session.permanent = True
                        try:
                            session['refresh_token'] = result['refresh_token']
                        except:
                            return redirect(url_for("dis.speciallinkdiscord"))
                        else:
                            cid = current_user.id

                            user = getuser(result['access_token'])
                            if Extras.query.filter(Extras.discord_user_id == user['id']).first():
                                flash(
                                    "This Discord account is already linked with an another user account. Any questions? Contact vACC Staff")
                                return redirect(url_for("views.dashboard"))

                            else:
                                guilds = getguilds(result['access_token'])

                                guilds_list = []
                                for g in guilds:
                                    guilds_list.append(g['id'])

                                if DISCORD_GUILD_ID not in guilds_list:
                                    query = Extras.query.filter_by(id=cid).first()
                                    if query:

                                        query.discord_server_data = "False"
                                        query.discord_link_data = "True"
                                        time_now = datetime.utcnow()
                                        system_log = SystemLog(
                                            action_by=current_user.id, action=f"Linked their Discord account.", timestamp=f"{time_now.strftime('%d-%m-%Y %H:%M:%S')} UTC")
                                        db.session.add(system_log)
                                        db.session.commit()
                                        session['token'] = result['access_token']
                                        session.permanent = True
                                    else:

                                        discord_data_add = Extras(id=cid, discord_link_data="True",
                                                                  discord_server_data="False", discord_user_id=user['id'])
                                        db.session.add(discord_data_add)
                                        time_now = datetime.utcnow()
                                        system_log = SystemLog(
                                            action_by=current_user.id, action=f"Linked their Discord account.", timestamp=f"{time_now.strftime('%d-%m-%Y %H:%M:%S')} UTC")
                                        db.session.add(system_log)
                                        db.session.commit()
                                        session['token'] = result['access_token']
                                        session.permanent = True

                                    return redirect(url_for("views.dashboard"))

                                elif DISCORD_GUILD_ID in guilds_list:
                                    query = Extras.query.filter_by(id=cid).first()
                                    if query:

                                        query.discord_server_data = "True"
                                        query.discord_link_data = "True"
                                        time_now = datetime.utcnow()
                                        system_log = SystemLog(
                                            action_by=current_user.id, action=f"Linked their Discord account.", timestamp=f"{time_now.strftime('%d-%m-%Y %H:%M:%S')} UTC")
                                        db.session.add(system_log)
                                        db.session.commit()
                                        session['token'] = result['access_token']
                                        session.permanent = True

                                    else:

                                        discord_data_add = Extras(id=cid, discord_link_data="True",
                                                                  discord_server_data="True", discord_user_id=user['id'])
                                        db.session.add(discord_data_add)
                                        time_now = datetime.utcnow()
                                        system_log = SystemLog(
                                            action_by=current_user.id, action=f"Linked their Discord account.", timestamp=f"{time_now.strftime('%d-%m-%Y %H:%M:%S')} UTC")
                                        db.session.add(system_log)
                                        db.session.commit()
                                        session.permanent = True
                                        session['token'] = result['access_token']
                                        print(session['token'])

                                    return redirect(url_for("views.dashboard"))
                    else:
                        return redirect(url_for("dis.oauth"))
                else:
                    return redirect(url_for("views.dashboard"))
            else:
                abort(403)

        else:
            return redirect(url_for("views.policy"))
    else:
        return redirect(url_for("auth.login"))


@dis.route("/discord/server/join")
def ServerJoin():
    if current_user.is_authenticated:
        query = Users.query.filter_by(id=current_user.id).first()
        if query.PrivacyPolicyAccept == "True":
            if current_user.has_role(THREE):
                abort(403)
            else:
                return redirect(DISCORD_SERVER_URI)
        else:
            return redirect(url_for("views.policy"))
    else:
        return redirect(url_for("auth.login"))


@dis.route("/discord/server/join/callback")
def ServerJoinCallback():
    if current_user.is_authenticated:
        query = Users.query.filter_by(id=current_user.id).first()
        if query.PrivacyPolicyAccept == "True":
            if current_user.has_role(THREE) == False:
                code = request.args.get("code")

                result = discordserverjoinlogin(code)

                session['access_token_guilds'] = result['access_token']
                session.permanent = True
                if "access_token_guilds" in session:
                    cid = current_user.id
                    user = getuser(result['access_token'])
                    guilds = getguilds(result['access_token'])

                    guilds_list = []
                    for g in guilds:
                        guilds_list.append(g['id'])

                    if DISCORD_GUILD_ID not in guilds_list:
                        query = Extras.query.filter_by(id=cid).first()
                        name_query = Users.query.filter_by(id=cid).first()
                        if query:
                            if name_query.UseCID == "False" and name_query.UseFirst == "False":
                                name = name_query.NameFull
                                check = 1

                            elif name_query.UseCID == "False" and name_query.UseFirst == "True":
                                name = name_query.NameFirst
                                check = 2

                            elif name_query.UseCID == "True":
                                name = None
                                check = 3

                            guild_id = DISCORD_GUILD_ID

                            add_guild_member(guild_id, user['id'], session['access_token_guilds'], name, cid, check)
                            query.discord_server_data = "True"
                            time_now = datetime.utcnow()
                            system_log = SystemLog(action_by=current_user.id, action=f"Joined Nepal vACC Discord server.",
                                                   timestamp=f"{time_now.strftime('%d-%m-%Y %H:%M:%S')} UTC")
                            db.session.add(system_log)
                            db.session.commit()

                            return redirect(url_for("views.dashboard"))

                        else:
                            return redirect(url_for("dis.oauth"))

                    elif DISCORD_GUILD_ID in guilds_list:
                        flash("You are already a member of the Nepal vACC Discord server.")
                        return redirect(url_for("views.dashboard"))

                else:
                    return redirect(url_for("dis.ServerJoin"))

            else:
                abort(403)
        else:
            return redirect(url_for("views.policy"))
    else:
        return redirect(url_for("auth.login"))


@dis.route("/discord/profile/set")
def discordprofilepicset():
    if current_user.is_authenticated:
        query = Users.query.filter_by(id=current_user.id).first()
        if query.PrivacyPolicyAccept == "True":
            if current_user.has_role(THREE) == False:
                if "token" in session:
                    if "refresh_token" in session:
                        cid = current_user.id

                        try:
                            some_variable = refreshtoken(session['refresh_token'])
                        except:
                            return redirect(url_for("dis.speciallinkdiscord"))

                        access_token = some_variable['access_token']
                        session.permanent = True
                        session['token'] = access_token
                        session['refresh_token'] = some_variable['refresh_token']

                        store = getuser(access_token)
                        
                        try:
                            if store['avatar'].startswith("a_"):
                                profile_link = f"https://cdn.discordapp.com/avatars/{store['id']}/{store['avatar']}.gif"
                            else:
                                profile_link = f"https://cdn.discordapp.com/avatars/{store['id']}/{store['avatar']}.png"
                        except:
                            profile_link = "None"

                        profile_link = profile_link
                        query1 = Extras.query.filter_by(id=cid).first()
                        query1.discord_profile_link = profile_link
                        query1.discord_profile_use = "True"
                        query.user_own_upload = "False"
                        time_now = datetime.utcnow()
                        system_log = SystemLog(action_by=current_user.id, action=f"Set their profile picture as Discord profile picture.",
                                               timestamp=f"{time_now.strftime('%d-%m-%Y %H:%M:%S')} UTC")
                        db.session.add(system_log)
                        db.session.commit()
                        flash("Discord profile picture set as avatar.", category='success')
                        return redirect(url_for("views.dashboard"))

                    else:
                        session['nepal-vacc-referrer'] = request.base_url
                        return redirect(url_for("dis.speciallinkdiscord"))

                else:
                    session['nepal-vacc-referrer'] = request.base_url
                    return redirect(url_for("dis.speciallinkdiscord"))

            else:
                abort(403)

        else:
            return redirect(url_for("views.policy"))

    else:
        return redirect(url_for("auth.login"))


@dis.route("/discord/profile/remove")
def discordprofilepicrem():
    if current_user.is_authenticated:
        query = Users.query.filter_by(id=current_user.id).first()
        if query.PrivacyPolicyAccept == "True":
            if current_user.has_role(THREE) == False:
                cid = current_user.id

                query = Extras.query.filter_by(id=cid).first()
                query.discord_profile_link = "None"
                query.discord_profile_use = "False"
                time_now = datetime.utcnow()
                system_log = SystemLog(action_by=current_user.id, action=f"Removed their discord profile picture from dashboard.",
                                        timestamp=f"{time_now.strftime('%d-%m-%Y %H:%M:%S')} UTC")
                db.session.add(system_log)
                db.session.commit()
                return redirect(url_for("views.dashboard"))

            else:
                abort(403)

        else:
            return redirect(url_for("views.policy"))

    else:
        return redirect(url_for("auth.login"))


@dis.route("/discord/special/link")
def speciallinkdiscord():
    if current_user.is_authenticated:
        query = Users.query.filter_by(id=current_user.id).first()
        if query.PrivacyPolicyAccept == "True":
            if current_user.has_role(THREE):
                abort(403)
            else:
                return redirect(DISCORD_SPECIAL_REDIRECT_URI)

        else:
            return redirect(url_for("views.policy"))

    else:
        return redirect(url_for("auth.login"))


@dis.route("/discord/special/link/callback")
def speciallinkdiscordcallback():
    if current_user.is_authenticated:
        query = Users.query.filter_by(id=current_user.id).first()
        if query.PrivacyPolicyAccept == "True":
            if current_user.has_role(THREE) == False:
                code = request.args.get("code")

                result = discordspeciallogin(code)

                session['refresh_token'] = result['refresh_token']
                session['token'] = result['access_token']
                return redirect(url_for("views.dashboard"))

            else:
                abort(403)

        else:
            return redirect(url_for("views.policy"))

    else:
        return redirect(url_for("auth.login"))


@dis.route("/discord/unlink")
def discordlogout():
    if current_user.is_authenticated:
        query = Users.query.filter_by(id=current_user.id).first()
        if query.PrivacyPolicyAccept == "True":
            if current_user.has_role(THREE) == False:
                cid = current_user.id
                query = Extras.query.filter_by(id=cid).first()
                if query:
                    user_id = query.discord_user_id
                    if query.discord_server_data == "True":

                        discordlogoutrequest()

                        data = {
                            "content": f"<@{user_id}> Unlinked his/her Discord account from the Dashboard, hence they were kicked! :wink: "}
                        post_discord_message(data, DISCORD_BOT_TOKEN, DISCORD_ENDPOINT, DISCORD_CHANNEL_ID)

                if query.discord_server_data == "True":
                    try:
                        session.pop("access_token_guilds")
                    except KeyError:
                        print("User did not join from our service")
                try:
                    session.pop("refresh_token")
                except KeyError:
                    pass
                try:
                    session.pop("token")
                except KeyError:
                    pass

                Extras.query.filter_by(id=cid).delete()
                time_now = datetime.utcnow()
                system_log = SystemLog(action_by=current_user.id, action=f"Unlinked their Discord account.",
                                       timestamp=f"{time_now.strftime('%d-%m-%Y %H:%M:%S')} UTC")
                db.session.add(system_log)
                db.session.commit()

                return redirect(url_for("views.dashboard"))

            else:
                abort(403)
        else:
            return redirect(url_for("views.policy"))

    else:
        return redirect(url_for("auth.login"))

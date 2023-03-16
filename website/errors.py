from flask import Blueprint, render_template, request
from flask_login import current_user
from .emailfunc import send_email
from dotenv import load_dotenv
from .models import Users

import os

errors = Blueprint("errors", __name__)

load_dotenv()
THREE = os.getenv("THREE")
IT_EMAIL = os.getenv("IT_EMAIL")


@errors.app_errorhandler(404)
def notfound(error):
    if current_user.is_authenticated:
        query = Users.query.filter_by(id=current_user.id).first()

        if query.UseCID == "False":
            name = query.NameFull
        elif query.UseCID == "True":
            name = current_user.id

        if query.UseCID == "False" and query.UseFirst == "False":
            name = query.NameFull
        elif query.UseCID == "False" and query.UseFirst == "True":
            name = query.NameFirst
        elif query.UseCID == "True":
            name = current_user.id

        user_avatar_path = f"/static/public/Initials/{current_user.id}.png"

    else:
        name = "None"
        user_avatar_path = "None"

    return render_template("/errors/404.html", url=request.url, name=name, user_avatar_path=user_avatar_path), 404


@errors.app_errorhandler(403)
def forbidden(error):
    if current_user.is_authenticated:
        query = Users.query.filter_by(id=current_user.id).first()
        user_id = current_user.id
        
        if query.UseCID == "False":
            name = query.NameFull
        elif query.UseCID == "True":
            name = current_user.id

        if query.UseCID == "False" and query.UseFirst == "False":
            name = query.NameFull
        elif query.UseCID == "False" and query.UseFirst == "True":
            name = query.NameFirst
        elif query.UseCID == "True":
            name = current_user.id

        user_avatar_path = f"/static/public/Initials/{current_user.id}.png"

        if current_user.has_role(THREE) == True:
            restricted = "True"
        else:
            restricted = "False"


    else:
        name = "None"
        user_avatar_path = "None"
        restricted = "False"
        user_id = request.remote_addr

    send_email('Nepal vACC 403 Server Error', 'no-reply@nepalvacc.com', [IT_EMAIL], None, None, render_template(
        "/email/emailerrors.html", user_id=user_id, error=error, url=request.url))
    return render_template("/errors/403.html",url=request.url, name=name, user_avatar_path=user_avatar_path, restricted=restricted), 403


@errors.app_errorhandler(500)
def servererror(error):
    print(request.method)
    if current_user.is_authenticated:
        query = Users.query.filter_by(id=current_user.id).first()
        user_id = current_user.id
        
        if query.UseCID == "False":
            name = query.NameFull
        elif query.UseCID == "True":
            name = current_user.id

        if query.UseCID == "False" and query.UseFirst == "False":
            name = query.NameFull
        elif query.UseCID == "False" and query.UseFirst == "True":
            name = query.NameFirst
        elif query.UseCID == "True":
            name = current_user.id

        user_avatar_path = f"/static/public/Initials/{current_user.id}.png"

    else:
        name = "None"
        user_avatar_path = "None"
        user_id = request.remote_addr
    send_email('Nepal vACC 500 Server Error', 'no-reply@nepalvacc.com', [IT_EMAIL], None, None, render_template(
        "/email/emailerrors.html", user_id=user_id, error=error, url=request.url))
    return render_template("/errors/500.html", url=request.url, name=name, user_avatar_path=user_avatar_path), 500

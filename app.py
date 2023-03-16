from flask import render_template, redirect, url_for, abort, request, session
from flask_login import logout_user, current_user
from flask_admin import Admin, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_security import Security, SQLAlchemyUserDatastore
from flask_admin.menu import MenuLink
from dotenv import load_dotenv
from waitress import serve
from website import create_app
from website.models import Extras, db, Role, Users, VATSIM, SystemLog
from urllib.parse import urlparse, urlunparse

import os
import random




load_dotenv()
ZERO = os.getenv("ZERO")
ONE = os.getenv("ONE")
TWO = os.getenv("TWO")
DIRECTOR = os.getenv("DIRECTOR")


app = create_app()

user_datastore = SQLAlchemyUserDatastore(db, Users, Role)
security = Security(app, user_datastore)


class UserController(ModelView):
    can_view_details = True
    column_list = ['id', 'NameFirst', 'NameLast', 'NameFull', 'Email', "RatingLong", "RatingShort", "PilotShort", "PilotLong", "DivisionID", "DivisionName",
                   "RegionID", "RegionName", "SubdivisionID", "SubdivisionName", "DiscordLinked", "DiscordServerJoin", "PrivacyPolicyAccept", "OptinEmails"]
    column_filters = [
        'id',
        'NameFirst',
        'NameLast',
        'NameFull',
        'Email',
        "RatingLong",
        "RatingShort",
        "PilotShort",
        "PilotLong",
        "DivisionID",
        "DivisionName",
        "RegionID",
        "RegionName",
        "SubdivisionID",
        "SubdivisionName",
        "DiscordLinked",
        "DiscordServerJoin",
        "roles",
        "PrivacyPolicyAccept",
        "OptinEmails"]
    column_details_list = [
        'id',
        'NameFirst',
        'NameLast',
        'NameFull',
        'Email',
        "RatingLong",
        "RatingShort",
        "PilotShort",
        "PilotLong",
        "DivisionID",
        "DivisionName",
        "RegionID",
        "RegionName",
        "SubdivisionID",
        "SubdivisionName",
        "DiscordLinked",
        "DiscordServerJoin",
        "PrivacyPolicyAccept",
        "OptinEmails",
        "roles",
    ]

    def is_accessible(self):
        if current_user.is_authenticated:
            if current_user.has_role(ZERO):
                self.can_create = True
                self.can_edit = True
                self.can_delete = True
                return current_user.is_authenticated

            elif current_user.has_role(ONE):
                self.can_create = False
                self.can_edit = False
                self.can_delete = False
                return current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        return abort(403)


class RoleController(ModelView):
    column_details_list = [
        'name',
        'description',
    ]
    def is_accessible(self):
        if current_user.is_authenticated:
            if current_user.has_role(ZERO):
                self.can_view_details = True
                self.can_create = True
                self.can_edit = True
                self.can_delete = True
                return current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        return abort(403)


class ExtrasController(ModelView):
    column_list = ['id', 'discord_link_data', 'discord_server_data', 'discord_user_id', 'discord_profile_use', 'discord_profile_link']
    def is_accessible(self):
        if current_user.is_authenticated:
            if current_user.has_role(ZERO):
                self.can_view_details = True
                self.can_create = True
                self.can_edit = True
                self.can_delete = True
                return current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        return abort(403)


class VATSIMController(ModelView):
    def is_accessible(self):
        if current_user.is_authenticated:
            if current_user.has_role(ZERO):
                self.can_view_details = True
                self.can_create = True
                self.can_edit = True
                self.can_delete = True
                return current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        return abort(403)


class SystemLogController(ModelView):
    can_view_details = True
    column_filters = [
        'action_by',
        "action",
        "timestamp"
    ]
    column_default_sort = ('value', True)

    def is_accessible(self):
        if current_user.is_authenticated:
            if current_user.has_role(ZERO):
                self.can_create = True
                self.can_edit = True
                self.can_delete = True
                return current_user.is_authenticated

            elif current_user.id == int(DIRECTOR):
                self.can_create = False
                self.can_edit = False
                self.can_delete = False
                return current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        return abort(403)


class MyAdminIndexView(AdminIndexView):
    def is_accessible(self):
        if current_user.is_authenticated:
            if current_user.has_role(ZERO) or current_user.has_role(ONE) or current_user.has_role(TWO):
                return current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        return abort(403)

    def render(self, template, **kwargs):

        # we are only interested in the edit page
        if template == 'admin/index.html':

            query = Users.query.filter_by(id=current_user.id).first()
            kwargs['user'] = query.NameFirst
            welcome_list = ['Hello', 'Hi', 'Gutten Tag', 'Hola', 'Sup', 'Hiya', 'Ahoy', 'Howdy']
            kwargs['welcome'] = random.choice(welcome_list)
            kwargs['total_discord_links'] = len(Extras.query.all())
            kwargs['total_users'] = len(Users.query.all())

        return super(MyAdminIndexView, self).render(template, **kwargs)


admin = Admin(app, template_mode='bootstrap4', name="Administrative Panel",
              index_view=MyAdminIndexView(url='/dashboard/admin'), url='/dashboard/admin')
admin.add_view(UserController(Users, db.session, url="/dashboard/admin/users"))
admin.add_view(RoleController(Role, db.session, name="Roles", url="/dashboard/admin/permissions"))
admin.add_view(ExtrasController(Extras, db.session, name="Discord Links", url="/dashboard/admin/discord"))
admin.add_view(VATSIMController(VATSIM, db.session, name="Dashboard Info", url="/dashboard/admin/vatsiminfo"))
admin.add_view(SystemLogController(SystemLog, db.session, name='System Log', url="/dashboard/admin/system/log"))
admin.add_link(MenuLink(name='Exam Questions', url="/dashboard/admin/exam/questions"))
admin.add_link(MenuLink(name='Exam Tokens', url="/dashboard/admin/exam/tokens"))
admin.add_link(MenuLink(name='Mass Email', url="/dashboard/admin/mass/email"))


@app.before_request
def redirect_nonwww():
    """Redirect non-www requests to www."""
    urlparts = urlparse(request.url)
    if urlparts.netloc == 'members.nepalvacc.com':
        urlparts_list = list(urlparts)
        urlparts_list[1] = 'www.members.nepalvacc.com'
        return redirect(urlunparse(urlparts_list), code=301)
    
    try: 
        if session["origin-nepal-vacc"]:
            pass
    except KeyError:
        session["origin-nepal-vacc"] = request.base_url
        return redirect(request.base_url)


@app.route("/")
def home():
    if current_user.is_authenticated:
        query = Users.query.filter_by(id=current_user.id).first()
        if query.UseCID == "True":
            name = current_user.id
        elif query.UseCID == "False":
            name = query.NameFirst
        return render_template("home.html", user=current_user, name=name)
    else:
        return render_template("home.html", user=current_user)
    

@app.route("/logout")
def logout():
    if current_user.is_authenticated:
        logout_user()
    try:
        session.pop("origin-nepal-vacc")
    except:
        pass
    
    return redirect(url_for("home"))



if __name__ == "__main__":
    app.run(debug=True)
    #serve(app, host='0.0.0.0', threads=8)

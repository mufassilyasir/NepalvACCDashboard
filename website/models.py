from flask import Blueprint
from flask_security.core import RoleMixin
from flask_login import UserMixin
from . import db


models = Blueprint("models", __name__, static_folder="static", template_folder="templates")


class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    description = db.Column(db.String(100))

    def __str__(self):
        return self.name


roles_users = db.Table('roles_users',
                       db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
                       db.Column('role_id', db.Integer, db.ForeignKey('role.id')))
                       


class Users(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    NameFirst = db.Column(db.String(500))
    NameLast = db.Column(db.String(500))
    NameFull = db.Column(db.String(500))
    Email = db.Column(db.String(450))
    RatingLong = db.Column(db.String(550))
    RatingShort = db.Column(db.String(500))
    PilotShort = db.Column(db.String(500))
    PilotLong = db.Column(db.String(500))
    DivisionID = db.Column(db.String(500), default="None")
    DivisionName = db.Column(db.String(500), default="None")
    RegionID = db.Column(db.String(500), default="None")
    RegionName = db.Column(db.String(500), default="None")
    SubdivisionID = db.Column(db.String(500), default="None")
    SubdivisionName = db.Column(db.String(500), default="None")
    DiscordLinked = db.Column(db.Boolean, default=False)
    DiscordServerJoin = db.Column(db.Boolean, default=False)
    StaffPosition = db.Column(db.String(500), default="None")
    PrivacyPolicyAccept = db.Column(db.String(500), default="False")
    OptinEmails = db.Column(db.String(500), default="False")
    UseCID = db.Column(db.String(500), default="False")
    UseFirst = db.Column(db.String(500), default="False")
    user_own_upload = db.Column(db.String(500), default="False")
    user_own_upload_link = db.Column(db.String(450), default="None")
    roles = db.relationship('Role', secondary=roles_users, backref=db.backref('users', lazy='select'))

    def __init__(self, id, NameFirst, NameLast, NameFull, Email, RatingLong, RatingShort, PilotShort, PilotLong, DivisionID, DivisionName, RegionID, RegionName, SubdivisionID, SubdivisionName, UseCID):
        self.id = id
        self.NameFirst = NameFirst
        self.NameLast = NameLast
        self.NameFull = NameFull
        self.Email = Email
        self.RatingLong = RatingLong
        self.RatingShort = RatingShort
        self.PilotLong = PilotLong
        self.PilotShort = PilotShort
        self.DivisionID = DivisionID
        self.DivisionName = DivisionName
        self.RegionID = RegionID
        self.RegionName = RegionName
        self.SubdivisionID = SubdivisionID
        self.SubdivisionName = SubdivisionName
        self.UseCID = UseCID

    def get_id(self):
        return (self.id)

    def has_role(self, *args):
        return set(args).issubset({role.name for role in self.roles})

    def __repr__(self) -> str:
        return super().__repr__()


class Extras(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    discord_link_data = db.Column(db.String(500))
    discord_server_data = db.Column(db.String(500))
    discord_user_id = db.Column(db.String(400))
    discord_profile_use = db.Column(db.String(500), default="False")
    discord_profile_link = db.Column(db.String(500), default="None")


class VATSIM(db.Model):
    value = db.Column(db.Integer, primary_key=True)
    json_data = db.Column(db.String(500))
    time = db.Column(db.String(500))
    time_datetime = db.Column(db.String(500))


class Events(db.Model):
    value = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.String(500))
    end_time = db.Column(db.String(500))
    event_link = db.Column(db.String(500))
    event_banner = db.Column(db.String(500))
    last_updated = db.Column(db.String(500))


class Exam(db.Model):
    value = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.String(500))
    student_assigned = db.Column(db.String(500))
    exam_grade = db.Column(db.String(500))
    exam_date = db.Column(db.String(500))
    exam_rating = db.Column(db.String(500))
    exam_link = db.Column(db.String(500))
    exam_status = db.Column(db.String(500))
    question_answer = db.Column(db.JSON())
    mentor_id = db.Column(db.String(500))
    mentor_assigned = db.Column(db.String(500))


class PendingExams(db.Model):
    value = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.String(500))
    student_assigned = db.Column(db.String(500))
    exam_link = db.Column(db.String(500))
    exam_date = db.Column(db.String(500))
    exam_rating = db.Column(db.String(500))
    mentor_id = db.Column(db.String(500))
    mentor_assigned = db.Column(db.String(500))
    exam_start_time = db.Column(db.String(500))
    exam_end_time = db.Column(db.String(500))
    exam_questions = db.Column(db.JSON())
    exam_generated = db.Column(db.String(500))
    starter_accepted = db.Column(db.String(500))
    exam_status = db.Column(db.String(500))


class ExamPool(db.Model):
    value = db.Column(db.Integer, primary_key=True)
    Question = db.Column(db.String(1000))
    Answer1 = db.Column(db.String(900))
    Answer2 = db.Column(db.String(900))
    Answer3 = db.Column(db.String(900))
    Answer4 = db.Column(db.String(900))
    Correct_Answer = db.Column(db.String(500))
    Rating = db.Column(db.String(500))
    Noofoptions = db.Column(db.String(500))


class SystemLog(db.Model):
    value = db.Column(db.Integer, primary_key=True)
    action_by = db.Column(db.String(500))
    action = db.Column(db.String(500))
    timestamp = db.Column(db.String(500))

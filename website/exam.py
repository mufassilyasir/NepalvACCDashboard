from flask import Blueprint, render_template, redirect, request, flash, abort
from flask.helpers import url_for
from .models import ExamPool, db, Extras, Users, Exam, PendingExams, SystemLog, VATSIM
from flask_login import current_user
from dotenv import load_dotenv
from datetime import datetime
from .emailfunc import send_email
from website.examutils import calculation, examgenerator, statuscalculate


import os
import json

load_dotenv()


exam = Blueprint("exam", __name__)

ZERO = os.getenv("ZERO")
ONE = os.getenv("ONE")
TWO = os.getenv("TWO")
THREE = os.getenv("THREE")
DASHBOARD_ENDPOINT = os.getenv("DASHBOARD_ENDPOINT")
STAFF_EMAIL = os.getenv("STAFF_EMAIL")
DIRECTOR = os.getenv("DIRECTOR")
DEPUTY_DIRECTOR = os.getenv("DEPUTY_DIRECTOR")
ME = os.getenv("ME")


@exam.route("/dashboard/admin/exam/questions", methods=["GET", "POST"])
def examquestions():
    if current_user.is_authenticated:
        if current_user.has_role(ZERO) or current_user.has_role(ONE):
            if current_user.id == int(DIRECTOR) or current_user.id == int(DEPUTY_DIRECTOR) or current_user.id == int(ME):
                if request.method == "POST":
                    try:
                        query = ExamPool.query.filter_by(value=request.form["question_rem"]).first()
                        question = query.Question
                        removal_question = True
                    except KeyError:
                        pass
                    else:
                        return redirect(f"/dashboard/admin/exam/questions/{query.value}/edit")

                    if True:
                        if request.form["Question"] == "":
                            flash("You need to add a question", category='error')
                        else:
                            question = request.form["Question"]

                        if request.form["Option1"] == "":
                            flash("You need to add the first option!", category='error')
                        else:
                            option_1 = request.form["Option1"]

                        if request.form["Option2"] == "":
                            flash("You need to add the second option!", category='error')
                        else:
                            option_2 = request.form["Option2"]

                        try:
                            if int(request.form["noofoptions"]) == 2:
                                option_3 = "None"
                                option_4 = "None"

                            elif int(request.form["noofoptions"]) == 4:
                                if request.form["Option3"] == "":
                                    flash("You need to add the third option!", category='error')
                                    return redirect(request.base_url)
                                else:
                                    option_3 = request.form["Option3"]

                                if request.form["Option4"] == "":
                                    flash("You need to add the forth option!", category='error')
                                    return redirect(request.base_url)
                                else:
                                    option_4 = request.form["Option4"]
                            else:
                                flash("System only supports 2 or 4 option questions. Sorry :(", category='error')
                                return redirect(request.base_url)

                        except ValueError:
                            flash("You must enter number of options as 2 or 4 only.", category='error')

                        else:

                            if request.form["answer"] == "":
                                flash("You need to add the answer option!", category='error')
                            else:
                                try:
                                    int(request.form["answer"])
                                except ValueError:
                                    flash(
                                        "Answer must be an integer number 1-4, for example it answer is Option 1, add 1 in answer field.", category='error')
                                else:
                                    if int(request.form["noofoptions"]) == 2:
                                        if int(request.form["answer"]) == 3 or int(request.form["answer"]) == 4:
                                            flash(
                                                "If you are selecting this question as 2 options, answer must be option 1 or 2 duhh?", category='error')
                                            return redirect(request.base_url)

                                    answer = request.form["answer"]
                                    question_add = ExamPool(Question=question, Answer1=option_1, Answer2=option_2,
                                                            Answer3=option_3, Answer4=option_4, Correct_Answer=answer, Noofoptions=int(request.form["noofoptions"]))
                                    db.session.add(question_add)
                                    time_now = datetime.utcnow()
                                    system_log = SystemLog(
                                        action_by=current_user.id, action=f"Added exam question. '{question}'", timestamp=f"{time_now.strftime('%d-%m-%Y %H:%M:%S')} UTC")
                                    db.session.add(system_log)
                                    db.session.commit()
                                    flash("Question was added!", category='success')

                exam_pool = ExamPool.query.all()
                return render_template("examquestions.html", exam_pool=exam_pool)

            else:
                abort(403)
        else:
            abort(403)
    else:
        return redirect(url_for("auth.login"))


@exam.route("/dashboard/admin/exam/questions/<exam_number>/<typedeloredit>", methods=['POST', 'GET'])
def editexamquestion(exam_number, typedeloredit):
    if current_user.is_authenticated:
        if current_user.has_role(ZERO) or current_user.has_role(ONE):
            if current_user.id == int(DIRECTOR) or current_user.id == int(DEPUTY_DIRECTOR) or current_user.id == int(ME):
                if typedeloredit == "edit":
                    exam = ExamPool.query.filter_by(value=exam_number).first()

                    if request.method == "POST":

                        if request.form["Question"] == "":
                            flash("You need to add a question", category='error')
                            return redirect(url_for("exam questions.examquestions"))
                        else:
                            question = request.form["Question"]

                        if request.form["Option1"] == "":
                            flash("You need to add the first option!", category='error')
                            return redirect(url_for("exam questions.examquestions"))
                        else:
                            option_1 = request.form["Option1"]

                        if request.form["Option2"] == "":
                            flash("You need to add the second option!", category='error')
                            return redirect(url_for("exam questions.examquestions"))
                        else:
                            option_2 = request.form["Option2"]
                        
                        if request.form.get('rating_select') == None:
                            flash("You need to select the rating!", category='error')
                            return redirect(url_for("exam questions.examquestions"))
                        else:
                            rating_select = request.form.get('rating_select')

                        try:
                            if int(request.form["noofoptions"]) == 2:
                                option_3 = "None"
                                option_4 = "None"

                            elif int(request.form["noofoptions"]) == 4:
                                if request.form["Option3"] == "":
                                    flash("You need to add the third option!", category='error')
                                    return redirect(request.base_url)
                                else:
                                    option_3 = request.form["Option3"]

                                if request.form["Option4"] == "":
                                    flash("You need to add the forth option!", category='error')
                                    return redirect(request.base_url)
                                else:
                                    option_4 = request.form["Option4"]
                            else:
                                flash("System only supports 2 or 4 option questions. Sorry :(", category='error')
                                return redirect(request.base_url)

                        except ValueError:
                            flash("You must enter number of options as 2 or 4 only.", category='error')

                        else:
                            if request.form["answer"] == "":
                                flash("You need to add the answer option!", category='error')
                            else:
                                try:
                                    int(request.form["answer"])
                                except ValueError:
                                    flash(
                                        "Answer must be an integer number 1-4, for example it answer is Option 1, add 1 in answer field.", category='error')
                                else:
                                    if int(request.form["noofoptions"]) == 2:
                                        if int(request.form["answer"]) == 3 or int(request.form["answer"]) == 4:
                                            flash(
                                                "If you are selecting this question as 2 options, answer must be option 1 or 2 duhh?", category='error')
                                            return redirect(request.base_url)

                                    exam.Question = question
                                    exam.Answer1 = option_1
                                    exam.Answer2 = option_2
                                    exam.Answer3 = option_3
                                    exam.Answer4 = option_4
                                    exam.Correct_Answer = request.form["answer"]
                                    exam.Noofoptions = int(request.form["noofoptions"])
                                    exam.Rating = rating_select.upper()
                                    time_now = datetime.utcnow()
                                    system_log = SystemLog(
                                        action_by=current_user.id, action=f"Edited exam question. '{question}'", timestamp=f"{time_now.strftime('%d-%m-%Y %H:%M:%S')} UTC")
                                    db.session.add(system_log)
                                    db.session.commit()
                                    flash("Question was edited!", category='success')
                                    return redirect(request.base_url)
                    if exam:
                        return render_template("exameditquestion.html", question=exam.Question, 
                        option1=exam.Answer1, option2=exam.Answer2, option3=exam.Answer3, 
                        option4=exam.Answer4, noofoptions=exam.Noofoptions, answer=exam.Correct_Answer, 
                        question_value=exam_number, rating=exam.Rating)
                    else:
                        abort(404)

                elif typedeloredit == "delete":
                    exam = ExamPool.query.filter_by(value=exam_number).first()
                    if exam:
                        ExamPool.query.filter_by(value=int(exam_number)).delete()
                        time_now = datetime.utcnow()
                        system_log = SystemLog(
                            action_by=current_user.id, action=f"Deleted exam question. Exam question '{exam.Question}'", timestamp=f"{time_now.strftime('%d-%m-%Y %H:%M:%S')} UTC")
                        db.session.add(system_log)
                        db.session.commit()
                        flash("Exam Question Removed!", category='success')
                        return redirect(url_for("exam questions.examquestions"))
                    else:
                        abort(404)
            else:
                abort(404)
        else:
            abort(404)
    else:
        return redirect(url_for("auth.login"))

@exam.route("/dashboard/exams", strict_slashes=False)
def examdashboard():
    if current_user.is_authenticated:
        query = Users.query.filter_by(id=current_user.id).first()
        if query.PrivacyPolicyAccept == "True":
            if current_user.has_role(THREE) == False:

                if current_user.has_role(ZERO):
                    check_admin = "True"
                elif current_user.has_role(ONE):
                    check_admin = "True"
                elif current_user.has_role(TWO):
                    check_admin = "True"
                else:
                    check_admin = "False"

                user = Users.query.filter_by(id=current_user.id).first()

                if user.UseCID == "False" and user.UseFirst == "False":
                    name = user.NameFull
                elif user.UseCID == "False" and user.UseFirst == "True":
                    name = user.NameFirst
                elif user.UseCID == "True":
                    name = current_user.id

                exams = Exam.query.filter_by(student_id=current_user.id).all()
                exam_list = []
                if exams:
                    for exam in exams:
                        past_exam = "value"
                        value1 = {
                            'exam_value': exam.value,
                            'exam_grade': exam.exam_grade,
                            'exam_rating': exam.exam_rating,
                            'exam_date':  exam.exam_date,
                            'exam_status': exam.exam_status,
                            'exam_link': exam.exam_link,
                        }
                        exam_list.append(value1)
                else:
                    exam_value = ""
                    exam_rating = "No past exam found"
                    exam_grade = ""
                    exam_date = ""
                    exam_status = ""
                    exam_link = "None"
                    past_exam = "None"
                    value1 = {
                        'exam_value': exam_value,
                        'exam_rating': exam_rating,
                        'exam_grade': exam_grade,
                        'exam_date':  exam_date,
                        'exam_status': exam_status,
                        'exam_link': exam_link
                    }
                    exam_list.append(value1)

                pending_exams = PendingExams.query.filter_by(student_id=current_user.id).all()
                pending_exam_list = []
                if pending_exams:
                    for pending in pending_exams:
                        value1 = {
                            'exam_value': pending.value,
                            'exam_date':  pending.exam_date,
                            'exam_rating': pending.exam_rating,
                            'exam_status': 'Pending',
                            'exam_link': pending.exam_link,
                            'exam_status': pending.exam_status,
                        }
                        pending_exam_list.append(value1)
                    assigned_exam = "True"
                else:
                    exam_value = ""
                    exam_rating = "No exam assigned"
                    exam_date = "None"
                    exam_status = ""
                    exam_link = "None"
                    value1 = {
                        'exam_value': exam_value,
                        'exam_rating': exam_rating,
                        'exam_date':  exam_date,
                        'exam_status': exam_status,
                        'exam_link': exam_link
                    }
                    assigned_exam = "False"
                    pending_exam_list.append(value1)

                fetch1 = VATSIM.query.filter_by(value=1).first()
                residents = fetch1.json_data

                fetch2 = VATSIM.query.filter_by(value=2).first()
                visitors = fetch2.json_data

                fetch3 = VATSIM.query.filter_by(value=3).first()
                solopeeps = fetch3.json_data

                fetch4 = VATSIM.query.filter_by(value=4).first()
                mentors = fetch4.json_data

                if query.user_own_upload == "True":
                    user_avatar_path = query.user_own_upload_link
                else:
                    user_avatar_path = f"/static/public/Initials/{current_user.id}.png"

                if check_admin == "True":
                    query2 = Exam.query.all()

                else:
                    query2 = "None"

                query1 = Extras.query.filter_by(id=current_user.id).first()
                if query1:
                    is_linked = query1.discord_link_data
                    is_member = query1.discord_server_data
                    is_discord_profile_allowed = query1.discord_profile_use
                    discord_profile_link = query1.discord_profile_link
                    return render_template("examsystem.html", name=name, check_admin=check_admin, is_linked=is_linked, is_member=is_member, is_discord_profile_allowed=is_discord_profile_allowed, discord_profile_link=discord_profile_link, cid=current_user.id, user_avatar_path=user_avatar_path, userUseCID=user.UseCID, OptinEmails=user.OptinEmails, exam_list=exam_list, pending_exam_list=pending_exam_list, assigned_exam=assigned_exam, past_exam=past_exam, query2=query2, residents=residents, visitors=visitors, solopeeps=solopeeps, mentors=mentors)
                else:
                    return render_template("examsystem.html", name=name, check_admin=check_admin, is_linked="No", is_member="No", is_discord_profile_allowed="False", discord_profile_link="None", cid=current_user.id, user_avatar_path=user_avatar_path, userUseCID=user.UseCID, OptinEmails=user.OptinEmails,  exam_list=exam_list, pending_exam_list=pending_exam_list, assigned_exam=assigned_exam, past_exam=past_exam, query2=query2, residents=residents, visitors=visitors, solopeeps=solopeeps, mentors=mentors)
            else:
                abort(403)
        else:
            return redirect(url_for("views.policy"))
    else:
        return redirect(url_for("auth.login"))


@exam.route("/dashboard/admin/exam/tokens", strict_slashes=False, methods=["POST", "GET"])
def examtokens():
    if current_user.is_authenticated:
        if current_user.has_role(ZERO) or current_user.has_role(ONE):
            if current_user.id == int(DIRECTOR) or current_user.id == int(DEPUTY_DIRECTOR) or current_user.id == int(ME):
                if request.method == "POST":
                    try:
                        student_name = request.form["student_name"]
                        exam_rating = request.form["exam-rating"].upper()
                    except KeyError:
                        student_name = "None"
                        exam_rating = "None"

                    try:
                        revoke_token = request.form["revoke-token"]
                    except KeyError:
                        revoke_token = "None"
                    if student_name != "None" and exam_rating != "None":
                        query = Users.query.filter_by(id=student_name).first()
                        query2 = Users.query.filter_by(id=current_user.id).first()
                        if query:
                            query3 = PendingExams.query.filter_by(student_id=student_name).all()
                            if query3:
                                for query_checker in query3:
                                    if query_checker.exam_rating == exam_rating:
                                        flash(f"{student_name} already has {exam_rating} token issued :(", category='error')
                                        return redirect(url_for("exam questions.examtokens"))
                            now = datetime.utcnow()
                            stored_value_check = PendingExams.query.filter_by(value=1).first()
                            stored_value = int(stored_value_check.exam_link)
                            new_value = stored_value + 1
                            stored_value_check.exam_link = new_value
                            issue_exam_token = PendingExams(value=new_value, student_id=student_name, student_assigned=query.NameFull, exam_link=f"{DASHBOARD_ENDPOINT}/dashboard/exams/{new_value}", exam_date=now.strftime(
                                "%d-%m-%Y %H:%M:%S"), exam_rating=exam_rating, mentor_id=current_user.id, mentor_assigned=query2.NameFull, exam_generated="False", starter_accepted="False", exam_status="Pending")
                            db.session.add(issue_exam_token)
                            system_log = SystemLog(
                                action_by=current_user.id, action=f"Issued exam token for {student_name}, rating {exam_rating}, exam_id {new_value}", timestamp=f"{now.strftime('%d-%m-%Y %H:%M:%S')} UTC")
                            db.session.add(system_log)
                            db.session.commit()
                            if query.OptinEmails == "True":
                                email = query.Email
                                mentor_assigned = query2.NameFull
                                mentor_id = query2.id
                                send_email(f'{exam_rating} Token Issued!', 'no-reply@nepalvacc.com', [email], None, None, render_template(
                                    "/email/emailexam.html", exam_rating=exam_rating, mentor_assigned=mentor_assigned, mentor_id=mentor_id))
                            flash("Exam Token Issued!", category='success')

                    if revoke_token == "None":
                        pass
                    elif revoke_token != "1":
                        query = PendingExams.query.filter_by(value=revoke_token).first()
                        PendingExams.query.filter_by(value=revoke_token).delete()
                        time_now = datetime.utcnow()
                        system_log = SystemLog(
                            action_by=current_user.id, action=f"Revoked exam token for {query.student_id}, rating {query.exam_rating}", timestamp=f"{time_now.strftime('%d-%m-%Y %H:%M:%S')} UTC")
                        db.session.add(system_log)
                        db.session.commit()
                        flash("Successfully revoked exam token!", category='success')
                    elif revoke_token == "1":
                        flash("Noice, you thought I wouldn't make a fail safe? ERROR cannot delete system token.", category="error")

                students = Users.query.all()
                pending = PendingExams.query.all()

                return render_template("examtokens.html", students=students, pending=pending)

            else:
                abort(403)
        else:
            abort(403)
    else:
        return redirect(url_for("auth.login"))


@exam.route("/dashboard/exams/<exam_number>", strict_slashes=False, methods=["POST", "GET"])
def startexam(exam_number):
    if current_user.is_authenticated:
        query = Users.query.filter_by(id=current_user.id).first()
        if query.PrivacyPolicyAccept == "True":
            if current_user.has_role(THREE) == False:
                query2 = PendingExams.query.filter_by(value=exam_number).first()
                if query2:
                    if int(query2.student_id) == int(current_user.id):
                        exam_rating = query2.exam_rating
                        discord_query = Extras.query.filter_by(id=current_user.id).first()
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

                        if current_user.has_role(ZERO):
                            check_admin = "True"
                        elif current_user.has_role(ONE):
                            check_admin = "True"
                        elif current_user.has_role(TWO):
                            check_admin = "True"
                        else:
                            check_admin = "False"

                        if query.user_own_upload == "True":
                            user_avatar_path = query.user_own_upload_link
                        else:
                            user_avatar_path = f"/static/public/Initials/{current_user.id}.png"

                        if query2.starter_accepted == "True":
                            if request.method == "POST":

                                end_time_calculate = query2.exam_end_time
                                now_time = datetime.utcnow()

                                end_time = datetime.strptime(end_time_calculate, '%B %d %Y %H:%M:%S')
                                diff = end_time - now_time
                                actual = (diff.total_seconds() / 60)

                                question_in_exam = []
                                total_marks = 0
                                make_list = []

                                if actual > 0:

                                    for num in ExamPool.query.filter_by().all():
                                        try:
                                            return_ansss = (request.form[f"btnradio{num.value}"])
                                            return_ans = json.loads(return_ansss)
                                            answer = int(return_ans[1])

                                        except KeyError:
                                            return_ans = [0, 0]
                                            answer = "None"

                                        finally:
                                            if int(return_ans[0]) == int(num.value):
                                                if int(return_ans[1]) == int(num.Correct_Answer):
                                                    dictionary = {
                                                        'Value': num.value,
                                                        'Question': num.Question,
                                                        'Answer1': num.Answer1,
                                                        'Answer2': num.Answer2,
                                                        'Answer3': num.Answer3,
                                                        'Answer4': num.Answer4,
                                                        'Correct': num.Correct_Answer,
                                                        'Noofoptions': num.Noofoptions,
                                                        'Student_Ans': str(answer)
                                                    }
                                                    question_in_exam.append(dictionary)
                                                    total_marks = total_marks + 1
                                                    make_list.append(num.value)
                                                else:
                                                    dictionary = {
                                                        'Value': num.value,
                                                        'Question': num.Question,
                                                        'Answer1': num.Answer1,
                                                        'Answer2': num.Answer2,
                                                        'Answer3': num.Answer3,
                                                        'Answer4': num.Answer4,
                                                        'Correct': num.Correct_Answer,
                                                        'Noofoptions': num.Noofoptions,
                                                        'Student_Ans': str(answer)
                                                    }
                                                    question_in_exam.append(dictionary)
                                                    make_list.append(num.value)

                                    for num1 in ExamPool.query.filter_by().all():
                                        for n_question in query2.exam_questions:
                                            if n_question not in make_list:
                                                if int(n_question) == int(num1.value):
                                                    dictionary = {
                                                        'Value': num1.value,
                                                        'Question': num1.Question,
                                                        'Answer1': num1.Answer1,
                                                        'Answer2': num1.Answer2,
                                                        'Answer3': num1.Answer3,
                                                        'Answer4': num1.Answer4,
                                                        'Correct': num1.Correct_Answer,
                                                        'Noofoptions': num.Noofoptions,
                                                        'Student_Ans': "0"
                                                    }
                                                    question_in_exam.append(dictionary)

                                    exam_status = statuscalculate(exam_rating, total_marks)

                                else:

                                    for num in ExamPool.query.filter_by().all():
                                        try:
                                            return_ansss = (request.form[f"btnradio{num.value}"])
                                            return_ans = json.loads(return_ansss)
                                            answer = int(return_ans[1])

                                        except KeyError:
                                            return_ans = [0, 0]
                                            answer = "None"

                                        finally:
                                            if int(return_ans[0]) == int(num.value):
                                                if int(return_ans[1]) == int(num.Correct_Answer):
                                                    dictionary = {
                                                        'Value': num.value,
                                                        'Question': num.Question,
                                                        'Answer1': num.Answer1,
                                                        'Answer2': num.Answer2,
                                                        'Answer3': num.Answer3,
                                                        'Answer4': num.Answer4,
                                                        'Correct': num.Correct_Answer,
                                                        'Noofoptions': num.Noofoptions,
                                                        'Student_Ans': str(answer)
                                                    }
                                                    question_in_exam.append(dictionary)
                                                    total_marks = total_marks + 1
                                                    make_list.append(num.value)
                                                else:
                                                    dictionary = {
                                                        'Value': num.value,
                                                        'Question': num.Question,
                                                        'Answer1': num.Answer1,
                                                        'Answer2': num.Answer2,
                                                        'Answer3': num.Answer3,
                                                        'Answer4': num.Answer4,
                                                        'Correct': num.Correct_Answer,
                                                        'Noofoptions': num.Noofoptions,
                                                        'Student_Ans': str(answer)
                                                    }
                                                    question_in_exam.append(dictionary)
                                                    make_list.append(num.value)

                                    for num1 in ExamPool.query.filter_by().all():
                                        for n_question in query2.exam_questions:
                                            if n_question not in make_list:
                                                if int(n_question) == int(num1.value):
                                                    dictionary = {
                                                        'Value': num1.value,
                                                        'Question': num1.Question,
                                                        'Answer1': num1.Answer1,
                                                        'Answer2': num1.Answer2,
                                                        'Answer3': num1.Answer3,
                                                        'Answer4': num1.Answer4,
                                                        'Correct': num1.Correct_Answer,
                                                        'Noofoptions': num.Noofoptions,
                                                        'Student_Ans': "0"
                                                    }
                                                    question_in_exam.append(dictionary)

                                    exam_status = "Failed"

                                time_now = now_time.strftime("%d-%m-%Y %H:%M:%S")

                                move_to_exam = Exam(value=exam_number, student_id=query2.student_id, student_assigned=query2.student_assigned, exam_grade=total_marks, exam_date=time_now, exam_rating=query2.exam_rating,
                                                    exam_link=f"{DASHBOARD_ENDPOINT}/dashboard/exams/{exam_number}/view", exam_status=exam_status, question_answer=question_in_exam, mentor_id=query2.mentor_id, mentor_assigned=query2.mentor_assigned)
                                db.session.add(move_to_exam)
                                system_log = SystemLog(
                                    action_by=current_user.id, action=f"Completed exam. Exam Link {DASHBOARD_ENDPOINT}/dashboard/exams/{exam_number}/view", timestamp=f"{now_time.strftime('%d-%m-%Y %H:%M:%S')} UTC")
                                db.session.add(system_log)
                                PendingExams.query.filter_by(value=exam_number).delete()
                                db.session.commit()

                                student_id = query.id
                                student_name = query.NameFull
                                exam_status = exam_status
                                exam_grade = total_marks
                                wait_time = 24

                                if exam_status == "Failed":
                                    if query.OptinEmails == "True":
                                        email = query.Email

                                        send_email(f'Your {exam_rating} Theory Exam Result!', 'no-reply@nepalvacc.com', [email], None, None, render_template("/email/examresultstudent.html", exam_rating=exam_rating, exam_grade=exam_grade, student_id=student_id,
                                                   student_name=student_name, exam_status=exam_status, exam_future=f"You need to wait until {wait_time} hours have been completed and than request the vACC Staff to assign you the exam again if they didn't do it already by the time!"))
                                    send_email(f'Exam {exam_status}!', 'no-reply@nepalvacc.com', [STAFF_EMAIL], None, None, render_template("/email/examresultsstaff.html", exam_rating=exam_rating, exam_grade=exam_grade,
                                               student_id=student_id, student_name=student_name, exam_status=exam_status, exam_future=f"Recommend {wait_time} hours waiting time before re-issuing the exam token!"))

                                elif exam_status == "Passed":
                                    if query.OptinEmails == "True":
                                        email = query.Email
                                        send_email(f'Your {exam_rating} Theory Exam Result!', 'no-reply@nepalvacc.com', [email], None, None, render_template("/email/examresultstudent.html", exam_rating=exam_rating, exam_grade=exam_grade,
                                                   student_id=student_id, student_name=student_name, exam_status=exam_status, exam_future=f"You need to contact your mentor and let them know you have completed the exam and they will take it from there."))
                                    send_email(f'Exam {exam_status}!', 'no-reply@nepalvacc.com', [STAFF_EMAIL], None, None, render_template(
                                        "/email/examresultsstaff.html", exam_rating=exam_rating, exam_grade=exam_grade, student_id=student_id, student_name=student_name, exam_status=exam_status, exam_future=f"Start training them!"))

                                return redirect(url_for("exam questions.examdashboard"))

                            if query2.exam_generated == "False":
                                examgenerator(exam_number)
                                db.session.commit()

                            questions = []
                            questions_num = []
                            for questionnum in query2.exam_questions:
                                questions_num.append(questionnum)

                            for question in questions_num:
                                query_maker = ExamPool.query.filter_by(value=question).first()
                                questions_checker = {
                                    'Value': query_maker.value,
                                    'Question': query_maker.Question,
                                    'Answer1': query_maker.Answer1,
                                    'Answer2': query_maker.Answer2,
                                    'Answer3': query_maker.Answer3,
                                    'Answer4': query_maker.Answer4,
                                    'Noofoptions': query_maker.Noofoptions,
                                }
                                questions.append(questions_checker)

                            time_to_check = query2.exam_end_time
                            if discord_query:
                                is_linked = discord_query.discord_link_data
                                is_member = discord_query.discord_server_data
                                is_discord_profile_allowed = discord_query.discord_profile_use
                                discord_profile_link = discord_query.discord_profile_link

                                return render_template("examitself.html", exam_rating=exam_rating, questions=questions, time_to_check=time_to_check, name=name, check_admin=check_admin, is_linked=is_linked, is_member=is_member, is_discord_profile_allowed=is_discord_profile_allowed, discord_profile_link=discord_profile_link, user_avatar_path=user_avatar_path, OptinEmails=query.OptinEmails)
                            else:
                                return render_template("examitself.html", exam_rating=exam_rating, questions=questions, time_to_check=time_to_check, name=name, check_admin=check_admin, is_linked="No", is_member="No", is_discord_profile_allowed="False", discord_profile_link="None", user_avatar_path=user_avatar_path, OptinEmails=query.OptinEmails)
                        else:
                            time_limit, minimum_grade, question_num = calculation(exam_rating)

                            try:
                                if request.form["starter"] == exam_rating:
                                    query2.starter_accepted = "True"
                                    db.session.commit()
                                    return redirect(f"{request.base_url}")
                            except KeyError:
                                pass

                            if discord_query:
                                is_linked = discord_query.discord_link_data
                                is_member = discord_query.discord_server_data
                                is_discord_profile_allowed = discord_query.discord_profile_use
                                discord_profile_link = discord_query.discord_profile_link
                                return render_template("examstarter.html", exam_rating=exam_rating, question_num=question_num, minimum_grade=minimum_grade, time_limit=time_limit, name=name, check_admin=check_admin, is_linked=is_linked, is_member=is_member, is_discord_profile_allowed=is_discord_profile_allowed, discord_profile_link=discord_profile_link, user_avatar_path=user_avatar_path, OptinEmails=query.OptinEmails)
                            else:
                                return render_template("examstarter.html", exam_rating=exam_rating, question_num=question_num, minimum_grade=minimum_grade, time_limit=time_limit, name=name, check_admin=check_admin, is_linked="No", is_member="No", is_discord_profile_allowed="False", discord_profile_link="None", user_avatar_path=user_avatar_path, OptinEmails=query.OptinEmails)
                    else:
                        abort(403)
                else:
                    abort(404)
            else:
                abort(403)
        else:
            return redirect(url_for("views.policy"))
    else:
        return redirect(url_for("auth.login"))


@exam.route("/dashboard/exams/<exam_number>/view", strict_slashes=False)
def viewexam(exam_number):
    if current_user.is_authenticated and current_user.PrivacyPolicyAccept:
        if current_user.PrivacyPolicyAccept == "True":
            if current_user.has_role(THREE) == False:
                query2 = Exam.query.filter_by(value=exam_number).first()
                if query2:
                    if current_user.has_role(ZERO) or current_user.has_role(ONE):
                        staff = "True"

                    elif int(query2.student_id) == int(current_user.id):
                        staff = "False"

                    else:
                        abort(403)

                    discord_query = Extras.query.filter_by(id=current_user.id).first()
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

                    if current_user.has_role(ZERO):
                        check_admin = "True"
                    elif current_user.has_role(ONE):
                        check_admin = "True"
                    elif current_user.has_role(TWO):
                        check_admin = "True"
                    else:
                        check_admin = "False"

                    if query.user_own_upload == "True":
                        user_avatar_path = query.user_own_upload_link
                    else:
                        user_avatar_path = f"/static/public/Initials/{current_user.id}.png"

                    if discord_query:
                        is_linked = discord_query.discord_link_data
                        is_member = discord_query.discord_server_data
                        is_discord_profile_allowed = discord_query.discord_profile_use
                        discord_profile_link = discord_query.discord_profile_link
                    else:
                        is_linked = "No"
                        is_member = "No"
                        is_discord_profile_allowed = "False"
                        discord_profile_link = "None"

                    return render_template("viewexamitself.html", exam_rating=query2.exam_rating, exam_status=query2.exam_status, exam_grade=query2.exam_grade, student_id=query2.student_id, staff=staff, student_name=query2.student_assigned, mentor_id=query2.mentor_id, mentor_name=query2.mentor_assigned, exam_answer=query2.question_answer, name=name, check_admin=check_admin, is_linked=is_linked, is_member=is_member, is_discord_profile_allowed=is_discord_profile_allowed, discord_profile_link=discord_profile_link, user_avatar_path=user_avatar_path, OptinEmails=query.OptinEmails)

                else:
                    abort(404)
            else:
                abort(403)
        else:
            return redirect(url_for("views.policy"))
    else:
        return redirect(url_for("auth.login"))

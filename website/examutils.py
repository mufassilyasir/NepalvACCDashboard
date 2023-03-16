from website.models import ExamPool, PendingExams
from datetime import datetime, timedelta

import random


def examgenerator(exam_number):
    query2 = PendingExams.query.filter_by(value=exam_number).first()
    query3 = ExamPool.query.filter_by().all()
    exam_pool_list = []

    for exam_value in query3:
        exam_pool_list.append(exam_value.value)


    questions_random = random.sample(exam_pool_list, k=10)

    query2.exam_questions = questions_random
    query2.exam_generated = "True"
    time_now = datetime.utcnow()

    query2.exam_start_time = time_now

    time_end_calculate = timedelta(minutes=20)
    time_end_calculate1 = time_now + time_end_calculate

    month = datetime.utcnow().month
    months = ["January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"]
    monthName = months[month - 1]

    time_end = time_end_calculate1.strftime(f'{monthName} %d %Y %H:%M:%S')
    query2.exam_end_time = time_end
    query2.exam_status = "In Progress"

    return


def calculation(exam_rating):
    # if exam_rating == "S2":
    #     minimum_grade = 8
    #     question_num = 10
    # elif exam_rating == "S3":
    #     question_num = 10
    #     minimum_grade = 8
    # elif exam_rating == "C1":
    #     question_num = 10
    #     minimum_grade = 8

    #time_limit = 20

    return 20, 8, 10


def statuscalculate(exam_rating, total_marks):
    if exam_rating == "S2":
        if total_marks >= 8:
            exam_status = "Passed"
        else:
            exam_status = "Failed"
    
    if exam_rating == "S3":
        if total_marks >= 8:
            exam_status = "Passed"
        else:
            exam_status = "Failed"
    
    if exam_rating == "C1":
        if total_marks >= 8:
            exam_status = "Passed"
        else:
            exam_status = "Failed"
    
    return exam_status

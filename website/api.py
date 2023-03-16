from flask import Blueprint, jsonify, request
from datetime import datetime
from .models import VATSIM, db, Events

import aiohttp
import asyncio
import requests

api = Blueprint("api", __name__)



async def get_api_data(cs, url):
    async with cs.get(url) as response:
        if response.status == 200:
            data = await response.json()
            return data
        else:
            return None


@api.route("/dashboard/update")
async def dashboardupdate():
    api_key = request.headers.get("Authorization")

    if api_key == "$WnY%#vMN@U_UA28xtg":
        resident_list = []
        visitor_list = []
        solo_list = []
        mentors_list = []
        actions = []
        api_urls = ["https://hq.vatwa.net/api/vacc/NPL/resident", "https://hq.vatwa.net/api/vacc/NPL/visitor",
                    "https://hq.vatwa.net/api/solo/vacc/NPL", "https://hq.vatwa.net/api/vacc/NPL/mentor"]

        counter = 0

        async with aiohttp.ClientSession() as cs:
            for url in api_urls:
                actions.append(asyncio.ensure_future(get_api_data(cs, url)))

            api_data = await asyncio.gather(*actions)

            for data in api_data:
                if data != None:

                    if counter == 0:
                        for residents in data:
                            resident_list.append(residents)
                        counter = counter + 1
                        residents_num = len(resident_list)

                    elif counter == 1:
                        for visitors in data:
                            visitor_list.append(visitors)
                        counter = counter + 1
                        visitors_num = len(visitor_list)

                    elif counter == 2:
                        for solopeeps in data:
                            solo_list.append(solopeeps)
                        counter = counter + 1
                        solo_num = len(solo_list)

                    elif counter == 3:
                        for mentors in data:
                            mentors_list.append(mentors)
                        counter = counter + 1
                        mentors_num = len(mentors_list)

            if data != None:

                found_json = VATSIM.query.filter_by(value=1).first()
                found_json.json_data = residents_num
                db.session.commit()
                print("Mufassil, Residents Updated In The Database!")

                found_json = VATSIM.query.filter_by(value=2).first()
                found_json.json_data = visitors_num
                db.session.commit()
                print("Mufassil, Visitors Updated In The Database!")

                if len(solo_list) == 0:
                    found_json = VATSIM.query.filter_by(value=3).first()
                    found_json.json_data = 0
                    db.session.commit()
                    print("Mufassil, Solo Was Updated In Database!")

                elif len(solo_list) != 0:
                    found_json = VATSIM.query.filter_by(value=3).first()
                    found_json.json_data = solo_num
                    db.session.commit()
                    print("Mufassil, Solo Was Updated In Database!")

                found_json = VATSIM.query.filter_by(value=4).first()
                found_json.json_data = mentors_num
                db.session.commit()
                print("Mufassil, Mentors Was Updated In Database!")


                responses = {
                    'details' : 'completed'
                }
                return jsonify(responses)
            
            elif data == None:
                responses = {
                    'details' : 'VATWA HQ returned None'
                }
                return jsonify(responses), 400
                

    elif not api_key:
        Missing_Key = {
        'details' : 'Authentication credentials were not provided.',
        }
        return jsonify(Missing_Key), 401
    
    else:
        Invalid_Key = {
        'details' : 'Authentication credentials were incorrect.',
        }
        return jsonify(Invalid_Key), 401




@api.route("/events/update")
def updateevents():
    api_key = request.headers.get("Authorization")

    if api_key == "$WnY%#vMN@U_UA28xtg":
        r = requests.get("https://hq.vatwa.net/api/events/future")
        
        if r.status_code == 200:
            events = r.json()
            for data in events:
                if "NPL" in data['vacc']:
                    query1 = Events.query.filter_by(value=data['id']).first()
                    replace_start = data['start'].replace('T', ' ')
                    replace_end = data['end'].replace('T', ' ')

                    if query1:
                        query1.start_time = replace_start
                        query1.end_time = replace_end
                        query1.event_banner = data['banner_link']
                        db.session.commit()

                    else:
                        insert_event = Events(value=data['id'], start_time=replace_start, end_time=replace_end,
                                                event_banner=data['banner_link'], event_link=f"https://hq.vatwa.net/event/{data['id']}")
                        db.session.add(insert_event)
                        db.session.commit()

                    # delete old events from DB
                    times = Events.query.all()
                    if times:
                        time_now = datetime.utcnow()

                        for time in times:
                            stored = time.end_time[:-8]
                            stored_time = datetime.strptime(stored, '%Y-%m-%d %H:%M:%S')
                            diff = stored_time - time_now
                            actual_diff = (diff.total_seconds() / 60)
                            if actual_diff <= 0:
                                get_time = time.end_time
                                Events.query.filter_by(end_time=get_time).delete()
                                db.session.commit()
                    
            responses = {
                'details' : 'completed'
            }
            return jsonify(responses)
        
        else:
            responses = {
                'details' : 'VATWA HQ did not return 200 status code',
            }
            return jsonify(responses), 400


    elif not api_key:
        Missing_Key = {
        'details' : 'Authentication credentials were not provided.',
        }
        return jsonify(Missing_Key), 401
    
    else:
        Invalid_Key = {
        'details' : 'Authentication credentials were incorrect.',
        }
        return jsonify(Invalid_Key), 401

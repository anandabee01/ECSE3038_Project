# 620143209
# Tia A. Brown
# ECSE3038
# Project 

from fastapi import FastAPI, Request, HTTPException, status
from datetime import datetime, timedelta, date
import json
from fastapi.responses import Response, JSONResponse
import pydantic
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from bson import ObjectId
import re
import os 
import motor.motor_asyncio
from bson import ObjectId

referencetemp = 28

load_dotenv()

app = FastAPI()

origins = ["https://simple-smart-hub-client.netlify.app/"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],   #Allows for all HTTP requests
    allow_headers=["*"],
)

pydantic.json.ENCODERS_BY_TYPE[ObjectId] = str

client = motor.motor_asyncio.AsyncIOMotorClient("mongodb+srv://anandabee01234@cluster0.o37kf0x.mongodb.net/?retryWrites=true&w=majority")
db = client.

sensor_readings = db['sensor_readings']
data = db['data']

def get_sunset():
    sunset_api_endpoint = "https://api.sunrise-sunset.org/json?lat={user_latitude}&lng={user_longitude}"

    sunset_response = requests.get(sunset_api_endpoint)
    sunset_data = sunset_response.json()

    sunset_field = sunset_data['results']['sunset']
    sunset_time = datetime.strptime(sunset_data,"%I:%M:%S %p") + timedelta(hours = -5)
    newsunset_time = datetime.strftime(sunset_time, "%H:%M:%S")

    return newsunset_time

@app.get("/")
async def Welcome():
    return {"This is my project": "ECSE3038_Project"}

@app.get('/graph')
async def graph(request: Request, size:int):
    size = int(request.query_data.get('size'))
    readings = await db ["Embedded"].find().sort('_id', -1).limit(size).to_list(size)
    data_info = []

    for info in readings:
        temperature = info.get("temperature")
        presence = info.get("presence")
        datetime = info.get("date_time")

        data_info.append({
            "temperature": temperature,
            "presence": presence,
            "datetime": datetime
        })

    return data_info

    data_info = [{**data, "_id": str(data["_id"])} 
                 for data in data_info]
    return JSONResponse(content=data_info)

#PUT /Embedded
@app.put("/Settings", status_code=201)
async def embedded_data(request: Request):
    what_am_i = await request.json()
    what_am_i["skittles"] = "Wild Berry"

    user_temp = what_am_i["user_temp"]
    user_light = what_am_i["user_light"]
    light_duration = what_am_i["light_duration"]
    

    if what_am_i["user_light"] == "sunset":             #check sunset 
        what_am_i["user_light"] = get_sunset()          #check sunset time
    else:
        user_light = datetime.strptime(user_light, "%H:%M:%S")
    
    new_user_light = user_light + parse_time(light_duration)


    output = {
        "user_temp": user_temp,
        "user_light": str(user_light()),
        "light_duration": str(new_user_light())
        }
    
    # new_settings = await sensor_readings(output)
    # new_settings = await sensor_readings.find_one({"_id":updated_settings.inserted_id})
    # return new_settings

    obj = await sensor_readings.find().sort('_id', -1).limit(1).to_list(1)

    if obj:
        await sensor_readings.update_one({"_id": obj[0]["_id"]}, {"$set": output})
        new_obj = await sensor_readings.find_one({"_id": obj[0]["_id"]})
    else:
        new = await sensor_readings.insert_one(output)
        new_obj = await sensor_readings.find_one({"_id": new.inserted_id})
    return new_obj

@app.post("/temperature")
async def toggle(request: Request): 
    state = await request.json()

    param = await sensor_readings.find().sort('_id', -1).limit(1).to_list(1)

    if param:
        temperature = param[0]["user_temp"]   
        user_light = datetime.datetime.strptime(param[0]["user_light"], "%H:%M:%S")
        time_off = datetime.datetime.strptime(param[0]["light_time_off"], "%H:%M:%S")
    else:
        temperature = 28
        user_light = datetime.datetime.strptime("18:00:00", "%H:%M:%S")
        time_off = datetime.strptime("20:00:00", "%H:%M:%S")
        time_off = datetime.strptime("20:00:00", "%H:%M:%S")

    now_time = datetime.datetime.now(pytz.timezone('Jamaica')).time()
    current_time = datetime.datetime.strptime(str(now_time),"%H:%M:%S.%f")


    state["light"] = ((current_time < user_light) and (current_time < time_off ) & (state["presence"] == 1 ))
    state["fan"] = ((float(state["temperature"]) >= temperature) & (state["presence"]==1))
    state["current_time"]= str(datetime.datetime.now())

    new_settings = await data.insert_one(state)
    new_obj = await data.find_one({"_id":new_settings.inserted_id}) 
    return new_obj

regex = re.compile(r'((?P<hours>\d+?)h)?((?P<minutes>\d+?)m)?((?P<seconds>\d+?)s)?')

def parse_time(time_str):
    parts = regex.match(time_str)
    if not parts:
        return
    parts = parts.groupdict()
    time_params = {}
    for name, param in parts.items():
        if param:
            time_params[name] = int(param)
    return timedelta(**time_params)

#retreves last try 
@app.get("/state", status_code= 200)
async def get_state():
    last_try = await data.find().sort('_id', -1).limit(1).to_list(1)

    if not last_try:
        return {
            "presence": False,
            "fan": False,
            "light": False,
            "current_time": datetime.datetime.now()
        }

    return last_try
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

cred = credentials.Certificate("face-recg-80f92-firebase-adminsdk-hb9m9-235ebc60e2.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://face-recg-80f92-default-rtdb.firebaseio.com/"
})

ref = db.reference('Students')

data = {
    "00001":
        {
            "name": "Aaditya Aaryan",
            "major": "AIML",
            "starting_year": 2021,
            "total_attendance": 1,
            "standing": "G",
            "year": 3,
            "last_attendance_time": "2022-12-11 00:54:34"
        },
    "000018":
        {
            "name": "Rishi Raj",
            "major": "ISE",
            "starting_year": 2018,
            "total_attendance": 12,
            "standing": "B",
            "year": 3,
            "last_attendance_time": "2022-12-11 00:54:34"
        },
    "000024":
        {
            "name": "Mansi",
            "major": "AIML",
            "starting_year": 2021,
            "total_attendance": 12,
            "standing": "A",
            "year": 3,
            "last_attendance_time": "2022-12-11 00:54:34"
        },
    "000002":
        {
            "name": "Aksahy Bhardwaj",
            "major": "AIML",
            "starting_year": 2021,
            "total_attendance": 12,
            "standing": "B",
            "year": 3,
            "last_attendance_time": "2022-12-11 00:54:34"
        },

    "00045":
        {
            "name": "Abhay",
            "major": "ECE",
            "starting_year": 2021,
            "total_attendance": 7,
            "standing": "G",
            "year": 3,
            "last_attendance_time": "2022-12-11 00:54:34"
        }
}

for key, value in data.items():
    ref.child(key).set(value)
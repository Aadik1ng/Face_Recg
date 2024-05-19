import os
import pickle
from datetime import datetime

import cv2
import face_recognition
import cvzone
import firebase_admin
from firebase_admin import credentials, db, storage
import numpy as np
import streamlit as st
from streamlit_webrtc import VideoTransformerBase, webrtc_streamer

# Initialize Firebase (check if already initialized)
if not firebase_admin._apps:
    cred = credentials.Certificate("face-recg-80f92-firebase-adminsdk-hb9m9-235ebc60e2.json")
    firebase_admin.initialize_app(cred, {
        'databaseURL': "https://face-recg-80f92-default-rtdb.firebaseio.com/",
        'storageBucket': "face-recg-80f92.appspot.com"
    })

bucket = storage.bucket()

# Load the encoding file
with open('EncodeFile.p', 'rb') as file:
    encodeListKnownWithIds = pickle.load(file)
encodeListKnown, studentIds = encodeListKnownWithIds

folderModePath = 'Resources/Modes'
modePathList = os.listdir(folderModePath)
imgModeList = [cv2.imread(os.path.join(folderModePath, path)) for path in modePathList]

imgBackground = cv2.imread('Resources/background.png')

class VideoTransformer(VideoTransformerBase):
    def __init__(self):
        self.encodeListKnown = encodeListKnown
        self.studentIds = studentIds
        self.modeType = 0
        self.counter = 0
        self.id = -1
        self.imgStudent = []
        self.imgBackground = imgBackground.copy()
        self.imgModeList = imgModeList

    def transform(self, frame):
        img = frame.to_ndarray(format="bgr24")

        imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
        imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

        faceCurFrame = face_recognition.face_locations(imgS)
        encodeCurFrame = face_recognition.face_encodings(imgS, faceCurFrame)

        self.imgBackground[162:162 + 480, 55:55 + 640] = img

        if faceCurFrame:
            for encodeFace, faceLoc in zip(encodeCurFrame, faceCurFrame):
                matches = face_recognition.compare_faces(self.encodeListKnown, encodeFace)
                faceDis = face_recognition.face_distance(self.encodeListKnown, encodeFace)

                matchIndex = np.argmin(faceDis)

                if matches[matchIndex]:
                    y1, x2, y2, x1 = faceLoc
                    y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                    bbox = 55 + x1, 162 + y1, x2 - x1, y2 - y1
                    self.imgBackground = cvzone.cornerRect(self.imgBackground, bbox, rt=0)
                    self.id = self.studentIds[matchIndex]
                    if self.counter == 0:
                        cvzone.putTextRect(self.imgBackground, "Loading", (275, 400))
                        self.counter = 1
                        self.modeType = 1

            if self.counter != 0:
                if self.counter == 1:
                    studentInfo = db.reference(f'Students/{self.id}').get()

                    blob = bucket.get_blob(f'Images/{self.id}.jpg')
                    array = np.frombuffer(blob.download_as_string(), np.uint8)
                    self.imgStudent = cv2.imdecode(array, cv2.IMREAD_COLOR)

                    datetimeObject = datetime.strptime(studentInfo['last_attendance_time'], "%Y-%m-%d %H:%M:%S")
                    secondsElapsed = (datetime.now() - datetimeObject).total_seconds()
                    if secondsElapsed > 30:
                        ref = db.reference(f'Students/{self.id}')
                        studentInfo['total_attendance'] += 1
                        ref.child('total_attendance').set(studentInfo['total_attendance'])
                        ref.child('last_attendance_time').set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                    else:
                        self.modeType = 3
                        self.counter = 0
                        self.imgBackground[44:44 + 633, 808:808 + 414] = self.imgModeList[self.modeType]

                if self.modeType != 3:
                    if 10 < self.counter < 20:
                        self.modeType = 2

                    self.imgBackground[44:44 + 633, 808:808 + 414] = self.imgModeList[self.modeType]

                    if self.counter <= 10:
                        cv2.putText(self.imgBackground, str(studentInfo['total_attendance']), (861, 125),
                                    cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 1)
                        cv2.putText(self.imgBackground, str(studentInfo['major']), (1006, 550),
                                    cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
                        cv2.putText(self.imgBackground, str(self.id), (1006, 493),
                                    cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
                        cv2.putText(self.imgBackground, str(studentInfo['standing']), (910, 625),
                                    cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)
                        cv2.putText(self.imgBackground, str(studentInfo['year']), (1025, 625),
                                    cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)
                        cv2.putText(self.imgBackground, str(studentInfo['starting_year']), (1125, 625),
                                    cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)

                        (w, h), _ = cv2.getTextSize(studentInfo['name'], cv2.FONT_HERSHEY_COMPLEX, 1, 1)
                        offset = (414 - w) // 2
                        cv2.putText(self.imgBackground, str(studentInfo['name']), (808 + offset, 445),
                                    cv2.FONT_HERSHEY_COMPLEX, 1, (50, 50, 50), 1)
                        self.imgStudent = cv2.resize(self.imgStudent, (216, 216))
                        self.imgBackground[175:175 + 216, 909:909 + 216] = self.imgStudent

                    self.counter += 1

                    if self.counter >= 20:
                        self.counter = 0
                        self.modeType = 0
                        studentInfo = []
                        self.imgStudent = []
                        self.imgBackground[44:44 + 633, 808:808 + 414] = self.imgModeList[self.modeType]

            self.modeType = 0
            self.counter = 0

        return self.imgBackground

st.title("Face Recognition Attendance System")

webrtc_streamer(key="example", video_transformer_factory=VideoTransformer)

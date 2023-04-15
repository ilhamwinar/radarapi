import requests
from pydantic import BaseModel
from datetime import datetime, timedelta
import numpy as np
import joblib
from model import method_prediksi
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import uvicorn
from fastapi import FastAPI, Body, Depends, HTTPException, Form
import logging
from passlib.context import CryptContext

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s.%(msecs)03d [%(levelname)s] %(message)s",
    datefmt="%m/%d/%Y %H:%M:%S",
)

app=FastAPI()
security = HTTPBasic()
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"])

PWD_CONTEXT = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return PWD_CONTEXT.hash(password)
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return PWD_CONTEXT.verify(plain_password, hashed_password)

def get_current_username(credentials: HTTPBasicCredentials = Depends(security)):
    current_username_bytes = credentials.username
    correct_username_bytes = "$2b$12$7a2om6UEbMNKkk3dT8JrMeort9GrTudi7qkH1y.g21wIRUrlzw6yS"
    is_correct_username=verify_password(current_username_bytes, correct_username_bytes)
    current_password_bytes = credentials.password
    correct_password_bytes = "$2b$12$7a2om6UEbMNKkk3dT8JrMeort9GrTudi7qkH1y.g21wIRUrlzw6yS"
    is_correct_password=verify_password(current_password_bytes, correct_password_bytes) 
    
    if not (is_correct_username and is_correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


url = "https://jid.jasamarga.com/graph/contraflow_display/getPredictionApi"

# #input method tanggal 

@app.post("/ml_radar", tags=["mengambil grafik radar"])
def add_post(metode_prediksi: str = Form(...), range_prediksi: int = Form(...),skala_prediksi: int = Form(...),id: int = Form(...),sampai: str = Form(...),username: str = Depends(get_current_username)):
    #inisialisasi variable
    preda=[]
    predb=[]
    pred_date=[]
    temp_a_prediksi=[]
    temp_b_prediksi=[]
    tanggal1=sampai
    skala_forecasting=skala_prediksi
    metode_prediksi=metode_prediksi
    range_prediksi=range_prediksi
    id=id

    if metode_prediksi == "ml":
        logging.info("METODE PREDIKSI MENGGUNAKAN ML")
        request_body = {
                        "metode_prediksi":"arima",
                        "range_prediksi":range_prediksi,
                        "skala_prediksi":0,
                        "id":id,
                        "sampai": tanggal1
        }

        headers = {"Content-Type": "application/x-www-form-urlencoded",}

        response = requests.post(url, headers=headers, data=request_body)
        logging.info("BERIKUT ADALAH RESPONSE: "+str(response.text))

        lalina=int(response.json()['current']['a'][-1]['y'])
        lalinb=int(response.json()['current']['b'][-1]['y'])

        tanggal1=datetime.strptime(tanggal1,'%Y-%m-%dT%H:00')
        current_hour=tanggal1.hour

        acta=np.array([[lalina,current_hour]])
        actb=np.array([[lalinb,current_hour]])
        model = joblib.load("model_radar_japek_bawah.dat")

        
        for x in range(skala_forecasting):
            if len(preda)==0:
                resulta = model.predict(acta)
                resultb = model.predict(actb)

                preda.append(int(resulta))
                predb.append(int(resultb))
                next_date = current_hour 
                pred_date.append(next_date)

            elif len(preda)>0:
                i=int(x)-1
                temp=preda[i]
                acta=np.array([[preda[i],pred_date[i]]])
                actb=np.array([[predb[i],pred_date[i]]])
                resulta = model.predict(acta)
                preda.append(int(resulta))
                predb.append(int(resultb))
                next_date = next_date + 1
                pred_date.append(next_date)

        logging.info("HASIL PREDIKSI A ADALAH: "+str(preda))
        logging.info("HASIL PREDIKSI B ADALAH: "+str(predb))
        logging.info("TANGGAL PREDIKSI ADALAH: "+str(pred_date))

        print(tanggal1)
        tanggal=tanggal1.strftime('%d-%m-%Y')
        temp_a_prediksi=response.json()['current']['a']
        temp_b_prediksi=response.json()['current']['b']

        for i in range(skala_forecasting):
            add=i+1
            try:
                temp_dict_a={'x': "Prediksi "+tanggal+" "+str(pred_date[i])+":"+"00"+" - "+str(pred_date[add])+":"+"00",'y':preda[i]}
                temp_dict_b={'x': "Prediksi "+tanggal+" "+str(pred_date[i])+":"+"00"+" - "+str(pred_date[add])+":"+"00",'y':predb[i]}
            except:
                if (pred_date[i]+1) == 24:
                    temp_dict_a={'x': "Prediksi "+tanggal+" "+str(pred_date[i])+":"+"00"+" - "+"00"+":"+"00",'y':preda[i]}
                    temp_dict_b={'x': "Prediksi "+tanggal+" "+str(pred_date[i])+":"+"00"+" - "+"00"+":"+"00",'y':predb[i]}
                else:
                    temp_dict_a={'x': "Prediksi "+tanggal+" "+str(pred_date[i])+":"+"00"+" - "+str(pred_date[i]+1)+":"+"00",'y':preda[i]}
                    temp_dict_b={'x': "Prediksi "+tanggal+" "+str(pred_date[i])+":"+"00"+" - "+str(pred_date[i]+1)+":"+"00",'y':predb[i]}

            temp_a_prediksi.append(temp_dict_a)
            temp_b_prediksi.append(temp_dict_b)

        temp_dict={"a":temp_a_prediksi,"b":temp_b_prediksi}
        current_dict={"current":temp_dict}

    else:
        raise Exception("SALAH METODE FORECASTING")

    return current_dict

if __name__ == "__main__":
    uvicorn.run("main:app", host="20.10.20.185", port=8100,log_level="info")


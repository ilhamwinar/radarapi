FROM python:3.9-slim-bullseye
#FROM python:3.7
ENV TZ="Asia/Jakarta"
RUN python -m pip install --upgrade pip
RUN pip install numpy 
RUN pip install schedule 
RUN pip install joblib
RUN pip install python-decouple
RUN pip install scikit-learn
RUN pip install xgboost
RUN pip install fastapi
RUN pip install uvicorn
RUN pip install passlib
RUN pip install pydantic
RUN pip install requests 
RUN pip install python-multipart


COPY ./ .
WORKDIR /

EXPOSE 8200:8200



CMD ["uvicorn", "main:app","--host","0.0.0.0","--port", "8200"]

from pydantic import BaseModel, Field,EmailStr


#method body
# # request_body = {
#     "metode_prediksi": "ML",
#     "range_prediksi":12,
#     "skala_prediksi":0,
#     "id":6,
#     "sampai": "2023-03-13T00:00"
# }

class method_prediksi(BaseModel):
    metode_prediksi: str=Field(default=None)
    range_prediksi: int= Field(default=None)
    skala_prediksi : int= Field(default=None)
    id : int= Field(default=None)
    sampai : str=Field(default=None)
    class Config:
        schema_extra={
            "post_demo":{
                "metode_prediksi":"menggunakan machine learning",
                "range_prediksi":"maksimal 12",
                " skala_prediksi":"skala 3",
                "id": "tergantung lokasi radar",
                "sampai": "2023-03-13T00:00"
            }
        }
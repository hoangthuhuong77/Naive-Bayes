from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import pandas as pd


du_lieu = joblib.load("mo_hinh_naive_bayes.pkl")

mo_hinh = du_lieu["mo_hinh"]
bo_ma_mau_sac = du_lieu["bo_ma_mau_sac"]
bo_ma_mui_huong = du_lieu["bo_ma_mui_huong"]
bo_ma_loai_hoa = du_lieu["bo_ma_loai_hoa"]


app = FastAPI(title="API Phân loại hoa bằng Naive Bayes")


class ThongTinHoa(BaseModel):
    chieu_dai_canh_hoa: float
    chieu_rong_canh_hoa: float
    mui_huong: str
    mau_sac: str


@app.get("/")
def trang_chu():
    return {
        "thong_bao": "API phân loại hoa đang hoạt động"
    }


@app.post("/du-doan")
def du_doan_hoa(data: ThongTinHoa):

    mui_huong = bo_ma_mui_huong.transform([data.mui_huong])[0]
    mau_sac = bo_ma_mau_sac.transform([data.mau_sac])[0]

    hoa_moi = pd.DataFrame([{
        "chieu_dai_canh_hoa": data.chieu_dai_canh_hoa,
        "chieu_rong_canh_hoa": data.chieu_rong_canh_hoa,
        "mui_huong": mui_huong,
        "mau_sac": mau_sac
    }])

    du_doan = mo_hinh.predict(hoa_moi)

    ten_hoa = bo_ma_loai_hoa.inverse_transform(du_doan)[0]

    return {
        "loai_hoa_du_doan": ten_hoa
    }
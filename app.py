import streamlit as st
from datetime import datetime
from pymongo import MongoClient
from bson.objectid import ObjectId
import pickle
import numpy as np

# ---------------- MODEL ----------------
@st.cache_resource
def load_model():
    with open("expense_model.pkl", "rb") as f:
        return pickle.load(f)

model = load_model()

# ---------------- MONGO ----------------
mongo_uri = st.secrets["MONGO"]["URI"]
client = MongoClient(mongo_uri)
db = client["finance_db"]
collection = db["expenses"]

st.set_page_config(layout="wide")

# ---------------- ÜST ROW (Buton + Sonuç) ----------------
col_left, col_right = st.columns([9,1])
prediction_placeholder = col_left.empty()

if col_right.button("📊 Gelecek Ay Tahmini"):
    march_2026_index = 27
    prediction = model.predict(np.array([[march_2026_index]]))
    prediction_placeholder.success(f"📈 {prediction[0]:,.2f} ₺")  

col1, col2 = st.columns(2)

# ---------------- SOL TARAF (Harcama Listesi) ----------------
with col1:
    st.subheader("📋 Harcama Listesi")
    expenses = list(collection.find().sort("date", 1))
    if expenses:
        for expense in expenses:
            col_a, col_b = st.columns([4,1])
            with col_a:
                st.write(f"""
                **Kategori:** {expense['category']}  
                **Tutar:** {expense['amount']} ₺  
                **Açıklama:** {expense['description']}  
                **Tarih:** {expense['date'].strftime("%d-%m-%Y")}
                """)
            with col_b:
                if st.button("❌", key=str(expense["_id"])):
                    collection.delete_one({"_id": expense["_id"]})
                    st.rerun()
            st.markdown("---")
    else:
        st.info("Henüz harcama eklenmedi.")

# ---------------- SAĞ TARAF (Yeni Harcama Formu) ----------------
with col2:
    st.subheader("➕ Yeni Harcama Ekle")
    with st.form("expense_form"):
        category = st.selectbox("Kategori", ["Market", "Kira", "Fatura", "Ulaşım", "Diğer"])
        amount = st.number_input("Tutar (₺)", min_value=0.0, step=1.0)
        description = st.text_input("Açıklama")
        date = st.date_input("Tarih")

        submit = st.form_submit_button("Kaydet")
        if submit:
            expense = {
                "category": category,
                "amount": amount,
                "description": description,
                "date": datetime.combine(date, datetime.min.time())
            }
            collection.insert_one(expense)
            st.success("Harcama kaydedildi ✅")
            st.rerun()
# Dashboard Kinerja Lelang

Dashboard Streamlit sederhana untuk menjawab studi kasus visualisasi data aset dan
lelang. Data yang dipakai adalah data dummy pada `data/Dummy_Kinerja_Lelang.xlsx`.

## Menjalankan dashboard

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run src/app.py
```

Eksplorasi dan pembuatan CSV hasil olahan bersifat opsional:

```bash
python src/exploration.py
```

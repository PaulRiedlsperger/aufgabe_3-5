import streamlit as st
import read_data 
from PIL import Image
from read_pandas import read_my_csv
from HR_functions import make_plot_with_zones, get_average_power, get_max_power, get_hr_zone

tab1 ,tab2 = st.tabs(["Versuchsperson", "Daten"])

with tab1:
   
    # Session State wird leer angelegt, solange er noch nicht existiert
    if 'current_user' not in st.session_state:
        st.session_state.current_user = 'None'

    # Legen Sie eine neue Liste mit den Personennamen an indem Sie ihre 
    # Funktionen aufrufen
    person_dict = read_data.load_person_data()
    person_names = read_data.get_person_list(person_dict)
    # bzw: wenn Sie nicht zwei separate Funktionen haben
    # person_names = read_data.get_person_list()

    # Eine Überschrift der ersten Ebene
    st.write("# EKG APP")

    # Eine Überschrift der zweiten Ebene
    st.write("## Versuchsperson auswählen")

    # Eine Auswahlbox, das Ergebnis wird in current_user gespeichert
    st.session_state.current_user = st.selectbox(
        'Versuchsperson',
        options = person_names, key="sbVersperson_namesuchsperson")

    # Anlegen des Session State. Bild, wenn es kein Bild gibt
    if 'picture_path' not in st.session_state:
        st.session_state.picture_path = 'data/pictures/none.jpg'

    st.session_state.picture_path = read_data.find_person_data_by_name(st.session_state.current_user)["picture_path"]

    image = Image.open(st.session_state.picture_path)
    st.image(image, caption=st.session_state.current_user)


with tab2: 
    df = read_my_csv()
    st.plotly_chart(make_plot_with_zones(df, HRmax=200))
 
    st.write("Durchschnittliche Leistung: ", get_average_power(df))
    st.write("Maximale Leistung: ", get_max_power(df))

    HRmax = st.slider("Maximale Herzfrequenz (HRmax)", 150, 220, 200)

    # Zonen zuweisen
    df["zone"] = df["HeartRate"].apply(lambda x: get_hr_zone(x, HRmax))

    # Zonen-Zeit
    zone_zeiten = df["zone"].value_counts().sort_index()
    st.subheader("🕒 Zeit in den Herzfrequenz-Zonen (in Sekunden)")
    st.dataframe(zone_zeiten.rename("Zeit (s)"))

    # Durchschnittsleistung je Zone
    leistung_zone = df.groupby("zone")["PowerOriginal"].mean().round(1)
    st.subheader("⚡ Durchschnittliche Leistung pro Zone")
    st.dataframe(leistung_zone.rename("Ø Leistung (Watt)"))
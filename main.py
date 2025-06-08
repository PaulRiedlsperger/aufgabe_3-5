import streamlit as st
import read_data 
import json
from PIL import Image
from read_pandas import read_my_csv
from HR_functions import make_plot_with_zones, get_average_power, get_max_power, get_hr_zone
from ekgdata import EKGdata
from person import Person

tab1 ,tab2 ,tab3 = st.tabs(["Versuchsperson", "Daten", "EKG-Analyse"])

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

    #HRmax = st.slider("Maximale Herzfrequenz (HRmax)", 150, 220, 200)

    HRmax = st.slider(
    "Maximale Herzfrequenz (HRmax)",
    150, 220, st.session_state.get("HRmax", 200),
    key="slider_hrmax_tab2"
    )
    st.session_state.HRmax = HRmax

    df = read_my_csv()
    st.plotly_chart(make_plot_with_zones(df, HRmax))
 
    st.write("Durchschnittliche Leistung: ", get_average_power(df))
    st.write("Maximale Leistung: ", get_max_power(df))

    
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

with tab3:
    file = open("data/person_db.json")
    person_data = json.load(file)
    suchid = st.number_input("Gib eine ID ein", min_value=0, step=1)


    if suchid:
        selected_dict = Person.find_person_data_by_id(suchid)

        if selected_dict:
            st.write("🔍 Ausgewählte Person:", selected_dict)

            # EKG-Daten laden
            ekg_dict = selected_dict["ekg_tests"][0]
            ekg = EKGdata(ekg_dict)

            st.write("📊 EKG-Daten (Vorschau):")
            st.dataframe(ekg.df.head())

            # Analyse
            threshold = st.slider("🩺 Schwellwert für Peaks", 0.1, 1.0, 0.4)
            peaks = ekg.find_peaks(threshold)
            ekg.peaks = peaks

            heart_rate = ekg.estimate_heart_rate(peaks)
            st.metric("❤️ Geschätzte Herzfrequenz", f"{heart_rate} bpm")

            # Plot
            if hasattr(ekg, 'peaks'):
                st.subheader("📈 EKG-Zeitreihe mit markierten Peaks")
                fig = ekg.plot_time_series()
                st.plotly_chart(fig, use_container_width=True)

        else:
            st.warning("⚠️ Keine Person mit dieser ID gefunden.")

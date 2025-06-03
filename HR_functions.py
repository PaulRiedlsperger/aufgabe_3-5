from read_pandas import read_my_csv
import streamlit as st
import plotly.graph_objects as go

df = read_my_csv()

# Beispielhafte Daten (falls du keine eigenen einliest)
# df = pd.read_csv("deine_datei.csv")  # alternativ
# Hier als Beispiel:
# df = pd.DataFrame({"time": [...], "HeartRate": [...]})


def make_plot_with_zones(df, HRmax):

    
    # Zone pro Zeile berechnen
    def get_zone(hr):
        if hr < HRmax * 0.6:
            return "Zone 1"
        elif hr < HRmax * 0.7:
            return "Zone 2"
        elif hr < HRmax * 0.8:
            return "Zone 3"
        elif hr < HRmax * 0.9:
            return "Zone 4"
        else:
            return "Zone 5"

    df["zone"] = df["HeartRate"].apply(get_zone)
    

    # Farben pro Zone
    zone_colors = {
        "Zone 1": "rgba(0,255,0,0.1)",     # grün
        "Zone 2": "rgba(100,200,0,0.1)",
        "Zone 3": "rgba(255,255,0,0.1)",   # gelb
        "Zone 4": "rgba(255,165,0,0.1)",   # orange
        "Zone 5": "rgba(255,0,0,0.1)"      # rot
    }

    # Vertikale farbige Shapes definieren
    shapes = []
    start_time = df["time"].iloc[0]
    current_zone = df["zone"].iloc[0]

    for i in range(1, len(df)):
        if df["zone"].iloc[i] != current_zone:
            end_time = df["time"].iloc[i]

            shapes.append(dict(
                type="rect",
                xref="x", yref="paper",
                x0=start_time,
                x1=end_time,
                y0=0, y1=1,
                fillcolor=zone_colors[current_zone],
                line=dict(width=0),
                layer="below"
            ))

            start_time = end_time
            current_zone = df["zone"].iloc[i]

    # Letzten Bereich anhängen
    shapes.append(dict(
        type="rect",
        xref="x", yref="paper",
        x0=start_time,
        x1=df["time"].iloc[-1],
        y0=0, y1=1,
        fillcolor=zone_colors[current_zone],
        line=dict(width=0),
        layer="below"
    ))

    # Plot erstellen
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df["time"],
        y=df["HeartRate"],
        mode="lines",
        name="Herzfrequenz",
        line=dict(color="black")
    ))

    fig.update_layout(
        title="Herzfrequenz über Zeit mit farbigen Zonen",
        xaxis_title="Zeit (s)",
        yaxis_title="Herzfrequenz (bpm)",
        shapes=shapes,
        yaxis=dict(range=[df["HeartRate"].min() - 5, HRmax + 10])
    )

    fig.add_trace(go.Scatter(
        x=df["time"],
        y=df["PowerOriginal"],
        mode="lines",
        name="Leistung (Watt)",
        yaxis="y2",  # zweite Y-Achse
        line=dict(color="blue", dash="dot")
    ))

    fig.update_layout(
        title="Herzfrequenz & Leistung über Zeit mit Zonen",
        xaxis_title="Zeit (s)",
        yaxis=dict(
            title="Herzfrequenz (bpm)",
            range=[df["HeartRate"].min() - 5, HRmax + 10]
        ),
        yaxis2=dict(
            title="Leistung (Watt)",
            overlaying="y",
            side="right",
            showgrid=False
        ),
        shapes=shapes  # falls du die vertikalen Zonen drin hast
    )


    return fig

  
def get_average_power(df):
    """
    Gibt den Mittelwert der Spalte 'Power' zurück.
    """
    return df["PowerOriginal"].mean()

def get_max_power(df):
    """
    Gibt den Maximalwert der Spalte 'Power' zurück.
    """
    return df["PowerOriginal"].max()

HRmax = st.slider("Maximale Herzfrequenz (HRmax)", min_value=150, max_value=220, value=200)

def get_hr_zone(hr, HRmax):
    if hr < HRmax * 0.6:
        return "Zone 1"
    elif hr < HRmax * 0.7:
        return "Zone 2"
    elif hr < HRmax * 0.8:
        return "Zone 3"
    elif hr < HRmax * 0.9:
        return "Zone 4"
    else:
        return "Zone 5"

df["zone"] = df["HeartRate"].apply(lambda x: get_hr_zone(x, HRmax))

zone_zeiten = df["zone"].value_counts().sort_index()
st.subheader("🕒 Zeit in den Herzfrequenz-Zonen (in Sekunden)")
st.dataframe(zone_zeiten.rename("Zeit (s)"))

leistung_zone = df.groupby("zone")["PowerOriginal"].mean().round(1)
st.subheader("⚡ Durchschnittliche Leistung pro Zone")
st.dataframe(leistung_zone.rename("Ø Leistung (Watt)"))

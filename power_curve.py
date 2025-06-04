import pandas as pd
from read_pandas import read_my_csv
import plotly.graph_objects as go
import numpy as np

def read_my_csv(path):
    df = pd.read_csv(path)
    
    t_end= len(df)
    time = np.arange(0, t_end)
    df["time"] = time
    
    return df



def find_best_effort(series, window_seconds):
    """
    Findet die höchste durchschnittliche Leistung innerhalb eines gegebenen Zeitfensters.
    
    Args:
        series (pd.Series): Zeitreihe mit Leistungswerten (z. B. Watt), indiziert nach Zeitstempeln.
        window_seconds (int): Dauer des Zeitfensters in Sekunden.

    Returns:
        Tuple[float, pd.Timestamp]: (Maximale Durchschnittsleistung, Startzeitpunkt des besten Abschnitts)
    """

    # Gleitendes Fenster über den angegebenen Zeitraum (z. B. '300s' für 5 Minuten)
    rolling_avg = series.rolling(window_seconds).mean()             #window_seconds ändern!  

    # Maximalwert finden
    max_avg_power = rolling_avg.max()
    best_time = rolling_avg.idxmax()

    return max_avg_power, best_time


def generate_power_curve(series, window_list=[60, 120, 300, 600, 900, 1200, 1800]) -> pd.DataFrame:
    """
    Erzeugt eine Power Curve aus einer Zeitreihe und mehreren Fenstergrößen.

    Args:
        series (pd.Series): Zeitreihe mit Leistungswerten (z. B. Watt), Zeitstempel als Index.
        window_list (list[int]): Liste von Fenstergrößen in Sekunden.

    Returns:
        pd.DataFrame: Power Curve mit Spalten 'window_seconds' und 'avg_power'.
    """
    results = []

    for window in window_list:
        try:
            max_avg, _ = find_best_effort(series, window)
            results.append({"window_seconds": window, "avg_power": max_avg})
        except Exception as e:
            print(f"Fehler bei Fenster {window} Sekunden: {e}")
            results.append({"window_seconds": window, "avg_power": None})


    return pd.DataFrame(results).sort_values("window_seconds").reset_index(drop=True)

def plot_power_curve(df2, time_unit="min"):
    """
    Plottet eine Power Curve aus einem DataFrame mit 'window_seconds' und 'avg_power'.
    """

    # Zeitachse skalieren
    if time_unit == "min":
        x_values = df2["window_seconds"] / 60
        x_title = "Zeitfenster (min)"
    else:
        x_values = df2["window_seconds"]
        x_title = "Zeitfenster (s)"

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=x_values,
        y=df2["avg_power"],
        mode='lines+markers',
        name='Power Curve',
        line=dict(width=3),
        marker=dict(size=6)
    ))

    fig.update_layout(
        title="Power Curve",
        xaxis_title=x_title,
        yaxis_title="Durchschnittsleistung (Watt)",
        template="plotly_white"
    )

    return fig



if __name__ == "__main__":
    df = read_my_csv("data/activities/activity.csv")
    print(df.head())

    watts300, time300 = find_best_effort(df["PowerOriginal"], 300)
    print(f"Beste Leistung in 300 Sekunden: {watts300} Watt, Startzeit: {time300}")
    df2 = generate_power_curve(series=df["PowerOriginal"], window_list=[60, 120, 300, 600, 900, 1200, 1800])
    print(df2)
    #plot_power_curve(df2)
    fig = plot_power_curve(df2)
    #fig.write_image("power_curve.png")
    fig.show()
    

    

    




   

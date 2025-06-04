import pandas as pd
from read_pandas import read_my_csv
import plotly.graph_objects as go
import numpy as np

def read_my_csv():
    # Einlesen eines Dataframes
    ## "\t" steht für das Trennzeichen in der txt-Datei (Tabulator anstelle von Beistrich)
    ## header = None: es gibt keine Überschriften in der txt-Datei
    df = pd.read_csv("data/activities/activity.csv")

    t_end= len(df)
    time = np.arange(0, t_end)
    df["time"] = time

    # Setzt die Columnnames im Dataframe
    #df.columns = ["Messwerte in mV","Zeit in ms"]
    
    # Gibt den geladen Dataframe zurück
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
    # Sicherstellen, dass der Index ein Zeitindex ist
    if not isinstance(series.index, pd.DatetimeIndex):
        raise ValueError("Index der Series muss ein DatetimeIndex sein.")

    # Gleitendes Fenster über den angegebenen Zeitraum (z. B. '300s' für 5 Minuten)
    rolling_avg = series.rolling(f"{window_seconds}s").mean()

    # Maximalwert finden
    max_avg_power = rolling_avg.max()
    best_time = rolling_avg.idxmax()

    return max_avg_power, best_time


def generate_power_curve(series: pd.Series = None, window_list: list[int] = None) -> pd.Series:
    """
    Erzeugt eine Power Curve aus einer Zeitreihe und mehreren Fenstergrößen.

    Args:
        series (pd.Series): Leistungsdaten mit Zeitstempel als Index.
        window_list (list[int]): Liste von Fenstergrößen in Sekunden.

    Returns:
        pd.Series: Power Curve.
    """
    if series is None:
        df = read_my_csv()
        series = df["PowerOriginal"]
        # Falls noch kein Zeitindex gesetzt ist:
        if not isinstance(series.index, pd.DatetimeIndex):
            series.index = pd.date_range(start='2023-01-01', periods=len(series), freq='s')

    if window_list is None:
        window_list = [5, 10, 30, 60, 120, 300, 600, 1200, 1800]

    curve = {}
    for window in window_list:
        try:
            max_avg, _ = find_best_effort(series, window)
            curve[window] = max_avg
        except Exception as e:
            print(f"Fehler bei Fenster {window} Sekunden: {e}")
            curve[window] = None

    return pd.Series(curve).sort_index()

  

def plot_power_curve(power_curve: pd.Series, time_unit: str = "min") -> go.Figure:
    """
    Erzeugt eine Plotly-Figur zur Darstellung der Power Curve.
    
    Args:
        power_curve (pd.Series): Index = Zeitfenster in Sekunden, Werte = Durchschnittsleistung (Watt).
        time_unit (str): "s" für Sekunden oder "min" für Minuten auf der x-Achse.
    
    Returns:
        go.Figure: Interaktive Plotly-Grafik.
    """
    # Zeitachse skalieren
    if time_unit == "min":
        x_values = power_curve.index / 60
        x_title = "Zeitfenster (min)"
    else:
        x_values = power_curve.index
        x_title = "Zeitfenster (s)"
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=x_values,
        y=power_curve.values,
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
    power_curve = generate_power_curve()  # <- Keine Argumente nötig
    fig = plot_power_curve(power_curve)
    fig.show()
    fig.write_image("power_curve.png")



   

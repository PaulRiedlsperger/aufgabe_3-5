import json
import pandas as pd
import plotly.express as px
from person import Person
import plotly.graph_objects as go
import plotly.io as pio


# %% Objekt-Welt 

# Klasse EKG-Data für Peakfinder, die uns ermöglicht peaks zu finden

class EKGdata:

## Konstruktor der Klasse soll die Daten einlesen
    @staticmethod
    def find_person_data_by_id(suchid):

        """ Eine Funktion der Nachname, Vorname als ein String übergeben wird
        und die die Person als Dictionary zurück gibt"""

        person_data = Person.load_person_data()
        #print(suchstring)
        if suchid == "None":
            return {}

        
        for eintrag in person_data:
            print(eintrag)
            if eintrag["id"] == suchid:
                print()
                return eintrag
        else:
            return {}
    def __init__(self, ekg_dict):
            #pass
            self.id = ekg_dict["id"]
            self.date = ekg_dict["date"]
            self.data = ekg_dict["result_link"]
            self.df = pd.read_csv(self.data, sep='\t', header=None, names=['Messwerte in mV','Zeit in ms',])
            self.df = self.df.iloc[:5000]
            
    def find_peaks(self, threshold, respacing_factor=5):
        series = self.df["Messwerte in mV"]
        #df = pd.read_csv(self.result_link, sep='\t', header=None, names=['EKG in mV','Time in ms',])   
        #df.head()
        
        # Respace the series
        series = series.iloc[::respacing_factor]
        
        # Filter the series
        series = series[series>threshold]


        peaks = []
        last = 0
        current = 0
        next = 0

        for index, row in series.items():
            last = current
            current = next
            next = row

            if last < current and current > next and current > threshold:
                peaks.append(index-respacing_factor)

        return peaks
    
    def estimate_heart_rate(self, peaks, sampling_rate=500):
        
        if len(peaks) < 2:
            return None
        
        # Berechne die Differenzen zwischen den Peaks
        rr_intervals = [j - i for i, j in zip(peaks[:-1], peaks[1:])]
        
        # Mittelwert der RR-Intervalle in Samples
        avg_rr = sum(rr_intervals) / len(rr_intervals)

        # Umrechnung in Herzfrequenz
        heart_rate = 60 * sampling_rate / avg_rr
        return round(heart_rate, 2)
        


    def plot_time_series(self):

        # Erstellte einen Line Plot, der ersten 2000 Werte mit der Zeit aus der x-Achse
        fig = px.line(self.df.head(2000), x="Zeit in ms", y="Messwerte in mV")
        # Peaks extrahieren (sofern vorhanden)
        if hasattr(self, 'peaks'):
            peak_df = self.df.iloc[self.peaks]
            fig.add_scatter(x=peak_df["Zeit in ms"], y=peak_df["Messwerte in mV"],
                            mode='markers',
                            marker=dict(color='red', size=6),
                            name="Peaks")
            

        #self.fig = fig
        return fig

if __name__ == "__main__":
    print("This is a module with some functions to read the EKG data")
    file = open("data/person_db.json")
    person_data = json.load(file)
    ekg_dict = person_data[0]["ekg_tests"][0]
    print(ekg_dict)
    ekg = EKGdata(ekg_dict)
    print(ekg.df.head())

    Person_dict= Person.find_person_data_by_id(3)
    print(Person_dict)
    
    peaks = ekg.find_peaks(340)
    print(peaks)

    heart_rate = ekg.estimate_heart_rate(peaks)
    print(f"Estimated Heart Rate: {heart_rate} bpm")

    fig= ekg.plot_time_series()
    fig.write_html("ekg_plot.html", auto_open=True)

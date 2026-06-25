import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Any

# ==========================================
# 1. KONFIGURATION
# ==========================================
MAX_TEMPS = [180, 185, 190, 180, 185, 190,] 
TOTAL_DURATION = 1000 
CSV_FILENAME = "mock_measurements.csv"
XML_FILENAME = "mock_config.xml"

# ==========================================
# 2. ZEITLICHE BERECHNUNGEN (Sekunden)
# ==========================================
t = np.linspace(0, TOTAL_DURATION, TOTAL_DURATION + 1)

t_inlet_open = 0.05 * TOTAL_DURATION
t_inlet_close = 0.10 * TOTAL_DURATION
t_heat_start = 0.15 * TOTAL_DURATION

# Neu: Zeitpunkte für die Medium-Pumpe (First Injection)
t_pump_start = 0.20 * TOTAL_DURATION
t_pump_stop = 0.25 * TOTAL_DURATION

t_peak_reached = 0.45 * TOTAL_DURATION
t_vac_start = 0.45 * TOTAL_DURATION
t_vac_deep = 0.50 * TOTAL_DURATION
t_vent1_start = 0.55 * TOTAL_DURATION
t_saddle = 0.60 * TOTAL_DURATION
t_vent2_start = 0.65 * TOTAL_DURATION
t_ambient = 0.70 * TOTAL_DURATION
t_outlet_open = 0.75 * TOTAL_DURATION
t_outlet_close = 0.80 * TOTAL_DURATION

# ==========================================
# 3. DATEN GENERIEREN
# ==========================================
start_time = datetime(2024, 1, 1, 12, 0, 0)
read_time_strings = [(start_time + timedelta(seconds=float(sec))).strftime("%d/%m/%y %H:%M:%S:%f") for sec in t]

data_dict: dict[str, Any] = {"ReadTime": read_time_strings}
sensors_meta = []

# --- BULKHEADS & PUMPE ---
inlet_data = np.where((t >= t_inlet_open) & (t <= t_inlet_close), 1, 0)
data_dict["PrcChbInletBulkheadOpen"] = inlet_data
sensors_meta.append({"name": "PrcChbInletBulkheadOpen", "unit": "", "r": 200, "g": 200, "b": 200})

outlet_data = np.where((t >= t_outlet_open) & (t <= t_outlet_close), 1, 0)
data_dict["PrcChbOutletBulkheadOpen"] = outlet_data
sensors_meta.append({"name": "PrcChbOutletBulkheadOpen", "unit": "", "r": 180, "g": 180, "b": 180})

# NEU: Medium Pumpe (für die First Injection)
pump_data = np.where((t >= t_pump_start) & (t <= t_pump_stop), 1, 0)
data_dict["St_MediumPump"] = pump_data
sensors_meta.append({"name": "St_MediumPump", "unit": "", "r": 150, "g": 150, "b": 150})

# --- VAKUUM ---
# 1. Deine Basis-Punkte (inklusive dem Peak bei t_ambient+1)
vac_xp = [0, t_vac_start, t_vac_deep, t_vent1_start, t_saddle, t_vent2_start, t_ambient, (t_ambient+1), (t_ambient+2), TOTAL_DURATION]
vac_fp = [1000, 1000, 50, 50, 500, 500, 1000, 1150, 1000, 1000]

# 2. Lineare Interpolation (erstmal ohne Rauschen!)
vacuum_data = np.interp(t, vac_xp, vac_fp)

# 3. Die lineare Phase durch die e-Funktion ersetzen
mask = (t > t_vent1_start) & (t <= t_saddle)
t_phase = t[mask] - t_vent1_start
dauer_phase = t_saddle - t_vent1_start

p_start = 50   # Dein Wert bei t_vent1_start
p_end = 500    # Dein Wert bei t_saddle
tau = dauer_phase / 5.0 

# Überschreiben der linearen Daten mit der Kurve
vacuum_data[mask] = p_end - (p_end - p_start) * np.exp(-t_phase / tau)

# 4. Rauschen über den gesamten Verlauf (inklusive der neuen e-Kurve) legen
vacuum_data = vacuum_data + np.random.normal(0, 1.5, len(t))

# 5. Speichern
data_dict["VacuumActualV"] = np.clip(vacuum_data, 0, None)
sensors_meta.append({"name": "VacuumActualV", "unit": "mbar", "r": 50, "g": 50, "b": 255})

# --- SAUERSTOFF ---
oxy_xp = [0, t_inlet_close, t_heat_start, t_outlet_open, t_outlet_close, TOTAL_DURATION]
oxy_fp = [21000, 21000, 100, 100, 21000, 21000]
oxy_data = np.interp(t, oxy_xp, oxy_fp) + np.random.normal(0, 20, len(t))
data_dict["O2Analyse2|Actual"] = np.clip(oxy_data, 0, None)
sensors_meta.append({"name": "O2Analyse2|Actual", "unit": "ppm", "r": 100, "g": 250, "b": 100})

# --- TEMPERATUR-KANÄLE ---
for i, max_temp in enumerate(MAX_TEMPS):
    ch_name = f"TempMeasureCh{i+1}SS"
    temp_xp = [0, t_heat_start, t_peak_reached, t_vent2_start, t_ambient, TOTAL_DURATION]
    temp_fp = [25.0, 30.0, max_temp, max_temp - 15, 60.0, 40.0]
    temp_data = np.interp(t, temp_xp, temp_fp) + np.random.normal(0, 0.4, len(t))
    data_dict[ch_name] = temp_data
    sensors_meta.append({"name": ch_name, "unit": "°C", "r": 255, "g": 50 + (i*30), "b": 50})

# ==========================================
# 4. CSV EXPORTIEREN
# ==========================================
df = pd.DataFrame(data_dict)
df.to_csv(CSV_FILENAME, sep=";", index=False, float_format="%.2f")
print(f"CSV-Datei erfolgreich erstellt: {CSV_FILENAME}")

# ==========================================
# 5. XML EXPORTIEREN
# ==========================================
xml_lines = [
    '<?xml version="1.0" encoding="utf-8"?>',
    '<MeasurementConfiguration xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema">',
    '  <EnvelopeDataPointsTemp/>',
    '  <SelectedDataPoints>'
]

start_id = 14480
start_line = 2345

for i, meta in enumerate(sensors_meta):
    r, g, b = meta["r"], meta["g"], meta["b"]
    sc_r, sc_g, sc_b = r / 255.0, g / 255.0, b / 255.0

    xml_lines.append('    <DataPointConfiguration>')
    xml_lines.append(f'      <Id>{start_id + i}</Id>')
    xml_lines.append(f'      <Line>{start_line + i}</Line>')
    xml_lines.append('      <Field>0</Field>')
    xml_lines.append(f'      <Name>{meta["name"]}</Name>')
    xml_lines.append(f'      <DisplayName>{meta["name"]}</DisplayName>')
    xml_lines.append(f'      <Unit>{meta["unit"]}</Unit>')
    xml_lines.append('      <Color>')
    xml_lines.append('        <A>255</A>')
    xml_lines.append(f'        <R>{r}</R>')
    xml_lines.append(f'        <G>{g}</G>')
    xml_lines.append(f'        <B>{b}</B>')
    xml_lines.append('        <ScA>1</ScA>')
    xml_lines.append(f'        <ScR>{sc_r:.9f}</ScR>')
    xml_lines.append(f'        <ScG>{sc_g:.9f}</ScG>')
    xml_lines.append(f'        <ScB>{sc_b:.9f}</ScB>')
    xml_lines.append('      </Color>')
    xml_lines.append('      <Type xsi:type="xsd:double">-1.7976931348623157E+308</Type>')
    xml_lines.append('      <LowLow>0</LowLow>')
    xml_lines.append('      <Low>0</Low>')
    xml_lines.append('      <High>0</High>')
    xml_lines.append('      <HighHigh>0</HighHigh>')
    xml_lines.append('      <Target>0</Target>')
    xml_lines.append('      <TargetTime>0</TargetTime>')
    xml_lines.append('      <IsEnvelope>false</IsEnvelope>')
    xml_lines.append('      <EnvelopeNo>-1</EnvelopeNo>')
    xml_lines.append('      <IsEnvelopeBorder>false</IsEnvelopeBorder>')
    xml_lines.append('      <EnvelopeBorderId1>0</EnvelopeBorderId1>')
    xml_lines.append('      <EnvelopeBorderId2>0</EnvelopeBorderId2>')
    xml_lines.append('    </DataPointConfiguration>')

xml_lines.append('  </SelectedDataPoints>')
xml_lines.append('</MeasurementConfiguration>')

with open(XML_FILENAME, "w", encoding="utf-8") as f:
    f.write("\n".join(xml_lines))

print(f"XML-Datei erfolgreich erstellt: {XML_FILENAME}")

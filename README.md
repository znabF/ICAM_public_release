# Synthetic Physiologically Plausible EMG and PPG Signal Modeling
Research contribution made from ICAM (2026). Open source for all researchers in biomedical fields to use where there is lack of real EMG and PPG data collected. 

## Files

| File | Description |
|------|-------------|
| `emg/emg_generator.py` & `emg/muscle_specific.py` | Generalized EMG generator with muscle-specific MUAP morphology |
| `ppg/ppg_generator.py` | Baseline PPG generator with physiological HRV and pulse morphology |
---

## EMG Generator

### Quick Start

```python
from emgGenerator import generate_emg_signal
from muscleProfile import MUSCLE_PROFILES

# Generate 30 seconds of diaphragm EMG at 15 breaths/min
t, emg = generate_emg_signal(duration=30, fs=1000, muscle="diaphragm", contraction_rate=15)

# Generate biceps EMG during tonic (sustained) contraction
t, emg = generate_emg_signal(duration=20, fs=1000, muscle="biceps_brachii", contraction_pattern="tonic")
```

### Available Muscles

All MUAP durations are from Buchthal & Rosenfalck (1955), age 20-29. Firing rates are from De Luca & Hostage (2010) and Rubin & Lamb (2023).

| Key | Muscle | MUAP Duration (ms) |
|-----|--------|--------------------|
| `deltoid` | Deltoid | 11.4 |
| `biceps_brachii` | Biceps Brachii | 9.2 |
| `triceps` | Triceps | 10.4 |
| `thenar` | Thenar Muscles | 10.2 |
| `first_dorsal_interosseous` | First Dorsal Interosseous | 9.0 |
| `abductor_digiti_minimi` | Abductor Digiti Minimi | 11.9 |
| `tibialis_anterior` | Tibialis Anterior | 11.5 |
| `vastus_lateralis` | Vastus Lateralis | 10.3 |
| `gastrocnemius` | Gastrocnemius | 9.2 |
| `extensor_digitorum_brevis` | Extensor Digitorum Brevis | 9.1 |
| `diaphragm` | Diaphragm | 12.0 |
| `facial` | Facial (orbicularis oris / frontalis) | 5.3 |

### Custom Muscle Profiles

```python
from muscleProfile import MuscleProfile
from emgGenerator import generate_emg_signal

custom = MuscleProfile(
    name="My Custom Muscle",
    muap_duration_ms=10.0,
    muap_duration_range_ms=(8.0, 12.0),
    firing_rate_range=(8.0, 25.0),
    burst_duration_range=(0.3, 1.0),
    spectral_band=(20.0, 400.0),
)

t, emg = generate_emg_signal(duration=20, fs=1000, muscle=custom, contraction_rate=12)
```

### Contraction Patterns

- `"phasic"` — rhythmic bursts (breathing, walking, repetitive tasks)
- `"tonic"` — sustained contraction (postural, isometric holds)

### Batch Generation with Random Parameters

```python
from emg_model import sample_emg_params, generate_emg_signal

params = sample_emg_params(muscle="tibialis_anterior", seed=42)
t, emg = generate_emg_signal(duration=30, fs=1000, **params)
```

---

## PPG Generator

### Quick Start

```python
from ppg_generator import generate_ppg_signal

# Generate 60 seconds of resting PPG at 72 bpm
t, ppg = generate_ppg_signal(duration=60, fs=100, heart_rate=72)
```

### Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `duration` | 60 | Signal length in seconds |
| `fs` | 100 | Sampling frequency in Hz |
| `heart_rate` | 72 | Mean heart rate in bpm (60-100 normal) |
| `baseline_amplitude` | 1.0 | Pulse amplitude (arbitrary units) |
| `amplitude_variability` | 0.05 | Beat-to-beat amplitude variability (0-1) |
| `noise_level` | 0.02 | Additive Gaussian noise level |
| `resp_freq` | None | Respiratory freq in Hz (None = random 0.15-0.30) |

### Physiological Features Included

- **OU-like IBI jitter** — realistic heart rate variability matching SDNN/RMSSD norms
- **Respiratory sinus arrhythmia** — 2% IBI modulation at respiratory frequency
- **Dicrotic notch** — aortic valve closure marker at ~1/3 heart period
- **Diastolic peak** — secondary wave reflection from peripheral vasculature
- **Respiratory amplitude modulation** — 2% PPG amplitude coupling with breathing
- **Baseline wander** — slow thermoregulatory and vasomotor drift

### Batch Generation with Random Parameters

```python
from ppg_generator import sample_ppg_params, generate_ppg_signal

params = sample_ppg_params(seed=42)
t, ppg = generate_ppg_signal(duration=60, fs=100, **params)
```

---
## Citing
If you use these generators in your research, please cite this software and the relevant literature sources listed in the bibliography files.
This software
`` Fatima SZ. (2026) Synthetic Physiologically Plausible EMG and PPG Signal Modeling. 
GitHub.``

``bibtex@software{fatima2026biosignal,
  author       = {Fatima, Syeda Zainab},
  title        = {Synthetic Physiologically Plausible EMG and PPG Signal Modeling},
  year         = {2026},
}``

### Key literature references used

* EMG durations: Buchthal F, Rosenfalck P. (1955) Acta Psychiatr Neurol Scand. 30:125-131.
* EMG firing rates: De Luca CJ, Hostage EC. (2010) J Neurophysiol. 104(2):1034-1046.
* PPG morphology: Elgendi M. (2012) Curr Cardiol Rev. 8(1):14-25.
* HRV standards: Task Force of ESC and NASPE. (1996) Circulation. 93:1043-1065.

## Requirements

```
numpy
scipy
```

Both generators require only NumPy and SciPy (EMG uses `scipy.signal` for bandpass filtering). No other dependencies.

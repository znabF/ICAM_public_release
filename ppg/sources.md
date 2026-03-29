# PPG Model: Literature Sources and Novel Contributions

## Parameters Directly from Literature

### Pulse Morphology

| Parameter | Value | Source |
|-----------|-------|--------|
| Systolic upstroke tau1 | ~60 ms base | Elgendi 2012; consistent with fast arterial pulse rise in fingertip PPG |
| Diastolic decay tau2 | ~250 ms base | Elgendi 2012; slower venous return and peripheral resistance effects |
| Per-beat tau1 jitter | 0.9x–1.15x | Novel variability envelope around literature base value |
| Per-beat tau2 jitter | 0.9x–1.2x | Novel variability envelope around literature base value |

### Dicrotic Notch and Diastolic Peak

| Parameter | Value | Source |
|-----------|-------|--------|
| Notch delay after systolic peak | 0.18–0.32 s | Charlton et al. 2023 (VascAgeNet review): notch at ~1/3 of heart period, ~1/3 down descending wave |
| Notch depth | 7–16% of pulse amplitude | Elgendi 2012; Charlton et al. 2024 (pyPPG); morphological range in healthy adults |
| Notch Gaussian width | 20–50 ms | Novel parameterization consistent with notch sharpness in fingertip PPG |
| Diastolic peak delay after notch | 30–100 ms | Elgendi 2012: diastolic peak follows notch as secondary reflection |
| Diastolic peak amplitude | 5–14% of pulse amplitude | Elgendi 2012; Couceiro et al. 2023 decomposition studies |
| Diastolic peak Gaussian width | 30–70 ms | Novel parameterization consistent with broad diastolic component |

### Heart Rate and Inter-Beat Interval Variability

| Parameter | Value | Source |
|-----------|-------|--------|
| Normal resting heart rate | 60–100 bpm | Shaffer & Ginsberg 2017 |
| Default mean HR | 72 bpm | Standard clinical resting value |
| OU mean-reversion rate (theta) | 0.2 | Produces realistic mean-reverting IBI dynamics; OU process standard in HRV modeling (Clifford 2002) |
| OU noise intensity (sigma) | 0.03 × base_ibi | Produces SDNN ~20–50 ms, RMSSD ~20–40 ms consistent with healthy resting norms (Shaffer & Ginsberg 2017; Task Force 1996) |
| Additional per-beat jitter | N(0, 0.03 × base_ibi) | Adds measurement-like variability on top of OU dynamics |
| Minimum IBI floor | 0.35 × base_ibi | Prevents physiologically impossible heart rates |

### Respiratory Sinus Arrhythmia (RSA)

| Parameter | Value | Source |
|-----------|-------|--------|
| Respiratory frequency range | 0.15–0.30 Hz | Task Force 1996: HF band = 0.15–0.40 Hz; normal adult breathing 12–20 breaths/min |
| RSA amplitude | 2% of base IBI | Within 1–5% physiological range (Berntson et al. 1993) |
| Respiratory amplitude modulation of PPG | 2% modulation depth | Respiratory-induced changes in venous return and stroke volume |

### Noise and Drift

| Parameter | Value | Source |
|-----------|-------|--------|
| Gaussian measurement noise | 0.01–0.05 (configurable) | Standard range for fingertip PPG sensor noise |
| Low-frequency physiological drift | 0.004 amplitude, 0.04–0.12 Hz | Vasomotor / Mayer wave oscillations (~0.1 Hz); Task Force 1996 LF band |
| Baseline wander (random walk) | 0.0005 cumulative step / fs | Slow thermoregulatory and postural drift |

---

## Novel Contributions

1. **Double-exponential + Gaussian notch synthesis.** While the two-Gaussian PPG model is established (Elgendi et al. 2020), and pulse decomposition into systolic/diastolic components is standard (Couceiro et al. 2023), our specific combination of a double-exponential carrier with additive Gaussian dicrotic notch and diastolic peak is a synthesis of these approaches into a lightweight, parameterized generator. The exact parameter ranges for notch depth, delay, and width are derived from the morphological descriptions in the literature but packaged as tunable generation parameters.

2. **OU-driven IBI with coupled RSA.** The Ornstein-Uhlenbeck process for IBI modeling is established (Clifford 2002), and RSA is well-characterized (Berntson et al. 1993). Our contribution is coupling both into a single beat-timing loop where the OU correction, RSA sinusoid, and random jitter all contribute to each IBI, producing realistic HRV spectral characteristics without requiring a separate HRV simulation pipeline.

3. **`sample_ppg_params()` for batch generation.** A convenience function that samples physiologically plausible parameter combinations, letting researchers generate large synthetic datasets with natural inter-subject variability in one line.

---

## Full Bibliography

1. Elgendi M. (2012) "On the analysis of fingertip photoplethysmogram signals." *Curr Cardiol Rev.* 8(1):14-25. PMC3394104. — Defines systolic peak, dicrotic notch, diastolic peak fiducial points; describes anacrotic (systolic) and catacrotic (diastolic) phases; pulse morphology parameters.

2. Charlton PH et al. (2024) "pyPPG: a Python toolbox for comprehensive photoplethysmography signal analysis." *Physiol Meas.* 45:035002. PMC11003363. — Standardized fiducial point definitions; dicrotic notch as end-of-systole marker; recommended 0.5–12 Hz bandpass for PPG analysis.

3. Elgendi M et al. (2020) "Synthetic photoplethysmogram generation using two Gaussian functions." *Sci Rep.* 10:13883. — Two-Gaussian synthesis model: systolic and diastolic waves as separate Gaussians; circular motion for periodicity; beat-to-beat interval simulation with normal distribution.

4. Couceiro R et al. (2023) "Decomposing photoplethysmogram waveforms into systolic and diastolic waves, with application to hyperbaric environments." *Biomed Signal Process Control.* — Systolic wave as Gaussian, diastolic as lognormal; 13 morphological parameters (width, time, amplitude, area ratios).

5. Charlton PH et al. (2023) "Arterial pulse wave modeling and analysis for vascular-age studies: a review from VascAgeNet." *Am J Physiol Heart Circ Physiol.* 325:H1193-H1233. — Dicrotic notch at ~1/3 of heart period; notch visibility decreases with age and arterial stiffness; comprehensive pulse wave morphology review.

6. Task Force of ESC and NASPE. (1996) "Heart rate variability: standards of measurement, physiological interpretation and clinical use." *Circulation.* 93:1043-1065. — HRV frequency bands (VLF, LF, HF); HF band 0.15–0.40 Hz corresponds to respiratory modulation; SDNN and RMSSD definitions and norms; vagal modulation dominates resting HRV.

7. Shaffer F, Ginsberg JP. (2017) "An overview of heart rate variability metrics and norms." *Front Public Health.* 5:258. PMC5624990. — Normal resting HR 60–100 bpm; normative SDNN and RMSSD values for short-term recordings; contextual factors affecting HRV measurement.

8. Berntson GG, Cacioppo JT, Quigley KS. (1993) "Respiratory sinus arrhythmia: autonomic origins, physiological mechanisms, and psychophysiological implications." *Psychophysiology.* 30:183-196. — RSA amplitude and mechanisms; parasympathetic modulation of heart rate at respiratory frequency.

9. Clifford GD. (2002) "Signal processing methods for heart rate variability." *PhD thesis, University of Oxford.* — Ornstein-Uhlenbeck process for synthetic IBI generation; synthetic tachogram construction with LF and HF components.

10. Charlton PH et al. (2022) "Wearable photoplethysmography for cardiovascular monitoring." *Proc IEEE.* 110(3):355-381. — PPG signal quality factors; wavelength effects; motion artifact; measurement site differences (finger vs wrist).

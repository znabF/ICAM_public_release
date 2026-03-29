import numpy as np


# ---------------------------------------------------------------------------
# PPG Signal Generator
#
# Generates realistic photoplethysmogram (PPG) signals with:
#   - Double-exponential pulse morphology (fast systolic upstroke, slower
#     diastolic decay)
#   - Ornstein-Uhlenbeck-like inter-beat interval jitter for realistic HRV
#   - Respiratory sinus arrhythmia (RSA)
#   - Dicrotic notch and diastolic peak
#   - Respiratory amplitude modulation
#   - Baseline wander and low-frequency drift
#
# LITERATURE SOURCES:
#
#   Pulse morphology (double-exponential + Gaussian dicrotic notch):
#     Elgendi M. (2012) "On the analysis of fingertip photoplethysmogram
#     signals." Curr Cardiol Rev. 8(1):14-25. PMC3394104.
#     -- Defines systolic peak, dicrotic notch, diastolic peak fiducial
#        points and their physiological origins.
#
#     Charlton PH et al. (2024) "pyPPG: a Python toolbox for comprehensive
#     photoplethysmography signal analysis." Physiol Meas. 45:035002.
#     PMC11003363.
#     -- Standardized fiducial point definitions; dicrotic notch marks
#        end of systole / aortic valve closure.
#
#   Two-Gaussian PPG synthesis model:
#     Elgendi M et al. (2020) "Synthetic photoplethysmogram generation
#     using two Gaussian functions." Sci Rep. 10:13883.
#     -- Systolic wave modeled as one Gaussian, diastolic as another;
#        circular motion principle for periodicity. Beat-to-beat intervals
#        simulated with normal distribution.
#
#   Pulse wave decomposition (systolic + diastolic):
#     Couceiro R et al. (2023) "Decomposing photoplethysmogram waveforms
#     into systolic and diastolic waves." Biomed Signal Process Control.
#     -- Systolic wave as Gaussian, diastolic as lognormal; 13 morphological
#        parameters extracted.
#
#   Arterial pulse wave modeling:
#     Charlton PH et al. (2023) "Arterial pulse wave modeling and analysis
#     for vascular-age studies: a review from VascAgeNet." Am J Physiol
#     Heart Circ Physiol. 325:H1193-H1233.
#     -- Dicrotic notch at ~1/3 of heart period, ~1/3 down descending wave.
#        Notch visibility decreases with age and arterial stiffness.
#
#   Heart rate variability:
#     Task Force of ESC and NASPE. (1996) "Heart rate variability: standards
#     of measurement, physiological interpretation and clinical use."
#     Circulation. 93:1043-1065.
#     -- Standard HRV metrics; RSA in HF band (0.15-0.40 Hz); vagal
#        modulation dominates resting HRV.
#
#     Shaffer F, Ginsberg JP. (2017) "An overview of heart rate variability
#     metrics and norms." Front Public Health. 5:258. PMC5624990.
#     -- Normal resting HR 60-100 bpm; SDNN and RMSSD normative values.
#
#   Ornstein-Uhlenbeck IBI model:
#     The OU process for IBI jitter is a standard stochastic model for
#     mean-reverting physiological time series. The parameters theta
#     (mean-reversion rate) and sigma (noise intensity) used here produce
#     realistic beat-to-beat variability consistent with the HRV literature.
#     See also: Clifford GD. (2002) "Signal processing methods for heart
#     rate variability." PhD thesis, University of Oxford.
#
#   Respiratory sinus arrhythmia (RSA):
#     RSA modulates IBI at the respiratory frequency (0.15-0.40 Hz),
#     corresponding to the HF band of HRV. Amplitude of RSA is typically
#     1-5% of IBI in healthy adults at rest.
#     Berntson GG et al. (1993) "Respiratory sinus arrhythmia: autonomic
#     origins, physiological mechanisms, and psychophysiological
#     implications." Psychophysiology. 30:183-196.
# ---------------------------------------------------------------------------


# feature of ppg signals
# Each heartbeat is modeled as a double-exponential pulse (fast upstroke, slower decay)
def _double_exponential_pulse(t, t0, A, tau1, tau2):
    """
    Generate a single cardiac pulse at time t0 with amplitude A.

    The double-exponential model captures the fast systolic upstroke
    (tau1, ~60ms) and slower diastolic decay (tau2, ~250ms) observed
    in real PPG waveforms.

    Parameters tau1 and tau2 are consistent with fingertip PPG
    morphology described in Elgendi (2012) and Charlton et al. (2023).
    """
    pulse = np.zeros_like(t)
    idx = t >= t0
    pulse[idx] = A * (np.exp(-(t[idx] - t0) / tau2) - np.exp(-(t[idx] - t0) / tau1))
    return pulse


def generate_ppg_signal(
    duration=60,
    fs=100,
    heart_rate=72,
    baseline_amplitude=1.0,
    amplitude_variability=0.05,
    noise_level=0.02,
    resp_freq=None,
):
    """
    Generate a realistic baseline PPG signal.

    Produces a clean PPG with physiological beat-to-beat variability,
    respiratory sinus arrhythmia, dicrotic notch, diastolic peak,
    respiratory amplitude modulation, and baseline wander.

    With no additional modifications, can get a healthy resting PPG.
    For event-based modifications (e.g., apnea, exercise), but
    post-process the returned signal or extend this function.

    Parameters
    ----------
    duration : float
        Total signal length in seconds.
    fs : int
        Sampling frequency in Hz. 100 Hz is standard for PPG.
    heart_rate : float
        Mean heart rate in beats per minute. Normal resting range
        is 60-100 bpm (Shaffer & Ginsberg 2017).
    baseline_amplitude : float
        Baseline pulse amplitude (arbitrary units).
    amplitude_variability : float
        Fractional beat-to-beat amplitude variability (0-1).
        Typical range: 0.02-0.08.
    noise_level : float
        Additive Gaussian noise level. Typical: 0.01-0.05.
    resp_freq : float or None
        Respiratory frequency in Hz. If None, sampled uniformly
        from 0.15-0.30 Hz (~9-18 breaths/min), consistent with
        the HF band of HRV (Task Force 1996).

    Returns
    -------
    t : ndarray
        Time vector.
    ppg : ndarray
        PPG signal.
    """
    # ------ Time set up ------
    t = np.arange(0, duration, 1.0 / fs)

    # ------ Respiratory frequency ------
    # RSA occurs in the HF band (0.15-0.40 Hz) per Task Force 1996.
    # Normal adult breathing rate: 12-20 breaths/min = 0.20-0.33 Hz.
    # We use 0.15-0.30 Hz as default range.
    if resp_freq is None:
        resp_freq_global = np.random.uniform(0.15, 0.30)
    else:
        resp_freq_global = resp_freq

    # ------ Beat timing with OU-like jitter ------
    # Heartbeats are not perfectly regular; each beat is slightly shifted.
    # ibi = inter-beat interval
    # theta*(base_ibi - ibi) = tendency toward a mean heart rate
    #   (Ornstein-Uhlenbeck-like correction)
    # np.random.normal(0, sigma) = random variation (stochastic jitter)
    #
    # theta = 0.2: moderate mean-reversion rate
    # sigma = 0.03 * base_ibi: produces realistic RMSSD-scale variability
    # These values generate IBI series with SDNN ~20-50ms and RMSSD
    # ~20-40ms, consistent with healthy resting HRV norms
    # (Shaffer & Ginsberg 2017, Task Force 1996).

    base_ibi = 60.0 / max(30.0, min(140.0, heart_rate))
    beat_times = []
    bt = 0.0
    ibi = base_ibi
    theta = 0.2
    sigma = 0.03 * base_ibi

    while bt < duration:
        # OU-like IBI update
        ibi = ibi + theta * (base_ibi - ibi) + np.random.normal(0, sigma)

        # Respiratory sinus arrhythmia: ~2% IBI modulation at resp frequency
        # RSA amplitude of 1-5% IBI is physiologically normal
        # (Berntson et al. 1993)
        rsa = 0.02 * base_ibi * np.sin(2 * np.pi * bt * resp_freq_global)

        # Additional random jitter
        jitter = np.random.normal(0, 0.03 * base_ibi)

        # Ensure minimum IBI (prevent unrealistically fast beats)
        bt = bt + max(0.35 * base_ibi, ibi + rsa + jitter)
        if bt < duration:
            beat_times.append(bt)

    ppg = np.zeros_like(t)

    # ------ Pulse morphology parameters ------
    # tau1 (systolic upstroke): ~60ms base, consistent with fast arterial
    # pulse rise time in fingertip PPG (Elgendi 2012)
    # tau2 (diastolic decay): ~250ms base, consistent with slower venous
    # return and peripheral resistance effects
    tau1_base = 0.06
    tau2_base = 0.25

    # ------ Generate each heartbeat pulse ------
    for bt in beat_times:
        # Beat-to-beat amplitude variability
        amp = baseline_amplitude * (
            1 + np.random.uniform(-amplitude_variability, amplitude_variability)
        )

        # real-life effects: slight variation in pulse shape per beat
        tau1 = tau1_base * np.random.uniform(0.9, 1.15)
        tau2 = tau2_base * np.random.uniform(0.9, 1.2)
        pulse = _double_exponential_pulse(t, bt, amp, tau1, tau2)

        # Dicrotic notch: produced by aortic valve closure, marks end of
        # systole and beginning of diastole (Elgendi 2012, Charlton 2023).
        # Occurs at ~1/3 of heart period after systolic peak
        # (Charlton et al. 2023 VascAgeNet review).
        # Notch delay: 0.18-0.32s after beat onset
        # Notch depth: 7-16% of pulse amplitude
        # Notch width: 20-50ms Gaussian
        notch_delay = np.random.uniform(0.18, 0.32)
        notch_width = np.random.uniform(0.02, 0.05)
        notch_depth = np.random.uniform(0.07, 0.16) * amp
        pulse -= notch_depth * np.exp(
            -0.5 * ((t - (bt + notch_delay)) / notch_width) ** 2
        )

        # Diastolic peak: small secondary peak after the dicrotic notch,
        # caused by elastic recoil of the aorta and wave reflections
        # from the periphery (Elgendi 2012).
        # Amplitude: 5-14% of pulse amplitude
        diastolic_delay = notch_delay + np.random.uniform(0.03, 0.10)
        diastolic_width = np.random.uniform(0.03, 0.07)
        diastolic_amp = np.random.uniform(0.05, 0.14) * amp
        pulse += diastolic_amp * np.exp(
            -0.5 * ((t - (bt + diastolic_delay)) / diastolic_width) ** 2
        )

        ppg += pulse

    # ------ Respiratory amplitude modulation ------
    # a respiratory modulation factor into signal. Simulates respiratory coupling
    # basically applying a common respiratory factor w/ EMG for synchronization
    # how blood flow changes with respiration essentially basic trig
    # Amplitude: ~2% modulation depth, consistent with respiratory-induced
    # changes in venous return and stroke volume.
    resp_mod = 1.0 + 0.02 * np.sin(2 * np.pi * resp_freq_global * t)
    ppg *= resp_mod

    # ------ Noise and drift ------
    # Additive Gaussian measurement noise
    ppg += noise_level * np.random.randn(len(t))

    # Low-frequency physiological drift (vasomotor oscillations, ~0.04-0.12 Hz)
    ppg += 0.004 * np.sin(
        2 * np.pi * np.random.uniform(0.04, 0.12) * t
    )

    # Very slow baseline wander (cumulative random walk, scaled by fs)
    ppg += np.cumsum(0.0005 * np.random.randn(len(t))) / fs

    return t, ppg


# ---------------------------------------------------------------------------
# This is Optional: parameter sampling for researchers who want randomized but
# realistic PPG configurations.
# ---------------------------------------------------------------------------

def sample_ppg_params(seed=None):
    """
    Sample randomized but physiologically plausible PPG parameters.

    Heart rate range 60-100 bpm covers normal resting adults
    (Shaffer & Ginsberg 2017). Respiratory frequency 0.15-0.30 Hz
    covers normal adult breathing (Task Force 1996).

    Returns a dict that can be unpacked directly into generate_ppg_signal().
    """
    if seed is not None:
        np.random.seed(seed)

    return {
        "heart_rate": int(np.random.normal(72, 10)),
        "baseline_amplitude": np.random.uniform(0.8, 1.2),
        "amplitude_variability": np.random.uniform(0.02, 0.08),
        "noise_level": np.random.uniform(0.01, 0.05),
        "resp_freq": np.random.uniform(0.15, 0.30),
    }

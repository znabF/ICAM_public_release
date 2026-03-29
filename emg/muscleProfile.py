import numpy as np
from scipy import signal
from dataclasses import dataclass, field
from typing import Optional, Dict, Tuple
 
 
# ---------------------------------------------------------------------------
# Muscle Profile System
#
# Each muscle has distinct electrophysiological properties that shape its
# EMG signature. Rather than applying post-hoc scaling to a single fixed
# MUAP, we parameterize the MUAP morphology itself per muscle.
#
# The triphasic MUAP model (initial positive -> main negative -> late
# positive afterwave) is standard in clinical EMG. What varies across
# muscles is:
#   - Overall MUAP duration (varies by muscle and age)
#   - Firing rate ranges (small muscles: higher rates, large muscles:
#     lower rates with more recruitment)
#   - Motor unit count and innervation ratio
#   - Spectral content (superficial muscles: more high-freq content)
#
# MUAP duration values come from the Buchthal & Rosenfalck (1955) normative
# table (age group 20-29, midpoint of reported range), as reproduced in
# Preston & Shapiro, Electromyography and Neuromuscular Disorders, Table 15-1.
#
# Firing rate values come from De Luca & Hostage (2010), J Neurophysiol
# 104(2):1034-1046, Table 3 and Figures 2-3, plus Rubin & Lamb (2023),
# Clin Neurophysiol 148:93-94, and Connelly et al. (1999).
#
# Motor unit counts and innervation ratios from Feinstein et al. (1955),
# Buchthal et al. (1959), and Gath & Stalberg (1981), as compiled in
# Piasecki et al. (2016), Biogerontology 17:485-496.
#
# Define a MuscleProfile and pass it to the generator. Predefined
# profiles are provided for common muscles.
# ---------------------------------------------------------------------------
 
@dataclass
class MuscleProfile:
    """
    Electrophysiological profile for a specific muscle.
 
    Parameters
    ----------
    name : str
        Human-readable muscle name.
    muap_duration_ms : float
        Mean MUAP duration in milliseconds for a healthy adult (age 20-29).
        Source: Buchthal & Rosenfalck (1955), midpoint of reported range.
    muap_duration_range_ms : tuple of 2 floats
        (low, high) MUAP duration range in ms for age 20-29.
        Source: Buchthal & Rosenfalck (1955).
    phase_centers : tuple of 3 floats
        Relative positions (0-1) of the three MUAP phases within the
        duration window. Controls the temporal spread of the triphasic
        waveform. NOTE: these are derived from the triphasic model
        (novel parameterization, not directly from a single paper).
    phase_widths : tuple of 3 floats
        Gaussian sigma for each phase in seconds. Scaled proportionally
        to muap_duration_ms. NOTE: novel parameterization -- see docstring
        for _muap_template().
    phase_amplitudes : tuple of 3 floats
        Relative amplitudes of (initial positive, main negative, late
        positive). NOTE: novel parameterization derived from the general
        triphasic morphology described in clinical EMG literature.
    firing_rate_range : tuple of 2 floats
        (min_hz, max_hz) for motor unit firing rates during voluntary
        contraction. Sources vary per muscle (see profile comments).
    max_recruitment_threshold_pct : float
        Maximum percent MVC at which the last motor unit is recruited.
        Source: De Luca & Hostage (2010) for VL, TA, FDI.
    motor_unit_count : int or None
        Estimated number of motor units in the muscle.
        Source: Feinstein et al. (1955).
    innervation_ratio : tuple of 2 floats or None
        (low, high) estimated fibers per motor unit.
        Source: Buchthal et al. (1959), Gath & Stalberg (1981),
        Feinstein et al. (1955).
    burst_duration_range : tuple of 2 floats
        (min_s, max_s) typical burst duration in seconds.
    spectral_band : tuple of 2 floats
        (low_hz, high_hz) for the bandpass filter. Surface EMG from
        deep muscles has less high-frequency content.
    baseline_noise : float
        Background noise floor relative to burst amplitude.
    cardiac_artifact : float
        Amplitude of cardiac artifact (ECG crosstalk). Higher for
        trunk/thoracic muscles, near zero for distal limb muscles.
    drift_amplitude : float
        Low-frequency baseline drift amplitude.
    polyphasia_pct : float
        Percentage of MUAPs that are normally polyphasic (>4 phases).
        Source: Buchthal (1977), Preston & Shapiro textbook.
    recruitment_style : str
        "graded" for size-principle recruitment (most muscles), or
        "synchronous" for muscles with more synchronous firing.
    """
    name: str
    muap_duration_ms: float = 10.0
    muap_duration_range_ms: Tuple[float, float] = (8.0, 12.0)
    phase_centers: Tuple[float, float, float] = (0.25, 0.45, 0.75)
    phase_widths: Tuple[float, float, float] = (0.001, 0.0015, 0.003)
    phase_amplitudes: Tuple[float, float, float] = (0.3, 1.0, 0.2)
    firing_rate_range: Tuple[float, float] = (6.0, 30.0)
    max_recruitment_threshold_pct: float = 70.0
    motor_unit_count: Optional[int] = None
    innervation_ratio: Optional[Tuple[float, float]] = None
    burst_duration_range: Tuple[float, float] = (0.3, 1.0)
    spectral_band: Tuple[float, float] = (20.0, 450.0)
    baseline_noise: float = 0.01
    cardiac_artifact: float = 0.005
    drift_amplitude: float = 0.003
    polyphasia_pct: float = 10.0
    recruitment_style: str = "graded"
 
 
# ---------------------------------------------------------------------------
# Predefined muscle profiles -- LITERATURE SOURCES PER PARAMETER
#
# MUAP DURATION SOURCE:
#   Buchthal F, Rosenfalck P. (1955) "Action potential parameters in
#   different human muscles." Acta Psychiatr Neurol Scand. 30:125-131.
#   Values below are for age group 20-29 (midpoint of reported range).
#   Reproduced as Table 15-1 in Preston & Shapiro, Electromyography and
#   Neuromuscular Disorders, 4th ed.
#
# FIRING RATE SOURCES:
#   De Luca CJ, Hostage EC. (2010) "Relationship between firing rate and
#   recruitment threshold of motoneurons in voluntary isometric
#   contractions." J Neurophysiol. 104(2):1034-1046. [VL, FDI, TA]
#
#   Rubin DI, Lamb CJ. (2023) "Motor unit potential recruitment reference
#   values in common upper and lower extremity muscles." Clin Neurophysiol.
#   148:93-94. [upper limits of fastest firing rates at low-moderate effort]
#
#   Connelly DM et al. (1999) "Motor unit firing rates and contractile
#   properties in tibialis anterior." J Appl Physiol. 87:843-852.
#
#   Solomonow M et al. (1990) surface EMG firing rate range 10-40 Hz.
#
#   Van Boxtel A, Schomaker LRB. (1983) "Motor unit firing rate during
#   static contraction indicated by the surface EMG power spectrum."
#   IEEE Trans Biomed Eng. [facial muscle firing rates]
#
# MOTOR UNIT COUNT / INNERVATION RATIO SOURCES:
#   Feinstein B et al. (1955) "Morphologic studies of motor units in
#   normal human muscles." Acta Anat. 23:127-142.
#
#   Buchthal F, Erminio F, Rosenfalck P. (1959) "Motor unit territory in
#   different human muscles." Acta Physiol Scand. 45:72-87.
#
#   Gath I, Stalberg E. (1981) "In situ measurement of the innervation
#   ratio of motor units in human muscles." Exp Brain Res. 43:198-203.
#
#   Piasecki M et al. (2016) "Age-dependent motor unit remodelling in
#   human limb muscles." Biogerontology. 17:485-496.
#
# POLYPHASIA SOURCE:
#   Buchthal F. (1977); also Preston & Shapiro: up to 10-15% polyphasic
#   MUAPs normal in most muscles; up to 25% in deltoid and tibialis
#   anterior (also confirmed by Campbell 1999).
#
# GENERAL MUAP MORPHOLOGY (triphasic model):
#   Nandedkar SD et al. (1988) "Simulation of single muscle fiber action
#   potentials." Med Biol Eng Comput. 26:286-292.
#   Stashuk DW. (2001) "Simulation of electromyographic signals."
#   J Electromyogr Kinesiol. 11:105-120.
#   Dumitru D et al. (1999) "Determinants of motor unit action potential
#   duration." Clin Neurophysiol. 110:1876-1882.
# ---------------------------------------------------------------------------
 
MUSCLE_PROFILES: Dict[str, MuscleProfile] = {
 
    # -- Upper limb --
    "deltoid": MuscleProfile(
        name="Deltoid",
        # Buchthal 1955, age 20-29: 9.5-13.2 ms
        muap_duration_ms=11.4,
        muap_duration_range_ms=(9.5, 13.2),
        # Triphasic shape: novel parameterization scaled to duration
        phase_centers=(0.25, 0.45, 0.75),
        phase_widths=(0.0009, 0.0014, 0.0028),
        phase_amplitudes=(0.3, 1.0, 0.2),
        # Rubin & Lamb 2023: upper limit 12-15 Hz at low-moderate effort;
        # slightly higher in deltoid than other muscles.
        firing_rate_range=(6.0, 30.0),
        max_recruitment_threshold_pct=80.0,
        # Gath & Stalberg 1981: ~339 fibers per MU
        motor_unit_count=None,
        innervation_ratio=(200, 400),
        burst_duration_range=(0.3, 1.5),
        spectral_band=(20.0, 450.0),
        baseline_noise=0.008,
        cardiac_artifact=0.003,
        drift_amplitude=0.002,
        # Buchthal 1977: up to 25% polyphasia normal in deltoid
        polyphasia_pct=25.0,
        recruitment_style="graded",
    ),
 
    "biceps_brachii": MuscleProfile(
        name="Biceps Brachii",
        # Buchthal 1955, age 20-29: 7.7-10.7 ms
        muap_duration_ms=9.2,
        muap_duration_range_ms=(7.7, 10.7),
        phase_centers=(0.25, 0.45, 0.75),
        phase_widths=(0.0007, 0.0011, 0.0022),
        phase_amplitudes=(0.25, 1.0, 0.15),
        # Solomonow et al. 1990: mean firing freq 17.8-24.7 Hz
        # across contraction levels in biceps brachii.
        firing_rate_range=(6.0, 25.0),
        max_recruitment_threshold_pct=80.0,
        # Buchthal et al. 1959: 209-750 fibers per MU
        motor_unit_count=None,
        innervation_ratio=(209, 750),
        burst_duration_range=(0.3, 1.5),
        spectral_band=(20.0, 450.0),
        baseline_noise=0.008,
        cardiac_artifact=0.002,
        drift_amplitude=0.002,
        polyphasia_pct=10.0,
        recruitment_style="graded",
    ),
 
    "first_dorsal_interosseous": MuscleProfile(
        name="First Dorsal Interosseous",
        # Buchthal 1955 table does not include FDI directly. ADM (abductor
        # digiti minimi) age 20-29: 9.9-13.8 ms. Bischoff et al. (1994)
        # studied FDI with multi-MUAP and found shorter durations than
        # Buchthal for all muscles due to higher contraction levels.
        # General clinical consensus: 8-14 ms for normal MUAPs.
        # Using conservative estimate for this small hand muscle.
        muap_duration_ms=9.0,
        muap_duration_range_ms=(7.0, 11.0),
        phase_centers=(0.22, 0.42, 0.72),
        phase_widths=(0.0005, 0.0008, 0.0016),
        phase_amplitudes=(0.2, 1.0, 0.1),
        # De Luca & Hostage 2010: FDI fires at 47-92 pps max range,
        # sustained max ~32.7 pps at 100% MVC. Max recruitment
        # threshold ~55-67% MVC.
        firing_rate_range=(8.0, 33.0),
        max_recruitment_threshold_pct=55.0,
        # Feinstein et al. 1955: ~120 motor units, ~40,000 fibers
        # Innervation ratio ~340 (Feinstein 1955)
        motor_unit_count=120,
        innervation_ratio=(200, 500),
        burst_duration_range=(0.2, 1.0),
        spectral_band=(20.0, 500.0),
        baseline_noise=0.005,
        cardiac_artifact=0.001,
        drift_amplitude=0.001,
        polyphasia_pct=10.0,
        recruitment_style="graded",
    ),
 
    # -- Lower limb --
    "tibialis_anterior": MuscleProfile(
        name="Tibialis Anterior",
        # Buchthal 1955, age 20-29: 9.6-13.3 ms
        muap_duration_ms=11.5,
        muap_duration_range_ms=(9.6, 13.3),
        phase_centers=(0.25, 0.45, 0.75),
        phase_widths=(0.0009, 0.0013, 0.0027),
        phase_amplitudes=(0.28, 1.0, 0.18),
        # De Luca & Hostage 2010: TA fires at 40-58 pps max range,
        # sustained max ~27.4 pps at 100% MVC. Max recruitment
        # threshold ~70-90% MVC.
        # Connelly et al. 1999: max 58 pps, mean 41.9 +/- 8.2 at MVC.
        firing_rate_range=(6.0, 28.0),
        max_recruitment_threshold_pct=70.0,
        # Feinstein et al. 1955: ~445 motor units
        # Innervation ratio 329-562 (Feinstein 1955, Gath & Stalberg 1981)
        motor_unit_count=445,
        innervation_ratio=(329, 562),
        burst_duration_range=(0.3, 1.2),
        spectral_band=(20.0, 450.0),
        baseline_noise=0.008,
        cardiac_artifact=0.001,
        drift_amplitude=0.002,
        # Buchthal 1977: up to 25% polyphasia normal in tib ant
        polyphasia_pct=25.0,
        recruitment_style="graded",
    ),
 
    "vastus_lateralis": MuscleProfile(
        name="Vastus Lateralis",
        # Buchthal 1955 lists "Quad" for age 20-29: 8.6-12.0 ms
        muap_duration_ms=10.3,
        muap_duration_range_ms=(8.6, 12.0),
        phase_centers=(0.25, 0.45, 0.75),
        phase_widths=(0.0008, 0.0012, 0.0024),
        phase_amplitudes=(0.3, 1.0, 0.22),
        # De Luca & Hostage 2010: VL fires at 37-50 pps max range,
        # sustained max ~26.0 pps at 100% MVC. Max recruitment
        # threshold ~85-95% MVC. Slopes of firing rate vs recruitment
        # threshold: -0.30 +/- 0.11.
        firing_rate_range=(6.0, 26.0),
        max_recruitment_threshold_pct=85.0,
        motor_unit_count=None,
        innervation_ratio=None,
        burst_duration_range=(0.3, 2.0),
        spectral_band=(20.0, 400.0),
        baseline_noise=0.01,
        cardiac_artifact=0.001,
        drift_amplitude=0.003,
        polyphasia_pct=10.0,
        recruitment_style="graded",
    ),
 
    "gastrocnemius": MuscleProfile(
        name="Gastrocnemius",
        # Buchthal 1955, age 20-29: 7.7-10.7 ms
        muap_duration_ms=9.2,
        muap_duration_range_ms=(7.7, 10.7),
        phase_centers=(0.25, 0.45, 0.75),
        phase_widths=(0.0007, 0.0011, 0.0022),
        phase_amplitudes=(0.28, 1.0, 0.18),
        # Feinstein 1955: innervation ratio ~1934 for medial gastroc
        firing_rate_range=(6.0, 22.0),
        max_recruitment_threshold_pct=80.0,
        motor_unit_count=None,
        innervation_ratio=(1000, 2000),
        burst_duration_range=(0.3, 1.5),
        spectral_band=(20.0, 400.0),
        baseline_noise=0.008,
        cardiac_artifact=0.001,
        drift_amplitude=0.002,
        polyphasia_pct=10.0,
        recruitment_style="graded",
    ),
 
    # -- Respiratory --
    "diaphragm": MuscleProfile(
        name="Diaphragm",
        # The diaphragm is NOT in the Buchthal 1955 table (it covers
        # limb and facial muscles only). Diaphragm EMG is typically
        # recorded with esophageal or surface electrodes. General
        # clinical EMG: normal MUAPs 8-14 ms. Diaphragmatic MUAPs
        # are typically in the 10-15 ms range.
        # Dumitru et al. (1999): "MUAP duration for most muscles
        # approaches 10-15 ms."
        muap_duration_ms=12.0,
        muap_duration_range_ms=(8.0, 15.0),
        phase_centers=(0.25, 0.45, 0.75),
        phase_widths=(0.001, 0.0015, 0.003),
        phase_amplitudes=(0.3, 1.0, 0.2),
        # Respiratory muscles fire at higher rates due to rhythmic
        # phasic activation during breathing.
        firing_rate_range=(15.0, 45.0),
        max_recruitment_threshold_pct=70.0,
        motor_unit_count=None,
        innervation_ratio=None,
        burst_duration_range=(0.4, 0.8),
        spectral_band=(20.0, 200.0),
        baseline_noise=0.01,
        cardiac_artifact=0.008,  # high -- close to heart
        drift_amplitude=0.003,
        polyphasia_pct=10.0,
        recruitment_style="graded",
    ),
 
    # -- Facial --
    "facial": MuscleProfile(
        name="Facial Muscles (orbicularis oris / frontalis)",
        # Buchthal 1955, age 20-29: 4.4-6.2 ms (column "Facial")
        muap_duration_ms=5.3,
        muap_duration_range_ms=(4.4, 6.2),
        phase_centers=(0.22, 0.42, 0.70),
        phase_widths=(0.0003, 0.0005, 0.001),
        phase_amplitudes=(0.15, 1.0, 0.08),
        # Small facial motor units with very low innervation ratios.
        # Feinstein 1955: 5-10 fibers/MU in extraocular/laryngeal;
        # facial muscles have similarly small motor units.
        # Van Boxtel & Schomaker 1983: facial muscles show firing
        # rate peaks in EMG power spectrum at 20-40 Hz range.
        firing_rate_range=(10.0, 40.0),
        max_recruitment_threshold_pct=50.0,
        motor_unit_count=None,
        innervation_ratio=(5, 50),
        burst_duration_range=(0.1, 0.6),
        spectral_band=(20.0, 500.0),
        baseline_noise=0.004,
        cardiac_artifact=0.001,
        drift_amplitude=0.001,
        polyphasia_pct=10.0,
        # Van Boxtel & Schomaker 1983: facial muscles can show
        # more synchronous firing patterns
        recruitment_style="synchronous",
    ),
 
    # -- Other commonly studied muscles from Buchthal table --
    "abductor_digiti_minimi": MuscleProfile(
        name="Abductor Digiti Minimi",
        # Buchthal 1955, age 20-29: 9.9-13.8 ms
        muap_duration_ms=11.9,
        muap_duration_range_ms=(9.9, 13.8),
        phase_centers=(0.25, 0.45, 0.75),
        phase_widths=(0.0009, 0.0014, 0.0028),
        phase_amplitudes=(0.25, 1.0, 0.15),
        firing_rate_range=(8.0, 30.0),
        max_recruitment_threshold_pct=60.0,
        motor_unit_count=None,
        innervation_ratio=None,
        burst_duration_range=(0.2, 1.0),
        spectral_band=(20.0, 500.0),
        baseline_noise=0.005,
        cardiac_artifact=0.001,
        drift_amplitude=0.001,
        polyphasia_pct=10.0,
        recruitment_style="graded",
    ),
 
    "extensor_digitorum_brevis": MuscleProfile(
        name="Extensor Digitorum Brevis",
        # Buchthal 1955, age 20-29: 7.6-10.6 ms
        muap_duration_ms=9.1,
        muap_duration_range_ms=(7.6, 10.6),
        phase_centers=(0.25, 0.45, 0.75),
        phase_widths=(0.0007, 0.0011, 0.0022),
        phase_amplitudes=(0.25, 1.0, 0.15),
        firing_rate_range=(8.0, 28.0),
        max_recruitment_threshold_pct=60.0,
        motor_unit_count=None,
        innervation_ratio=None,
        burst_duration_range=(0.2, 1.0),
        spectral_band=(20.0, 500.0),
        baseline_noise=0.005,
        cardiac_artifact=0.001,
        drift_amplitude=0.001,
        polyphasia_pct=10.0,
        recruitment_style="graded",
    ),
 
    "triceps": MuscleProfile(
        name="Triceps",
        # Buchthal 1955, age 20-29: 8.7-12.1 ms
        muap_duration_ms=10.4,
        muap_duration_range_ms=(8.7, 12.1),
        phase_centers=(0.25, 0.45, 0.75),
        phase_widths=(0.0008, 0.0012, 0.0024),
        phase_amplitudes=(0.28, 1.0, 0.18),
        # Rubin & Lamb 2023: fastest firing rate upper limit slightly
        # higher in triceps than in FDI, AT, VM, TFL
        firing_rate_range=(6.0, 28.0),
        max_recruitment_threshold_pct=80.0,
        motor_unit_count=None,
        innervation_ratio=None,
        burst_duration_range=(0.3, 1.5),
        spectral_band=(20.0, 450.0),
        baseline_noise=0.008,
        cardiac_artifact=0.002,
        drift_amplitude=0.002,
        polyphasia_pct=10.0,
        recruitment_style="graded",
    ),
 
    "thenar": MuscleProfile(
        name="Thenar Muscles",
        # Buchthal 1955, age 20-29: 8.5-11.9 ms
        muap_duration_ms=10.2,
        muap_duration_range_ms=(8.5, 11.9),
        phase_centers=(0.25, 0.45, 0.75),
        phase_widths=(0.0008, 0.0012, 0.0024),
        phase_amplitudes=(0.25, 1.0, 0.15),
        firing_rate_range=(8.0, 30.0),
        max_recruitment_threshold_pct=60.0,
        motor_unit_count=None,
        innervation_ratio=None,
        burst_duration_range=(0.2, 1.0),
        spectral_band=(20.0, 500.0),
        baseline_noise=0.005,
        cardiac_artifact=0.001,
        drift_amplitude=0.001,
        polyphasia_pct=10.0,
        recruitment_style="graded",
    ),
}
 

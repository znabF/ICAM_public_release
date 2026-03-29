 ---------------------------------------------------------------------------
# Muscle Profile System
#
# Each muscle has distinct electrophysiological properties that shape its
# EMG signature. Rather than applying post-hoc scaling to a single fixed
# MUAP, we parameterize the MUAP morphology itself per muscle.
#
# The triphasic MUAP model (initial positive -> main negative -> late
# positive afterwave) is standard in clinical EMG. What varies across
# muscles is:
#   - Phase durations and relative timing (driven by fiber diameter,
#     conduction velocity, and motor unit territory size)
#   - Phase amplitude ratios (driven by recording geometry and fiber
#     density)
#   - Overall MUAP duration (5-30ms depending on muscle)
#   - Firing rate ranges (small muscles: higher rates, large muscles:
#     lower rates with more recruitment)
#   - Spectral content (superficial muscles: more high-freq content)
#
# You define a MuscleProfile and pass it to the generator. Predefined
# profiles are provided for common muscles based on published normative
# EMG data.
# ---------------------------------------------------------------------------
 
@dataclass
class MuscleProfile:
    """
    Electrophysiological profile for a specific muscle.
 
    You can use one of the predefined profiles (see MUSCLE_PROFILES dict)
    or build your own for any muscle by specifying these parameters.
 
    Parameters
    ----------
    name : str
        Human-readable muscle name.
    muap_duration_ms : float
        Total MUAP duration in milliseconds. Smaller/distal muscles have
        shorter MUAPs (~5-10ms), large proximal muscles longer (~15-25ms).
    phase_centers : tuple of 3 floats
        Relative positions (0-1) of the three MUAP phases within the
        duration window. Controls the temporal spread of the triphasic
        waveform. For example, (0.2, 0.45, 0.75) places the initial
        positive early, main negative near center, late positive later.
    phase_widths : tuple of 3 floats
        Gaussian sigma for each phase in seconds. Wider phases produce
        smoother, broader MUAPs (large motor units). Narrower phases
        produce sharper, crisper MUAPs (small motor units).
    phase_amplitudes : tuple of 3 floats
        Relative amplitudes of (initial positive, main negative, late
        positive). The main negative is typically the largest component.
        Sign convention: positive values for upward deflections, the
        generator applies the negative sign to phase 2 internally.
    firing_rate_range : tuple of 2 floats
        (min_hz, max_hz) for motor unit firing rates during steady
        contraction. Small hand muscles: ~8-30 Hz. Large limb muscles:
        ~6-20 Hz. Respiratory muscles: ~15-45 Hz.
    burst_duration_range : tuple of 2 floats
        (min_s, max_s) typical burst duration in seconds. For tonic
        muscles this might be continuous; for phasic muscles it is
        shorter bursts.
    spectral_band : tuple of 2 floats
        (low_hz, high_hz) for the bandpass filter applied to the
        background interference pattern. Surface EMG from deep muscles
        has less high-frequency content.
    baseline_noise : float
        Background noise floor relative to burst amplitude.
    cardiac_artifact : float
        Amplitude of cardiac artifact (ECG crosstalk). Higher for
        trunk/thoracic muscles, near zero for distal limb muscles.
    drift_amplitude : float
        Low-frequency baseline drift amplitude.
    recruitment_style : str
        "graded" for size-principle recruitment (most muscles), or
        "synchronous" for muscles that tend to fire more synchronously
        (e.g., facial muscles in certain contractions).
    """
    name: str
    muap_duration_ms: float = 15.0
    phase_centers: Tuple[float, float, float] = (0.25, 0.45, 0.75)
    phase_widths: Tuple[float, float, float] = (0.001, 0.0015, 0.003)
    phase_amplitudes: Tuple[float, float, float] = (0.3, 1.0, 0.2)
    firing_rate_range: Tuple[float, float] = (25.0, 45.0)
    burst_duration_range: Tuple[float, float] = (0.4, 0.8)
    spectral_band: Tuple[float, float] = (20.0, 200.0)
    baseline_noise: float = 0.01
    cardiac_artifact: float = 0.005
    drift_amplitude: float = 0.003
    recruitment_style: str = "graded"
 
 
# ---------------------------------------------------------------------------
# Predefined muscle profiles
#
# These are based on published normative EMG data. MUAP durations and
# firing rates reference:
#   - Buchthal & Schmalbruch (1980) - motor unit territory
#   - De Luca & Hostage (2010) - firing rate behavior
#   - Stashuk (2001) - MUAP simulation parameters
#   - Nandedkar et al. (1988) - MUAP morphology by muscle
# ---------------------------------------------------------------------------
 
MUSCLE_PROFILES: Dict[str, MuscleProfile] = {
 
    # -- Respiratory --
    "diaphragm": MuscleProfile(
        name="Diaphragm",
        muap_duration_ms=15.0,
        phase_centers=(0.25, 0.45, 0.75),
        phase_widths=(0.001, 0.0015, 0.003),
        phase_amplitudes=(0.3, 1.0, 0.2),
        firing_rate_range=(15.0, 45.0),
        burst_duration_range=(0.4, 0.8),
        spectral_band=(20.0, 200.0),
        baseline_noise=0.01,
        cardiac_artifact=0.008,  # high - close to heart
        drift_amplitude=0.003,
        recruitment_style="graded",
    ),
 
    # -- Upper limb --
    "biceps_brachii": MuscleProfile(
        name="Biceps Brachii",
        muap_duration_ms=12.0,
        phase_centers=(0.22, 0.42, 0.72),
        phase_widths=(0.0008, 0.0012, 0.0025),
        phase_amplitudes=(0.25, 1.0, 0.15),
        firing_rate_range=(8.0, 25.0),
        burst_duration_range=(0.3, 1.5),
        spectral_band=(20.0, 450.0),
        baseline_noise=0.008,
        cardiac_artifact=0.002,
        drift_amplitude=0.002,
        recruitment_style="graded",
    ),
 
    "first_dorsal_interosseous": MuscleProfile(
        name="First Dorsal Interosseous",
        muap_duration_ms=8.0,
        phase_centers=(0.20, 0.40, 0.70),
        phase_widths=(0.0005, 0.0008, 0.0015),
        phase_amplitudes=(0.2, 1.0, 0.1),
        # small hand muscles fire faster with fewer motor units
        firing_rate_range=(10.0, 35.0),
        burst_duration_range=(0.2, 1.0),
        spectral_band=(20.0, 500.0),
        baseline_noise=0.005,
        cardiac_artifact=0.001,
        drift_amplitude=0.001,
        recruitment_style="graded",
    ),
 
    # -- Lower limb --
    "tibialis_anterior": MuscleProfile(
        name="Tibialis Anterior",
        muap_duration_ms=14.0,
        phase_centers=(0.23, 0.43, 0.73),
        phase_widths=(0.0009, 0.0013, 0.0028),
        phase_amplitudes=(0.28, 1.0, 0.18),
        firing_rate_range=(6.0, 20.0),
        burst_duration_range=(0.3, 1.2),
        spectral_band=(20.0, 400.0),
        baseline_noise=0.008,
        cardiac_artifact=0.001,
        drift_amplitude=0.002,
        recruitment_style="graded",
    ),
 
    "vastus_lateralis": MuscleProfile(
        name="Vastus Lateralis",
        muap_duration_ms=18.0,
        phase_centers=(0.22, 0.44, 0.74),
        phase_widths=(0.0012, 0.0018, 0.0035),
        phase_amplitudes=(0.3, 1.0, 0.22),
        # large motor units, lower firing rates, more recruitment-based
        firing_rate_range=(6.0, 18.0),
        burst_duration_range=(0.3, 2.0),
        spectral_band=(20.0, 350.0),
        baseline_noise=0.01,
        cardiac_artifact=0.001,
        drift_amplitude=0.003,
        recruitment_style="graded",
    ),
 
    # -- Trunk --
    "erector_spinae": MuscleProfile(
        name="Erector Spinae",
        muap_duration_ms=16.0,
        phase_centers=(0.24, 0.44, 0.74),
        phase_widths=(0.001, 0.0015, 0.003),
        phase_amplitudes=(0.28, 1.0, 0.2),
        firing_rate_range=(8.0, 22.0),
        # tonic postural muscle - longer sustained activity
        burst_duration_range=(0.5, 3.0),
        spectral_band=(20.0, 300.0),
        baseline_noise=0.01,
        cardiac_artifact=0.004,
        drift_amplitude=0.004,
        recruitment_style="graded",
    ),
 
    # -- Facial --
    "orbicularis_oris": MuscleProfile(
        name="Orbicularis Oris",
        muap_duration_ms=6.0,
        phase_centers=(0.20, 0.40, 0.68),
        phase_widths=(0.0004, 0.0006, 0.0012),
        phase_amplitudes=(0.15, 1.0, 0.08),
        # small facial motor units, high innervation ratio
        firing_rate_range=(15.0, 40.0),
        burst_duration_range=(0.1, 0.6),
        spectral_band=(20.0, 500.0),
        baseline_noise=0.004,
        cardiac_artifact=0.001,
        drift_amplitude=0.001,
        # facial muscles can show more synchronous firing patterns
        recruitment_style="synchronous",
    ),
}
 

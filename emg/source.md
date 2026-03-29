# EMG Model: Literature Sources and Novel Contributions

## Parameters Directly from Literature

### MUAP Duration (per muscle, age 20-29, midpoint of reported range)

| Muscle | Duration (ms) | Range (ms) | Source |
|--------|--------------|------------|--------|
| Deltoid | 11.4 | 9.5–13.2 | Buchthal & Rosenfalck 1955 |
| Biceps Brachii | 9.2 | 7.7–10.7 | Buchthal & Rosenfalck 1955 |
| Triceps | 10.4 | 8.7–12.1 | Buchthal & Rosenfalck 1955 |
| Thenar | 10.2 | 8.5–11.9 | Buchthal & Rosenfalck 1955 |
| ADM | 11.9 | 9.9–13.8 | Buchthal & Rosenfalck 1955 |
| Quadriceps/VL | 10.3 | 8.6–12.0 | Buchthal & Rosenfalck 1955 |
| Gastrocnemius | 9.2 | 7.7–10.7 | Buchthal & Rosenfalck 1955 |
| Tibialis Anterior | 11.5 | 9.6–13.3 | Buchthal & Rosenfalck 1955 |
| EDB | 9.1 | 7.6–10.6 | Buchthal & Rosenfalck 1955 |
| Facial | 5.3 | 4.4–6.2 | Buchthal & Rosenfalck 1955 |
| FDI | 9.0 | 7.0–11.0 | Estimated from Bischoff et al. 1994 (shorter than Buchthal ADM values) |
| Diaphragm | 12.0 | 8.0–15.0 | Dumitru et al. 1999 general range; not in Buchthal table |

### Firing Rates

| Muscle | Range (Hz) | Max sustained at MVC | Source |
|--------|-----------|---------------------|--------|
| VL | 6–26 | ~26 pps | De Luca & Hostage 2010 |
| TA | 6–28 | ~27.4 pps | De Luca & Hostage 2010; Connelly et al. 1999 |
| FDI | 8–33 | ~32.7 pps | De Luca & Hostage 2010 |
| Biceps | 6–25 | 17.8–24.7 Hz | Solomonow et al. 1990 |
| Facial | 10–40 | — | Van Boxtel & Schomaker 1983 |
| All muscles (low-mod effort) | upper limit 12–15 Hz | — | Rubin & Lamb 2023 |

### Motor Unit Counts / Innervation Ratios

| Muscle | MU count | Innervation ratio | Source |
|--------|---------|------------------|--------|
| FDI | ~120 | ~340 | Feinstein et al. 1955 |
| Tibialis Anterior | ~445 | 329–562 | Feinstein 1955; Gath & Stalberg 1981 |
| Biceps Brachii | — | 209–750 | Buchthal et al. 1959; Gath & Stalberg 1981 |
| Deltoid | — | ~339 | Gath & Stalberg 1981 |
| Gastrocnemius | — | ~1934 | Feinstein et al. 1955 |

### Recruitment Physiology

Henneman 1957 (size principle), De Luca & Erim 1994 ("onion skin"), De Luca & Hostage 2010 (operating point model with Eq. 4 parameters A, B, C, D, E per muscle).

### Polyphasia

Buchthal 1977, confirmed in Preston & Shapiro: up to 25% in deltoid and tibialis anterior, 5–15% in most other muscles.

---

## Novel Contributions

1. **Per-muscle MUAP morphology parameterization.** The triphasic Gaussian model (positive-negative-positive) is standard (Stashuk 2001, Nandedkar et al. 1988). What is new is systematically parameterizing the `phase_centers`, `phase_widths`, and `phase_amplitudes` per muscle, scaled proportionally to the Buchthal MUAP duration. No paper provides these Gaussian parameters directly — they are our synthesis of the duration data into a generative model.

2. **The `MuscleProfile` dataclass system.** Packaging MUAP duration, firing rates, innervation ratios, spectral band, and recruitment style into a single per-muscle profile that drives the entire signal generation pipeline. This lets researchers swap muscles with one argument change.

3. **The recruitment model coupling.** Connecting De Luca's onion-skin/operating-point findings to the burst generation via `_recruit_firing_rate()`, where contraction level modulates both firing rate and active motor unit fraction differently for "graded" vs "synchronous" muscles.

---

## Full Bibliography

1. Buchthal F, Rosenfalck P. (1955) "Action potential parameters in different human muscles." *Acta Psychiatr Neurol Scand.* 30(1-2):125-131. — MUAP duration normative table, all muscles except FDI and diaphragm.

2. Buchthal F, Guld C, Rosenfalck P. (1954) "Action potential parameters in normal human muscle and their dependence on physical variables." *Acta Physiol Scand.* 32:200-218. — MUAP amplitude variability within muscles.

3. Buchthal F, Erminio F, Rosenfalck P. (1959) "Motor unit territory in different human muscles." *Acta Physiol Scand.* 45:72-87. — Innervation ratios for biceps brachii (209-750).

4. Bischoff C, Stalberg E, Falck B, Eeg-Olofsson KE. (1994) "Reference values of motor unit action potentials obtained with multi-MUAP analysis." *Muscle & Nerve.* 17(8):842-851. — Modern MUAP reference values for deltoid, biceps, FDI, vastus lateralis, tibialis anterior. Reported shorter durations than Buchthal due to higher contraction levels.

5. De Luca CJ, Hostage EC. (2010) "Relationship between firing rate and recruitment threshold of motoneurons in voluntary isometric contractions." *J Neurophysiol.* 104(2):1034-1046. — Firing rates and recruitment thresholds for VL, FDI, TA. Sustained max firing rates: VL ~26, TA ~27.4, FDI ~32.7 pps. Max recruitment thresholds: VL 85-95%, TA 70-90%, FDI 55-67% MVC. Operating point model Eq. 4 with parameters A, B, C, D, E per muscle.

6. Rubin DI, Lamb CJ. (2023) "Motor unit potential recruitment reference values in common upper and lower extremity muscles." *Clin Neurophysiol.* 148:93-94. — Upper limits of normal fastest firing rates 12-15 Hz at low-moderate contraction across FDI, triceps, deltoid, AT, VM, TFL.

7. Connelly DM, Rice CL, Roos MR, Vandervoort AA. (1999) "Motor unit firing rates and contractile properties in tibialis anterior of young and old men." *J Appl Physiol.* 87:843-852. — TA max firing rate 58 pps, mean 41.9 +/- 8.2 pps at MVC.

8. Feinstein B, Lindegard B, Nyman E, Wohlfart G. (1955) "Morphologic studies of motor units in normal human muscles." *Acta Anat.* 23:127-142. — Motor unit counts: FDI ~120, TA ~445. Innervation ratios: FDI ~340, TA 329-562, medial gastroc ~1934.

9. Gath I, Stalberg E. (1981) "In situ measurement of the innervation ratio of motor units in human muscles." *Exp Brain Res.* 43:198-203. — Innervation ratios: biceps 209, TA 329, deltoid 239.

10. Piasecki M et al. (2016) "Age-dependent motor unit remodelling in human limb muscles." *Biogerontology.* 17:485-496. — Compilation of motor unit count and innervation ratio data across studies.

11. Henneman E. (1957) "Relation between size of neurons and their susceptibility to discharge." *Science.* 126:1345-1347. — Size principle.

12. De Luca CJ, Erim Z. (1994) "Common drive of motor units in regulation of muscle force." *Trends Neurosci.* 17:299-305. — Onion skin property.

13. Van Boxtel A, Schomaker LRB. (1983) "Motor unit firing rate during static contraction indicated by the surface EMG power spectrum." *IEEE Trans Biomed Eng.* — Facial muscle firing rate characteristics, synchronous patterns.

14. Stashuk DW. (2001) "Simulation of electromyographic signals." *J Electromyogr Kinesiol.* 11:105-120. — MUAP simulation methodology, Gaussian triphasic model.

15. Nandedkar SD et al. (1988) "Simulation of single muscle fiber action potentials." *Med Biol Eng Comput.* 26:286-292. — Single fiber AP simulation approach.

16. Dumitru D et al. (1999) "Determinants of motor unit action potential duration." *Clin Neurophysiol.* 110:1876-1882. — General MUAP duration 10-15 ms for most muscles; discrepancy between clinical and physiologic durations.

17. Solomonow M et al. (1990) — Average motor unit firing rate range 10-40 Hz across muscles.

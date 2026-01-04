import re
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import EngFormatter, LogLocator


def load_simulation_bode(filename):
    """
    Parse LTspice AC analysis Bode data from a text export.

    Extracts frequency, magnitude (dB), and phase (degrees) from lines of the form:
        <freq> (<mag>dB,<phase>°)

    Parameters
    ----------
    filename : str
        Path to LTspice AC analysis export file.

    Returns
    -------
    freq : numpy.ndarray
        Frequency in Hz.
    mag_db : numpy.ndarray
        Magnitude in dB.
    phase_deg : numpy.ndarray
        Phase in degrees.

    Notes
    -----
    Non-matching lines are ignored. Data order is preserved.
    """
    freq = []
    mag_db = []
    phase_deg = []

    pattern = re.compile(
        r"([0-9.eE+-]+)\s+\(\s*([0-9.eE+-]+)dB\s*,\s*([0-9.eE+-]+)°\s*\)"
    )

    with open(filename, "r") as f:
        for line in f:
            match = pattern.search(line)
            if match:
                freq.append(float(match.group(1)))
                mag_db.append(float(match.group(2)))
                phase_deg.append(float(match.group(3)))

    return (
        np.array(freq),
        np.array(mag_db),
        np.array(phase_deg),
    )

def load_measurement_bode(filename):
    """
    Load Bode magnitude and phase data from a Siglent oscilloscope CSV export.

    Parses a CSV file produced by the Siglent Bode plot / frequency response
    analysis. The file header is skipped until the column header line starting
    with 'Frequency(Hz)' is found. All subsequent rows are interpreted as
    numeric data.

    Expected columns:
        Frequency(Hz), Amplitude(dB), Phase(Deg)

    Parameters
    ----------
    filename : str
        Path to the Siglent Bode plot CSV file.

    Returns
    -------
    freq : numpy.ndarray
        Frequency in Hz.
    mag_db : numpy.ndarray
        Magnitude in dB.
    phase_deg : numpy.ndarray
        Phase in degrees.

    Raises
    ------
    RuntimeError
        If the expected CSV header ('Frequency(Hz)') is not found.

    Notes
    -----
    - Non-numeric rows and malformed lines are skipped.
    - Data order is preserved as stored in the file.
    """
    freq = []
    mag_db = []
    phase_deg = []

    with open(filename, "r") as f:
        lines = f.readlines()

    # Find start of numeric data
    start_idx = None
    for i, line in enumerate(lines):
        if line.strip().startswith("Frequency(Hz)"):
            start_idx = i + 1
            break

    if start_idx is None:
        raise RuntimeError("Could not find measurement data header")

    for line in lines[start_idx:]:
        parts = line.strip().split(",")
        if len(parts) < 3:
            continue

        try:
            freq.append(float(parts[0]))
            mag_db.append(float(parts[1]))
            phase_deg.append(float(parts[2]))
        except ValueError:
            pass

    return (
        np.array(freq),
        np.array(mag_db),
        np.array(phase_deg),
    )


def make_plot(sim_file,meas_file, title):
    f_sim, mag_sim, ph_sim = load_simulation_bode(sim_file)
    f_meas, mag_meas, ph_meas = load_measurement_bode(meas_file)

    # ------------------------------------------------------------
    # Plot
    # ------------------------------------------------------------
    fig, (ax_mag, ax_ph) = plt.subplots(2, 1, figsize=(8, 6), sharex=True )

    # Magnitude
    ax_mag.semilogx(f_sim, mag_sim, label="Simulation")
    ax_mag.semilogx(f_meas, mag_meas, label="Measurement", linestyle="--",linewidth=1.5)
    ax_mag.set_ylabel("Magnitude (dB)")
    ax_mag.grid(True, which="both")
    ax_mag.legend()

    # Phase
    ax_ph.semilogx(f_sim, ph_sim, label="Simulation")
    ax_ph.semilogx(f_meas, ph_meas, label="Measurement", linestyle="--",linewidth=1.5)
    ax_ph.set_ylabel("Phase (deg)")
    ax_ph.set_xlabel("Frequency (Hz)")
    ax_ph.grid(True, which="both")
    ax_ph.set_xlim(10, 120e6)
    ax_mag.set_title(title)
    

    for ax in (ax_mag, ax_ph):
        ax.xaxis.set_major_formatter(EngFormatter(unit="Hz"))
        ax.xaxis.set_major_locator(LogLocator(base=10.0, subs=(1.0,)))

    plt.tight_layout()
    plt.subplots_adjust(hspace=0.0)
    plt.show()





def interpolate_to(freq_src, mag_src, freq_dst):
    """
    Interpolate magnitude data onto a new frequency grid.
    Operates in linear frequency domain (OK for log-spaced data).
    """
    return np.interp(freq_dst, freq_src, mag_src)

def make_cmr_plot(
    sim_diff_file,
    meas_diff_file,
    sim_cm_file,
    meas_cm_file,
):
    f_sim_d, mag_sim_d, _ = load_simulation_bode(sim_diff_file)
    f_sim_c, mag_sim_c, _ = load_simulation_bode(sim_cm_file)

    f_meas_d, mag_meas_d, _ = load_measurement_bode(meas_diff_file)
    f_meas_c, mag_meas_c, _ = load_measurement_bode(meas_cm_file)

    mag_sim_c_i = interpolate_to(f_sim_c, mag_sim_c, f_sim_d)
    mag_meas_c_i = interpolate_to(f_meas_c, mag_meas_c, f_meas_d)


    cmrr_sim = mag_sim_d - mag_sim_c_i
    cmrr_meas = mag_meas_d - mag_meas_c_i

    fig, ax = plt.subplots(figsize=(8, 4))

    ax.semilogx(f_sim_d, cmrr_sim, label="Simulation")
    ax.semilogx(f_meas_d, cmrr_meas, "--", label="Measurement")

    ax.set_ylabel("CMRR (dB)")
    ax.set_xlabel("Frequency (Hz)")
    ax.set_xlim(10, 120e6)
    ax.grid(True, which="both")
    ax.legend()

    ax.xaxis.set_major_locator(LogLocator(base=10.0, subs=(1.0,)))
    ax.xaxis.set_major_formatter(EngFormatter(unit="Hz"))

    plt.tight_layout()
    plt.show()


textsize=10
plt.rcParams.update({
    "font.size": textsize,
    "axes.labelsize": textsize,
    "axes.titlesize": textsize,
    "legend.fontsize": textsize,
    "xtick.labelsize": textsize,
    "ytick.labelsize": textsize,
    })

make_plot(sim_file = "Simulation_DM.txt",
          meas_file = "SDS3034X_HD_Bode_transfer_DM.csv",
          title = "Current Sense Transformer - Gain"
          )

make_plot(sim_file = "Simulation_CM_extended_model.txt",
          meas_file = "SDS3034X_HD_Bode_commom_mode.csv",
          title = "Current Sense Transformer - Common Mode Suppression"
          )

make_cmr_plot(
    sim_diff_file="Simulation_DM.txt",
    meas_diff_file="SDS3034X_HD_Bode_transfer_DM.csv",
    sim_cm_file="Simulation_CM_extended_model.txt",
    meas_cm_file="SDS3034X_HD_Bode_commom_mode.csv",
)

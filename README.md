# ee-data-tools
A collection of scripts and utilities for analyzing electronics engineering simulations and measurement data.

---

## Bode

Scripts related to Bode plots (frequency response analysis).

### plot_ltspice_vs_siglent

Compare simulation and measurement data by plotting Bode diagrams.

- **Data sources**:
  - LTspice AC analysis export
  - Siglent oscilloscope Bode plot CSV (tested with SDS3034X HD)

- **Purpose**: Visualize and compare magnitude (dB) and phase (°) between simulation and measurement.

- **Contents**: Script for loading and plotting data, example files.

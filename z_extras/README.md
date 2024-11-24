# Additional Resources and Post-Processing Tools

This directory contains supplementary materials and post-processing tools used in the analysis of bursting bubbles and Worthington jets.

## Post-Processing Tools (`postProcessing/`)

### Data Extraction Tools (C)
- `getData*.c`: Core data extraction utilities for simulation outputs
- `getXheight*.c`: Tools for analyzing jet heights and characteristics
- `getbaseprop*.c`: Base property analysis tools
- `getdropstats*.c`: Droplet statistics computation
- `getFacet.c`, `getInertia.c`: Specialized analysis for facets and inertial properties
- `getCellcount.c`: Utility for cell counting

### Visualization & Analysis (Python)
- `VideoBurstingBubble*.py`: Various visualization scripts for bubble bursting phenomena
  - Includes facet analysis, two-bar representations, and viscous dissipation studies
- `out_*.py`: Data output and plotting utilities for different physical properties
  - Handles jet heights, base properties, inertia, velocity, and volume over time

### Jupyter Notebooks
- `testPlot.ipynb`: Interactive visualization and analysis notebook

### Utilities
- `convert.py`: File format conversion utility

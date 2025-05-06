# Viscoelastic Worthington Jets & Droplets Produced by Bursting Bubbles

[![DOI](https://zenodo.org/badge/893135483.svg)](https://doi.org/10.5281/zenodo.14349207)
[![Blog](https://img.shields.io/badge/Blog-Coming%20Soon-yellow?style=flat-square&logo=obsidian&logoColor=white)](https://blogs.comphy-lab.org/0_ToDo-Blog-public)

This repository contains the simulation code and analysis for studying the dynamics of viscoelastic Worthington jets and droplets produced by bursting bubbles. The code uses the ElastoFlow framework to simulate bubble cavity collapse in viscoelastic media, examining how elastic modulus and relaxation time affect jet and droplet formation.

The article can be found at: 

[![JFM](https://img.shields.io/static/v1.svg?style=flat-square&label=JFM&message=OA&color=orange)](https://doi.org/10.1017/jfm.2025.237)
[![arXiv](https://img.shields.io/static/v1.svg?style=flat-square&label=arXiv&message=2408.05089&color=green)](https://arxiv.org/abs/2408.05089)


## Overview

The project investigates how viscoelasticity influences bubble bursting dynamics by exploring the three-dimensional phase space of solvent Ohnesorge number, elastocapillary number, and Deborah number using volume of fluid-based finite volume simulations. The results demonstrate that polymer addition significantly influences the overall dynamics through the interplay of viscous and elastic effects.

## Installation and Setup

To ensure you have the necessary tools and a fresh Basilisk installation, use the provided script:

```bash
./reset_install_requirements.sh
```

### Function
This script checks for Basilisk installation and compiles it if not present.

### OS Compatibility
Designed for macOS. If you encounter issues on Linux, consider opening a GitHub issue.

### Dependencies
- Basilisk C is fetched and built automatically.
- Xcode Command Line Tools (macOS) or equivalent compiler toolchain (Linux) are required.

### Environment Setup
After running the script, a `.project_config` file is created, setting `BASILISK` and `PATH` automatically.

If you have previously installed Basilisk or changed dependencies, re-run the script with `--hard`:

```bash
./reset_install_requirements.sh --hard
```

## Running the Code

### Recommended Method: Using Makefile

The easiest way to compile and run the code is using the Makefile approach:

1. Navigate to the `testCases` directory:
```bash
cd testCases
```

2. Compile and run using make:
```bash
CFLAGS=-DDISPLAY=-1 make burstingBubbleVE.tst
```

### Alternative Method: Direct Compilation

You can compile the code directly using `qcc` in two ways:

1. Using include paths (recommended):
```bash
qcc -O2 -Wall -disable-dimensions -I$(PWD)/src-local -I$(PWD)/../src-local burstingBubbleVE.c -o burstingBubbleVE -lm
```

2. Without include paths:
```bash
qcc -O2 -Wall -disable-dimensions burstingBubbleVE.c -o burstingBubbleVE -lm
```
**Note**: If using method 2, you must first manually copy the `src-local` folder to your running directory.

### Local Execution

MacOS:

```bash
# First source the configuration
source .project_config

# Compile using include paths (recommended)
qcc -O2 -Wall -disable-dimensions -I$(PWD)/src-local -I$(PWD)/../src-local burstingBubbleVE.c -o burstingBubbleVE -lm

# Or compile without include paths (requires manually copying src-local folder)
qcc -O2 -Wall -disable-dimensions burstingBubbleVE.c -o burstingBubbleVE -lm

# Run the executable, only supports serial execution
./burstingBubbleVE
```

Linux:

```bash
# First source the configuration
source .project_config

# Compile using include paths (recommended)
qcc -O2 -Wall -disable-dimensions -fopenmp -I$(PWD)/src-local -I$(PWD)/../src-local burstingBubbleVE.c -o burstingBubbleVE -lm

# Or compile without include paths (requires manually copying src-local folder)
qcc -O2 -Wall -disable-dimensions -fopenmp burstingBubbleVE.c -o burstingBubbleVE -lm

# Set the number of OpenMP threads
export OMP_NUM_THREADS=4

# Run the executable
./burstingBubbleVE
```

### HPC Cluster Execution (e.g., Snellius)

For cluster environments, it is strongly recommended to manually copy the `src-local` folder to your working directory to ensure reliable compilation across different cluster configurations:

1. First, copy the required files:
```bash
cp -r /path/to/original/src-local .
```

2. Compile the code for MPI:
```bash
CC99='mpicc -std=c99' qcc -Wall -O2 -D_MPI=1 -disable-dimensions burstingBubbleVE.c -o burstingBubbleVE -lm
```

3. Create a SLURM job script (e.g., `run_simulation.sh`):
```bash
#!/bin/bash

#SBATCH --nodes=1
#SBATCH --ntasks=32
#SBATCH --time=1:00:00
#SBATCH --partition=genoa
#SBATCH --mail-type=ALL
#SBATCH --mail-user=v.sanjay@utwente.nl

srun --mpi=pmi2 -n 32 --gres=cpu:32 --mem-per-cpu=1750mb burstingBubbleVE
```

4. Submit the job:
```bash
sbatch run_simulation.sh
```

### Additional Running Scripts

The `z_extras/running` directory contains supplementary materials and post-processing tools used in the analysis. This includes C-based data extraction utilities, Python visualization scripts, and analysis notebooks. These tools were used to process simulation outputs and generate figures for the study. For detailed documentation of these tools, see the [README](z_extras/README.md) in the `z_extras` directory.

## Reset Install Requirements Script

The `reset_install_requirements.sh` script is designed to reset the installation requirements for the project. This can be useful when you want to ensure that all dependencies are fresh and up-to-date.

### Purpose

The script re-installs all required packages as specified in the requirements file, ensuring that the project's dependencies are up-to-date and consistent.

### Usage

To run the script, use the following command in your terminal:

```bash
bash reset_install_requirements.sh
```

Make sure to have the necessary permissions to execute the script.

## Citation

If you use this code in your research, please cite:

### Paper
```bibtex
@article{dixit2024viscoelastic,
  title={Viscoelastic Worthington jets & droplets produced by bursting bubbles},
  author={Dixit, Ayush K and Oratis, Alexandros and Zinelis, Konstantinos and Lohse, Detlef and Sanjay, Vatsal},
  journal={arXiv preprint arXiv:2408.05089},
  year={2024}
}
```

### Software
```bibtex
@software{vatsal_sanjay_2024_14210635,
  author       = {Vatsal Sanjay},
  title        = {{comphy-lab/Viscoelastic3D: 🌊 v2.5: ElastoFlow - 
                   Complete 2D/3D Viscoelastic Framework}},
  month        = nov,
  year         = 2024,
  publisher    = {Zenodo},
  version      = {v2.5},
  doi          = {10.5281/zenodo.14210635},
  url          = {https://doi.org/10.5281/zenodo.14210635}
}
```

## Features

- Simulation of bubble cavity collapse in viscoelastic media
- Analysis of Worthington jet formation and droplet ejection
- Investigation of polymer effects through:
  - Elastic modulus (elastocapillary number)
  - Relaxation time (Deborah number)
  - Viscous effects (Ohnesorge number)

## Dependencies

The code utilizes:
- Basilisk C ([basilliskpopinet](http://basilisk.fr))
- Volume of Fluid (VoF) method for interface tracking
- Adaptive Mesh Refinement (AMR) with quadtree grids

## Key Results

The simulations reveal:
1. Three distinct flow regimes:
   - Jets forming droplets
   - Jets without droplet formation
   - Absence of jet formation
2. Impact of viscoelasticity on:
   - Capillary wave propagation
   - Jet elongation and retraction
   - Droplet formation and size

## Additional Resources

The `z_extras` directory contains supplementary materials and post-processing tools used in the analysis. This includes C-based data extraction utilities, Python visualization scripts, and analysis notebooks. These tools were used to process simulation outputs and generate figures for the study. For detailed documentation of these tools, see the [README](z_extras/README.md) in the `z_extras` directory.

## Authors

- Ayush K. Dixit (University of Twente), [a.k.dixit@utwente.nl](mailto:a.k.dixit@utwente.nl)
- Alexandros Oratis (University of Twente), [a.oratis@utwente.nl](mailto:a.oratis@utwente.nl)
- Konstantinos Zinelis (Imperial College London & MIT), [k.zinelis17@imperial.ac.uk](mailto:k.zinelis17@imperial.ac.uk)
- Detlef Lohse (University of Twente & Max Planck Institute), [d.lohse@utwente.nl](mailto:d.lohse@utwente.nl)
- Vatsal Sanjay (University of Twente), [vatsalsanjay@gmail.com](mailto:vatsalsanjay@gmail.com)

## License

This project is licensed under standard academic terms. Please cite the paper and software if you use this code in your research. 

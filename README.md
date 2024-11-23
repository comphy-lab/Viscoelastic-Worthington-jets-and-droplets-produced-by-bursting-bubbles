# Viscoelastic Worthington Jets & Droplets Produced by Bursting Bubbles

This repository contains the simulation code and analysis for studying the dynamics of viscoelastic Worthington jets and droplets produced by bursting bubbles. The code uses the ElastoFlow framework to simulate bubble cavity collapse in viscoelastic media, examining how elastic modulus and relaxation time affect jet and droplet formation.

## Overview

The project investigates how viscoelasticity influences bubble bursting dynamics by exploring the three-dimensional phase space of solvent Ohnesorge number, elastocapillary number, and Deborah number using volume of fluid-based finite volume simulations. The results demonstrate that polymer addition significantly influences the overall dynamics through the interplay of viscous and elastic effects.

## Running the Code

### Local Execution

To compile and run the code locally:

```bash
# Compile the code
qcc -O2 -Wall -disable-dimensions -fopenmp burstingBubbleVE_v4.c -o burstingBubbleVE_v4 -lm

# Set the number of OpenMP threads
export OMP_NUM_THREADS=4

# Run the executable
./burstingBubbleVE_v4
```

### HPC Cluster Execution (e.g., Snellius)

1. Compile the code for MPI:
```bash
CC99='mpicc -std=c99' qcc -Wall -O2 -D_MPI=1 -disable-dimensions burstingBubbleVE_v4_Snellius.c -o burstingBubbleVE_v4_Snellius -lm
```

2. Create a SLURM job script (e.g., `run_simulation.sh`):
```bash
#!/bin/bash

#SBATCH --nodes=1
#SBATCH --ntasks=32
#SBATCH --time=1:00:00
#SBATCH --partition=genoa
#SBATCH --mail-type=ALL
#SBATCH --mail-user=v.sanjay@utwente.nl

srun --mpi=pmi2 -n 32 --gres=cpu:32 --mem-per-cpu=1750mb burstingBubbleVE_v4_Snellius
```

3. Submit the job:
```bash
sbatch run_simulation.sh
```

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

## Authors

- Ayush K. Dixit (University of Twente)
- Alexandros Oratis (University of Twente)
- Konstantinos Zinelis (Imperial College London & MIT)
- Detlef Lohse (University of Twente & Max Planck Institute)
- Vatsal Sanjay (University of Twente)

## License

This project is licensed under standard academic terms. Please cite the paper and software if you use this code in your research.

## Contact

For questions or collaborations, please contact the corresponding authors:
- Ayush K. Dixit: a.k.dixit@utwente.nl
- Alexandros Oratis: a.oratis@utwente.nl
- Konstantinos Zinelis: k.zinelis17@imperial.ac.uk
- Detlef Lohse: d.lohse@utwente.nl
- Vatsal Sanjay: vatsalsanjay@gmail.com

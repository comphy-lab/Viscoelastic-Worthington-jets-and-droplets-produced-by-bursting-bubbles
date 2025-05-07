# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This repository simulates viscoelastic Worthington jets and droplets produced by bursting bubbles. It uses the ElastoFlow framework based on Basilisk C to simulate bubble cavity collapse in viscoelastic media, examining how elastic modulus and relaxation time affect jet and droplet formation. The code implements log-conformation techniques for numerical stability at high Deborah numbers, crucial for viscoelastic fluid simulations.

## Key Components

- **Basilisk**: Core CFD library providing the fundamental numerical methods (grid-adaptive solver)
- **src-local**: Custom viscoelastic solvers implementing log-conformation technique
  - `log-conform-viscoelastic-scalar-2D.h` - 2D/axi log-conformation (scalar) implementation
  - `log-conform-viscoelastic-scalar-3D.h` - 3D log-conformation (scalar) implementation
  - `log-conform-viscoelastic.h` - 2D/axi log-conformation (tensor) implementation
  - `two-phaseVE.h` - Two-phase viscoelastic extension with phase-dependent properties
  - `eigen_decomposition.h` - 3x3 symmetric eigenvalue solver
- **simulationCases**: Example simulation cases (burstingBubbleVE.c) with parameter settings
- **postProcess**: Data extraction and visualization tools for post-processing
- **z_extras**: Additional post-processing and analysis utilities for research publications

## Code Standards

### Style Guidelines

- Indentation: 2 spaces (no tabs)
- Line length: Maximum 80 characters
- Comments: Use markdown-style comments starting with `/**` for documentation
- Function documentation: Include purpose, parameters, and return values
- Variable naming: Use descriptive names in camelCase or snake_case

### Documentation

- Core implementation files (`.h`) should have comprehensive markdown comments
- Simulation case files (`.c`) should include a header with usage instructions
- Document physical parameters and their meanings thoroughly
- Use standardized units and dimensionless numbers consistently

## Common Commands

### Initial Setup

Install and configure Basilisk:

```bash
./reset_install_requirements.sh
```

For a clean reinstallation:

```bash
./reset_install_requirements.sh --hard
```

Always ensure the environment variables are set:

```bash
source .project_config
```

### Building and Running Simulations

Compile using the Makefile approach (recommended):

```bash
cd simulationCases
CFLAGS=-DDISPLAY=-1 make burstingBubbleVE.tst
```

Direct compilation on macOS:

```bash
qcc -O2 -Wall -disable-dimensions -I$(PWD)/src-local -I$(PWD)/../src-local burstingBubbleVE.c -o burstingBubbleVE -lm
```

Direct compilation on Linux with OpenMP:

```bash
qcc -O2 -Wall -disable-dimensions -fopenmp -I$(PWD)/src-local -I$(PWD)/../src-local burstingBubbleVE.c -o burstingBubbleVE -lm
```

Run the simulation locally:

```bash
./burstingBubbleVE
```

Run with parameters (maxLevel De Ec Oh Bond tmax):

```bash
./burstingBubbleVE 10 0.1 0.01 1e-2 1e-3 1e0
```

### Building for MPI (Cluster Execution)

Compile with MPI support:

```bash
CC99='mpicc -std=c99' qcc -Wall -O2 -D_MPI=1 -disable-dimensions burstingBubbleVE.c -o burstingBubbleVE -lm
```

### Post-Processing

Compile post-processing tools:

```bash
cd postProcess
qcc -O2 -Wall getData-elastic-scalar2D.c -o getData-elastic-scalar2D -lm
qcc -O2 -Wall getFacet2D.c -o getFacet2D -lm
```

Run visualization script:

```bash
cd postProcess
python VideoAxi.py --caseToProcess=../simulationCases --folderToSave=visualizations --ZMAX=4.0 --RMAX=2.0 --ZMIN=-4.0
```

## Code Architecture

### Entry Point
- `burstingBubbleVE.c` - Main simulation setup and execution
  - Sets up simulation parameters and physical domain
  - Configures adaptive mesh refinement criteria
  - Initializes two-phase viscoelastic flow simulation
  - Handles output and logging

### Physics
- `log-conform-viscoelastic-scalar-2D.h` - 2D/axi log-conformation (scalar) implementation
  - Implements viscoelastic constitutive equations in log-conformation form
  - Provides stability at high Deborah numbers
  - Uses scalar projection for axisymmetric cases
- `log-conform-viscoelastic-scalar-3D.h` - 3D log-conformation (scalar) implementation
  - Extends scalar approach to 3D simulations
  - Full 3D vector and tensor operations
- `log-conform-viscoelastic.h` - 2D/axi log-conformation (tensor) implementation
  - Complete tensor-based implementation of log-conformation equations
  - Handles full polymer stress tensor evolution
- `two-phaseVE.h` - Two-phase viscoelastic extension with phase-dependent properties
  - Extends standard Basilisk two-phase flow with viscoelasticity
  - Handles discontinuous material properties across interfaces
  - Provides smooth transition in numerical implementation
- `eigen_decomposition.h` - 3x3 symmetric eigenvalue solver
  - Fast eigenvalue/eigenvector computation for viscoelastic tensors
  - Critical for log-conformation approach stability

### Numerical Methods
- Uses finite volume method with staggered grid arrangement
- Log-conformation technique for numerical stability at high Deborah numbers
  - Preserves positive-definiteness of conformation tensor
  - Improves stability in high-extension regions
- Adaptive mesh refinement with quadtree grids
  - Dynamic refinement based on key field gradients
  - Optimizes computational resources
- Volume of Fluid (VoF) method for interface tracking
  - Sharp interface representation
  - Conservative mass transport

### Parallel Processing
- OpenMP for shared-memory parallelization
  - Multi-threaded execution on single compute nodes
  - Used for efficiency on multi-core systems
- MPI for distributed memory parallelization
  - Domain decomposition across multiple compute nodes
  - Enables large-scale HPC simulations
- Post-processing supports parallel visualization with multiprocessing
  - Parallel data extraction and visualization

## Key Parameters

### Physical Parameters
- `De`: Deborah number (ratio of relaxation time to flow time)
  - Controls polymer relaxation characteristics
  - Higher values indicate more elastic behavior
- `Ec`: Elastocapillary number (ratio of elastic to surface tension forces)
  - Measures relative strength of elastic forces
  - Influences jet stretching and droplet formation
- `Oh`: Ohnesorge number (ratio of viscous to inertial-capillary forces)
  - Controls viscous damping of surface tension
  - Affects overall flow dynamics and time scales
- `Bond`: Bond number (ratio of gravitational to surface tension forces)
  - Measures importance of gravity vs. surface tension
  - Determines initial bubble shape in equilibrium

### Numerical Parameters
- `maxLevel`: Maximum refinement level for adaptive mesh
  - Controls maximum spatial resolution
  - Higher values provide more detail but increase computational cost
- `fErr`: Error tolerance for volume fraction (1e-3)
  - Controls mesh refinement near fluid interfaces
- `KErr`: Error tolerance for curvature calculation (1e-6)
  - Ensures accurate surface tension force calculation
- `VelErr`: Error tolerance for velocity field (1e-3)
  - Determines refinement in high-velocity gradient regions
- `AErr`: Error tolerance for conformation tensor (1e-3)
  - Controls refinement in regions with polymer stress gradients

## Website Documentation

The repository includes automatic documentation generation for the GitHub Pages website:

1. Documentation is generated using `.github/scripts/build.sh`
2. The generator processes source files in `src-local`, `simulationCases`, and `postProcess`
3. CSS and JavaScript customization are located in `.github/assets/`
4. The website deploys to `https://comphy-lab.org/repositoryName` (CNAME file)
5. Do not edit HTML files directly - they're auto-generated.
6. Do not edit files in the `docs/` directory - they're auto-generated.

## Important Notes

1. Use absolute paths with include flags when compiling to avoid dependency issues
2. For cluster execution, it's recommended to manually copy the `src-local` folder to the working directory
3. The repository contains pre-calculated initial bubble shape files (Bo*.dat) needed for simulations
4. Post-processing options like colorbar ranges may need manual adjustment based on the simulation case
5. When working with high Deborah numbers, check the log file for numerical stability issues
6. For detailed performance analysis, consider using the Basilisk profiling tools
7. When modifying viscoelastic solvers, ensure positive-definiteness of conformation tensors
8. The code is published as part of research work in J. Fluid Mech. (DOI: 10.1017/jfm.2025.237)

## Troubleshooting

Common issues and solutions:
- **Compilation errors**: Check inclusion paths and ensure all required headers are available
- **Energy blowup**: Reduce the time step (dtmax) or increase mesh resolution (maxLevel)
- **MPI errors**: Verify correct MPI configuration and check domain decomposition 
- **Memory issues**: Adjust maxLevel or increase available memory allocation
- **Visualization errors**: Ensure output files exist and check parameter ranges in visualization scripts
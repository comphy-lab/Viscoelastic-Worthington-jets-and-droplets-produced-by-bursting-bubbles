# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Basilisk CFD simulations of viscoelastic bubble bursting dynamics using the log-conformation method. Investigates Worthington jet and droplet formation in viscoelastic media across the phase space of Ohnesorge, elastocapillary, and Deborah numbers.

## Build & Run Commands

### Initial Setup
```bash
./reset_install_requirements.sh          # Install Basilisk and create .project_config
./reset_install_requirements.sh --hard   # Force reinstall
source .project_config                   # Load environment (BASILISK, PATH)
```

### Compile & Run (Makefile - Recommended)
```bash
cd simulationCases
CFLAGS=-DDISPLAY=-1 make burstingBubbleVE.tst
```

### Direct Compilation
```bash
# macOS (serial only)
qcc -O2 -Wall -disable-dimensions -I$PWD/src-local file.c -o executable -lm

# Linux (OpenMP)
qcc -O2 -Wall -disable-dimensions -fopenmp -I$PWD/src-local file.c -o executable -lm
export OMP_NUM_THREADS=4

# MPI (HPC clusters)
CC99='mpicc -std=c99' qcc -Wall -O2 -D_MPI=1 -disable-dimensions file.c -o executable -lm
```

### Parameter-Based Workflow (Recommended)
Uses two-stage execution: Stage 1 generates restart file (distance.h incompatible with MPI), Stage 2 runs full simulation.

```bash
# Edit default.params to set parameters, then:
./runSimulation.sh default.params           # Run both stages (default)
./runSimulation.sh --mpi 8 default.params   # Stage 1 serial, Stage 2 with MPI

# Run stages separately (for HPC workflows)
./runSimulation.sh --stage1 default.params  # Stage 1 only: generate restart
./runSimulation.sh --stage2 default.params  # Stage 2 only: full simulation

# Parameter sweep (edit sweep.params first)
./runParameterSweep.sh sweep.params         # Run all cases (Stage 1 + 2)
./runParameterSweep.sh --stage1-only        # Generate all restart files
./runParameterSweep.sh --stage2-only --mpi 8 # Run all Stage 2 simulations
./runParameterSweep.sh --dry-run            # Preview combinations
```

Case outputs are created in `simulationCases/<CaseNo>/` (4-digit, e.g., 1000/).

### Direct Execution (for quick tests)
```bash
./burstingBubbleVE MAXlevel De Ec Oh Bond tmax
# MAXlevel: AMR refinement level
# De: Deborah number (relaxation time / flow time)
# Ec: Elastocapillary number (elastic / surface tension forces)
# Oh: Ohnesorge number (viscous / inertial-capillary forces)
# Bond: Bond number (gravity / surface tension forces)
# tmax: Maximum simulation time
```

### Generate Documentation
```bash
bash .github/scripts/build.sh   # Generate HTML docs (do not deploy)
```

## Architecture

### Viscoelastic Solver Hierarchy
The `src-local/` headers implement the log-conformation method for numerical stability at high Deborah numbers:

**Viscoelastic (VE) - Oldroyd-B model:**
- **`log-conform-viscoelastic.h`**: 2D/axisymmetric tensor formulation (default)
- **`log-conform-viscoelastic-scalar-2D.h`**: 2D/axisymmetric scalar formulation (enable with `#define _SCALAR`)
- **`log-conform-viscoelastic-scalar-3D.h`**: 3D scalar formulation
- **`two-phaseVE.h`**: Two-phase VoF coupling for viscoelastic

**Elastoviscoplastic (EVP) - Saramito model:**
- **`log-conform-elastoviscoplastic.h`**: 2D/axisymmetric tensor formulation
- **`log-conform-elastoviscoplastic-scalar-2D.h`**: 2D/axisymmetric scalar formulation
- **`log-conform-elastoviscoplastic-scalar-3D.h`**: 3D scalar formulation
- **`two-phaseEVP.h`**: Two-phase VoF coupling for elastoviscoplastic

**Utilities:**
- **`eigen_decomposition.h`**: 3×3 symmetric eigenvalue solver for log-conformation

**Note:** Tensor formulations are limited to 2D/axi due to Basilisk boundary condition limitations; use scalar versions for 3D.

### Key Physical Parameters (defined in simulation `.c` files)
- `G`: Elastic modulus → polymeric stress T = G·f(A)
- `λ` (lambda): Relaxation time → conformation tensor evolution
- Conformation tensor A tracks polymer chain deformation

### Simulation Structure
Simulation cases in `simulationCases/` include headers via:
```c
#include "axi.h"                          // Axisymmetric geometry
#include "navier-stokes/centered.h"       // Momentum solver
#include "log-conform-viscoelastic.h"     // Viscoelastic constitutive model
#include "two-phaseVE.h"                  // Two-phase VoF coupling
```

## Code Style

- 2 spaces indentation, 80 char line limit
- Markdown in `/**` comments for documentation
- `snake_case` for variables, `camelCase` for functions
- Core functionality in `.h` headers, tests/simulations in `.c` files

## Key Directories

- `basilisk/src/`: Core Basilisk library (reference only, do not modify)
- `src-local/`: Custom viscoelastic solvers and parameter parsing utilities
- `simulationCases/`: Simulation source files and case outputs (numbered folders)
- `postProcess/`: Data extraction (`.c`) and visualization (`.py`) tools
- `docs/`: Auto-generated documentation (do not edit directly)

## Key Files

- `default.params`: Default simulation parameters (edit for single runs)
- `sweep.params`: Parameter sweep configuration (CASE_START/END, SWEEP_* variables)
- `runSimulation.sh`: Single case executor with two-stage model
- `runParameterSweep.sh`: Batch executor for parameter sweeps
- `runPostProcess-Ncases.sh`: Post-processing batch executor

## Post-Processing Workflow

### Compile C Helpers
```bash
# Compile data extraction utilities (run once)
qcc -O2 -Wall postProcess/getFacet.c -o postProcess/getFacet -lm
qcc -O2 -Wall postProcess/getData.c -o postProcess/getData -lm
```

### Generate Visualization Videos
```bash
# Single case
python3 postProcess/Video.py --caseToProcess simulationCases/1000

# Multiple cases with batch script
./runPostProcess-Ncases.sh 1000 1001 1002

# With custom settings
./runPostProcess-Ncases.sh --CPUs 8 --nGFS 100 1000

# Skip video encoding (only generate frames)
./runPostProcess-Ncases.sh --skip-video-encode 1000

# Adjust colorbar bounds
./runPostProcess-Ncases.sh --d2-vmin -2 --d2-vmax 3 --vel-vmin 0 --vel-vmax 2 1000
```

### Post-Processing Output
Each case generates:
- `simulationCases/<CaseNo>/Video/`: PNG frames (zero-padded timestamps)
- `simulationCases/<CaseNo>/<CaseNo>.mp4`: Encoded video

### Visualization Fields
- **Left colorbar**: log₁₀(D:D) - Strain-rate tensor magnitude
- **Right colorbar**: |u| - Velocity magnitude
- **Interface**: VOF facets (cyan lines)
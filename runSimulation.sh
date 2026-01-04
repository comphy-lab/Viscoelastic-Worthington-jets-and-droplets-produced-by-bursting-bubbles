#!/bin/bash
# runSimulation.sh - Run single viscoelastic bubble bursting simulation from root directory
# Creates case folder in simulationCases/<CaseNo>/ and runs simulation there
#
# IMPORTANT: This script uses TWO-STAGE EXECUTION because distance.h is
# incompatible with MPI. Run Stage 1 first to generate the restart file,
# then run Stage 2 for the full simulation.

set -euo pipefail  # Exit on error, unset variables, pipeline failures

# ============================================================
# Configuration
# ============================================================
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Source project configuration
if [ -f "${SCRIPT_DIR}/.project_config" ]; then
    source "${SCRIPT_DIR}/.project_config"
else
    echo "ERROR: .project_config not found" >&2
    exit 1
fi

# Source parameter parsing library
if [ -f "${SCRIPT_DIR}/src-local/parse_params.sh" ]; then
    source "${SCRIPT_DIR}/src-local/parse_params.sh"
else
    echo "ERROR: src-local/parse_params.sh not found" >&2
    exit 1
fi

# ============================================================
# Usage Information
# ============================================================
usage() {
    cat <<EOF
Usage: $0 [OPTIONS] [params_file]

Run single viscoelastic bubble bursting simulation from root directory.
Creates case folder in simulationCases/<CaseNo>/ based on parameter file.

This script uses TWO-STAGE EXECUTION:
  Stage 1: Generate restart file (distance.h incompatible with MPI)
  Stage 2: Full simulation from restart file

Stage Selection (mutually exclusive):
    (default)           Run both Stage 1 + Stage 2
    --stage1            Run Stage 1 only (generate restart file)
    --stage2            Run Stage 2 only (full simulation from restart)

Parallelization:
    --fopenmp [N]       Enable OpenMP with N threads (default: 8)
                        Stage 1: Linux only (macOS always serial)
                        Stage 2: Linux only (macOS runs serial with warning)
    --mpi [N]           Enable MPI with N cores (default: 2, Stage 2 only)

Other Options:
    -c, --compile-only  Compile but don't run simulation
    -d, --debug         Compile with debug flags (-g -DTRASH=1)
    -v, --verbose       Verbose output
    -h, --help          Show this help message

Parameter file mode (default):
    $0 default.params

If no parameter file specified, uses default.params from current directory.

Environment variables:
    QCC_FLAGS     Additional qcc compiler flags

Examples:
    # Run both stages (default)
    $0 default.params                         # Serial, Stage 1 + 2
    $0 --mpi 8 default.params                 # Stage 1 serial, Stage 2 MPI

    # Stage 1 only: Generate restart file
    $0 --stage1 default.params                # Serial
    $0 --stage1 --fopenmp default.params      # OpenMP (Linux only)

    # Stage 2 only: Full simulation (requires existing restart)
    $0 --stage2 default.params                # Serial
    $0 --stage2 --mpi 8 default.params        # MPI, 8 cores

    # Compile only (check for errors)
    $0 --compile-only default.params

For more information, see README.md
EOF
}

# ============================================================
# Parse Command Line Options
# ============================================================
COMPILE_ONLY=0
DEBUG_FLAGS=""
VERBOSE=0
STAGE=0                # Default to both stages (0 = both, 1 = stage1, 2 = stage2)
FOPENMP_ENABLED=0
FOPENMP_THREADS=8      # Default thread count
MPI_ENABLED=0
MPI_CORES=2            # Default core count
STAGE_EXPLICITLY_SET=0
QCC_FLAGS="${QCC_FLAGS:-}"

while [[ $# -gt 0 ]]; do
    case $1 in
        -c|--compile-only)
            COMPILE_ONLY=1
            shift
            ;;
        -d|--debug)
            DEBUG_FLAGS="-g -DTRASH=1"
            shift
            ;;
        --stage1)
            if [ $STAGE_EXPLICITLY_SET -eq 1 ] && [ $STAGE -ne 1 ]; then
                echo "ERROR: Cannot use both --stage1 and --stage2" >&2
                exit 1
            fi
            STAGE=1
            STAGE_EXPLICITLY_SET=1
            shift
            ;;
        --stage2)
            if [ $STAGE_EXPLICITLY_SET -eq 1 ] && [ $STAGE -ne 2 ]; then
                echo "ERROR: Cannot use both --stage1 and --stage2" >&2
                exit 1
            fi
            STAGE=2
            STAGE_EXPLICITLY_SET=1
            shift
            ;;
        --fopenmp)
            FOPENMP_ENABLED=1
            # Check if next arg is a number (optional thread count)
            if [[ "${2:-}" =~ ^[0-9]+$ ]]; then
                FOPENMP_THREADS="$2"
                shift
            fi
            shift
            ;;
        --mpi)
            MPI_ENABLED=1
            # Check if next arg is a number (optional core count)
            if [[ "${2:-}" =~ ^[0-9]+$ ]]; then
                MPI_CORES="$2"
                shift
            fi
            shift
            ;;
        -v|--verbose)
            VERBOSE=1
            shift
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        -*)
            echo "ERROR: Unknown option: $1" >&2
            usage
            exit 1
            ;;
        *)
            break
            ;;
    esac
done

# ============================================================
# Detect OS
# ============================================================
OS_TYPE=$(uname -s)

# ============================================================
# Validation
# ============================================================

# Check --mpi only valid with stage2 (not stage1-only)
if [ $MPI_ENABLED -eq 1 ] && [ $STAGE -eq 1 ]; then
    echo "ERROR: --mpi is only valid with --stage2 (Stage 1 cannot use MPI due to distance.h)" >&2
    exit 1
fi

# For both-stages mode with MPI, MPI only applies to Stage 2
if [ $MPI_ENABLED -eq 1 ] && [ $STAGE -eq 0 ]; then
    echo "Note: MPI will be used for Stage 2 only (Stage 1 runs serial)"
fi

# Check --mpi and --fopenmp are mutually exclusive
if [ $MPI_ENABLED -eq 1 ] && [ $FOPENMP_ENABLED -eq 1 ]; then
    echo "ERROR: --mpi and --fopenmp are mutually exclusive" >&2
    exit 1
fi

# Check --fopenmp on macOS
if [ "$OS_TYPE" = "Darwin" ] && [ $FOPENMP_ENABLED -eq 1 ]; then
    if [ $STAGE -eq 1 ]; then
        echo "ERROR: --fopenmp not supported on macOS for Stage 1 (always runs serial)" >&2
        exit 1
    else
        echo "WARNING: OpenMP not available on macOS, Stage 2 will run serial" >&2
        FOPENMP_ENABLED=0
    fi
fi

# Verify MPI tools if MPI is enabled
if [ $MPI_ENABLED -eq 1 ]; then
    if ! command -v mpicc &> /dev/null; then
        echo "ERROR: mpicc not found. MPI compilation requires mpicc (OpenMPI or MPICH)." >&2
        echo "       Install MPI tools or run without --mpi flag for serial execution." >&2
        exit 1
    fi
    if ! command -v mpirun &> /dev/null; then
        echo "ERROR: mpirun not found. MPI execution requires mpirun (OpenMPI or MPICH)." >&2
        echo "       Install MPI tools or run without --mpi flag for serial execution." >&2
        exit 1
    fi
fi

# ============================================================
# Determine Parameter File
# ============================================================
PARAM_FILE="${1:-default.params}"

if [ ! -f "$PARAM_FILE" ]; then
    echo "ERROR: Parameter file not found: $PARAM_FILE" >&2
    exit 1
fi

[ $VERBOSE -eq 1 ] && echo "Parameter file: $PARAM_FILE"

# ============================================================
# Parse Parameters
# ============================================================
parse_param_file "$PARAM_FILE"

CASE_NO=$(get_param "CaseNo")
De=$(get_param "De" "0.1")
Ec=$(get_param "Ec" "0.01")
Oh=$(get_param "Oh" "1e-2")
Bond=$(get_param "Bond" "1e-3")
MAXlevel=$(get_param "MAXlevel" "10")
tmax=$(get_param "tmax" "1.0")

if [ -z "$CASE_NO" ]; then
    echo "ERROR: CaseNo not found in parameter file" >&2
    exit 1
fi

# Validate CaseNo is 4 digits
if ! [[ "$CASE_NO" =~ ^[0-9]{4}$ ]] || [ "$CASE_NO" -lt 1000 ] || [ "$CASE_NO" -gt 9999 ]; then
    echo "ERROR: CaseNo must be 4-digit (1000-9999), got: $CASE_NO" >&2
    exit 1
fi

CASE_DIR="simulationCases/${CASE_NO}"

# ============================================================
# Display Configuration
# ============================================================
echo "========================================="
echo "Viscoelastic Bubble Bursting Simulation"
echo "========================================="
echo "Case Number: $CASE_NO"
echo "Case Directory: $CASE_DIR"
echo "Parameter File: $PARAM_FILE"
echo ""
echo "Physical Parameters:"
echo "  De=$De, Ec=$Ec, Oh=$Oh, Bond=$Bond"
echo "  MAXlevel=$MAXlevel, tmax=$tmax"
echo ""
if [ $STAGE -eq 0 ]; then
    echo "Stage: Both (Stage 1 + Stage 2)"
elif [ $STAGE -eq 1 ]; then
    echo "Stage: 1 only (generate restart)"
else
    echo "Stage: 2 only (full simulation)"
fi
if [ $MPI_ENABLED -eq 1 ]; then
    echo "Parallelization: MPI ($MPI_CORES cores)"
elif [ $FOPENMP_ENABLED -eq 1 ]; then
    echo "Parallelization: OpenMP ($FOPENMP_THREADS threads)"
else
    echo "Parallelization: Serial"
fi
echo ""

# ============================================================
# Create Case Directory
# ============================================================
if [ ! -d "$CASE_DIR" ]; then
    echo "Creating case directory: $CASE_DIR"
    mkdir -p "$CASE_DIR"
else
    echo "Case directory exists"
fi

# Copy parameter file to case directory for record keeping
cp "$PARAM_FILE" "$CASE_DIR/case.params"

# Change to case directory
cd "$CASE_DIR"
[ $VERBOSE -eq 1 ] && echo "Working directory: $(pwd)"

# ============================================================
# Source File Setup
# ============================================================
SRC_FILE_ORIG="../burstingBubbleVE.c"
SRC_FILE_LOCAL="burstingBubbleVE.c"
EXECUTABLE="burstingBubbleVE"

# Check if source file exists
if [ ! -f "$SRC_FILE_ORIG" ]; then
    echo "ERROR: Source file $SRC_FILE_ORIG not found" >&2
    exit 1
fi

# Copy source file to case directory
cp "$SRC_FILE_ORIG" "$SRC_FILE_LOCAL"
echo "Copied source file to case directory"

# Copy Bond-specific geometry file if exists
# Format Bond as 4 decimal places (e.g., 1e-3 -> 0.0010)
BOND_FORMATTED=$(printf "%.4f" "$Bond")
BOND_FILE="../DataFiles/Bo${BOND_FORMATTED}.dat"
if [ -f "$BOND_FILE" ]; then
    cp "$BOND_FILE" .
    echo "Copied geometry file Bo${BOND_FORMATTED}.dat"
else
    # Try alternate location (one level up from case dir)
    BOND_FILE_ALT="../Bo${BOND_FORMATTED}.dat"
    if [ -f "$BOND_FILE_ALT" ]; then
        cp "$BOND_FILE_ALT" .
        echo "Copied geometry file Bo${BOND_FORMATTED}.dat"
    else
        echo "WARNING: Geometry file Bo${BOND_FORMATTED}.dat not found" >&2
        echo "         Checked: $BOND_FILE and $BOND_FILE_ALT" >&2
        echo "         Simulation may fail during initialization" >&2
    fi
fi

# ============================================================
# Stage 1: Generate Restart File
# ============================================================
if [ $STAGE -eq 1 ] || [ $STAGE -eq 0 ]; then
    echo ""
    echo "========================================="
    echo "Stage 1: Generate Initial Condition"
    echo "========================================="

    # Compilation
    if [ $FOPENMP_ENABLED -eq 1 ]; then
        echo "Compiling with OpenMP..."
        [ $VERBOSE -eq 1 ] && echo "Compiler: qcc"
        [ $VERBOSE -eq 1 ] && echo "Include paths: -I../../src-local"
        [ $VERBOSE -eq 1 ] && echo "Flags: -O2 -Wall -disable-dimensions -fopenmp $DEBUG_FLAGS $QCC_FLAGS"

        qcc -I../../src-local \
            -O2 -Wall -disable-dimensions -fopenmp \
            $DEBUG_FLAGS $QCC_FLAGS \
            "$SRC_FILE_LOCAL" -o "$EXECUTABLE" -lm
    else
        echo "Compiling for serial execution..."
        [ $VERBOSE -eq 1 ] && echo "Compiler: qcc"
        [ $VERBOSE -eq 1 ] && echo "Include paths: -I../../src-local"
        [ $VERBOSE -eq 1 ] && echo "Flags: -O2 -Wall -disable-dimensions $DEBUG_FLAGS $QCC_FLAGS"

        qcc -I../../src-local \
            -O2 -Wall -disable-dimensions \
            $DEBUG_FLAGS $QCC_FLAGS \
            "$SRC_FILE_LOCAL" -o "$EXECUTABLE" -lm
    fi

    if [ $? -ne 0 ]; then
        echo "ERROR: Stage 1 compilation failed" >&2
        exit 1
    fi

    echo "Compilation successful: $EXECUTABLE"

    # Exit if compile-only mode
    if [ $COMPILE_ONLY -eq 1 ]; then
        echo ""
        echo "Compile-only mode: Stopping here"
        cd ../..
        exit 0
    fi

    # Execution
    echo ""
    echo "Running briefly to generate restart file..."
    if [ $FOPENMP_ENABLED -eq 1 ]; then
        echo "  OMP_NUM_THREADS=$FOPENMP_THREADS"
        export OMP_NUM_THREADS=$FOPENMP_THREADS
    else
        echo "  Running single-threaded"
    fi
    echo "  Command: ./${EXECUTABLE} $MAXlevel $De $Ec $Oh $Bond 0.01"

    ./${EXECUTABLE} $MAXlevel $De $Ec $Oh $Bond 0.01

    if [ ! -f "restart" ]; then
        echo "ERROR: Stage 1 failed - restart file was not created" >&2
        exit 1
    fi

    echo ""
    echo "========================================="
    echo "Stage 1 complete: restart file created"
    echo "Restart file location: $CASE_DIR/restart"
    if [ $STAGE -eq 1 ]; then
        echo ""
        echo "To run Stage 2:"
        echo "  $0 --stage2 $PARAM_FILE"
        echo "  $0 --stage2 --mpi $PARAM_FILE"
    fi
    echo "========================================="
fi

# ============================================================
# Stage 2: Full Simulation
# ============================================================
if [ $STAGE -eq 2 ] || [ $STAGE -eq 0 ]; then
    # Check restart file exists
    if [ ! -f "restart" ]; then
        echo "ERROR: restart file not found in $CASE_DIR" >&2
        echo "       Run Stage 1 first: $0 --stage1 $PARAM_FILE" >&2
        exit 1
    fi

    echo ""
    echo "========================================="
    echo "Stage 2: Full Simulation"
    echo "========================================="

    # Compilation
    if [ $MPI_ENABLED -eq 1 ]; then
        echo "Compiling with MPI..."

        if [ "$OS_TYPE" = "Darwin" ]; then
            # macOS
            [ $VERBOSE -eq 1 ] && echo "Compiler: CC99='mpicc -std=c99' qcc"
            [ $VERBOSE -eq 1 ] && echo "Include paths: -I../../src-local"
            [ $VERBOSE -eq 1 ] && echo "Flags: -Wall -O2 -D_MPI=1 -disable-dimensions $DEBUG_FLAGS $QCC_FLAGS"

            CC99='mpicc -std=c99' qcc -I../../src-local \
                -Wall -O2 -D_MPI=1 -disable-dimensions \
                $DEBUG_FLAGS $QCC_FLAGS \
                "$SRC_FILE_LOCAL" -o "$EXECUTABLE" -lm
        else
            # Linux
            [ $VERBOSE -eq 1 ] && echo "Compiler: CC99='mpicc -std=c99 -D_GNU_SOURCE=1' qcc"
            [ $VERBOSE -eq 1 ] && echo "Include paths: -I../../src-local"
            [ $VERBOSE -eq 1 ] && echo "Flags: -Wall -O2 -D_MPI=1 -disable-dimensions $DEBUG_FLAGS $QCC_FLAGS"

            CC99='mpicc -std=c99 -D_GNU_SOURCE=1' qcc -I../../src-local \
                -Wall -O2 -D_MPI=1 -disable-dimensions \
                $DEBUG_FLAGS $QCC_FLAGS \
                "$SRC_FILE_LOCAL" -o "$EXECUTABLE" -lm
        fi
    elif [ $FOPENMP_ENABLED -eq 1 ]; then
        echo "Compiling with OpenMP..."
        [ $VERBOSE -eq 1 ] && echo "Compiler: qcc"
        [ $VERBOSE -eq 1 ] && echo "Include paths: -I../../src-local"
        [ $VERBOSE -eq 1 ] && echo "Flags: -O2 -Wall -disable-dimensions -fopenmp $DEBUG_FLAGS $QCC_FLAGS"

        qcc -I../../src-local \
            -O2 -Wall -disable-dimensions -fopenmp \
            $DEBUG_FLAGS $QCC_FLAGS \
            "$SRC_FILE_LOCAL" -o "$EXECUTABLE" -lm
    else
        echo "Compiling for serial execution..."
        [ $VERBOSE -eq 1 ] && echo "Compiler: qcc"
        [ $VERBOSE -eq 1 ] && echo "Include paths: -I../../src-local"
        [ $VERBOSE -eq 1 ] && echo "Flags: -O2 -Wall -disable-dimensions $DEBUG_FLAGS $QCC_FLAGS"

        qcc -I../../src-local \
            -O2 -Wall -disable-dimensions \
            $DEBUG_FLAGS $QCC_FLAGS \
            "$SRC_FILE_LOCAL" -o "$EXECUTABLE" -lm
    fi

    if [ $? -ne 0 ]; then
        echo "ERROR: Stage 2 compilation failed" >&2
        exit 1
    fi

    echo "Compilation successful: $EXECUTABLE"

    # Exit if compile-only mode
    if [ $COMPILE_ONLY -eq 1 ]; then
        echo ""
        echo "Compile-only mode: Stopping here"
        cd ../..
        exit 0
    fi

    # Execution
    echo ""
    echo "Starting full simulation..."
    echo "  Command args: $MAXlevel $De $Ec $Oh $Bond $tmax"
    echo "========================================="

    if [ $MPI_ENABLED -eq 1 ]; then
        [ $VERBOSE -eq 1 ] && echo "Command: mpirun -np $MPI_CORES ./$EXECUTABLE $MAXlevel $De $Ec $Oh $Bond $tmax"
        mpirun -np $MPI_CORES ./$EXECUTABLE $MAXlevel $De $Ec $Oh $Bond $tmax
    elif [ $FOPENMP_ENABLED -eq 1 ]; then
        export OMP_NUM_THREADS=$FOPENMP_THREADS
        [ $VERBOSE -eq 1 ] && echo "OMP_NUM_THREADS=$FOPENMP_THREADS"
        [ $VERBOSE -eq 1 ] && echo "Command: ./$EXECUTABLE $MAXlevel $De $Ec $Oh $Bond $tmax"
        ./$EXECUTABLE $MAXlevel $De $Ec $Oh $Bond $tmax
    else
        [ $VERBOSE -eq 1 ] && echo "Command: ./$EXECUTABLE $MAXlevel $De $Ec $Oh $Bond $tmax"
        ./$EXECUTABLE $MAXlevel $De $Ec $Oh $Bond $tmax
    fi

    EXIT_CODE=$?

    echo "========================================="
    if [ $EXIT_CODE -eq 0 ]; then
        echo "Simulation completed successfully"
        echo "Output location: $CASE_DIR"
    else
        echo "Simulation failed with exit code $EXIT_CODE"
    fi
    echo "========================================="

    # Return to root directory
    cd ../..
    exit $EXIT_CODE
fi

# Return to root directory
cd ../..
exit 0

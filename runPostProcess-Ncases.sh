#!/bin/bash
# runPostProcess-Ncases.sh - Run post-processing pipeline on multiple VE simulation cases
# Author: Vatsal Sanjay
# vatsal.sanjay@comphy-lab.org
# CoMPhy Lab - Durham University
# Last updated: Jan 2026

set -euo pipefail  # Exit on error, unset variables, pipeline failures

# ============================================================
# Configuration
# ============================================================
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Source parameter parsing library
if [ -f "${SCRIPT_DIR}/src-local/parse_params.sh" ]; then
    source "${SCRIPT_DIR}/src-local/parse_params.sh"
else
    echo "ERROR: src-local/parse_params.sh not found" >&2
    exit 1
fi

# Post-processing script paths
VIDEO_SCRIPT="${SCRIPT_DIR}/postProcess/Video.py"

# C helper executables
HELPER_GETFACET="${SCRIPT_DIR}/postProcess/getFacet"
HELPER_GETDATA="${SCRIPT_DIR}/postProcess/getData"

# Case directory root
CASES_DIR="${SCRIPT_DIR}/simulationCases"

# ============================================================
# Usage Information
# ============================================================
usage() {
    cat <<EOF
Usage: $0 [OPTIONS] CASE_NO [CASE_NO ...]

Run post-processing pipeline on multiple viscoelastic bubble bursting simulation cases.
For each case, generates video frames with strain-rate and conformation tensor fields,
and interface facets.

Options:
    --CPUs N            Number of parallel workers (default: 4)
    --nGFS N            Number of snapshots to process (default: 500)
    --tsnap F           Time interval between snapshots (default: 0.01)
    --GridsPerR N       Radial grid resolution for video (default: 256)
    --ZMIN F            Minimum Z coordinate (default: -4.0)
    --ZMAX F            Maximum Z coordinate (default: 4.0)
    --RMAX F            Maximum R coordinate (default: 2.0)

    Colorbar bounds (VE-specific):
    --d2-vmin F         Min value for strain-rate colorbar (default: -3.0)
    --d2-vmax F         Max value for strain-rate colorbar (default: 2.0)
    --tra-vmin F        Min value for tr(A) colorbar (default: -3.0)
    --tra-vmax F        Max value for tr(A) colorbar (default: 2.0)

    --skip-video-encode Skip ffmpeg video encoding after frame generation

    -n, --dry-run       Show what would run without executing
    -v, --verbose       Verbose output
    -h, --help          Show this help message

Arguments:
    CASE_NO             4-digit case numbers (1000-9999)

Examples:
    # Process multiple cases with default settings
    $0 1000 1001 1002

    # Process with 8 CPUs
    $0 --CPUs 8 1000 1001

    # Process first 100 snapshots only (for testing)
    $0 --nGFS 100 1000

    # Skip video encoding (only generate frames)
    $0 --skip-video-encode 1000 1001

    # Dry run to preview commands
    $0 --dry-run 1000

Output locations:
    simulationCases/<CaseNo>/Video/        # PNG frames
    simulationCases/<CaseNo>/<CaseNo>.mp4  # Encoded video

For more information, see CLAUDE.md
EOF
}

# ============================================================
# Parse Command Line Options
# ============================================================
CPUS=4
NGFS=500
TSNAP=0.01
GRIDS_PER_R=256
ZMIN="-4.0"
ZMAX="4.0"
RMAX="2.0"
D2_VMIN="-3.0"
D2_VMAX="2.0"
TRA_VMIN="-3.0"
TRA_VMAX="2.0"

SKIP_VIDEO_ENCODE=0
DRY_RUN=0
VERBOSE=0

CASE_NUMBERS=()

while [[ $# -gt 0 ]]; do
    case $1 in
        --CPUs)
            CPUS="$2"
            if ! [[ "$CPUS" =~ ^[0-9]+$ ]] || [ "$CPUS" -lt 1 ]; then
                echo "ERROR: --CPUs requires a positive integer, got: $CPUS" >&2
                exit 1
            fi
            shift 2
            ;;
        --nGFS)
            NGFS="$2"
            if ! [[ "$NGFS" =~ ^[0-9]+$ ]] || [ "$NGFS" -lt 1 ]; then
                echo "ERROR: --nGFS requires a positive integer, got: $NGFS" >&2
                exit 1
            fi
            shift 2
            ;;
        --tsnap)
            TSNAP="$2"
            shift 2
            ;;
        --GridsPerR)
            GRIDS_PER_R="$2"
            if ! [[ "$GRIDS_PER_R" =~ ^[0-9]+$ ]] || [ "$GRIDS_PER_R" -lt 1 ]; then
                echo "ERROR: --GridsPerR requires a positive integer, got: $GRIDS_PER_R" >&2
                exit 1
            fi
            shift 2
            ;;
        --ZMIN)
            ZMIN="$2"
            shift 2
            ;;
        --ZMAX)
            ZMAX="$2"
            shift 2
            ;;
        --RMAX)
            RMAX="$2"
            shift 2
            ;;
        --d2-vmin)
            D2_VMIN="$2"
            shift 2
            ;;
        --d2-vmax)
            D2_VMAX="$2"
            shift 2
            ;;
        --tra-vmin)
            TRA_VMIN="$2"
            shift 2
            ;;
        --tra-vmax)
            TRA_VMAX="$2"
            shift 2
            ;;
        --skip-video-encode)
            SKIP_VIDEO_ENCODE=1
            shift
            ;;
        -n|--dry-run)
            DRY_RUN=1
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
            # Collect case numbers
            CASE_NUMBERS+=("$1")
            shift
            ;;
    esac
done

# ============================================================
# Validation
# ============================================================

# Check at least one case number provided
if [ ${#CASE_NUMBERS[@]} -eq 0 ]; then
    echo "ERROR: No case numbers provided" >&2
    usage
    exit 1
fi

# Validate case numbers are 4-digit
for case_no in "${CASE_NUMBERS[@]}"; do
    if ! [[ "$case_no" =~ ^[0-9]{4}$ ]]; then
        echo "ERROR: Case number must be 4 digits (1000-9999), got: $case_no" >&2
        exit 1
    fi
    if [ "$case_no" -lt 1000 ] || [ "$case_no" -gt 9999 ]; then
        echo "ERROR: Case number out of range (1000-9999), got: $case_no" >&2
        exit 1
    fi
done

# Check Python availability
if ! command -v python &> /dev/null; then
    echo "ERROR: python not found in PATH" >&2
    exit 1
fi

# Check Python script exists
if [ ! -f "$VIDEO_SCRIPT" ]; then
    echo "ERROR: Python script not found: $VIDEO_SCRIPT" >&2
    exit 1
fi

# Check C helpers exist
for helper in "$HELPER_GETFACET" "$HELPER_GETDATA"; do
    if [ ! -x "$helper" ]; then
        helper_name=$(basename "$helper")
        echo "ERROR: Compiled helper not found or not executable: $helper" >&2
        echo "       Compile with: qcc -O2 -Wall postProcess/${helper_name}.c -o postProcess/${helper_name} -lm" >&2
        exit 1
    fi
done

# ============================================================
# Display Configuration
# ============================================================
echo "========================================="
echo "Viscoelastic Bubble Bursting - Post-Processing Pipeline"
echo "========================================="
echo "Cases to process: ${CASE_NUMBERS[*]}"
echo "Total cases: ${#CASE_NUMBERS[@]}"
echo ""
echo "Settings:"
echo "  CPUs:       $CPUS"
echo "  nGFS:       $NGFS"
echo "  tsnap:      $TSNAP"
echo "  GridsPerR:  $GRIDS_PER_R"
echo "  Domain:     Z=[$ZMIN, $ZMAX], R=[0, $RMAX]"
echo "  Colorbars:  D2=[$D2_VMIN, $D2_VMAX], tr(A)=[$TRA_VMIN, $TRA_VMAX]"
echo ""
echo "Pipeline:"
[ $SKIP_VIDEO_ENCODE -eq 0 ] && echo "  [1] Video.py (frames + video)" || echo "  [1] Video.py (frames only, video SKIPPED)"
echo ""
[ $DRY_RUN -eq 1 ] && echo "Mode: DRY RUN (no execution)"
echo ""

# ============================================================
# Processing Functions
# ============================================================

run_video() {
    local case_no="$1"
    local case_dir="${CASES_DIR}/${case_no}"
    local video_dir="${case_dir}/Video"

    # Build command
    local cmd_args=(
        "--caseToProcess" "${case_dir}"
        "--folderToSave" "${video_dir}"
        "--CPUs" "${CPUS}"
        "--nGFS" "${NGFS}"
        "--tsnap" "${TSNAP}"
        "--GridsPerR" "${GRIDS_PER_R}"
        "--ZMIN" "${ZMIN}"
        "--ZMAX" "${ZMAX}"
        "--RMAX" "${RMAX}"
        "--d2-vmin" "${D2_VMIN}"
        "--d2-vmax" "${D2_VMAX}"
        "--tra-vmin" "${TRA_VMIN}"
        "--tra-vmax" "${TRA_VMAX}"
    )

    # Add skip flag if needed
    [ $SKIP_VIDEO_ENCODE -eq 1 ] && cmd_args+=("--skip-video-encode")

    if [ $VERBOSE -eq 1 ] || [ $DRY_RUN -eq 1 ]; then
        echo "  CMD: python ${VIDEO_SCRIPT} ${cmd_args[*]}"
    fi

    if [ $DRY_RUN -eq 0 ]; then
        python "${VIDEO_SCRIPT}" "${cmd_args[@]}"
    fi
}

# ============================================================
# Main Processing Loop
# ============================================================
echo "========================================="
echo "Processing Cases"
echo "========================================="

SUCCESSFUL_CASES=()
FAILED_CASES=()
FAILURE_REASONS=()

for case_no in "${CASE_NUMBERS[@]}"; do
    echo ""
    echo "-----------------------------------------"
    echo "Case $case_no"
    echo "-----------------------------------------"

    case_dir="${CASES_DIR}/${case_no}"
    intermediate_dir="${case_dir}/intermediate"

    # Validate case directory exists
    if [ ! -d "$case_dir" ]; then
        echo "  ERROR: Case directory not found: $case_dir"
        FAILED_CASES+=("$case_no")
        FAILURE_REASONS+=("Case directory not found")
        continue
    fi

    if [ ! -d "$intermediate_dir" ]; then
        echo "  ERROR: Intermediate directory not found: $intermediate_dir"
        FAILED_CASES+=("$case_no")
        FAILURE_REASONS+=("No intermediate/ snapshots")
        continue
    fi

    # Count snapshots
    snapshot_count=$(find "$intermediate_dir" -name "snapshot-*" 2>/dev/null | wc -l | tr -d ' ')
    echo "  Found $snapshot_count snapshots in intermediate/"

    if [ "$snapshot_count" -eq 0 ]; then
        echo "  ERROR: No snapshots found"
        FAILED_CASES+=("$case_no")
        FAILURE_REASONS+=("No snapshots in intermediate/")
        continue
    fi

    # Display case parameters if case.params exists
    case_params="${case_dir}/case.params"
    if [ -f "$case_params" ] && [ $VERBOSE -eq 1 ]; then
        parse_param_file "$case_params"
        echo "  Parameters: De=$(get_param "De" "?"), Ec=$(get_param "Ec" "?"), Oh=$(get_param "Oh" "?")"
    fi

    # Track step failures
    step_failed=0

    # Run video generation
    echo ""
    echo "  [1/1] Running Video.py..."
    if ! run_video "$case_no"; then
        echo "  ERROR: Video generation failed"
        step_failed=1
    else
        [ $DRY_RUN -eq 0 ] && echo "  [1/1] Video generation complete"
    fi

    # Record result
    if [ $step_failed -eq 0 ]; then
        SUCCESSFUL_CASES+=("$case_no")
        echo ""
        echo "  Case $case_no: SUCCESS"
    else
        FAILED_CASES+=("$case_no")
        FAILURE_REASONS+=("Processing step failed")
        echo ""
        echo "  Case $case_no: FAILED"
    fi
done

# ============================================================
# Summary
# ============================================================
echo ""
echo "========================================="
echo "Post-Processing Complete"
echo "========================================="
echo "Total cases: ${#CASE_NUMBERS[@]}"
echo "Successful:  ${#SUCCESSFUL_CASES[@]}"
echo "Failed:      ${#FAILED_CASES[@]}"

if [ ${#FAILED_CASES[@]} -gt 0 ]; then
    echo ""
    echo "Failed cases:"
    for i in "${!FAILED_CASES[@]}"; do
        echo "  - Case ${FAILED_CASES[$i]}: ${FAILURE_REASONS[$i]}"
    done
fi

if [ ${#SUCCESSFUL_CASES[@]} -gt 0 ]; then
    echo ""
    echo "Output locations:"
    for case_no in "${SUCCESSFUL_CASES[@]}"; do
        echo "  ${CASES_DIR}/${case_no}/"
    done
fi

echo ""

# Exit with error if any cases failed
if [ ${#FAILED_CASES[@]} -gt 0 ]; then
    exit 1
fi

exit 0

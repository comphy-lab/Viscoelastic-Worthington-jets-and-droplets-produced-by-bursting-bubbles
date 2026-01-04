# Author: Vatsal Sanjay
# vatsal.sanjay@comphy-lab.org
# CoMPhy Lab
# Durham University
# Last updated: Jan 2026

"""
Viscoelastic post-processing pipeline for Basilisk bubble bursting simulations.

Overview
--------
The helper executables `postProcess/getFacet` and `postProcess/getData` are
compiled as part of the Basilisk workflow. This Python wrapper shells out to
those binaries for every snapshot, reshapes the returned grids, and renders
axisymmetric visualisations with strain-rate and conformation tensor fields.

Usage
-----
Typical invocation from the repository root::

    python3 postProcess/Video.py --caseToProcess simulationCases/1000

Command-line switches expose all relevant knobs (grid density, domain limits,
time stride, CPU count). The output directory is created on-demand and filled
with zero-padded PNG files compatible with downstream stitching utilities.
"""

import argparse
import multiprocessing as mp
import os
import shutil
import subprocess as sp
from dataclasses import dataclass
from functools import partial
from datetime import datetime
from typing import Sequence, Tuple, Optional

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np
from matplotlib.collections import LineCollection
from matplotlib.ticker import StrMethodFormatter

# Configure matplotlib with LaTeX if available, fallback otherwise
matplotlib.rcParams["font.family"] = "serif"
if shutil.which("latex"):
    try:
        matplotlib.rcParams["text.usetex"] = True
        matplotlib.rcParams["text.latex.preamble"] = r"\usepackage{amsmath}"
    except Exception:
        matplotlib.rcParams["text.usetex"] = False
else:
    matplotlib.rcParams["text.usetex"] = False

# Custom colormap for conformation tensor trace (polymer stretching)
CUSTOM_COLORS = ["white", "#DA8A67", "#A0522D", "#400000"]
CUSTOM_CMAP = mcolors.LinearSegmentedColormap.from_list("custom_hot", CUSTOM_COLORS)

# Script directory for finding helper executables
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
HELPER_GETFACET = os.path.join(SCRIPT_DIR, "getFacet")
HELPER_GETDATA = os.path.join(SCRIPT_DIR, "getData")


@dataclass(frozen=True)
class DomainBounds:
    """
    Symmetry-aware domain description in cylindrical coordinates.

    The code expects r in [rmin, rmax] with rmin <= 0 to leverage the axis of
    symmetry; z spans freely between zmin and zmax.
    """

    rmin: float
    rmax: float
    zmin: float
    zmax: float


@dataclass(frozen=True)
class RuntimeConfig:
    """
    Run-time knobs collected from CLI arguments.

    Multiprocessing workers only need a single instance of this struct, making
    later CLI additions painless.
    """

    cpus: int
    n_snapshots: int
    grids_per_r: int
    tsnap: float
    zmin: float
    zmax: float
    rmax: float
    case_dir: str
    output_dir: str
    skip_video_encode: bool
    framerate: int
    output_fps: int
    # VE-specific colorbar bounds
    d2_vmin: float
    d2_vmax: float
    tra_vmin: float
    tra_vmax: float

    @property
    def rmin(self) -> float:
        return -self.rmax

    @property
    def bounds(self) -> DomainBounds:
        return DomainBounds(self.rmin, self.rmax, self.zmin, self.zmax)


@dataclass(frozen=True)
class PlotStyle:
    """
    Single source of truth for plot-level choices.

    Matplotlib tweaks become traceable: alter colours, fonts, or geometry here
    and every rendered frame will stay consistent without touching plotting
    logic.
    """

    figure_size: Tuple[float, float] = (19.20, 10.80)
    tick_label_size: int = 20
    zero_axis_color: str = "grey"
    axis_color: str = "black"
    line_width: float = 2.0
    interface_color: str = "#00B2FF"
    colorbar_width: float = 0.03
    left_colorbar_offset: float = 0.04
    right_colorbar_offset: float = 0.01


@dataclass(frozen=True)
class SnapshotInfo:
    """
    Metadata for an input snapshot and its output image.

    Storing paths and the physical time together simplifies filename logic and
    ensures logging statements stay informative.
    """

    index: int
    time: float
    source: str
    target: str


@dataclass
class FieldData:
    """
    Structured holder around the grids returned by getData.

    For VE simulations, includes strain-rate (D2), velocity, and
    conformation tensor trace (trA).
    """

    R: np.ndarray
    Z: np.ndarray
    strain_rate: np.ndarray
    velocity: np.ndarray
    conf_trace: np.ndarray  # VE-specific: log10(tr(A) - 1)
    nz: int

    @property
    def radial_extent(self) -> Tuple[float, float]:
        return self.R.min(), self.R.max()

    @property
    def axial_extent(self) -> Tuple[float, float]:
        return self.Z.min(), self.Z.max()


PLOT_STYLE = PlotStyle()


def log_status(message: str, *, level: str = "INFO") -> None:
    """Print timestamped status messages for long-running CLI workflows."""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] [{level}] {message}", flush=True)


def parse_arguments() -> RuntimeConfig:
    """Parse command-line arguments and construct runtime configuration.

    Returns:
        RuntimeConfig: Configuration object containing all parameters.
    """
    parser = argparse.ArgumentParser(
        description="Generate snapshot videos for viscoelastic bubble bursting."
    )
    parser.add_argument("--CPUs", type=int, default=4, help="Number of CPUs to use")
    parser.add_argument(
        "--nGFS", type=int, default=500, help="Number of restart files to process"
    )
    parser.add_argument(
        "--GridsPerR", type=int, default=256, help="Number of grids per R"
    )
    parser.add_argument(
        "--ZMIN", type=float, default=-4.0, help="Minimum Z value (default: -4.0)"
    )
    parser.add_argument(
        "--ZMAX", type=float, default=4.0, help="Maximum Z value (default: 4.0)"
    )
    parser.add_argument(
        "--RMAX", type=float, default=2.0, help="Maximum R value (default: 2.0)"
    )
    parser.add_argument("--tsnap", type=float, default=0.01, help="Time snap interval")
    parser.add_argument(
        "--caseToProcess",
        type=str,
        default="simulationCases/1000",
        help="Case to process",
    )
    parser.add_argument(
        "--folderToSave", type=str, default=None, help="Folder to save (default: <case>/Video)"
    )
    parser.add_argument(
        "--skip-video-encode", action="store_true",
        help="Skip ffmpeg video encoding after frame generation"
    )
    parser.add_argument(
        "--framerate", type=int, default=90,
        help="Input framerate for ffmpeg (default: 90)"
    )
    parser.add_argument(
        "--output-fps", type=int, default=30,
        help="Output video framerate (default: 30)"
    )
    # VE-specific colorbar bounds
    parser.add_argument(
        "--d2-vmin", type=float, default=-3.0,
        help="Min value for strain-rate colorbar (default: -3.0)"
    )
    parser.add_argument(
        "--d2-vmax", type=float, default=2.0,
        help="Max value for strain-rate colorbar (default: 2.0)"
    )
    parser.add_argument(
        "--tra-vmin", type=float, default=-3.0,
        help="Min value for conformation tensor trace colorbar (default: -3.0)"
    )
    parser.add_argument(
        "--tra-vmax", type=float, default=2.0,
        help="Max value for conformation tensor trace colorbar (default: 2.0)"
    )
    args = parser.parse_args()

    # Default output directory
    output_dir = args.folderToSave if args.folderToSave else os.path.join(args.caseToProcess, "Video")

    return RuntimeConfig(
        cpus=args.CPUs,
        n_snapshots=args.nGFS,
        grids_per_r=args.GridsPerR,
        tsnap=args.tsnap,
        zmin=args.ZMIN,
        zmax=args.ZMAX,
        rmax=args.RMAX,
        case_dir=args.caseToProcess,
        output_dir=output_dir,
        skip_video_encode=args.skip_video_encode,
        framerate=args.framerate,
        output_fps=args.output_fps,
        d2_vmin=args.d2_vmin,
        d2_vmax=args.d2_vmax,
        tra_vmin=args.tra_vmin,
        tra_vmax=args.tra_vmax,
    )


def ensure_directory(path: str) -> None:
    """Create an output directory if it does not exist."""
    if not os.path.isdir(path):
        os.makedirs(path, exist_ok=True)


def run_helper(command: Sequence[str], cwd: Optional[str] = None) -> Sequence[str]:
    """
    Run a helper executable and return its stderr as decoded lines.

    The compiled helpers deliberately emit their payload to stderr, so stdout is
    ignored and we return the informative stderr content.

    Note: Basilisk executables have issues with very long absolute paths,
    so we support running from a specific working directory with relative paths.
    """
    process = sp.Popen(command, stdout=sp.PIPE, stderr=sp.PIPE, cwd=cwd)
    _, stderr = process.communicate()
    if process.returncode != 0:
        raise RuntimeError(
            f"Command {' '.join(command)} failed with code {process.returncode}:\n"
            f"{stderr.decode('utf-8')}"
        )
    return stderr.decode("utf-8").split("\n")


def get_facets(filename: str, case_dir: str):
    """Collect interface facets from getFacet helper with axisymmetric mirroring.

    Shells out to the compiled ``getFacet`` executable, which extracts the
    volume-of-fluid (VOF) interface as a sequence of line segments. Since
    the simulation uses axisymmetric coordinates, only the r >= 0 half is
    computed. This function mirrors each segment about r=0.

    Args:
        filename: Relative path to snapshot file (e.g., 'intermediate/snapshot-0.0100')
        case_dir: Absolute path to case directory (used as cwd)

    Returns:
        list[tuple]: Sequence of line segments, each as ((r1, z1), (r2, z2)).
    """
    temp2 = run_helper([HELPER_GETFACET, filename], cwd=case_dir)
    segs = []
    skip = False
    if len(temp2) > 1e2:
        for n1 in range(len(temp2)):
            temp3 = temp2[n1].split(" ")
            if temp3 == [""]:
                skip = False
                continue
            if not skip and n1 + 1 < len(temp2):
                temp4 = temp2[n1 + 1].split(" ")
                r1, z1 = np.array([float(temp3[1]), float(temp3[0])])
                r2, z2 = np.array([float(temp4[1]), float(temp4[0])])
                segs.append(((r1, z1), (r2, z2)))
                segs.append(((-r1, z1), (-r2, z2)))
                skip = True
    return segs


def get_field(filename: str, case_dir: str, zmin: float, zmax: float, rmax: float, nr: int) -> FieldData:
    """Read field arrays for a single snapshot from getData helper.

    Shells out to the compiled ``getData`` executable, which samples the
    velocity, strain-rate, and conformation tensor trace fields on a
    structured grid.

    Args:
        filename: Relative path to snapshot file (e.g., 'intermediate/snapshot-0.0100')
        case_dir: Absolute path to case directory (used as cwd)
        zmin: Minimum axial coordinate for sampling domain
        zmax: Maximum axial coordinate for sampling domain
        rmax: Maximum radial coordinate (positive branch only)
        nr: Number of grid points in radial direction

    Returns:
        FieldData: Structured container with reshaped 2D arrays.
    """
    temp2 = run_helper(
        [
            HELPER_GETDATA,
            filename,
            str(zmin),
            str(0),
            str(zmax),
            str(rmax),
            str(nr),
        ],
        cwd=case_dir,
    )
    Rtemp, Ztemp, D2temp, veltemp, trAtemp = [], [], [], [], []

    for n1 in range(len(temp2)):
        temp3 = temp2[n1].split(" ")
        if temp3 == [""]:
            continue
        Ztemp.append(float(temp3[0]))
        Rtemp.append(float(temp3[1]))
        D2temp.append(float(temp3[2]))
        veltemp.append(float(temp3[3]))
        trAtemp.append(float(temp3[4]))

    R = np.asarray(Rtemp)
    Z = np.asarray(Ztemp)
    D2 = np.asarray(D2temp)
    vel = np.asarray(veltemp)
    trA = np.asarray(trAtemp)
    nz = int(len(Z) / nr)

    log_status(f"{os.path.basename(filename)}: nz = {nz}")

    R.resize((nz, nr))
    Z.resize((nz, nr))
    D2.resize((nz, nr))
    vel.resize((nz, nr))
    trA.resize((nz, nr))

    return FieldData(R=R, Z=Z, strain_rate=D2, velocity=vel, conf_trace=trA, nz=nz)


def build_snapshot_info(index: int, config: RuntimeConfig) -> SnapshotInfo:
    """Construct file paths for a given timestep index."""
    time = config.tsnap * index
    source = os.path.join(config.case_dir, "intermediate", f"snapshot-{time:.4f}")
    target = os.path.join(config.output_dir, f"{int(time * 1000):08d}.png")
    return SnapshotInfo(index=index, time=time, source=source, target=target)


def draw_domain_outline(ax, bounds: DomainBounds, style: PlotStyle) -> None:
    """Outline computational domain and symmetry line."""
    ax.plot(
        [0, 0],
        [bounds.zmin, bounds.zmax],
        "-.",
        color=style.zero_axis_color,
        linewidth=style.line_width,
    )
    ax.plot(
        [bounds.rmin, bounds.rmin],
        [bounds.zmin, bounds.zmax],
        "-",
        color=style.axis_color,
        linewidth=style.line_width,
    )
    ax.plot(
        [bounds.rmin, bounds.rmax],
        [bounds.zmin, bounds.zmin],
        "-",
        color=style.axis_color,
        linewidth=style.line_width,
    )
    ax.plot(
        [bounds.rmin, bounds.rmax],
        [bounds.zmax, bounds.zmax],
        "-",
        color=style.axis_color,
        linewidth=style.line_width,
    )
    ax.plot(
        [bounds.rmax, bounds.rmax],
        [bounds.zmin, bounds.zmax],
        "-",
        color=style.axis_color,
        linewidth=style.line_width,
    )


def add_colorbar(fig, ax, mappable, *, align: str, label: str, style: PlotStyle):
    """Attach a vertical colorbar on the requested side of the axis."""
    l, b, w, h = ax.get_position().bounds
    if align == "left":
        position = [l - style.left_colorbar_offset, b, style.colorbar_width, h]
    else:
        position = [l + w + style.right_colorbar_offset, b, style.colorbar_width, h]
    cb_ax = fig.add_axes(position)
    colorbar = plt.colorbar(mappable, cax=cb_ax, orientation="vertical")
    colorbar.set_label(label, fontsize=style.tick_label_size, labelpad=5)
    colorbar.ax.tick_params(labelsize=style.tick_label_size)
    colorbar.ax.yaxis.set_major_formatter(StrMethodFormatter("{x:,.2f}"))
    if align == "left":
        colorbar.ax.yaxis.set_ticks_position("left")
        colorbar.ax.yaxis.set_label_position("left")
    return colorbar


def plot_snapshot(
    field_data: FieldData,
    facets,
    bounds: DomainBounds,
    snapshot: SnapshotInfo,
    config: RuntimeConfig,
    style: PlotStyle,
) -> None:
    """
    Render and persist a single snapshot figure.

    For VE simulations:
    - Left side: log10(D:D) strain-rate field
    - Right side: log10(tr(A) - 1) conformation tensor trace
    """
    fig, ax = plt.subplots()
    fig.set_size_inches(*style.figure_size)

    draw_domain_outline(ax, bounds, style)
    line_segments = LineCollection(
        facets, linewidths=4, colors=style.interface_color, linestyle="solid"
    )
    ax.add_collection(line_segments)

    rminp, rmaxp = field_data.radial_extent
    zminp, zmaxp = field_data.axial_extent

    # Left: Strain-rate field (D:D)
    cntrl1 = ax.imshow(
        field_data.strain_rate,
        cmap="hot_r",
        interpolation="Bilinear",
        origin="lower",
        extent=[-rminp, -rmaxp, zminp, zmaxp],
        vmax=config.d2_vmax,
        vmin=config.d2_vmin,
    )

    # Right: Conformation tensor trace (VE-specific)
    cntrl2 = ax.imshow(
        field_data.conf_trace,
        interpolation="Bilinear",
        cmap=CUSTOM_CMAP,
        origin="lower",
        extent=[rminp, rmaxp, zminp, zmaxp],
        vmax=config.tra_vmax,
        vmin=config.tra_vmin,
    )

    ax.set_aspect("equal")
    ax.set_xlim(bounds.rmin, bounds.rmax)
    ax.set_ylim(bounds.zmin, bounds.zmax)
    ax.set_title(f"$t/\\tau_\\gamma$ = {snapshot.time:4.3f}", fontsize=style.tick_label_size)
    ax.axis("off")

    add_colorbar(
        fig,
        ax,
        cntrl1,
        align="left",
        label=r"$\log_{10}\left(\|\mathcal{D}\|\right)$",
        style=style,
    )
    add_colorbar(
        fig,
        ax,
        cntrl2,
        align="right",
        label=r"$\log_{10}\left(\text{tr}(\mathcal{A})-1\right)$",
        style=style,
    )

    plt.savefig(snapshot.target, bbox_inches="tight")
    plt.close(fig)


def process_timestep(index: int, config: RuntimeConfig, style: PlotStyle) -> None:
    """
    Worker executed for every timestep index.

    Performs availability checks, loads helper outputs, and calls plot_snapshot.
    """
    snapshot = build_snapshot_info(index, config)
    if not os.path.exists(snapshot.source):
        log_status(f"Missing: {os.path.basename(snapshot.source)}", level="WARN")
        return
    if os.path.exists(snapshot.target):
        log_status(f"Exists, skipping: {os.path.basename(snapshot.target)}")
        return

    # Show relative path: CaseNo/intermediate/filename
    src_parts = snapshot.source.split(os.sep)
    src_rel = os.sep.join(src_parts[-3:]) if len(src_parts) >= 3 else snapshot.source
    log_status(f"Processing {src_rel}")

    # Relative path for Basilisk helpers (they crash with very long absolute paths)
    rel_snapshot = os.path.join("intermediate", f"snapshot-{snapshot.time:.4f}")
    case_dir = os.path.abspath(config.case_dir)

    try:
        facets = get_facets(rel_snapshot, case_dir)
        nr = int(config.grids_per_r * config.rmax)
        field_data = get_field(
            rel_snapshot, case_dir, config.zmin, config.zmax, config.rmax, nr
        )
        plot_snapshot(field_data, facets, config.bounds, snapshot, config, style)

        # Show relative path: CaseNo/Video/filename
        tgt_parts = snapshot.target.split(os.sep)
        tgt_rel = os.sep.join(tgt_parts[-3:]) if len(tgt_parts) >= 3 else snapshot.target
        log_status(f"Saved: {tgt_rel}")

    except Exception as err:
        log_status(
            f"Error at {src_rel} (t={snapshot.time:.4f}): {err}", level="ERROR"
        )
        raise


def encode_video(config: RuntimeConfig) -> None:
    """
    Run ffmpeg to stitch PNG frames into an MP4 video.

    The output video is saved in the case directory with the case number
    as filename (e.g., simulationCases/1000/1000.mp4).
    """
    # Extract case number from path
    case_no = os.path.basename(config.case_dir)

    # Output path: <case_dir>/<case_no>.mp4
    output_path = os.path.join(config.case_dir, f"{case_no}.mp4")
    input_pattern = os.path.join(config.output_dir, "*.png")

    cmd = [
        "ffmpeg", "-y",
        "-framerate", str(config.framerate),
        "-pattern_type", "glob",
        "-i", input_pattern,
        "-vf", "pad=ceil(iw/2)*2:ceil(ih/2)*2",
        "-c:v", "libx264",
        "-r", str(config.output_fps),
        "-pix_fmt", "yuv420p",
        output_path
    ]

    log_status(f"Encoding video: {output_path}")
    result = sp.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        log_status(f"ffmpeg error: {result.stderr}", level="ERROR")
        raise RuntimeError(f"ffmpeg failed with code {result.returncode}")
    log_status(f"Video saved: {output_path}")


def main():
    """Entry point for CLI invocation."""
    config = parse_arguments()
    ensure_directory(config.output_dir)

    log_status(f"Processing case: {config.case_dir}")
    log_status(f"Domain: R=[{config.rmin:.2f},{config.rmax:.2f}], Z=[{config.zmin:.2f},{config.zmax:.2f}]")

    with mp.Pool(processes=config.cpus) as pool:
        worker = partial(process_timestep, config=config, style=PLOT_STYLE)
        pool.map(worker, range(config.n_snapshots))

    # Encode video unless skipped
    if not config.skip_video_encode:
        encode_video(config)


if __name__ == "__main__":
    main()

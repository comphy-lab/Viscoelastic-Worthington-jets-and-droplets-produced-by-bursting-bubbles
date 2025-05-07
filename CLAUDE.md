# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Structure 
- `basilisk/src/`: Core Basilisk CFD library (reference only, do not modify)
- `src-local/`: Custom header files extending Basilisk functionality
- `simulationCases/`: Test cases with their own Makefile 
- `postProcess/`: Project-specific post-processing tools
- `docs/`: Generated documentation (do not edit directly)

## Build & Test Commands
- Compile single file: `qcc -O2 -Wall -disable-dimensions file.c -o executable -lm`
- Compile with custom headers: `qcc -O2 -Wall -disable-dimensions -I$PWD/src-local file.c -o executable -lm`
- Run specific test case: `cd simulationCases && make test_name.tst`
- Generate documentation (but don't deploy): `bash .github/scripts/build.sh`

## Code Style

- **Indentation**: 2 spaces (no tabs).
- **Line Length**: Maximum 80 characters per line.
- **Comments**: Use markdown in comments starting with `/**`; avoid bare `*` in comments.
- **Spacing**: Include spaces after commas and around operators (`+`, `-`).
- **File Organization**: 
  - Place core functionality in `.h` headers
  - Implement tests in `.c` files
- **Naming Conventions**: 
  - Use `snake_case` for variables and parameters
  - Use `camelCase` for functions and methods
- **Error Handling**: Return meaningful values and provide descriptive `stderr` messages.

## Documentation Generation

- Read `.github/Website-generator-readme.md` for the website generation process.
- Do not auto-deploy the website; generating HTML is permitted using `.github/scripts/build.sh`.
- Avoid editing HTML files directly; they are generated using `.github/scripts/build.sh`, which utilizes `.github/scripts/generate_docs.py`.
- The website is deployed at `https://comphy-lab.org/repositoryName`; refer to the `CNAME` file for configuration. Update if not done already. 

## Purpose

This rule provides guidance for maintaining and generating documentation for code repositories in the CoMPhy Lab, ensuring consistency and proper workflow for website generation.

## Process Details

The documentation generation process utilizes Python scripts to convert source code files into HTML documentation. The process handles C/C++, Python, Shell, and Markdown files, generating a complete documentation website with navigation, search functionality, and code highlighting.

## Best Practices

- Always use the build script for generating documentation rather than manually editing HTML files
- Customize styling through CSS files in `.github/assets/css/`
- Modify functionality through JavaScript files in `.github/assets/js/`
- For template changes, edit `.github/assets/custom_template.html`
- Troubleshoot generation failures by checking error messages and verifying paths and dependencies
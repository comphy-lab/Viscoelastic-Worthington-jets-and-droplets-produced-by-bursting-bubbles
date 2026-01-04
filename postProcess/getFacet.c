/**
# Getting Facets

A utility for extracting interface facets from fluid simulation data.

## Description
This program extracts and outputs the facets representing the interface
between different phases in a multiphase flow simulation. The facets
define the boundary between fluid phases, useful for geometric analysis
and visualization of the interface morphology.

## Physics Background
In multiphase fluid simulations, interfaces between different fluids are
critical features that determine many physical phenomena like surface tension
effects, droplet formation, and coalescence events. This utility identifies
these interfaces by extracting facets from volume fraction data, allowing
for quantitative analysis of interfacial dynamics.

## Usage

```
./getFacets input_file
```

- Author: Vatsal Sanjay  
vatsalsanjay@gmail.com  
Physics of Fluids Department  
University of Twente

*/

#include "utils.h"
#include "output.h"
#include "fractions.h"

scalar f[];  // Volume fraction field
char filename[80];

/**
### Main Function

Loads a simulation snapshot and extracts the interface facets.

- Input parameters:
  - `arguments[1]`: Filename of the simulation snapshot to process

- Process:
  1. Restores the simulation state from the specified file
  2. Extracts interface facets from the volume fraction field
  3. Outputs facet data to standard error

- Return value:
  - Returns 0 on successful completion

- Note:
  The facet extraction algorithm identifies where the volume fraction
  field crosses a threshold value (typically 0.5) between adjacent cells.
*/
int main(int a, char const *arguments[]) {
  sprintf(filename, "%s", arguments[1]);
  restore(file = filename);
  
  FILE *fp = ferr;
  output_facets(f, fp);
  fflush(fp);
  fclose(fp);
  
  return 0;
}
/**
# Matrix Eigenvalue Solver

This module provides algorithms for computing eigenvalues and eigenvectors of 
3x3 symmetric matrices, which are commonly encountered in computational fluid 
dynamics, solid mechanics, and other physics-based simulations.

## Mathematical Background

The implementation uses the Householder transformation to reduce a symmetric
matrix to tridiagonal form, followed by the QL algorithm with implicit shifts
to compute the eigenvalues and eigenvectors.

For a 3x3 symmetric matrix, these methods are particularly efficient and
numerically stable, providing accurate results even for matrices with closely
spaced eigenvalues.

### Tridiagonalize a 3x3 Symmetric Matrix

Reduces a 3x3 symmetric matrix to tridiagonal form using the Householder method,
which applies a series of orthogonal transformations to eliminate elements
below the subdiagonal.

- Parameters:
  - matrix[in]: Input 3x3 symmetric matrix to be tridiagonalized
  - eigenvectors[out]: Orthogonal matrix of Householder vectors
  - diagonal[out]: Diagonal elements of the resulting tridiagonal matrix
  - subdiagonal[out]: Subdiagonal elements of the tridiagonal matrix

- Implementation Notes:
  - The original matrix is preserved
  - The eigenvectors matrix is initialized to identity and then transformed
  - The algorithm exploits the symmetry of the input matrix
*/

#define SQUARE(x) ((x)*(x))

static void tridiagonalize_symmetric_3x3(double matrix[3][3], 
                                         double eigenvectors[3][3], 
                                         double diagonal[3], 
                                         double subdiagonal[2])
{
  const int size = 3;
  double householder_vector[size], temp_vector[size];
  double omega, scale, sigma, tau;
  
  // Initialize eigenvectors to the identity matrix
  for (int i = 0; i < size; i++) {
    eigenvectors[i][i] = 1.0;
    for (int j = 0; j < i; j++)
      eigenvectors[i][j] = eigenvectors[j][i] = 0.0;
  }

  // Compute the first Householder reflection
  scale = SQUARE(matrix[0][1]) + SQUARE(matrix[0][2]);
  sigma = (matrix[0][1] > 0) ? -sqrt(scale) : sqrt(scale);
  subdiagonal[0] = sigma;
  tau = sigma * matrix[0][1];
  householder_vector[1] = matrix[0][1] - sigma;
  householder_vector[2] = matrix[0][2];
  
  omega = scale - tau;
  if (omega > 0.0) {
    omega = 1.0 / omega;
    sigma = 0.0;
    for (int i = 1; i < size; i++) {
      tau = matrix[1][i] * householder_vector[1] + 
            matrix[i][2] * householder_vector[2];
      temp_vector[i] = omega * tau;
      sigma += householder_vector[i] * tau;
    }
    sigma *= 0.5 * SQUARE(omega);

    for (int i = 1; i < size; i++)
      temp_vector[i] -= sigma * householder_vector[i];
    
    diagonal[0] = matrix[0][0];
    diagonal[1] = matrix[1][1] - 2.0 * temp_vector[1] * householder_vector[1];
    diagonal[2] = matrix[2][2] - 2.0 * temp_vector[2] * householder_vector[2];
    
    for (int j = 1; j < size; j++) {
      tau = omega * householder_vector[j];
      for (int i = 1; i < size; i++)
        eigenvectors[i][j] -= tau * householder_vector[i];
    }

    subdiagonal[1] = matrix[1][2] - temp_vector[1] * householder_vector[2] - 
                     householder_vector[1] * temp_vector[2];
  }
  else {
    for (int i = 0; i < size; i++)
      diagonal[i] = matrix[i][i];
    subdiagonal[1] = matrix[1][2];
  }
}

/**
 ### Compute Eigenvalues and Eigenvectors of a 3x3 Symmetric Matrix
 
 Calculates the complete eigensystem (eigenvalues and eigenvectors) of a 3x3
 symmetric matrix using the QL algorithm with implicit shifts, after first
 reducing the matrix to tridiagonal form.
 
 - Parameters:
   - matrix[in]: Input 3x3 symmetric matrix whose eigensystem will be computed
   - eigenvectors[out]: Matrix whose columns are the eigenvectors
   - eigenvalues[out]: Array containing the eigenvalues
 
 - Return Value:
   - 0: Computation successful
   - -1: Algorithm failed to converge within the maximum number of iterations
 
 - Algorithm Details:
   - First checks if the matrix is already diagonal
   - If not, tridiagonalizes the matrix using Householder transformations
   - Applies the QL algorithm with implicit shifts to compute eigenvalues
   - Maximum of 30 iterations are allowed for convergence
   - Numerical tolerance of 1e-15 is used for detecting diagonal matrices
 
 - Usage Example:
   ```c
   double matrix[3][3] = {{1.0, 0.5, 0.3},
                          {0.5, 2.0, 0.1},
                          {0.3, 0.1, 3.0}};
   double eigenvectors[3][3];
   double eigenvalues[3];
   
   int result = compute_eigensystem_symmetric_3x3(matrix, eigenvectors, eigenvalues);
   if (result == 0) {
     // Computation successful
   }
   ```
 */
static int compute_eigensystem_symmetric_3x3(double matrix[3][3], 
                                            double eigenvectors[3][3], 
                                            double eigenvalues[3])
{
  const int size = 3;
  const int max_iterations = 30;
  double subdiagonal[3];
  double g, r, p, f, b, s, c, t;
  int iteration_count;
  int m;

  // Check for diagonal matrix with unit entries
  if (SQUARE(matrix[0][1]) < 1e-15 && SQUARE(matrix[0][2]) < 1e-15 && 
      SQUARE(matrix[1][2]) < 1e-15) {
    for (int i = 0; i < size; i++) {
      for (int j = 0; j < size; j++) {
        eigenvectors[i][j] = (i == j) ? 1.0 : 0.0;
      }
      eigenvalues[i] = matrix[i][i];
    }
    return 0;
  }

  tridiagonalize_symmetric_3x3(matrix, eigenvectors, eigenvalues, subdiagonal);
  
  for (int l = 0; l < size - 1; l++) {
    iteration_count = 0;
    while (1) {
      for (m = l; m <= size - 2; m++) {
        g = fabs(eigenvalues[m]) + fabs(eigenvalues[m+1]);
        if (fabs(subdiagonal[m]) + g == g)
          break;
      }
      if (m == l)
        break;
      
      if (iteration_count++ >= max_iterations)
        return -1;

      g = (eigenvalues[l+1] - eigenvalues[l]) / (2.0 * subdiagonal[l]);
      r = sqrt(SQUARE(g) + 1.0);
      g = eigenvalues[m] - eigenvalues[l] + subdiagonal[l] / 
          (g + (g > 0 ? fabs(r) : -fabs(r)));

      s = c = 1.0;
      p = 0.0;
      for (int i = m - 1; i >= l; i--) {
        f = s * subdiagonal[i];
        b = c * subdiagonal[i];
        if (fabs(f) > fabs(g)) {
          c = g / f;
          r = sqrt(SQUARE(c) + 1.0);
          subdiagonal[i+1] = f * r;
          c *= (s = 1.0 / r);
        }
        else {
          s = f / g;
          r = sqrt(SQUARE(s) + 1.0);
          subdiagonal[i+1] = g * r;
          s *= (c = 1.0 / r);
        }
        
        g = eigenvalues[i+1] - p;
        r = (eigenvalues[i] - g) * s + 2.0 * c * b;
        p = s * r;
        eigenvalues[i+1] = g + p;
        g = c * r - b;

        for (int k = 0; k < size; k++) {
          t = eigenvectors[k][i+1];
          eigenvectors[k][i+1] = s * eigenvectors[k][i] + c * t;
          eigenvectors[k][i]   = c * eigenvectors[k][i] - s * t;
        }
      }
      eigenvalues[l] -= p;
      subdiagonal[l] = g;
      subdiagonal[m] = 0.0;
    }
  }

  return 0;
}
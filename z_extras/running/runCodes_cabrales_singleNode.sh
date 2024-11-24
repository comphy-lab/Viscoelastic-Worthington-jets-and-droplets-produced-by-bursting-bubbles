#!/bin/bash

#SBATCH -N 1
#SBATCH --ntasks=64
#SBATCH --job-name=319
##SBATCH --time=24:00:00
#SBATCH --mail-type=ALL
#SBATCH --error=job.%J.err
#SBATCH --output=job.%J.out

MAXlevel="11"
Bond="1e-3"
tmax="1.5"

Ec=( " 4.000E-05 "  " 7.649E-05 "  " 1.463E-04 "  " 2.797E-04 "  " 5.348E-04 "  " 1.023E-03 "  " 1.956E-03 "  " 3.740E-03 "
     " 7.151E-03 "  " 1.367E-02 "  " 2.615E-02 "  " 5.000E-02 " )
Oh="5e-2" 

start=319


for i in {0..11};
do
cd  $(printf "%03d" $((start+i)))
export OMP_NUM_THREADS=64
./burstingBubbleVE_ElasticLimit_v3 $MAXlevel ${Ec[i]} $Oh $Bond $tmax 
cd ../
done
#CC99='mpicc -std=c99' qcc -Wall -O2 -D_MPI=1 burstingBubbleVE_ElasticLimit_v2_Snellius.c -o burstingBubbleVE_ElasticLimit_v2_Snellius -lm

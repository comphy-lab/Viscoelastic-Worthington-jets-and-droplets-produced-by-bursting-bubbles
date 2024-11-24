#!/bin/bash

#SBATCH -N 1
#SBATCH --ntasks=64
#SBATCH --job-name=271
#SBATCH --time=24:00:00
#SBATCH --mail-type=ALL
#SBATCH --error=job.%J.err
#SBATCH --output=job.%J.out
#SBATCH --mail-type=ALL
#SBATCH --mail-user=a.k.dixit@utwente.nl

MAXlevel="11"
Bond="1e-3"
tmax="1.2"

Ec=( " 4.000E-05 "  " 7.649E-05 "  " 1.463E-04 "  " 2.797E-04 "  " 5.348E-04 "  " 1.023E-03 "  " 1.956E-03 "  " 3.740E-03 "
     " 7.151E-03 "  " 1.367E-02 "  " 2.615E-02 "  " 5.000E-02 "  " 4.000E-05 "  " 7.649E-05 "  " 1.463E-04 "  " 2.797E-04 "
     " 5.348E-04 "  " 1.023E-03 "  " 1.956E-03 "  " 3.740E-03 "  " 7.151E-03 "  " 1.367E-02 "  " 2.615E-02 "  " 5.000E-02 "
     " 4.000E-05 "  " 7.649E-05 "  " 1.463E-04 "  " 2.797E-04 "  " 5.348E-04 "  " 1.023E-03 "  " 1.956E-03 "  " 3.740E-03 "
     " 7.151E-03 "  " 1.367E-02 "  " 2.615E-02 "  " 5.000E-02 "  " 4.000E-05 "  " 7.649E-05 "  " 1.463E-04 "  " 2.797E-04 "
     " 5.348E-04 "  " 1.023E-03 "  " 1.956E-03 "  " 3.740E-03 "  " 7.151E-03 "  " 1.367E-02 "  " 2.615E-02 "  " 5.000E-02 " )

Oh=( " 4.000E-02 "  " 4.000E-02 "  " 4.000E-02 "  " 4.000E-02 "  " 4.000E-02 "  " 4.000E-02 "  " 4.000E-02 "  " 4.000E-02 "
     " 4.000E-02 "  " 4.000E-02 "  " 4.000E-02 "  " 4.000E-02 "  " 5.429E-02 "  " 5.429E-02 "  " 5.429E-02 "  " 5.429E-02 "
     " 5.429E-02 "  " 5.429E-02 "  " 5.429E-02 "  " 5.429E-02 "  " 5.429E-02 "  " 5.429E-02 "  " 5.429E-02 "  " 5.429E-02 "
     " 7.368E-02 "  " 7.368E-02 "  " 7.368E-02 "  " 7.368E-02 "  " 7.368E-02 "  " 7.368E-02 "  " 7.368E-02 "  " 7.368E-02 "
     " 7.368E-02 "  " 7.368E-02 "  " 7.368E-02 "  " 7.368E-02 "  " 1.000E-01 "  " 1.000E-01 "  " 1.000E-01 "  " 1.000E-01 "
     " 1.000E-01 "  " 1.000E-01 "  " 1.000E-01 "  " 1.000E-01 "  " 1.000E-01 "  " 1.000E-01 "  " 1.000E-01 "  " 1.000E-01 " )

start=271


for i in {0..5};
do
cd  $(printf "%03d" $((start+8*i)))
srun -n 8 --gres=cpu:8 --exclusive burstingBubbleVE_ElasticLimit_v3 $MAXlevel ${Ec[8*i]} ${Oh[8*i]} $Bond $tmax & 
cd ../
cd  $(printf "%03d" $((start+8*i+1)))
srun -n 8 --gres=cpu:8 --exclusive burstingBubbleVE_ElasticLimit_v3 $MAXlevel ${Ec[8*i+1]} ${Oh[8*i+1]} $Bond $tmax &
cd ../
cd  $(printf "%03d" $((start+8*i+2)))
srun -n 8 --gres=cpu:8 --exclusive burstingBubbleVE_ElasticLimit_v3 $MAXlevel ${Ec[8*i+2]} ${Oh[8*i+2]} $Bond $tmax &
cd ../
cd  $(printf "%03d" $((start+8*i+3)))
srun -n 8 --gres=cpu:8 --exclusive burstingBubbleVE_ElasticLimit_v3 $MAXlevel ${Ec[8*i+3]} ${Oh[8*i+3]} $Bond $tmax &
cd ../
cd  $(printf "%03d" $((start+8*i+4)))
srun -n 8 --gres=cpu:8 --exclusive burstingBubbleVE_ElasticLimit_v3 $MAXlevel ${Ec[8*i+4]} ${Oh[8*i+4]} $Bond $tmax &
cd ../
cd  $(printf "%03d" $((start+8*i+5)))
srun -n 8 --gres=cpu:8 --exclusive burstingBubbleVE_ElasticLimit_v3 $MAXlevel ${Ec[8*i+5]} ${Oh[8*i+5]} $Bond $tmax &
cd ../
cd  $(printf "%03d" $((start+8*i+6)))
srun -n 8 --gres=cpu:8 --exclusive burstingBubbleVE_ElasticLimit_v3 $MAXlevel ${Ec[8*i+6]} ${Oh[8*i+6]} $Bond $tmax &
cd ../
cd  $(printf "%03d" $((start+8*i+7)))
srun -n 8 --gres=cpu:8 --exclusive burstingBubbleVE_ElasticLimit_v3 $MAXlevel ${Ec[8*i+7]} ${Oh[8*i+7]} $Bond $tmax &
cd ../

wait
done
#CC99='mpicc -std=c99' qcc -Wall -O2 -D_MPI=1 burstingBubbleVE_ElasticLimit_v2_Snellius.c -o burstingBubbleVE_ElasticLimit_v2_Snellius -lm

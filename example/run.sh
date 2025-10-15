#!/bin/bash
#SBATCH --job-name=g16
#SBATCH --output=%x_%A.out
#SBATCH --error=%x_%A.err
#SBATCH --partition=C9654 
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=96

export g16root="/opt/share/gaussian"
export GAUSS_ARCHDIR="$g16root/g16/arch"
export G16BASIS="$g16root/g16/basis"
export GAUSS_BSDDIR="$g16root/g16/bsd"
export GAUSS_EXEDIR="$g16root/g16"
export GAUSS_SCRDIR="$g16root/src"
export PATH="$PATH:$g16root/g16/bsd:$g16root/g16/local:$g16root/g16/extras:$g16root/g16"
export LD_LIBRARY_PATH="$LD_LIBRARY_PATH:$g16root/g16/bsd:$g16root/g16/local:$g16root/g16/extras:$g16root/g16"

# srun $GAUSS_EXEDIR/g16 < C1C2Im[dca]_r32.gjf > C1C2Im[dca]_r32.out
srun $GAUSS_EXEDIR/g16 < complex.gjf > complex.log

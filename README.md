# abaqus-signed-mises
Abaqus python script to compute signed mises equivalent stress

The signed mises stress is calculated according to the [Abaqus 2023 method](https://help.3ds.com/2023/english/dssimulia_established/simacaeoutrefmap/simaout-c-std-elementintegrationpointvariables.htm?contextscope=all#simaout-c-stdoutputvar-t-TensorsAndAssociatedPrincipalValuesAndInvariants-stdoutvargroup1), sign(trace(S)).
The fieldOutput result S_MISES is stored in each frame of the odb file.

Usage:

    abaqus python s_mises.py Job-1.odb [Job-2.odb ...]
    
![image](https://github.com/costerwi/abaqus-signed-mises/assets/7069475/b69663a9-d2c1-4193-bfd7-da950d73e6a6)

Repair the oneDNN `benchdnn` regression in `/app/oneDNN`.

The supplied fused-convolution case exits abnormally in run and simulation modes. Diagnose the failure in the project-owned source, make the smallest appropriate repair, and do not change the problem descriptor, benchmark modes, build configuration, or `/app/reproduce.sh`.

Run `/app/reproduce.sh` before and after the repair. Briefly report the failing phase, root cause, code change, and verification evidence for both modes. Do not make a hardware-performance claim from this task.

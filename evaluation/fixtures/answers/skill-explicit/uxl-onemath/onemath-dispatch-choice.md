Use oneMath runtime dispatch if the app should choose CPU or GPU backends at runtime. Use compile-time dispatch when the build selects an explicit backend and the code uses that backend selector directly.

For this app, start with runtime dispatch if deployment flexibility matters across CPU and NVIDIA GPU. Confirm the required backend libraries are built and installed, and make sure the app can link the selector library and load the backend libraries at runtime.

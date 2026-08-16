# Diagnosis

The first failing phase is the final link. CMake configuration succeeds and the `sycl_stage` object library compiles with `icpx -fsycl`, but the final `transitive_probe` link lacks `-fsycl` and reports unresolved `sycl::_V1` symbols. The OpenCL CPU runtime is not the cause.

`sycl_stage` consumes `UXL::SYCL` privately. Because its objects are embedded in `transform_pipeline`, that private object-library usage does not establish a link requirement for the final consumer. The repair adds the interface target to `transform_pipeline` as a public, link-only usage requirement. The pipeline architecture remains intact, host compilation does not receive an unnecessary device flag, and the final executable inherits the DPC++ SYCL link contract without global flags, installation paths, or library filenames.

A clean build shows the final `icpx` link command carrying `-fsycl`. The public run selects the OpenCL CPU, reports the physical CPU name, and matches checksum and expected output. No GPU or other accelerator backend was present, so those device paths remain unverified.

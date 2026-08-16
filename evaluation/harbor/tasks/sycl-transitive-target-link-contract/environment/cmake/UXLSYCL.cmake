add_library(uxl_sycl_contract INTERFACE)
add_library(UXL::SYCL ALIAS uxl_sycl_contract)

target_compile_options(uxl_sycl_contract INTERFACE -fsycl)
target_link_options(uxl_sycl_contract INTERFACE -fsycl)

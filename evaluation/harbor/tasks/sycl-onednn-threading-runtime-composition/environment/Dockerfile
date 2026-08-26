FROM intel/oneapi@sha256:e9db518398753434ee5aab9740a25f1d3134396a30be1569cfad8f8b0d90740c

ARG ONEDNN_COMMIT=e72f65d70e36f552f902d35614aef7aa54f3c796
ENV DEBIAN_FRONTEND=noninteractive
ADD https://github.com/uxlfoundation/oneDNN/archive/${ONEDNN_COMMIT}.tar.gz /tmp/onednn.tar.gz

RUN mkdir -p /opt/onednn \
    && tar -xzf /tmp/onednn.tar.gz --strip-components=1 -C /opt/onednn \
    && rm /tmp/onednn.tar.gz \
    && test -f /opt/onednn/examples/cpu_rnn_inference_int8.cpp \
    && cmake -S /opt/onednn -B /opt/onednn/build-sycl \
        -DCMAKE_C_COMPILER=icx \
        -DCMAKE_CXX_COMPILER=icpx \
        -DCMAKE_BUILD_TYPE=Release \
        -DDNNL_CPU_RUNTIME=SYCL \
        -DDNNL_GPU_RUNTIME=SYCL \
        -DDNNL_GPU_VENDOR=GENERIC \
        -DDNNL_BUILD_EXAMPLES=OFF \
        -DDNNL_BUILD_TESTS=OFF \
        -DONEDNN_BUILD_GRAPH=OFF \
        -DDNNL_ENABLE_WORKLOAD=INFERENCE \
        '-DDNNL_ENABLE_PRIMITIVE=RNN;REORDER;MATMUL' \
    && cmake --build /opt/onednn/build-sycl --parallel 8 \
    && cmake -S /opt/onednn -B /opt/onednn/build-openmp \
        -DCMAKE_C_COMPILER=icx \
        -DCMAKE_CXX_COMPILER=icpx \
        -DCMAKE_BUILD_TYPE=Release \
        -DDNNL_CPU_RUNTIME=OMP \
        -DDNNL_GPU_RUNTIME=NONE \
        -DDNNL_BUILD_EXAMPLES=OFF \
        -DDNNL_BUILD_TESTS=OFF \
        -DONEDNN_BUILD_GRAPH=OFF \
        -DDNNL_ENABLE_WORKLOAD=INFERENCE \
        '-DDNNL_ENABLE_PRIMITIVE=RNN;REORDER;MATMUL' \
    && cmake --build /opt/onednn/build-openmp --parallel 8

WORKDIR /app
COPY CMakeLists.txt runtime.cmake reproduce.sh /app/
RUN cp /opt/onednn/examples/cpu_rnn_inference_int8.cpp /app/ \
    && cp /opt/onednn/examples/example_utils.hpp /app/ \
    && chmod +x /app/reproduce.sh \
    && sha256sum /app/CMakeLists.txt /app/cpu_rnn_inference_int8.cpp /app/example_utils.hpp /app/reproduce.sh > /opt/protected.sha256

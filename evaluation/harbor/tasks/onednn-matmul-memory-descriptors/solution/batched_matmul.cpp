#include <dnnl.hpp>

#include <cstddef>
#include <cstdlib>
#include <iomanip>
#include <iostream>
#include <vector>

static float patterned(std::size_t index, int multiplier, int seed_term,
                       int modulus, int shift, float divisor) {
    return static_cast<float>((static_cast<int>(index) * multiplier + seed_term) % modulus - shift) / divisor;
}

int main(int argc, char** argv) {
    if (argc != 6) {
        std::cerr << "usage: batched_matmul B M K N seed\n";
        return 2;
    }
    const int batch = std::atoi(argv[1]);
    const int m = std::atoi(argv[2]);
    const int k = std::atoi(argv[3]);
    const int n = std::atoi(argv[4]);
    const int seed = std::atoi(argv[5]);
    if (batch <= 0 || m <= 0 || k <= 0 || n <= 0) return 2;

    std::vector<float> src(static_cast<std::size_t>(batch) * m * k);
    std::vector<float> weights(static_cast<std::size_t>(batch) * n * k);
    std::vector<float> dst(static_cast<std::size_t>(batch) * m * n, 0.0f);
    for (std::size_t i = 0; i < src.size(); ++i)
        src[i] = patterned(i, 17, seed * 13, 29, 14, 17.0f);
    for (std::size_t i = 0; i < weights.size(); ++i)
        weights[i] = patterned(i, 7, seed * 5, 23, 11, 19.0f);

    using dt = dnnl::memory::data_type;
    using tag = dnnl::memory::format_tag;
    const dnnl::memory::dims src_dims{batch, m, k};
    const dnnl::memory::dims weights_dims{batch, k, n};
    const dnnl::memory::dims dst_dims{batch, m, n};

    dnnl::engine engine(dnnl::engine::kind::cpu, 0);
    dnnl::stream stream(engine);
    const auto src_md = dnnl::memory::desc(src_dims, dt::f32, tag::abc);
    const dnnl::memory::dims weights_strides{n * k, 1, k};
    const auto weights_md = dnnl::memory::desc(weights_dims, dt::f32, weights_strides);
    const auto dst_md = dnnl::memory::desc(dst_dims, dt::f32, tag::abc);
    const auto matmul_desc = dnnl::matmul::desc(src_md, weights_md, dst_md);
    const auto primitive_desc = dnnl::matmul::primitive_desc(matmul_desc, engine);

    dnnl::memory src_memory(src_md, engine, src.data());
    dnnl::memory weights_memory(weights_md, engine, weights.data());
    dnnl::memory dst_memory(dst_md, engine, dst.data());
    dnnl::matmul(primitive_desc).execute(
        stream,
        {{DNNL_ARG_SRC, src_memory}, {DNNL_ARG_WEIGHTS, weights_memory}, {DNNL_ARG_DST, dst_memory}});
    stream.wait();

    std::cout << std::setprecision(9);
    for (float value : dst) std::cout << value << '\n';
    return 0;
}

#include <oneapi/dnnl/dnnl.hpp>

#include <cstddef>
#include <cstdint>
#include <iomanip>
#include <iostream>
#include <stdexcept>
#include <unordered_map>
#include <vector>

using namespace dnnl;

static float patterned_value(
        std::size_t index, int multiplier, int seed_term, int modulus,
        int shift, float divisor) {
    const int value = static_cast<int>(
            (index * static_cast<std::size_t>(multiplier)
                    + static_cast<std::size_t>(seed_term))
            % static_cast<std::size_t>(modulus));
    return static_cast<float>(value - shift) / divisor;
}

int main(int argc, char **argv) {
    if (argc != 6) {
        std::cerr << "usage: weight_reorder iterations channels height width seed\n";
        return 2;
    }

    const int iterations = std::stoi(argv[1]);
    const int channels = std::stoi(argv[2]);
    const int height = std::stoi(argv[3]);
    const int width = std::stoi(argv[4]);
    const int seed = std::stoi(argv[5]);
    if (iterations <= 0 || channels <= 0 || height <= 0 || width <= 0) {
        throw std::invalid_argument("iterations and tensor dimensions must be positive");
    }

    const std::size_t tensor_size = static_cast<std::size_t>(channels)
            * static_cast<std::size_t>(height) * static_cast<std::size_t>(width);
    const std::size_t weights_size
            = static_cast<std::size_t>(channels) * static_cast<std::size_t>(channels);

    std::vector<float> src(tensor_size);
    std::vector<float> weights(weights_size);
    std::vector<float> bias(static_cast<std::size_t>(channels));
    std::vector<float> output(tensor_size, 0.0f);
    for (std::size_t i = 0; i < src.size(); ++i)
        src[i] = patterned_value(i, 17, seed * 13, 37, 18, 19.0f);
    for (std::size_t i = 0; i < weights.size(); ++i)
        weights[i] = patterned_value(i, 11, seed * 7, 31, 15, 23.0f);
    for (std::size_t i = 0; i < bias.size(); ++i)
        bias[i] = patterned_value(i, 5, seed * 3, 17, 8, 29.0f);

    engine eng(engine::kind::cpu, 0);
    stream strm(eng);
    const memory::dims tensor_dims = {1, channels, height, width};
    const memory::dims weights_dims = {channels, channels, 1, 1};
    const memory::dims bias_dims = {channels};
    const memory::dims strides = {1, 1};
    const memory::dims padding = {0, 0};

    const auto tensor_md = memory::desc(
            tensor_dims, memory::data_type::f32, memory::format_tag::nhwc);
    const auto user_weights_md = memory::desc(
            weights_dims, memory::data_type::f32, memory::format_tag::oihw);
    const auto any_weights_md = memory::desc(
            weights_dims, memory::data_type::f32, memory::format_tag::any);
    const auto bias_md = memory::desc(
            bias_dims, memory::data_type::f32, memory::format_tag::a);

    auto conv_desc = convolution_forward::desc(prop_kind::forward_inference,
            algorithm::convolution_direct, tensor_md, any_weights_md, bias_md,
            tensor_md, strides, padding, padding);
    auto conv_pd = convolution_forward::primitive_desc(conv_desc, eng);
    if (conv_pd.weights_desc() == user_weights_md) {
        throw std::runtime_error(
                "test shape did not select an optimized weight descriptor");
    }

    auto user_src = memory(tensor_md, eng, src.data());
    auto user_weights = memory(user_weights_md, eng, weights.data());
    auto user_bias = memory(bias_md, eng, bias.data());
    auto user_dst = memory(tensor_md, eng, output.data());
    auto conv = convolution_forward(conv_pd);

    for (int iteration = 0; iteration < iterations; ++iteration) {
        // Incorrect integration assumption: constant weights are repacked for each
        // request even though the primitive descriptor and user weights are stable.
        auto conv_weights = memory(conv_pd.weights_desc(), eng);
        reorder(user_weights, conv_weights).execute(
                strm, user_weights, conv_weights);
        conv.execute(strm,
                {{DNNL_ARG_SRC, user_src}, {DNNL_ARG_WEIGHTS, conv_weights},
                        {DNNL_ARG_BIAS, user_bias}, {DNNL_ARG_DST, user_dst}});
        strm.wait();
    }

    std::cout << std::setprecision(9);
    for (float value : output)
        std::cout << value << '\n';
    return 0;
}

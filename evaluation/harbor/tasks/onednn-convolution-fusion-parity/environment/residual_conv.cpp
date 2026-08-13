#include <oneapi/dnnl/dnnl.hpp>

#include <cstdlib>
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
        std::cerr << "usage: residual_conv channels height width seed residual_scale\n";
        return 2;
    }

    const int channels = std::stoi(argv[1]);
    const int height = std::stoi(argv[2]);
    const int width = std::stoi(argv[3]);
    const int seed = std::stoi(argv[4]);
    const float residual_scale = std::stof(argv[5]);
    if (channels <= 0 || height <= 0 || width <= 0) {
        throw std::invalid_argument("tensor dimensions must be positive");
    }

    const std::size_t output_size = static_cast<std::size_t>(channels)
            * static_cast<std::size_t>(height) * static_cast<std::size_t>(width);
    const std::size_t weights_size
            = static_cast<std::size_t>(channels) * static_cast<std::size_t>(channels);

    std::vector<float> src(output_size);
    std::vector<float> weights(weights_size);
    std::vector<float> bias(static_cast<std::size_t>(channels));
    std::vector<float> residual(output_size);
    for (std::size_t i = 0; i < src.size(); ++i)
        src[i] = patterned_value(i, 17, seed * 13, 29, 14, 17.0f);
    for (std::size_t i = 0; i < weights.size(); ++i)
        weights[i] = patterned_value(i, 7, seed * 5, 19, 9, 23.0f);
    for (std::size_t i = 0; i < bias.size(); ++i)
        bias[i] = patterned_value(i, 5, seed * 3, 13, 6, 19.0f);
    for (std::size_t i = 0; i < residual.size(); ++i) {
        residual[i] = residual_scale
                * patterned_value(i, 11, seed * 3, 31, 15, 13.0f);
    }

    engine eng(engine::kind::cpu, 0);
    stream strm(eng);
    const memory::dims tensor_dims = {1, channels, height, width};
    const memory::dims weights_dims = {channels, channels, 1, 1};
    const memory::dims bias_dims = {channels};
    const memory::dims strides = {1, 1};
    const memory::dims padding = {0, 0};

    const auto user_tensor_md = memory::desc(
            tensor_dims, memory::data_type::f32, memory::format_tag::nchw);
    const auto user_weights_md = memory::desc(
            weights_dims, memory::data_type::f32, memory::format_tag::oihw);
    const auto bias_md = memory::desc(
            bias_dims, memory::data_type::f32, memory::format_tag::a);
    const auto any_tensor_md = memory::desc(
            tensor_dims, memory::data_type::f32, memory::format_tag::any);
    const auto any_weights_md = memory::desc(
            weights_dims, memory::data_type::f32, memory::format_tag::any);

    post_ops conv_ops;
    conv_ops.append_eltwise(1.0f, algorithm::eltwise_relu, 0.0f, 0.0f);
    conv_ops.append_sum(1.0f);
    primitive_attr conv_attr;
    conv_attr.set_post_ops(conv_ops);

    auto conv_desc = convolution_forward::desc(prop_kind::forward_inference,
            algorithm::convolution_direct, any_tensor_md, any_weights_md,
            bias_md, any_tensor_md, strides, padding, padding);
    auto conv_pd
            = convolution_forward::primitive_desc(conv_desc, conv_attr, eng);

    auto user_src = memory(user_tensor_md, eng, src.data());
    auto user_weights = memory(user_weights_md, eng, weights.data());
    auto user_bias = memory(bias_md, eng, bias.data());
    std::vector<float> output(output_size, 0.0f);
    auto user_dst = memory(user_tensor_md, eng, output.data());

    auto conv_src = memory(conv_pd.src_desc(), eng);
    auto conv_weights = memory(conv_pd.weights_desc(), eng);
    auto conv_dst = memory(conv_pd.dst_desc(), eng);
    reorder(user_src, conv_src).execute(strm, user_src, conv_src);
    reorder(user_weights, conv_weights).execute(strm, user_weights, conv_weights);
    reorder(user_dst, conv_dst).execute(strm, user_dst, conv_dst);

    convolution_forward(conv_pd).execute(strm,
            {{DNNL_ARG_SRC, conv_src}, {DNNL_ARG_WEIGHTS, conv_weights},
                    {DNNL_ARG_BIAS, user_bias}, {DNNL_ARG_DST, conv_dst}});
    reorder(conv_dst, user_dst).execute(strm, conv_dst, user_dst);
    strm.wait();

    std::cout << std::setprecision(9);
    for (float value : output)
        std::cout << value << '\n';
    return 0;
}

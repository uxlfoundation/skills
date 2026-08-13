#include "daal.h"

#include <cmath>
#include <cstddef>
#include <cstdint>
#include <iostream>
#include <unordered_set>
#include <vector>

using namespace daal;
using namespace daal::data_management;
namespace dfr = daal::algorithms::decision_forest::regression;

static std::uint64_t next_random(std::uint64_t& state) {
    state ^= state << 13;
    state ^= state >> 7;
    state ^= state << 17;
    return state;
}

int main(int argc, char** argv) {
    const std::size_t rows = argc > 1 ? std::stoul(argv[1]) : 10000;
    const std::size_t cols = argc > 2 ? std::stoul(argv[2]) : 10;
    std::uint64_t state = argc > 3 ? std::stoull(argv[3]) : 2468;
    const bool use_weights = argc > 4 && std::stoul(argv[4]) != 0;
    std::vector<double> x(rows * cols);
    std::vector<double> y(rows);
    std::vector<double> weights(rows);

    for (std::size_t row = 0; row < rows; ++row) {
        double target = 0.0;
        for (std::size_t col = 0; col < cols; ++col) {
            const double value = static_cast<double>(next_random(state) % 2000001) / 1000000.0 - 1.0;
            x[row * cols + col] = value;
            target += value * static_cast<double>((col + 1) * 7);
        }
        y[row] = target;
        weights[row] = 0.5 + static_cast<double>((row % 11) + 1) / 11.0;
    }

    auto data = HomogenNumericTable<double>::create(x.data(), cols, rows);
    auto labels = HomogenNumericTable<double>::create(y.data(), 1, rows);
    auto sample_weights = HomogenNumericTable<double>::create(weights.data(), 1, rows);

    dfr::training::Batch<double, dfr::training::defaultDense> train;
    train.input.set(dfr::training::data, data);
    train.input.set(dfr::training::dependentVariable, labels);
    if (use_weights) train.input.set(dfr::training::weights, sample_weights);
    train.parameter().nTrees = 1;
    train.parameter().featuresPerNode = cols;
    train.parameter().minObservationsInLeafNode = 1;
    train.parameter().minObservationsInSplitNode = 2;
    train.parameter().bootstrap = false;
    train.parameter().splitter = daal::algorithms::decision_forest::training::random;
    train.parameter().seed = 0;
    train.compute();

    dfr::prediction::Batch<double> predict;
    predict.input.set(dfr::prediction::data, data);
    predict.input.set(dfr::prediction::model, train.getResult()->get(dfr::training::model));
    predict.compute();

    auto predictions = predict.getResult()->get(dfr::prediction::prediction);
    BlockDescriptor<double> block;
    predictions->getBlockOfRows(0, rows, readOnly, block);
    const double* values = block.getBlockPtr();
    double squared_error = 0.0;
    std::unordered_set<long long> unique;
    for (std::size_t row = 0; row < rows; ++row) {
        const double delta = y[row] - values[row];
        squared_error += delta * delta;
        unique.insert(std::llround(values[row] * 1000000.0));
    }
    predictions->releaseBlockOfRows(block);

    const double mse = squared_error / static_cast<double>(rows);
    const std::size_t minimum_unique = rows - (rows / 100);
    std::cout << "rows=" << rows << " cols=" << cols << " weighted=" << use_weights
              << " mse=" << mse << " unique_predictions=" << unique.size() << '\n';
    return (std::isfinite(mse) && mse < 1.0e-12 && unique.size() >= minimum_unique) ? 0 : 1;
}

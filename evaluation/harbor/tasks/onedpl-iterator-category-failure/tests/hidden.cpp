#include <oneapi/dpl/algorithm>
#include <oneapi/dpl/execution>
#include <oneapi/dpl/memory>
#include <oneapi/dpl/numeric>

#include <cstddef>
#include <iostream>
#include <iterator>
#include <memory>
#include <numeric>
#include <vector>

template <typename Iterator>
class no_comma_iterator {
public:
    using iterator_category = typename std::iterator_traits<Iterator>::iterator_category;
    using value_type = typename std::iterator_traits<Iterator>::value_type;
    using difference_type = typename std::iterator_traits<Iterator>::difference_type;
    using pointer = typename std::iterator_traits<Iterator>::pointer;
    using reference = typename std::iterator_traits<Iterator>::reference;

    no_comma_iterator() = default;
    explicit no_comma_iterator(Iterator iterator) : iterator_(iterator) {}
    reference operator*() const { return *iterator_; }
    pointer operator->() const { return iterator_.operator->(); }
    reference operator[](difference_type n) const { return iterator_[n]; }
    no_comma_iterator& operator++() { ++iterator_; return *this; }
    no_comma_iterator operator++(int) { auto copy = *this; ++*this; return copy; }
    no_comma_iterator& operator--() { --iterator_; return *this; }
    no_comma_iterator operator--(int) { auto copy = *this; --*this; return copy; }
    no_comma_iterator& operator+=(difference_type n) { iterator_ += n; return *this; }
    no_comma_iterator& operator-=(difference_type n) { iterator_ -= n; return *this; }
    no_comma_iterator operator+(difference_type n) const { return no_comma_iterator(iterator_ + n); }
    no_comma_iterator operator-(difference_type n) const { return no_comma_iterator(iterator_ - n); }
    difference_type operator-(const no_comma_iterator& other) const { return iterator_ - other.iterator_; }
    bool operator==(const no_comma_iterator& other) const { return iterator_ == other.iterator_; }
    bool operator!=(const no_comma_iterator& other) const { return !(*this == other); }
    bool operator<(const no_comma_iterator& other) const { return iterator_ < other.iterator_; }
    bool operator<=(const no_comma_iterator& other) const { return iterator_ <= other.iterator_; }
    bool operator>(const no_comma_iterator& other) const { return iterator_ > other.iterator_; }
    bool operator>=(const no_comma_iterator& other) const { return iterator_ >= other.iterator_; }
    template <typename T> void operator,(T&&) = delete;

private:
    Iterator iterator_{};
};

template <typename Iterator>
no_comma_iterator<Iterator> wrap(Iterator iterator) {
    return no_comma_iterator<Iterator>(iterator);
}

int main() {
    std::vector<int> input(257);
    std::iota(input.begin(), input.end(), 1);

    std::vector<int> transformed(input.size(), 0);
    oneapi::dpl::transform(oneapi::dpl::execution::par,
                           wrap(input.begin()), wrap(input.end()), transformed.begin(),
                           [](int value) { return value * 3; });

    std::vector<long long> scanned(input.size(), 0);
    oneapi::dpl::transform_exclusive_scan(oneapi::dpl::execution::par,
                                          wrap(input.begin()), wrap(input.end()), scanned.begin(),
                                          7LL, std::plus<long long>{},
                                          [](int value) { return static_cast<long long>(value); });

    std::allocator<int> allocator;
    int* copied = allocator.allocate(input.size());
    oneapi::dpl::uninitialized_copy(oneapi::dpl::execution::par,
                                    wrap(input.begin()), wrap(input.end()), copied);

    bool ok = true;
    long long prefix = 7;
    for (std::size_t i = 0; i < input.size(); ++i) {
        ok = ok && transformed[i] == input[i] * 3;
        ok = ok && scanned[i] == prefix;
        ok = ok && copied[i] == input[i];
        prefix += input[i];
    }

    std::destroy(copied, copied + input.size());
    allocator.deallocate(copied, input.size());
    std::cout << "hidden no-comma algorithms " << (ok ? "passed" : "failed") << '\n';
    return ok ? 0 : 1;
}

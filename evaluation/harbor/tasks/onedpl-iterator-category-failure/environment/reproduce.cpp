#include <oneapi/dpl/algorithm>
#include <oneapi/dpl/execution>

#include <cstddef>
#include <iostream>
#include <iterator>
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

    template <typename T>
    void operator,(T&&) = delete;

private:
    Iterator iterator_{};
};

int main() {
    std::vector<int> input(64);
    std::iota(input.begin(), input.end(), 1);
    std::vector<int> output(input.size(), 0);
    using iterator = no_comma_iterator<std::vector<int>::iterator>;

    oneapi::dpl::transform(oneapi::dpl::execution::par,
                           iterator(input.begin()), iterator(input.end()), output.begin(),
                           [](int value) { return value * 2; });

    for (std::size_t i = 0; i < output.size(); ++i) {
        if (output[i] != input[i] * 2) {
            return 1;
        }
    }
    std::cout << "no-comma iterator transform passed\n";
    return 0;
}

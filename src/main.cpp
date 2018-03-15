// https://github.com/libbitcoin/libbitcoin-explorer/wiki/bx-input-sign


#include <vector>
#include <iostream>

#include <bitcoin/bitcoin/chain/transaction.hpp>


using namespace std;
using namespace libbitcoin;

int main () {

    hash_digest h;
    decode_hash(h, "7c3e880e7c93a7b01506188c36a239f70b561dfa622d0aa0d8f3b7403c94017d");
    cout << encode_hash(h) << endl;

    chain::output_point op(h, 0);

    chain::input in;
    chain::output o;
    chain::transaction(0, 0, std::vector<chain::input>{in}, std::vector<chain::output>{o});


}

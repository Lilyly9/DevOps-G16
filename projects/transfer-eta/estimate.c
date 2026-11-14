#include "estimate.h"

uintmax_t estimate_seconds(uintmax_t size_mib, uintmax_t rate_mib_per_second)
{
    return size_mib / rate_mib_per_second
        + (size_mib % rate_mib_per_second != 0);
}

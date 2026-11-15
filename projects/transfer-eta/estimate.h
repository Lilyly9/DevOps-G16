#ifndef TRANSFER_ETA_ESTIMATE_H
#define TRANSFER_ETA_ESTIMATE_H

#include <stdint.h>

/* Preconditions: size_mib and rate_mib_per_second are positive. */
uintmax_t estimate_seconds(uintmax_t size_mib, uintmax_t rate_mib_per_second);

#endif

#include <errno.h>
#include <inttypes.h>
#include <stdio.h>
#include <string.h>

#include "defaults.h"
#include "estimate.h"

static int parse_positive(const char *text, uintmax_t *value)
{
    if (*text == '\0') {
        return 0;
    }
    for (const char *digit = text; *digit != '\0'; ++digit) {
        if (*digit < '0' || *digit > '9') {
            return 0;
        }
    }

    errno = 0;
    *value = strtoumax(text, NULL, 10);
    return errno != ERANGE && *value > 0;
}

static void usage(FILE *stream)
{
    fputs("Usage: transfer-eta SIZE_MIB [RATE_MIB_PER_SECOND]\n", stream);
    fprintf(stream, "Default transfer rate: %d MiB/s\n", DEFAULT_RATE_MIB_S);
}

int main(int argc, char **argv)
{
    uintmax_t size_mib;
    uintmax_t rate_mib_per_second = DEFAULT_RATE_MIB_S;

    if (argc == 2 && strcmp(argv[1], "--help") == 0) {
        usage(stdout);
        return 0;
    }
    if (argc < 2 || argc > 3) {
        usage(stderr);
        return 2;
    }
    if (!parse_positive(argv[1], &size_mib)
        || (argc == 3 && !parse_positive(argv[2], &rate_mib_per_second))) {
        fputs("Size and rate must be positive base-10 integers in range.\n",
              stderr);
        return 2;
    }

    printf("eta_seconds=%" PRIuMAX "\n",
           estimate_seconds(size_mib, rate_mib_per_second));
    return 0;
}

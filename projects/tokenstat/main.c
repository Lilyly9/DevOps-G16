#include <stdio.h>

#include "stats.h"

int main(int argc, char **argv)
{
    if (argc != 2) {
        fprintf(stderr, "usage: %s FILE\n", argv[0]);
        return 2;
    }
    FILE *stream = fopen(argv[1], "r");
    if (stream == NULL) {
        perror(argv[1]);
        return 2;
    }
    Stats stats = stats_count(stream);
    fclose(stream);
    printf("config=%d words=%d lines=%d\n", stats_config(), stats.words, stats.lines);
    return 0;
}

#ifndef STATS_H
#define STATS_H

#include <stdio.h>

typedef struct {
    int words;
    int lines;
} Stats;

Stats stats_count(FILE *stream);
int stats_config(void);

#endif

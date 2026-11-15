#include <ctype.h>
#include <stdio.h>

#include "config.h"
#include "stats.h"

Stats stats_count(FILE *stream)
{
    Stats result = {0, 0};
    int character;
    int in_word = 0;
    while ((character = fgetc(stream)) != EOF) {
        if (character == '\n') {
            result.lines++;
        }
        if (isspace((unsigned char)character)) {
            in_word = 0;
        } else if (!in_word) {
            in_word = 1;
            result.words++;
        }
    }
    return result;
}

int stats_config(void)
{
    return DEFAULT_FIELD;
}

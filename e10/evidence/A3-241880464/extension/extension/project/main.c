#ifdef MODE
#include "mode.h"
#endif
#include <stdio.h>
#include "config.h"
int helper(void);
int main(void){printf("%d\n",VALUE+helper());return 0;}

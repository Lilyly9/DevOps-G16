# tokenstat

Small C/Make command-line tool that reports the configured field, word count and
line count of a text file. It is maintained by A2 (241880496) as the E11-E12
subject project.

* `main.c` drives the CLI.
* `stats.c` counts words and lines and reads `config.h`.
* `stats.h` is the shared interface.
* `extra.h` is added by the target commit and is intentionally missing from the
  `stats.o` rule, producing `MD(stats.o, extra.h)`.
* `e11e12-project.json` is the A2 target/rule map consumed by EChecker.

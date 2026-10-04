CC ?= cc
CFLAGS ?= -O0 -Wall -Wextra
PYTHON ?= python3
.DEFAULT_GOAL := all

ifeq ($(OS),Windows_NT)
EXEEXT = .exe
else
EXEEXT =
endif

.PHONY: all clean
all: app$(EXEEXT)

app$(EXEEXT): main.o
	$(CC) main.o -o $@

DEPS = main.c unused.h
main.o: $(DEPS)
	$(CC) $(CFLAGS) -c $< -o $@

clean:
	$(PYTHON) -c "from pathlib import Path; [Path(p).unlink(missing_ok=True) for p in ('main.o', 'main.d', 'app', 'app.exe')]"

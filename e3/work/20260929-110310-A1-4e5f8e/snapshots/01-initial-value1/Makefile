CC ?= cc
CFLAGS ?= -O0 -Wall -Wextra
PYTHON ?= python3

ifeq ($(OS),Windows_NT)
EXEEXT = .exe
else
EXEEXT =
endif

.PHONY: all clean
all: app$(EXEEXT)

app$(EXEEXT): main.o
	$(CC) main.o -o $@

# Fault fixture: config.h is missing; unused.h is redundant.
main.o: main.c unused.h
	$(CC) $(CFLAGS) -c main.c -o $@

clean:
	$(PYTHON) -c "from pathlib import Path; [Path(p).unlink(missing_ok=True) for p in ('main.o', 'app', 'app.exe')]"

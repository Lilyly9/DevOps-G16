# EChecker 实验小项目（E3 的 A2 基线）。
# C0/C1/C2 三个版本以 Git tag 保存；三个版本共用本 Makefile 的路径。
CC ?= cc
CFLAGS = -O0 -DMODE=7
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

# C0/C1 的声明：只写了 main.c 和 config.h。C1 之后 main.c 还会读取 feature.h。
main.o: main.c config.h
	$(CC) $(CFLAGS) -c main.c -o $@

clean:
	$(PYTHON) -c "from pathlib import Path; [Path(p).unlink(missing_ok=True) for p in ('main.o', 'app', 'app.exe')]"

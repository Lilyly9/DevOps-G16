CFLAGS = -O0

transfer-eta: eta_cli.o estimate.o
	gcc $(CFLAGS) eta_cli.o estimate.o -o transfer-eta

eta_cli.o: eta_cli.c estimate.h
	gcc $(CFLAGS) -c eta_cli.c -o eta_cli.o

estimate.o: estimate.c estimate.h
	gcc $(CFLAGS) -c estimate.c -o estimate.o

.PHONY: clean test
clean:
	rm -f transfer-eta transfer-eta.exe eta_cli.o estimate.o

test: transfer-eta
	sh tests/smoke.sh

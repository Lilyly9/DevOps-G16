CFLAGS = -O1 -std=c11 -Wall

app: main.o stats.o
	gcc main.o stats.o -o app

main.o: main.c stats.h
	gcc $(CFLAGS) -c main.c -o main.o

stats.o: stats.c stats.h
	gcc $(CFLAGS) -c stats.c -o stats.o

test: app
	@./app tests/sample.txt | grep -qx 'config=1 words=7 lines=3'

clean:
	rm -f main.o stats.o app

.PHONY: test clean

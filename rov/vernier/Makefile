# Makefile for goio
# (c) 2014 Edward Sternin

CFLAGS=-O2 -Wall #-Werror -Wstrict-prototypes
LIBS=-lusb -lGoIO
BINDIR=/usr/local/bin

all: goio

goio: goio.c Makefile
	$(CC) $(CFLAGS) -DVERSION="\"`date '+%Y-%b-%d-%H:%M'`\"" -DTARGET_OS_LINUX -o goio goio.c $(LIBS)

clean:
	rm -f `find . -name "*~" -or -name "*.[oa]" -or -name core`
	rm -f goio

install: all
	install -m 755 goio $(BINDIR)

DESTDIR ?= /usr/local
bindir = $(DESTDIR)/bin

INSTALL = install
INSTALL_PROGRAM = $(INSTALL)

PGM = gmail2maildir
INST_PGM = $(bindir)/$(PGM)

clean_files     = $(PGM)
clobber_files   = $(clean_files)
distclean_files = $(clobber_files)

all: $(PGM)

install: $(INST_PGM)

$(PGM): $(PGM).py
	$(INSTALL_PROGRAM) '$<' '$@'

$(INST_PGM): $(PGM)
	$(INSTALL_PROGRAM) '$<' '$@'
	
clean clobber distclean:
	$(RM) -- $($@_files)


.PHONY: all install clean clobber distclean
.DELETE_ON_ERROR:


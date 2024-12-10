CFLAGS += -O2 -disable-dimensions
CFLAGS += -I$(PWD)/src-local -I$(PWD)/../src-local

include $(BASILISK)/Makefile.defs

%.tst: %
	@mkdir -p $(basename $@)
	cp Bo*.dat $(basename $@)/
	cd $(basename $@) && ../$(basename $@) $(ARGS)
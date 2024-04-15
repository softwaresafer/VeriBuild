CC      = gcc
CFLAGS  = -Wall -O
INCLUDEFLAGS =
LDFLAGS =
OBJS    = foo.o bar.o
TARGETS = test_seq

.PHONY:all
all : $(TARGETS)

test_seq: $(OBJS)
	$(CC) -o $@ $^ $(LDFLAGS)

%.o:%.c
	$(CC) -o $@ -c $< $(CFLAGS) $(INCLUDEFLAGS)

%.d:%.c
	@set -e; rm -f $@; $(CC) -MM $< $(INCLUDEFLAGS) > $@.$$$$; \
	sed 's,\($*\)\.o[ :]*,\1.o $@ : ,g' < $@.$$$$ > $@; \
	rm -f $@.$$$$

-include $(OBJS:.o=.d)

.PHONY:clean
clean:
	rm -f $(TARGETS) *.o *.d *.d.*
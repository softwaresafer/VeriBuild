cc = gcc
prom = calc
source = main.c getch.c getop.c stack.c
 
$(prom): $(source)
    $(cc) -o $(prom) $(source)
-----------------------------------------
cc = gcc
prom = calc
deps = calc.h
obj = main.o getch.o getop.o stack.o
 
$(prom): $(obj)
    $(cc) -o $(prom) $(obj)

main.o: main.c $(deps)
    $(cc) -c main.c

getch.o: getch.c $(deps)
    $(cc) -c getch.c

getop.o: getop.c $(deps)
    $(cc) -c getop.c

stack.o: stack.c $(deps)
    $(cc) -c stack.c    
---------------------------------------------
cc = gcc
prom = calc
deps = calc.h
obj = main.o getch.o getop.o stack.o

$(prom): $(obj)
    $(cc) -o $(prom) $(obj)

%.o: %.c $(deps)
    $(cc) -c $< -o $@
---------------------------------------------
all: generated.h foo

generated.h: config
	gen config -o generated.h

foo: foo.c
	gcc foo.c -o foo
--------------------------------
helloworld : main.o print.o 
	gcc -o helloworld main.o print.o

main.o : main.c print.h
	gcc -c main.c

print.o : print.c print.h
	gcc -c print.c
-----------------------------------
cc = gcc
prom = helloworld
deps = print.h
obj = main.o print.o

$(prom): $(obj)
    $(cc) -o $(prom) $(obj)

%.o: %.c $(deps)
    $(cc) -c $< -o $@
---------------------------------
OBJS := foo.o bar.o

# link
proggie: $(OBJS)
	gcc $(OBJS) -o proggie

# compile
%.o: %.c
	gcc -c $(CFLAGS) $*.c -o $*.o

# remove compilation products
clean:
	rm -f proggie *.o
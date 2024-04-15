cc = gcc
prom = helloworld
deps = print.h
obj = main.o print.o

$(prom): $(obj)
	$(cc) -o $(prom) $(obj)

%.o: %.c $(deps)
	$(cc) -c $< -o $@

main.o: print.h
# A Makefile to generate archive file  

CFLAGS += -g -Wall -Werror -O2

CC := $(COMPILE_CROSS)gcc
GG := $(COMPILE_CROSS)g++

INC := -I ../main/inc 
INC += -I ../testA/inc 
INC += -I ../testB/inc 

SRC_FILES = $(wildcard src/*.cpp)
SRC_OBJ   = $(patsubst %.cpp,%.o,$(SRC_FILES))
SRC_LIB	  = testA.a

all:$(SRC_LIB)

$(SRC_LIB):$(SRC_OBJ)
	$(AR) rcs $@ $^ 
	cp $@ ../libs

$(SRC_OBJ):%.o:%.cpp
	$(GG) $(CFLAG) -c $< -o $@ $(INC)

clean:
	$(RM) $(SRC_OBJ) $(SRC_LIB)

distclean:
	$(RM) $(SRC_OBJ) $(SRC_LIB) 


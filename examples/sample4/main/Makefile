# A Makefile to generate archive file  
CC := $(COMPILE_CROSS)gcc
GG := $(COMPILE_CROSS)g++

CFLAGS += -g -Wall -Werror -O2
LDFLAGS += ./../libs/testA.a ./../libs/testB.a

INC := -I ../main/inc 
INC += -I ../testA/inc 
INC += -I ../testB/inc 

SRC_FILES = $(wildcard src/*.cpp)
SRC_OBJ   = $(patsubst %.cpp,%.o,$(SRC_FILES))
SRC_BIN	  = target_bin

all:$(SRC_BIN)

$(SRC_BIN):$(SRC_OBJ)
	$(CC)  -o $@  $^ $(INC) $(LDFLAGS)

$(SRC_OBJ):%.o:%.cpp
	$(GG) $(CFLAG) -c $< -o $@ $(INC)

clean:
	$(RM) $(SRC_OBJ) $(SRC_BIN) $(SRC_BIN)

distclean:
	$(RM) $(SRC_OBJ) $(SRC_BIN) $(SRC_BIN)


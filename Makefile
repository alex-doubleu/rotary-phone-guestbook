all: RotaryPhoneRecorder

RotaryPhoneRecorder: RotaryPhoneRecorder.cpp
	g++ -g -Wall -Wextra -Wpedantic RotaryPhoneRecorder.cpp -o bin/RotaryPhoneRecorder -lpthread -lm -ldl

run: all
	bin/RotaryPhoneRecorder

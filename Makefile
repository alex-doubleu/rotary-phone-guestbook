all: RotaryPhoneRecorder

RotaryPhoneRecorder: RotaryPhoneRecorder.cpp
	g++ -g -Wall -Wextra -Wpedantic RotaryPhoneRecorder.cpp -o RotaryPhoneRecorder -lpthread -lm -ldl

%% Experimenting with conversion from matlab to ipynb
% This is a second comment line within the header block
% Next, I will put in an empty line (new cell?) and then some code

% This is some code:
t = linspace(1, 6*pi, 100);
a = sin(t);
plot(a)
grid on

%% A new cell
b = cos(t);
plot(b);
b(1:10) % What happens if you print to the command line?
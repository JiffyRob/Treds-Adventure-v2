import string

lorum_ipsum = "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum."

lowercase_letters = string.ascii_lowercase
uppercase_letters = string.ascii_uppercase
letters = string.ascii_letters
numbers = string.digits
alphanumeric = letters + numbers
punctuation = string.punctuation
alphapunc = alphanumeric + punctuation
whitespace = string.whitespace
filename = alphanumeric + "_- ()"  # I think...

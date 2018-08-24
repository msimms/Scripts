#  MIT License
#
#  Copyright (c) 2018 Michael J Simms. All rights reserved.
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#  SOFTWARE.

import random

MAX_MODS = 'max modifications'
CONFIG_MODIFIERS = 'modifiers'
MOD_CHANGE = 'change'
MOD_INSERT = 'insert'
MOD_DELETE = 'delete'

class Fuzzer(object):
    """Randomly modifies data."""
    
    def __init__(self, config):
        self.config = config

    def max_modifications(self):
        """Accessor method for retrieving the max modifications setting, or the default if it was not provided."""
        if MAX_MODS in self.config:
            return self.config[MAX_MODS]
        return 1

    def allowed_modifications(self):
        """Accessor method for retrieving the allowed modifications setting, or the default if it was not provided."""
        if CONFIG_MODIFIERS in self.config:
            return self.config[CONFIG_MODIFIERS]
        return [MOD_CHANGE, MOD_INSERT, MOD_DELETE]

    def insert_random_data(self, data, data_len):
        """Inserts random data into the buffer, increasing it's length."""
        index = random.randint(0, data_len - 1)
        data[index:0] = bytearray([random.randint(0, 255)])
        return data, data_len + 1

    def delete_random_data(self, data, data_len):
        """Removes a random amount of data from the buffer."""
        index = random.randint(0, data_len - 1)
        amount_to_delete = random.randint(0, data_len - index - 1)
        data = data[:index] + data[index + amount_to_delete:]
        data_len = data_len - amount_to_delete
        return data, data_len

    def modify_random_byte(self, data, data_len):
        """Randomly selects and modifies a single byte in the buffer."""
        index = random.randint(0, data_len)
        new_byte = random.randint(0, 255)
        data[index] = new_byte
        return data

    def fuzz_once(self, data, data_len):
        """Performs a single modification to the buffer."""
        modifications = self.allowed_modifications()
        mod_to_perform = modifications[random.randint(0, len(modifications) - 1)]
        print mod_to_perform
        if mod_to_perform == MOD_CHANGE:
            data = self.modify_random_byte(data, data_len)
        elif mod_to_perform == MOD_INSERT:
            data, data_len = self.insert_random_data(data, data_len)
        elif mod_to_perform == MOD_DELETE:
            data, data_len = self.delete_random_data(data, data_len)
        return data, data_len

    def fuzz(self, data, data_len):
        """Entry point for fuzzing. Will apply the rules specified by the config that was passed to the constructor."""
        if isinstance(data, basestring):
            data = bytearray(data)
        max_mods = self.max_modifications()
        for _ in range(0,max_mods):
            data, data_len = self.fuzz_once(data, data_len)
        return data, data_len

def main():
    # Test data.
    data = "the quick brown fox jumps over the lazy dog."

    # Fuzz.
    fuzzer = Fuzzer({})
    data, _ = fuzzer.fuzz(data, len(data))
    print data

if __name__ == "__main__":
    main()

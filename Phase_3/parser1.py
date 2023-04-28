from anytree import Node, RenderTree, AsciiStyle

from scanner import Scanner


class Parser1:
    table = {}
    first = {}
    follow = {}
    starting_symbol = ''
    errors = ''

    def create_first_table(self):
        file = open('files/first_table.txt', 'r')
        lines = file.readlines()
        title = lines[0].strip('\n').split('\t')
        for i in range(1, len(lines)):
            line = lines[i].strip('\n').split('\t')
            set = []
            for j in range(1, len(line)):
                if line[j] == '+':
                    set.append(title[j - 1])
            self.first[line[0]] = set

    def create_follow_table(self):
        file = open('files/follow_table.txt', 'r')
        lines = file.readlines()
        title = lines[0].strip('\n').split('\t')
        for i in range(1, len(lines)):
            line = lines[i].strip('\n').split('\t')
            set = []
            for j in range(1, len(line)):
                if line[j] == '+':
                    set.append(title[j - 1])
            self.follow[line[0]] = set

    def is_terminal(self, candidate):
        if candidate == 'EPSILON':
            return False
        if self.follow.__contains__(candidate):
            return False
        return True

    def get_first(self, symbol):
        if self.is_terminal(symbol) or symbol == 'EPSILON':
            return [symbol]
        return self.first[symbol]

    def find_first_of_string(self, symbols):
        set = ['EPSILON']
        for i in range(len(symbols)):
            if set.__contains__('EPSILON'):
                set.remove('EPSILON')
                set.extend(self.get_first(symbols[i]))
        return set

    def create_parse_table(self):
        self.create_first_table()
        self.create_follow_table()
        file = open('files/grammer.txt', 'r')
        file_raw = open('files/grammer_raw.txt', 'r')
        lines = file.readlines()
        lines_raw = file_raw.readlines()
        self.starting_symbol = lines_raw[0].split(' ')[0]
        for i in range(len(lines_raw)):
            line_raw = lines_raw[i].strip('\n').split(' ')
            line = lines[i].strip('\n').split(' ')
            target = line_raw[0]
            first_set = self.find_first_of_string(line_raw[1:])
            for symbol in first_set:
                if not symbol == 'EPSILON':
                    self.table[(target, symbol)] = line[1:]
                else:
                    for member in self.follow[target]:
                        self.table[(target, member)] = line[1:]

        for non_terminal, f_set in self.follow.items():
            for member in f_set:
                if not self.table.__contains__((non_terminal, member)):
                    self.table[(non_terminal, member)] = 'synch'

    def get_class(self, token):
        if token[0] == 'NUMBER':
            return 'NUM'
        if token[0] == 'ID':
            return 'ID'
        if token[0] == 'KEYWORD' or token[0] == 'SYMBOL':
            return token[1]
        if token[1] == '$':
            return '$'

    def parse(self):
        self.create_parse_table()
        root_node = None
        stack = [('$', root_node), (self.starting_symbol, None)]
        top = stack[-1][0]
        scanner = Scanner('input.txt')
        token, line_no = scanner.get_next_token()
        eof = True
        while True:
            if top[0].startswith('#'):
                stack.pop()
                self.cod_gen(top, token)
                top = stack[-1][0]
            elif top == 'EPSILON':
                epsilon = stack.pop()
                Node('epsilon', epsilon[1])
                top = stack[-1][0]
            elif self.is_terminal(top):
                if token[0] == 'KEYWORD' or token[0] == 'SYMBOL':
                    check = token[1]
                elif token[0] == 'ID':
                    check = 'ID'
                else:
                    check = 'NUM'
                if top == check:
                    name = token[0]
                    if name == 'NUMBER': name = 'NUM'
                    Node('(' + name + ', ' + token[1] + ')', stack[-1][1])
                    stack.pop()
                    top = stack[-1][0]
                    token, line_no = scanner.get_next_token()
                else:
                    if top == '$':
                        break
                    print('error', top)
                    self.errors += '#' + str(line_no) + ' : syntax error, missing ' + top + '\n'
                    stack.pop()
                    if len(stack) > 0:
                        top = stack[-1][0]
                    else:
                        break
            else:
                table_cell = None
                if self.table.__contains__((top, self.get_class(token))):
                    table_cell = self.table[(top, self.get_class(token))]
                if table_cell is None:
                    if not token[1] == '$':
                        self.errors += '#' + str(line_no) + ' : syntax error, illegal ' + self.get_class(token) + '\n'
                        token, line_no = scanner.get_next_token()
                    else:
                        self.errors += '#' + str(line_no) + ' : syntax error, Unexpected EOF' + '\n'
                        eof = False
                        break
                elif table_cell == 'synch':
                    self.errors += '#' + str(line_no) + ' : syntax error, missing ' + top + '\n'
                    stack.pop()
                    top = stack[-1][0]
                else:
                    father = stack.pop()
                    if father[1] is not None:
                        father_node = Node(father[0], father[1])
                    else:
                        root_node = father_node = Node(father[0])
                    list = []
                    for member in table_cell:
                        node = (member, father_node)
                        list.append(node)
                    stack.extend(reversed(list))
                    top = stack[-1][0]
        if eof:
            Node('$', root_node)

        file = open("parse_tree.txt", "w", encoding='utf-8')
        for pre, fill, node in RenderTree(root_node):
            print("%s%s" % (pre, node.name), file=file)
        file.close()

        file = open("syntax_errors.txt", "w")
        if self.errors == '':
            self.errors = 'There is no syntax error.'
        file.write(self.errors)
        file.close()
        ###################
        temp = 0
        for i in range(len(self.symbol_table) - 1, -1, -1):
            if self.symbol_table[i][0] == 'main':
                temp = self.symbol_table[i]
                break
        if self.first_method != -100:
            self.program_block[self.first_method] = '(JP, ' + str(temp[6]) + ', , )'
        ######################
        for index in self.end:
            self.program_block[index] = '(JP, ' + str(len(self.program_block)) + ', , )'
        ######################
        file = open("output.txt", "w", encoding='utf-8')
        for i in range(len(self.program_block)):
            print(str(i) + '\t' + self.program_block[i], file=file)
        file.close()

        file = open("syntax_errors.txt", "w")
        if self.errors == '':
            self.errors = 'There is no syntax error.'
        file.write(self.errors)
        file.close()

    ######################
    new_code_addr = 0
    new_data_addr = 1008
    new_temp_addr = 2000
    stack = 3000
    # lexeme, (proc or func or var), num of args, type of var, scope, address variable, address of code, return?
    symbol_table = []
    semantic_stack = []
    program_block = []
    scope_stack = []
    current_called_function = ''
    current_function = ''
    scope = 1
    first_method = -100
    end = []
    req_for_link = []
    assignment_flag = 0

    def get_addr(self, lexeme):
        if lexeme == 'output':
            self.current_called_function = 'output'
        else:
            for element in reversed(self.symbol_table):
                if element[0] == lexeme:
                    if element[1] == 'func':
                        self.current_called_function = element[0]
                    return element[5]
            self.symbol_table.append((lexeme, 0, 0, 0, self.scope, self.new_data_addr, self.new_code_addr, 0))
            self.new_data_addr += 4
            return self.symbol_table[-1][5]
        return lexeme

    def get_temp(self):
        # self.program_block.append('(ASSIGN, #0' + ', ' + str(self.new_temp_addr) + ', )')
        self.new_temp_addr += 4
        return self.new_temp_addr - 4

    def in_main(self):
        for element in reversed(self.symbol_table):
            if element[0] == 'main':
                return True
        return False

    def cod_gen(self, top, token):
        print(self.semantic_stack)
        print('--- top is ', top, 'line no is ' + str(len(self.program_block)) + ' next token is ', token[1])
        if top == '#pid':
            self.semantic_stack.append(('direct', self.get_addr(token[-1])))
        elif top == '#push_num':
            self.semantic_stack.append(('literal', token[-1]))
        elif top == '#unify_power':
            self.unify_power()
        elif top == '#assign':
            second = self.semantic_stack.pop()
            first = self.semantic_stack.pop()
            if first[0] == 'literal':
                first = '#' + str(first[1])
            elif first[0] == 'direct':
                first = str(first[1])
            elif first[0] == 'indirect':
                first = '@' + str(first[1])
            else:
                print('error')
            if second[0] == 'literal':
                second = '#' + str(second[1])
            elif second[0] == 'direct':
                second = str(second[1])
            elif second[0] == 'indirect':
                second = '@' + str(second[1])
            else:
                print('error')
            self.program_block.append('(ASSIGN, ' + second + ', ' + first + ', )')
            self.assignment_flag = 0
        elif top == '#add':
            self.add_sub_mult('ADD')
        elif top == '#sub':
            self.add_sub_mult('SUB')
        elif top == '#mult':
            self.add_sub_mult('MULT')
        elif top == '#check':
            self.check()
        elif top == '#save_op':
            self.semantic_stack.append(('op', token[-1]))
        elif top == '#save':
            self.semantic_stack.append(('line', str(len(self.program_block))))
            self.scope_stack.append(('while', str(len(self.program_block))))
            self.program_block.append(('none'))
        elif top == '#save_if':
            self.semantic_stack.append(('line', str(len(self.program_block))))
            self.program_block.append(('none'))
        elif top == '#jpf_save':
            line_no = int(self.semantic_stack.pop()[1])
            condition = int(self.semantic_stack.pop()[1])
            current_line_no = len(self.program_block) + 1
            self.program_block[line_no] = '(JPF, ' + str(condition) + ', ' + str(current_line_no) + ', )'
            self.semantic_stack.append(('line', str(len(self.program_block))))
            self.program_block.append('@@@@@@@@@@@@@@@')
        elif top == '#jpf':
            line_no = int(self.semantic_stack.pop()[1])
            condition = int(self.semantic_stack.pop()[1])
            current_line_no = len(self.program_block)
            self.program_block[line_no] = '(JPF, ' + str(condition) + ', ' + str(current_line_no) + ', )'
        elif top == '#jp':
            line_no = self.semantic_stack.pop()[1]
            self.program_block[int(line_no)] = '(JP, ' + str(len(self.program_block)) + ', , )'
        elif top == '#set_return':
            temp, index = 0, 0
            for i in range(len(self.symbol_table) - 1, -1, -1):
                if self.symbol_table[i][1] == 'func':
                    temp = self.symbol_table[i]
                    index = i
                    break
            self.symbol_table[index] = (temp[0], temp[1], temp[2], temp[3], temp[4], temp[5], temp[6], 1)
            value = self.semantic_stack.pop()
            if temp[0] != 'main':
                if value[0] == 'literal':
                    self.program_block.append('(ASSIGN, #' + str(value[1]) + ', ' + '1000, )')
                    self.program_block.append('(JP, @1004, , )')
                elif value[0] == 'direct':
                    self.program_block.append('(ASSIGN, ' + str(value[1]) + ', ' + '1000, )')
                    self.program_block.append('(JP, @1004, , )')
                else:
                    print('error')
            else:
                self.end.append(len(self.program_block))
                self.program_block.append('(*********)')
        elif top == '#set_return_null':
            temp, index = 0, 0
            for i in range(len(self.symbol_table) - 1, -1, -1):
                if self.symbol_table[i][1] == 'func':
                    temp = self.symbol_table[i]
                    index = i
                    break
            if temp[7] == 1:
                return
            if temp[0] != 'main':
                self.symbol_table[index] = (temp[0], temp[1], temp[2], temp[3], temp[4], temp[5], temp[6], temp[7])
                self.program_block.append('(JP, @1004, , )')
            else:
                self.end.append(len(self.program_block))
                self.program_block.append('(*********)')
        elif top == '#while':
            while_start = self.semantic_stack.pop()[1]
            condition = self.semantic_stack.pop()[1]
            while_end = self.semantic_stack.pop()[1]
            self.program_block[int(while_start)] = '(JPF, ' + str(condition) + ', ' + str(
                len(self.program_block) + 1) + ', )'
            self.program_block.append('(JP, ' + str(while_end) + ', , )')
            current_scope = len(self.scope_stack)
            address = self.scope_stack.pop()[1]
            target = []
            for element in self.req_for_link:
                if element[1] == current_scope:
                    target.append(element)
            for element in target:
                self.program_block[element[2]] = '(JP, ' + str(len(self.program_block)) + ', , )'
            self.req_for_link = [x for x in self.req_for_link if x not in target]
        elif top == '#label':
            self.semantic_stack.append(('line', str(len(self.program_block))))
        elif top == '#call':
            if self.current_called_function == 'output' or self.semantic_stack[-2][1] == 'output':
                temp = self.semantic_stack.pop()
                self.semantic_stack.pop()
                if temp[0] == 'literal':
                    self.program_block.append('(PRINT, #' + str(temp[1]) + ', , )')
                elif temp[0] == 'direct':
                    self.program_block.append('(PRINT, ' + str(temp[1]) + ', , )')
                elif temp[0] == 'indirect':
                    self.program_block.append('(PRINT, @' + str(temp[1]) + ', , )')
                else:
                    print('error')
            else:
                temp = 0
                for i in range(len(self.symbol_table) - 1, -1, -1):
                    if self.symbol_table[i][0] == self.current_called_function:
                        temp = self.symbol_table[i]
                        break
                addr = temp[5]
                num_args = temp[2]
                check_list = []
                for i in range(num_args):
                    check_list.append(self.semantic_stack.pop())
                check_list.reverse()
                for element in check_list:
                    if element[0] == 'literal':
                        self.program_block.append('(ASSIGN, #' + str(element[1]) + ', ' + str(addr) + ', )')
                    elif element[0] == 'direct':
                        self.program_block.append('(ASSIGN, ' + str(element[1]) + ', ' + str(addr) + ', )')
                    elif element[0] == 'indirect':
                        self.program_block.append('(ASSIGN, @' + str(element[1]) + ', ' + str(addr) + ', )')
                    else:
                        print('error')
                    addr += 4
                self.semantic_stack.pop()
                temp_address = self.get_temp()
                if not self.in_main():
                    self.program_block.append('(ASSIGN, 1004, ' + str(temp_address) + ' )')
                self.program_block.append('(ASSIGN, #' + str(len(self.program_block) + 2) + ', 1004, )')
                self.program_block.append('(JP, ' + str(temp[6]) + ', , )')
                if not self.in_main():
                    self.program_block.append('(ASSIGN, ' + str(temp_address) + ', 1004, )')
                if temp[7] == 1 or self.assignment_flag:
                    address = self.get_temp()
                    self.program_block.append('(ASSIGN, 1000, ' + str(address) + ', )')
                    self.semantic_stack.append(('direct', address))

        elif top == '#def_func':
            if token[-1] != 'main' and self.first_method == -100:
                self.first_method = len(self.program_block)
                self.program_block.insert(len(self.program_block), '************')
            # lexeme, (proc or func or var), num of args, type of var, scope, address
            self.symbol_table.append(
                (token[-1], 'func', 0, None, self.scope, self.new_data_addr, len(self.program_block), 0))
            self.current_function = token[-1]
        elif top == '#add_var':
            for i in range(len(self.symbol_table) - 1, -1, -1):
                if self.symbol_table[i][0] == self.current_function:
                    temp = self.symbol_table[i]
                    self.symbol_table[i] = (temp[0], temp[1], temp[2] + 1, temp[3], temp[4], temp[5], temp[6], temp[7])
                    self.semantic_stack.pop()
                    break
        elif top == '#create_vector':
            first = self.semantic_stack.pop()
            name = self.semantic_stack.pop()
            # lexeme, (proc or func or var), num of args, type of var, scope, address variable, address of code
            for i in range(len(self.symbol_table) - 1, -1, -1):
                if self.symbol_table[i][5] == name[1]:
                    temp = self.symbol_table[i]
                    self.symbol_table[i] = (temp[0], 'array', 1, temp[3], temp[4], temp[5], temp[6], temp[7])
                    if first[0] == 'literal':
                        self.program_block.append('(ASSIGN, #' + str(first[1]) + ', ' + str(name[1]) + ', )')
                    elif first[0] == 'direct':
                        self.program_block.append('(ASSIGN, ' + str(first[1]) + ', ' + str(name[1]) + ', )')
                    else:
                        print('error')
                    break
        elif top == '#add_length':
            new_value = self.semantic_stack.pop()
            temp = self.symbol_table[-1]
            addr = str(temp[5] + 4 * int(temp[2]))
            if new_value[0] == 'literal':
                self.program_block.append('(ASSIGN, #' + str(new_value[1]) + ', ' + addr + ', )')
            elif new_value[0] == 'direct':
                self.program_block.append('(ASSIGN, ' + str(new_value[1]) + ', ' + addr + ', )')
            else:
                print('error')
            self.symbol_table[-1] = (temp[0], temp[1], temp[2] + 1, temp[3], temp[4], temp[5], temp[6], temp[7])
            self.new_data_addr += 4
        elif top == '#find_array_value':
            index = self.semantic_stack.pop()
            base_addr = self.check_for_indirect(self.semantic_stack.pop())
            print('changed to', base_addr)
            if index[0] == 'literal':
                if base_addr[0] == 'literal':
                    addr = str(int(base_addr[1]) + int(index[1]) * 4)
                    self.semantic_stack.append(('direct', addr))
                else:
                    temp_addr = str(self.get_temp())
                    self.program_block.append('(MULT, #4, #' + str(index[1]) + ', ' + temp_addr + ' )')
                    self.program_block.append('(ADD, ' + temp_addr + ', ' + str(base_addr[1]) + ', ' + temp_addr + ' )')
                    self.semantic_stack.append(('indirect', temp_addr))
            elif index[0] == 'direct':
                if base_addr[0] == 'literal':
                    base_addr = '#' + str(base_addr[1])
                else:
                    base_addr = str(base_addr[1])
                temp_addr = str(self.get_temp())
                self.program_block.append('(MULT, #4, ' + str(index[1]) + ', ' + temp_addr + ' )')
                self.program_block.append('(ADD, ' + temp_addr + ', ' + str(base_addr) + ', ' + temp_addr + ' )')
                self.semantic_stack.append(('indirect', temp_addr))
            elif index[0] == 'indirect':
                if base_addr[0] == 'literal':
                    base_addr = '#' + str(base_addr[1])
                else:
                    base_addr = str(base_addr[1])
                temp_addr = str(self.get_temp())
                self.program_block.append('(MULT, #4, @' + str(index[1]) + ', ' + temp_addr + ' )')
                self.program_block.append('(ADD, ' + temp_addr + ', ' + str(base_addr) + ', ' + temp_addr + ' )')
                self.semantic_stack.append(('indirect', temp_addr))
            else:
                print('error')
        elif top == '#end_func':
            index = 0
            for i in range(len(self.symbol_table) - 1, -1, -1):
                if self.symbol_table[i][0] == self.current_function:
                    index = i
                    break
            self.symbol_table = self.symbol_table[0:index + 1]
        elif top == '#continue':
            line = self.scope_stack[-1][1]
            self.program_block.append('(JP, ' + line + ', , )')
        elif top == '#break':
            self.req_for_link.append(('break', len(self.scope_stack), len(self.program_block)))
            self.program_block.append(('none'))
        elif top == '#assign_flag':
            self.assignment_flag = 1
        elif top == '':
            pass
        elif top == '':
            pass
        else:
            print('top is ', top)

    def check_for_indirect(self, base):
        temp = 0
        for i in range(len(self.symbol_table) - 1, -1, -1):
            if self.symbol_table[i][0] == self.current_function:
                temp = self.symbol_table[i]
                break
        print(base[1], temp[5] + ((temp[2] - 1) * 4))
        if int(base[1]) > temp[5] + ((temp[2] - 1) * 4):
            return ('literal', base[1])
        else:
            for i in range(len(self.symbol_table) - 1, -1, -1):
                if self.symbol_table[i][1] == 'func':
                    temp = self.symbol_table[i]
                    break
            if base[1] < temp[5]:
                return ('literal', base[1])
            else:
                return ('direct', base[1])

    def add_sub_mult(self, operation):
        second = self.semantic_stack.pop()
        first = self.semantic_stack.pop()
        if first[0] == 'indirect' and int(first[1]) >= 2000:
            self.program_block.append('(ASSIGN, @' + str(first[1]) + ', ' + str(first[1]) + ', )')
        if second[0] == 'indirect' and int(second[1]) >= 2000:
            self.program_block.append('(ASSIGN, @' + str(second[1]) + ', ' + str(first[1]) + ', )')
        if first[0] == 'literal' and second[0] == 'literal':
            sum = 0
            if operation == 'ADD':
                sum = int(first[1]) + int(second[1])
            elif operation == 'SUB':
                sum = int(first[1]) - int(second[1])
            elif operation == 'MULT':
                sum = int(first[1]) * int(second[1])
            else:
                print('error')
            self.semantic_stack.append(('literal', str(sum)))
        else:
            if second[0] == 'literal':
                second = '#' + str(second[1])
            else:
                second = str(second[1])
            if first[0] == 'direct' and int(first[1]) >= 2000:
                self.program_block.append(
                    '(' + operation + ', ' + str(first[1]) + ', ' + second + ', ' + str(first[1]) + ')')
                self.semantic_stack.append(first)
            else:
                if first[0] == 'literal':
                    first = '#' + str(first[1])
                else:
                    first = str(first[1])
                temp_addr = self.get_temp()
                self.program_block.append('(' + operation + ', ' + first + ', ' + second + ', ' + str(temp_addr) + ')')
                self.semantic_stack.append(('direct', temp_addr))

    def unify_power(self):
        power = self.semantic_stack.pop()
        number = self.semantic_stack.pop()
        if power[0] == 'literal':
            if number[0] == 'literal':
                sum = int(number[1]) ** int(power[1])
                self.semantic_stack.append(('literal', str(sum)))
            elif number[0] == 'direct':
                addr = self.get_temp()
                self.program_block.append('(ASSIGN, #1 ,' + str(addr) + ', )')
                self.semantic_stack.append(('direct', addr))
                for i in range(int(power[1])):
                    self.program_block.append(
                        '(' + 'MULT' + ', ' + str(number[1]) + ', ' + str(addr) + ', ' + str(addr) + ')')
                self.semantic_stack.append(('direct', addr))
            else:
                print('error')
        elif power[0] == 'direct':
            acc = self.get_temp()
            self.program_block.append('(ASSIGN, #1 ,' + str(acc) + ', )')
            count = self.get_temp()
            self.program_block.append('(ASSIGN, ' + str(power[1]) + ', ' + str(count) + ', )')
            line = len(self.program_block) + 1
            my_num = str(number[1])
            if number[0] == 'literal':
                my_num = '#' + str(number[1])
            self.program_block.append('(JPF, ' + str(count) + ', ' + str(line + 3) + ', )')
            self.program_block.append('(' + 'MULT' + ', ' + my_num + ', ' + str(acc) + ', ' + str(acc) + ')')
            self.program_block.append('(' + 'SUB' + ', ' + str(count) + ', ' + str(1) + ', ' + str(count) + ')')
            self.program_block.append('(JP, ' + str(line) + ', , )')
            self.semantic_stack.append(('direct', acc))
        else:
            print('error')

    def check(self):
        second = self.semantic_stack.pop()
        operator = self.semantic_stack.pop()[1]
        first = self.semantic_stack.pop()
        addr = self.get_temp()
        if operator == '==' or operator == '<':
            if second[0] == 'direct':
                second = str(second[1])
            elif second[0] == 'indirect':
                second = '@' + str(second[1])
            elif second[0] == 'literal':
                second = '#' + str(second[1])
            else:
                print('error')
            if first[0] == 'direct':
                first = str(first[1])
            elif first[0] == 'indirect':
                first = '@' + str(first[1])
            elif first[0] == 'literal':
                first = '#' + str(first[1])
            else:
                print('error')
            if operator == '==':
                operator = 'EQ'
            elif operator == '<':
                operator = 'LT'
            else:
                print('error')
            self.program_block.append('(' + operator + ', ' + first + ', ' + second + ', ' + str(addr) + ')')
            self.semantic_stack.append(('direct', addr))
        else:
            print('error')

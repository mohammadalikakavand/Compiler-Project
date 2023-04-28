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
        lines = file.readlines()
        self.starting_symbol = lines[0].split(' ')[0]
        for line in lines:
            line = line.strip('\n').split(' ')
            target = line[0]
            first_set = self.find_first_of_string(line[1:])
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
            if top == 'EPSILON':
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

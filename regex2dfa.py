import graphviz as gv


class Edge:
    def __init__(self, s, t, v):
        self.start = s
        self.end = t
        self.value = v


class RegexDFA:
    _reg = ""
    _value = []
    _node = 0
    _edges = []
    _edge_dict = {}
    _end = -1
    _has_nfa = False

    def __init__(self, regex):
        self._reg = regex
        self._value = []
        _op = []

        def judge_concat():
            if i + 1 < len(self._reg) and self._reg[i + 1] not in ['*', '|', ')']:
                _op.append('.')

        for i in range(0, len(self._reg)):
            ch = self._reg[i]
            if ch == '*':
                v = self._value.pop()
                self._value.append(('*', v))
                judge_concat()
            elif ch == '|':
                while _op[-1] == '.':
                    v1 = self._value.pop()
                    v2 = self._value.pop()
                    self._value.append((_op.pop(), v2, v1))
                _op.append('|')
            elif ch == '(':
                _op.append('(')
            elif ch == ')':
                op = _op.pop()
                while op != '(':
                    v1 = self._value.pop()
                    v2 = self._value.pop()
                    self._value.append((op, v2, v1))
                    op = _op.pop()
                judge_concat()
            else:
                self._value.append(('v', ch))
                judge_concat()
        while len(_op) != 0:
            v1 = self._value.pop()
            v2 = self._value.pop()
            self._value.append((_op.pop(), v2, v1))
        self._value = self._value[0]

    def print_regex(self):
        print(self._reg)

    def print_value(self):
        print(self._value)

    def _new_node(self):
        self._node += 1
        return self._node

    def _new_edge(self, s, t, v):
        e = self._edge_dict.get((s, t))
        if e is None:
            self._edges.append(Edge(s, t, v))
            self._edge_dict[(s, t)] = len(self._edges) - 1
        else:
            self._edges[e].value += "," + v

    def _generate_nfa(self, v, s, t=None):
        if v[0] == 'v':
            if t is None:
                t = self._new_node()
            self._new_edge(s, t, v[1])
            return s, t
        elif v[0] == '.':
            e1 = self._generate_nfa(v[1], s)
            e2 = self._generate_nfa(v[2], e1[1], t)
            return s, e2[1]
        elif v[0] == '|':
            if t is None:
                t = self._new_node()
            e1 = self._generate_nfa(v[1], s, t)
            e2 = self._generate_nfa(v[2], s, t)
            return s, t
        elif v[0] == '*':
            self._generate_nfa(v[1], s, s)
            if t is not None:
                self._new_edge(s, t, '_')
            return s, s

    def generate_nfa(self):
        self._node = 0
        self._edges = []
        self._edge_dict = {}
        e = self._generate_nfa(self._value, self._new_node())
        self._end = e[1]
        self._has_nfa = True

    def print_nfa_edges(self):
        if not self._has_nfa:
            self.generate_nfa()
        for e in self._edges:
            print(e.start, e.end, e.value)

    def draw_nfa(self, filename="nfa"):
        if not self._has_nfa:
            self.generate_nfa()
        g = gv.Digraph(format="pdf")
        for i in range(1, self._node + 1):
            if i == self._end:
                g.node(str(i), peripheries="2")
            else:
                g.node(str(i))
        for e in self._edges:
            g.edge(str(e.start), str(e.end), label=str(e.value))
        g.render(filename)


if __name__ == '__main__':
    dfa = RegexDFA('1(1010*|1(010)*1)*0')
    dfa.print_regex()
    dfa.print_value()
    dfa.draw_nfa('nfa1')

    print("----")

    dfa = RegexDFA('1(0|1)*101')
    dfa.print_regex()
    dfa.print_value()
    dfa.draw_nfa('nfa2')

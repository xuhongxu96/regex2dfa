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
    _edge_go = {}
    _value_set = set()
    _end = -1
    _has_nfa = False
    _dfa = []
    _has_dfa = False
    _dfa_node = []

    EPSILON = '\u03B5'

    def __init__(self, regex):
        self._reg = regex
        self._value = []
        self._value_set = set()
        self._node = 0
        self._edges = []
        self._edge_dict = {}
        self._edge_go = {}
        self._end = -1
        self._has_nfa = False
        self._dfa = []
        self._has_dfa = False
        self._dfa_node = []
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
                self._value_set.add(ch)
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
        s = str(s)
        t = str(t)
        v = str(v)
        e = self._edge_dict.get((s, t))
        if e is None:
            self._edges.append(Edge(s, t, v))
            self._edge_dict[(s, t)] = len(self._edges) - 1
        else:
            self._edges[e].value += "," + v
        eg = self._edge_go.get((s, v))
        if eg is None:
            self._edge_go[(s, v)] = [t]
        else:
            self._edge_go[(s, v)].append(t)

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
                self._new_edge(s, t, RegexDFA.EPSILON)  # epsilon == '\u03B5'
            return s, s

    def generate_nfa(self):
        self._node = 0
        self._edges = []
        self._edge_dict = {}
        self._edge_go = {}
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
            if i == 1:
                g.node(str(i), color="blue")
            elif i == self._end:
                g.node(str(i), peripheries="2", color="red")
            else:
                g.node(str(i))
        for e in self._edges:
            g.edge(e.start, e.end, label=e.value)
        g.render(filename)

    def _e_closure(self, i):
        if i is None:
            return []
        return [i] + self._edge_go.get((i, RegexDFA.EPSILON), [])

    def _move(self, i, k):
        return self._edge_go.get((i, k), [])

    def generate_dfa(self):
        self._has_dfa = False
        self._dfa_node = []
        self._dfa = []
        if not self._has_nfa:
            self.generate_nfa()
        e = []
        DT = []
        T = [self._e_closure(1)]
        while len(T) > 0:
            t = T.pop()
            DT.append(t)
            for k in self._value_set:
                U = set()
                for i in str(t):
                    for d in self._move(i, k):
                        if d == str(self._end):
                            U.add('T')
                        U = U.union(set(self._e_closure(d)))
                if len(U) == 0:
                    continue
                e.append((t, U, k))
                if U not in DT and U not in T:
                    T.append(U)
        for s, t, k in e:
            s = str(DT.index(s) + 1)
            t = str(DT.index(t) + 1)
            self._dfa.append((s, t, k))
        self._dfa_node = DT

    def print_dfa_edges(self):
        if not self._has_dfa:
            self.generate_dfa()
        print(self._dfa)

    def draw_dfa(self, filename="dfa"):
        if not self._has_dfa:
            self.generate_dfa()
        g = gv.Digraph(format="pdf")
        for i in range(1, len(self._dfa_node) + 1):
            if i == 1:
                g.node(str(i), color="blue")
            elif 'T' in self._dfa_node[i - 1]:
                g.node(str(i), peripheries="2", color="red")
            else:
                g.node(str(i))
        for s, t, k in self._dfa:
            g.edge(s, t, label=k)
        g.render(filename)

if __name__ == '__main__':
    dfa = RegexDFA('1(1010*|1(010)*1)*0')
    print("regex:")
    dfa.print_regex()
    print("tree:")
    dfa.print_value()
    print("NFA Edges:")
    dfa.print_nfa_edges()
    dfa.draw_nfa('nfa1')
    print("DFA Edges:")
    dfa.print_dfa_edges()
    dfa.draw_dfa('dfa1')

    print(" --- ")

    dfa = RegexDFA('1(0|1)*101')
    print("regex:")
    dfa.print_regex()
    print("tree:")
    dfa.print_value()
    print("NFA Edges:")
    dfa.print_nfa_edges()
    dfa.draw_nfa('nfa2')
    print("DFA Edges:")
    dfa.print_dfa_edges()
    dfa.draw_dfa('dfa2')

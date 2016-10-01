import graphviz as gv

"""UnionFind.py

Union-find data structure. Based on Josiah Carlson's code,
http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/215912
with significant additional changes by D. Eppstein.
"""


class UnionFind:
    """Union-find data structure.

    Each unionFind instance X maintains a family of disjoint sets of
    hashable objects, supporting the following two methods:

    - X[item] returns a name for the set containing the given item.
      Each set is named by an arbitrarily-chosen one of its members; as
      long as the set remains unchanged it will keep the same name. If
      the item is not yet part of a set in X, a new singleton set is
      created for it.

    - X.union(item1, item2, ...) merges the sets containing each item
      into a single larger set.  If any item is not yet part of a set
      in X, it is added to X as one of the members of the merged set.
    """

    def __init__(self):
        """Create a new empty union-find structure."""
        self.weights = {}
        self.parents = {}

    def __getitem__(self, object):
        """Find and return the name of the set containing the object."""

        # check for previously unknown object
        if object not in self.parents:
            self.parents[object] = object
            self.weights[object] = 1
            return object

        # find path of objects leading to the root
        path = [object]
        root = self.parents[object]
        while root != path[-1]:
            path.append(root)
            root = self.parents[root]

        # compress the path and return
        for ancestor in path:
            self.parents[ancestor] = root
        return root

    def __iter__(self):
        """Iterate through all items ever found or unioned by this structure."""
        return iter(self.parents)

    def union(self, *objects):
        """Find the sets containing the objects and merge them all."""
        roots = [self[x] for x in objects]
        heaviest = max([(self.weights[r], r) for r in roots])[1]
        for r in roots:
            if r != heaviest:
                self.weights[heaviest] += self.weights[r]
                self.parents[r] = heaviest


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
    _dfa_end = set()
    _dfa_go = {}

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
        self._dfa_end = set()
        self._dfa_go = {}
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
                while len(_op) != 0 and _op[-1] == '.':
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
        if RegexDFA.EPSILON in self._value_set:
            self._value_set.remove(RegexDFA.EPSILON)

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
            self._edges.append([s, t, v])
            self._edge_dict[(s, t)] = len(self._edges) - 1
        else:
            self._edges[e][2] += "," + v
        eg = self._edge_go.get((s, v))
        if eg is None:
            self._edge_go[(s, v)] = [t]
        else:
            self._edge_go[(s, v)].append(t)

    def _generate_nfa(self, v, s, t=None):
        if v[0] == 'v':
            if t is None and v[1] == RegexDFA.EPSILON:
                return s, s
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
        print(self._edges)

    def draw_nfa(self, filename="nfa"):
        if not self._has_nfa:
            self.generate_nfa()
        g = gv.Digraph(format="pdf")
        for i in range(1, self._node + 1):
            if i == self._end:
                g.node(str(i), peripheries="2", color="red")
            elif i == 1:
                g.node(str(i), color="blue")
            else:
                g.node(str(i))
        for s, t, v in self._edges:
            g.edge(s, t, label=v)
        g.render(filename)

    def _e_closure(self, i):
        if i is None:
            return []
        return {i}.union(self._edge_go.get((i, RegexDFA.EPSILON), []))

    def _move(self, i, k):
        return self._edge_go.get((i, k), [])

    def generate_dfa(self):
        self._has_dfa = False
        self._dfa_node = []
        self._dfa = []
        self._dfa_go = {}
        if not self._has_nfa:
            self.generate_nfa()
        e = []
        DT = []
        self._dfa_end = set()
        T = [self._e_closure('1')]
        while len(T) > 0:
            t = T.pop()
            DT.append(t)
            for k in self._value_set:
                U = set()
                for i in t:
                    i = str(i)
                    for d in self._move(i, k):
                        U = U.union(set(self._e_closure(d)))
                    if str(self._end) in U:
                        U.add('T')
                if len(U) == 0:
                    continue
                e.append((t, U, k))
                if U not in DT and U not in T:
                    T.append(U)
        for s, t, k in e:
            s = str(DT.index(s) + 1)
            t = str(DT.index(t) + 1)
            self._dfa.append((s, t, k))
            self._dfa_go[(s, k)] = t
        DT[0].add('S')
        self._dfa_node = DT
        self._has_dfa = True

    def minimize_dfa(self):
        if not self._has_dfa:
            self.generate_dfa()

        ct = len(self._dfa_node)
        T = set()
        S = set()
        for p in range(ct):
            if 'T' in self._dfa_node[p]:
                T.add(str(p + 1))
            else:
                S.add(str(p + 1))
        table = {}
        for i in range(1, ct + 1):
            for j in range(1, i):
                i = str(i)
                j = str(j)
                if (i in T and j in S) or (i in S and j in T):
                    table[(i, j)] = 1
                else:
                    table[(i, j)] = 0
        changed = True
        while changed:
            changed = False
            for k in table:
                for a in self._value_set:
                    i = self._dfa_go.get((str(k[0]), a))
                    j = self._dfa_go.get((str(k[1]), a))
                    if i is None and j is None:
                        continue
                    elif i is None or j is None:
                        if table[k] == 0:
                            table[k] = 1
                            changed = True
                        continue
                    if i == j: continue
                    if int(i) < int(j):
                        i, j = j, i
                    if table[k] == 0 and table[(i, j)] == 1:
                        table[k] = 1
                        changed = True
        N = [-1 for i in range(0, ct)]
        DT = {}

        uf = UnionFind()
        for k, v in table.items():
            if v == 0:
                uf.union(k[0], k[1])
        for i in range(1, ct + 1):
            if DT.get(uf[str(i)]) is None:
                DT[uf[str(i)]] = {i}
            else:
                DT[uf[str(i)]].add(i)
        DNode = []
        DFA = []
        for k, v in DT.items():
            DNode.append(v)
        for i in range(len(DNode)):
            for a in self._value_set:
                gi = self._dfa_go.get((str(list(DNode[i])[0]), a))
                if gi is not None:
                    gi = DNode.index(DT[uf[gi]])
                    DFA.append((str(i + 1), str(gi + 1), a))

        for n in DNode:
            if 1 in n:
                n.add('S')
            if str(list(n)[0]) in T:
                n.add('T')

        self._dfa_node = DNode
        self._dfa = DFA

    def print_dfa_edges(self):
        if not self._has_dfa:
            self.generate_dfa()
        print(self._dfa)

    def draw_dfa(self, filename="dfa"):
        if not self._has_dfa:
            self.generate_dfa()
        g = gv.Digraph(format="pdf")
        for i in range(1, len(self._dfa_node) + 1):
            if 'T' in self._dfa_node[i - 1]:
                g.node(str(i), peripheries="2", color="red")
            elif 'S' in self._dfa_node[i - 1]:
                g.node(str(i), color="blue")
            else:
                g.node(str(i))
        for s, t, k in self._dfa:
            g.edge(s, t, label=k)
        g.render(filename)

if __name__ == '__main__':
    # unsigned number
    dfa = RegexDFA('(dd*|dd*.dd*|.dd*)(' + RegexDFA.EPSILON +
                   '|10(s|' + RegexDFA.EPSILON
                   + ')dd*)|10(s|' + RegexDFA.EPSILON + ')dd*')
    dfa.minimize_dfa()
    dfa.draw_dfa()

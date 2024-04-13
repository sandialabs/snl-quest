import pyutilib.misc
import pyutilib.th as unittest
from pyutilib.misc.visitor import SimpleVisitor, ValueVisitor


class Node(object):

    def __init__(self):
        self.children = []
        self.num = 0

    def __str__(self):      #pragma: no cover
        return str(self.num)

class CountVisitor(SimpleVisitor):

    def __init__(self):
        self.count = 0

    def visit(self, node):
        self.count += 1
        node.num = self.count

    def finalize(self):
        return self.count

class CollectVisitor(SimpleVisitor):

    def __init__(self):
        self.ans = []

    def visit(self, node):
        self.ans.append(node.num)
        
    def finalize(self):
        return self.ans

class SumVisitor(ValueVisitor):

    def __init__(self):
        self.count = 0

    def visit(self, node, values):
        if values is None or len(values) == 0:
            self.count = node.num
        else:
            self.count = node.num + sum(values)
        return self.count
    
    def finalize(self, ans):
        return self.count


class Test(unittest.TestCase):

    def setUp(self):
        root = Node()
        root.children = [Node(), Node(), Node()]
        root.children[0].children = [Node(), Node(), Node()]
        root.children[0].children[0].children = [Node(), Node(), Node()]
        root.children[0].children[1].children = [Node(), Node(), Node()]
        root.children[0].children[2].children = [Node(), Node(), Node()]
        root.children[1].children = [Node(), Node(), Node()]
        root.children[1].children[0].children = [Node(), Node(), Node()]
        root.children[1].children[1].children = [Node(), Node(), Node()]
        root.children[1].children[2].children = [Node(), Node(), Node()]
        root.children[2].children = [Node(), Node(), Node()]
        root.children[2].children[0].children = [Node(), Node(), Node()]
        root.children[2].children[1].children = [Node(), Node(), Node()]
        root.children[2].children[2].children = [Node(), Node(), Node()]

        cvisitor = CountVisitor()
        cvisitor.bfs(root)
        self.root = root
        
    def test_bfs(self):
        visitor = CollectVisitor()
        ans = visitor.bfs(self.root)
        self.assertEqual(ans, [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40])

    def test_dfs_preorder(self):
        visitor = CollectVisitor()
        ans = visitor.dfs(self.root)
        self.assertEqual(ans, [1,2,5,14,15,16,6,17,18,19,7,20,21,22,3,8,23,24,25,9,26,27,28,10,29,30,31,4,11,32,33,34,12,35,36,37,13,38,39,40])

    def test_dfs_inorder(self):
        visitor = CollectVisitor()
        ans = visitor.dfs_inorder(self.root)
        self.assertEqual(ans, [14,5,15,5,16,2,17,6,18,6,19,2,20,7,21,7,22,1,23,8,24,8,25,3,26,9,27,9,28,3,29,10,30,10,31,1,32,11,33,11,34,4,35,12,36,12,37,4,38,13,39,13,40])

    def test_dfs_postorder(self):
        visitor = CollectVisitor()
        ans = visitor.dfs_postorder(self.root)
        self.assertEqual(ans, [14,15,16,5,17,18,19,6,20,21,22,7,2,23,24,25,8,26,27,28,9,29,30,31,10,3,32,33,34,11,35,36,37,12,38,39,40,13,4,1])

    def test_retval_dfs_postorder_tree(self):
        visitor = SumVisitor()
        ans = visitor.dfs_postorder_deque(self.root)
        self.assertEqual(ans, 820)
        visitor = SumVisitor()
        ans = visitor.dfs_postorder_stack(self.root)
        self.assertEqual(ans, 820)

    def test_retval_dfs_postorder_trivial(self):
        root = Node()
        root.num = 1
        visitor = SumVisitor()
        ans = visitor.dfs_postorder_deque(root)
        self.assertEqual(ans, 1)
        visitor = SumVisitor()
        ans = visitor.dfs_postorder_stack(root)
        self.assertEqual(ans, 1)

    def test_count_bfs(self):
        cvisitor = CountVisitor()
        ans = cvisitor.bfs(self.root)
        self.assertEqual(ans,40)
        
    def test_count_xbfs(self):
        cvisitor = CountVisitor()
        ans = cvisitor.xbfs(self.root)
        self.assertEqual(ans,40)
        

if __name__ == "__main__":
    unittest.main()

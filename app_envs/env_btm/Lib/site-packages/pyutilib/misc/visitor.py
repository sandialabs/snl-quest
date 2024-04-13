from collections import deque


class SimpleVisitor(object):

    def visit(self, node):  #pragma: no cover
        """
	    Visit a node in a tree and perform some operation on
	    it.

        This method should be over-written by a user
        that is creating a sub-class.

        Args:
            node: a node in a tree

        Returns:
            nothing
        """
        pass

    def children(self, node):
        """
        Return the children for a node in a tree.
        
        This method has a default implementation, but
        this implementation will likely be redefined
        to reflect the tree data structures used for 
        a specific application.

        Args:
            node: a node in a tree

        Returns:
            A list of children of the specified node.
        """ 
        return node.children
    
    def is_leaf(self, node):
        """
        Return :const:`True` if the node has no children.

        Args:
            node: a node in a tree

        Returns:
            :const:`True` if this node has no children, and :const:`False`
            otherwise
        """
        return len(node.children) == 0

    def finalize(self):     #pragma: no cover
        """
        Return the "final value" of the search.

        The default implementation returns :const:`None`, because
        the traditional visitor pattern does not return a value.

        Returns:
            The final value after the search.  Default is :const:`None`.
        """
        pass

    def bfs(self, node):
        """
        Perform breadth-first search starting at a node.

        Args:
            node: a node in a tree

        Returns:
            The value of the :func:`finalize` method.
        """
        dq = deque([node])
        while dq:
            current = dq.popleft()
            self.visit(current)
            if not self.is_leaf(current):
                dq.extend(self.children(current))
        return self.finalize()

    def xbfs(self, node):
        """
        Perform breadth-first search starting at a node,
        except that leaf nodes are immediately visited.

        Immediately visiting leaf nodes eliminates 
        storing and retrieving leaf nodes, which is an expense
        that may not be necessary if the search order can be
        changed from the standard BFS.

        Args:
            node: a node in a tree

        Returns:
            The value of the :func:`finalize` method.
        """
        dq = deque([node])
        while dq:
            current = dq.popleft()
            self.visit(current)
            for c in self.children(current):
                if self.is_leaf(c):
                    self.visit(c)
                else:
                    dq.append(c)
        return self.finalize()

    def dfs_preorder(self, node):
        """
        Perform depth-first search starting at a node,
        where nodes are visited before their children.

        Args:
            node: a node in a tree

        Returns:
            The value of the :func:`finalize` method.
        """
        dq = deque([node])
        while dq:
            current = dq.pop()
            self.visit(current)
            if not self.is_leaf(current):
                for c in reversed(self.children(current)):
                    dq.append(c)
        return self.finalize()

    dfs = dfs_preorder

    def dfs_postorder(self, node):
        """
        Perform depth-first search starting at a node,
        where nodes are visited after their children.

        Args:
            node: a node in a tree

        Returns:
            The value of the :func:`finalize` method.
        """
        expanded = set()
        dq = deque([node])
        while dq:
            current = dq[-1]
            if id(current) in expanded:
                dq.pop()
                self.visit(current)
            else:
                for c in reversed(self.children(current)):
                    dq.append(c)
                expanded.add(id(current))
        return self.finalize()

    def dfs_inorder(self, node):
        """
	    Perform depth-first search starting at a root node for
	    a binary tree, where a node is visited after the left 
        child and before the right child.

        Args:
            node: a node in a tree

        Returns:
            The value of the :func:`finalize` method.
        """
        expanded = set()
        dq = deque([node])
        while dq:
            current = dq.pop()
            if id(current) in expanded or self.is_leaf(current):
                self.visit(current)
            else:
                first = True
                for c in reversed(self.children(current)):
                    if first:
                        first = False
                    else:
                        dq.append(current)
                    dq.append(c)
                expanded.add(id(current))
        return self.finalize()


class ValueVisitor(object):

    def visit(self, node, values):  #pragma: no cover
        """
	    Visit a node in a tree and compute its value using
        the values of its children.

        This method should be over-written by a user
        that is creating a sub-class.

        Args:
            node: a node in a tree
            values: a list of values of this node's children

        Returns:
            The *value* for this node, which is computed using :attr:`values`
        """
        pass

    def children(self, node):
        """
        Return the children for a node in a tree.
        
        This method has a default implementation, but
        this implementation will likely be redefined
        to reflect the tree data structures used for 
        a specific application.

        Args:
            node: a node in a tree

        Returns:
            A list of children of the specified node.
        """ 
        return node.children
    
    def is_leaf(self, node):
        """
        Return :const:`True` if the node has no children.

        Args:
            node: a node in a tree

        Returns:
            :const:`True` if this node has no children, and :const:`False`
            otherwise
        """
        return len(node.children) == 0

    def finalize(self, ans):    #pragma: no cover
        """
        Return the "final value" of the search.

        The default implementation returns the value of the
        initial node (aka the root node), because
        this visitor pattern computes and returns value for each
        node to enable the computation of this value.

        Args:
            ans: The final value computed by the search method.

        Returns:
            The final value after the search. Defaults to simply
            returning :attr:`ans`.
        """
        return ans

    def visiting_potential_leaf(self, node):
        """ 
        Visit a node and return its value if it is a leaf.

        Args:
            node: a node in a tree

        Returns:
            A tuple: ``(flag, value)``.   If ``flag`` is False,
            then the node is not a leaf and ``value`` is :const:`None`.  
            Otherwise, ``value`` is used to compute the value of the 
            parent node.
        """
        #
        # This default implementation relise on the is_leaf() and visit()
        # methods.  While this provides a simple implementation,
        # in practice a more efficient implementation would 
        # ignore the is_leaf() method and implement this
        # method separately for a specific application.
        #
        if not self.is_leaf(node):
            return False, None
        return True, self.visit(node, None)

    def dfs_postorder_deque(self, node):
        """
        Perform depth-first search starting at a node,
        where nodes are visited after their children.

        This method uses a deque to manage the
        set of nodes that need to be explored.

        Args:
            node: a node in a tree

        Returns:
            The value of the :func:`finalize` method.
        """
        flag, value = self.visiting_potential_leaf(node)
        if flag:
            return value
        _values = [[]]
        expanded = set()
        dq = deque([node])
        while dq:
            current = dq[-1]
            if id(current) in expanded:
                dq.pop()
                values = _values.pop()
                _values[-1].append( self.visit(current, values) )
                continue
            flag, value = self.visiting_potential_leaf(current)
            if flag:
                _values[-1].append(value)
                dq.pop()
            else:
                for c in reversed(self.children(current)):
                    dq.append(c)
                expanded.add(id(current))
                _values.append( [] )
        return self.finalize(_values[-1][0])

    def dfs_postorder_stack(self, node):
        """
        Perform depth-first search starting at a node,
        where nodes are visited after their children.

        This method uses a stack to manage the
        set of nodes that need to be explored.

        Args:
            node: a node in a tree

        Returns:
            The value of the :func:`finalize` method.
        """
        flag, value = self.visiting_potential_leaf(node)
        if flag:
            return value
        _stack = [ (node, self.children(node), 0, len(self.children(node)), [])]
        #
        # Iterate until the stack is empty
        #
        # Note: 1 is faster than True for Python 2.x
        #
        while 1:
            #
            # Get the top of the stack
            #   _obj        Current expression object
            #   _argList    The arguments for this expression objet
            #   _idx        The current argument being considered
            #   _len        The number of arguments
            #
            _obj, _argList, _idx, _len, _result = _stack.pop()
            #
            # Iterate through the arguments
            #
            while _idx < _len:
                _sub = _argList[_idx]
                _idx += 1
                flag, value = self.visiting_potential_leaf(_sub)
                if flag:
                    _result.append( value )
                else:
                    #
                    # Push an expression onto the stack
                    #
                    _stack.append( (_obj, _argList, _idx, _len, _result) )
                    _obj                    = _sub
                    _argList                = self.children(_sub)
                    _idx                    = 0
                    _len                    = len(_argList)
                    _result                 = []
            #
            # Process the current node
            #
            ans = self.visit(_obj, _result)
            if _stack:
                #
                # "return" the recursion by putting the return value on the end of the results stack
                #
                _stack[-1][-1].append( ans )
            else:
                return self.finalize(ans)



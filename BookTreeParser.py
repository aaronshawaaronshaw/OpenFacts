from HTMLParser import HTMLParser
import re
import sys

class Stack(object):
  def __init__(self):
    self.items = []

  def is_empty(self):
    return self.items == []

  def push(self, item):
    self.items.append(item)

  def pop(self):
    return self.items.pop()

  def pop_quiet(self):
    del self.items[-1]

  def peek(self):
    return self.items[-1]

  def clear(self):
    self.items == []

  def size(self):
    return len(self.items)

  def count(self, item):
    return self.items.count(item)

  def __repr__(self):
    return str(self.items)

def enum(*sequential, **named):
    enums = dict(zip(sequential, range(len(sequential))), **named)
    reverse = dict((value, key) for key, value in enums.iteritems())
    enums['to_string'] = reverse
    return type('Enum', (), enums)

NodeType = enum('BOOK', 'UNIT', 'CHAPTER', 'PAGE', 'SECTION', 'FEATURE', 'TEXT')
node_type_assign = {
  'note' : NodeType.FEATURE,
  'section' : NodeType.SECTION,
  'page' : NodeType.PAGE,
  'chapter' : NodeType.CHAPTER,
  'unit' : NodeType.UNIT
}

class BookTreeNode(object):
  def __init__(self, parent, sibling_prev, node_type, cargo):
    self.parent = parent
    self.children = []
    self.sibling_prev = sibling_prev
    self.sibling_next = None
    self.node_type = node_type
    self.cargo = cargo

    if parent is not None:
      parent.add_child(self)
    self.sibling_prev = sibling_prev
    if sibling_prev is not None:
      sibling_prev.sibling_next = self

  def add_child(self, child):
    self.children.append(child)

  def rm_child(self, child):
    self.children.remove(child)

  def print_as_root(self, level=0):
    #if self.node_type != NodeType.TEXT:
    print "#",
    for _ in range(level):
      print "|",
    print self
    for child in self.children:
      child.print_as_root(level + 1)

  def __repr__(self):
    return "<BOOK_NODE node_type=" + NodeType.to_string[self.node_type] + " cargo=" + str(self.cargo) + ">"

class BookTreeParser(HTMLParser):
  # TODO: Instead of a group of connected nodes, form a tree object with actual properties and methods
  def __init__(self):
    HTMLParser.__init__(self)
    self.full_parent_level = 0
    self.relevant_levels = [0]
    self.tree_parent_stack = Stack()
    self.titling = False
    self.within_metadata = False
    self.last_sibling = None

    self.text_buffer = ''

    book_root = BookTreeNode(None, None, NodeType.BOOK, None)
    self.root = book_root
    self.tree_parent_stack.push(book_root)

  def handle_starttag(self, tag, attrs):
    self.full_parent_level += 1
    if not self.within_metadata:
      if tag == 'title':
        self.titling = True
      elif tag in ('div', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'section'):
        if tag == 'section':
          attrs.append(('data-type', 'section'))
        for attr_pair in attrs:
          if attr_pair[0] == 'data-type':
            data_type = attr_pair[1]
            if data_type == 'metadata':
              self.within_metadata = True
              self.relevant_levels.append(self.full_parent_level)
            elif data_type in node_type_assign:

              # Just in case
              self.titling = False

              self.relevant_levels.append(self.full_parent_level)
              node_type = node_type_assign[data_type]
              opened_node = BookTreeNode(self.tree_parent_stack.peek(), self.last_sibling, node_type, None)
              self.tree_parent_stack.push(opened_node)

              if self.last_sibling is not None and self.last_sibling.node_type == NodeType.TEXT:
                common_parent = self.last_sibling.parent
                sentences = re.findall('[^?.]*?[.?]', self.last_sibling.cargo)
                prev_it_sibling = self.last_sibling.sibling_prev
                for nth_sent in sentences:
                  current_sentence = BookTreeNode(common_parent, prev_it_sibling, NodeType.TEXT, nth_sent)
                  prev_it_node = current_sentence
                common_parent.rm_child(self.last_sibling)

              self.last_sibling = None
            elif data_type in ('document-title', 'title'):
              self.titling = True

  def handle_endtag(self, tag):
    if self.full_parent_level == self.relevant_levels[-1]:
      if self.within_metadata:
        self.within_metadata = False
      else:
        if self.last_sibling is not None and self.last_sibling.node_type == NodeType.TEXT:
          common_parent = self.last_sibling.parent
          sentences = self.last_sibling.cargo.split('.')
          prev_it_sibling = self.last_sibling.sibling_prev
          for nth_sent in sentences:
            current_sentence = BookTreeNode(common_parent, prev_it_sibling, NodeType.TEXT, nth_sent)
            prev_it_node = current_sentence
          common_parent.rm_child(self.last_sibling)
        self.last_sibling = self.tree_parent_stack.pop()
      del self.relevant_levels[-1]
    self.full_parent_level -= 1

  def handle_startendtag(self, tag, attrs):
    # Don't know if this is important for our purposes
    pass

  def handle_data(self, data):
    # TODO: instead of immediately parsing into nodes, store in memory until surrounding text nodes are also parsed
    # We want to prevent something like <p> Some text <span> within </span> the same sentence. </p> from becoming a problem
    # May also help with entity-ref TODO
    if not self.within_metadata:
      if not data.isspace():
        text = re.sub( '\s+', ' ', data)
        parent = self.tree_parent_stack.peek()
        if self.titling:
          if parent.cargo is None and parent.node_type != NodeType.FEATURE:
            parent.cargo = text
            self.titling = False
          elif parent.node_type == NodeType.FEATURE:
            self.titling = False
        else:
          if self.last_sibling is not None and self.last_sibling.node_type == NodeType.TEXT:
            self.last_sibling.cargo += text
          else:
            current_node = BookTreeNode(parent, self.last_sibling, NodeType.TEXT, text)
            self.last_sibling = current_node
  
  def handle_entityref(self, data):
    # TODO: Convert to unicode and append into surrounding text
    pass

  def handle_charref(self, name):
    print "---Parser Warning: Encountered CharRef!---"
    print name
  
  def handle_comment(self, data):
    pass

  def handle_decl(self, decl):
    pass

  def unknown_decl(self,data):
    pass

  def handle_pi(self, data):
    pass

args = sys.argv
usage = "Usage: python BookTreeParser.py [-p] file_name|-help"


if len(args) < 2 or args[1] == '-help':
  print usage
else:
  flag_print_tree = False
  if '-p' in args:
    flag_print_tree = True
    args.remove('-p')

  parser = BookTreeParser()
  with open(sys.argv[1]) as xhtml_input:
    parser.feed(xhtml_input.read())
  if flag_print_tree:
    parser.root.print_as_root()
  print "DONE"

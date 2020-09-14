#!/usr/bin/env python

import argparse
import csv
import sys

import types


class Node:
    def __init__(
        self,
        name,
        parent=None,
        postcode=None,
        is_town=False,
        ag_sub_id=None,
        ag_sub_cde=None,
        local_gov=None,
        children=None,
    ):
        self.name = name
        self.parent = parent
        self.postcode = postcode
        self.is_town = is_town
        self.ag_sub_id = ag_sub_id
        self.ag_sub_cde = ag_sub_cde
        self.local_gov = local_gov
        if children is None:
            self.children = []
        else:
            self.children = children

    def __iter__(self):
        # print("HERE:", self.children)
        yield self
        for node in self.children:
            node_iter = iter(node)
            for part in node_iter:
                yield part

    def __hash__(self):
        return hash(str(self))

    def add_child(self, child_node):
        if child_node.name not in [n.name for n in self.children]:
            self.children.append(child_node)
            child_node.parent = self

    def __repr__(self):
        return "Node({}{})".format(
            self.name,
            (": " + ", ".join([c.name for c in self.children]))
            if len(self.children)
            else "",
        )


class LocationTree:
    def __init__(self):
        self.name_to_node = {}
        self.root = Node(name="root", parent=None)

    def add_node(self, node, parent=None):
        if parent is None:
            parent = self.root
            self.root.children.append(node)
            for child in self.root.children:
                if child.name in node.children:
                    child.parent = node
        node.parent = parent
        parent.add_child(node)
        self.name_to_node[node.name] = node

    def add_by_name(self, name, child_name):
        if child_name in self.name_to_node:
            child_node = self.name_to_node[child_name]
        else:
            child_node = Node(name=child_name)
            self.name_to_node[child_name] = child_node
        if name in self.name_to_node:
            node = self.name_to_node[name]
        else:
            node = Node(name=name)
            self.name_to_node[name] = node
            self.root.add_child(node)
        node.add_child(child_node)

    def depth(self):
        max_depth = 0
        node_depths = {self.root: 0}
        for node in self:
            if node.parent is None:
                continue
            try:
                depth = node_depths[node.parent] + 1
            except KeyError:
                raise KeyError(
                    "child: {} parent: {}".format(node.name, node.parent.name)
                )
            if depth > max_depth:
                max_depth = depth
            node_depths[node] = depth
        return max_depth

    def find_node_by_name(self, name):
        nodes = []
        for node in self:
            if node.name == name:
                nodes.append(node)
        return nodes

    def is_ancestor(self, ancestor_node, node):
        if node is None:
            # should this return an error if a lookup is attempted on a name that doesn't
            # exist in the tree?
            return False

        parent = node.parent
        while parent is not None:
            if parent == ancestor_node:
                return True
            parent = parent.parent
        return False

    def __iter__(self):
        for node in iter(self.root):
            yield node

    def __repr__(self):
        return "Tree({})".format(",".join([str(n) for n in self]))


def afrigis_to_tree(input_file, transform=False, exclude=[]):
    reader = csv.DictReader(input_file, delimiter="\t")
    children = {}
    tree = LocationTree()
    town_count = 0
    if transform:
        exclude = [
            (t[0].upper().replace(" ", "-"), t[1].upper().replace(" ", "-"))
            for t in exclude
        ]
        cape_town_name = "CAPE-TOWN"
    else:
        cape_town_name = "Cape Town"
    cape_town_node = Node(name=cape_town_name)
    tree.add_node(cape_town_node)
    excluded_places_set = set(exclude)
    for row in reader:
        suburb = row["SUBURB"]
        town = row["TOWN"]
        sub_id = row["AG_SUB_ID"]
        sub_cde = row["AG_SUB_CDE"]
        postcode = row["STRCODE"]
        municipality = row["LOCALMUNICIPALITY"]
        in_ct = (
            True
            if municipality == "City of Cape Town Metropolitan Municipality"
            else False
        )
        if transform:
            suburb = suburb.upper().strip().replace(" ", "-")
            town = town.upper().strip().replace(" ", "-")
            municipality = municipality.upper().strip().replace(" ", "-")

        if (suburb, town) in excluded_places_set:
            # this is to deal with places like Mfuleni, Khayelitsha
            continue        

        # print(suburb, town, municipality)
        # if suburb == town:
        #     # add at root of tree
        #     node = Node(town, local_gov=municipality)
        #     tree.add_node(node)
        #     continue
        if town == "Cape Town" or town == "CAPE-TOWN":
            node = cape_town_node
        else:
            node_list = [
                node
                for node in tree.find_node_by_name(town)
                if node.local_gov == municipality
            ]
            assert len(node_list) < 2, "found duplicate town name {}".format(town)
            if len(node_list) == 0:
                # this is a town name that we have not seen before
                town_count += 1
                ct_parent = cape_town_node if in_ct else None
                node = Node(
                    town, postcode=postcode, is_town=True, local_gov=municipality
                )
                if suburb == town:
                    node.ag_sub_id = sub_id
                    node.ag_sub_cde = sub_cde
                tree.add_node(node, parent=ct_parent)
            else:
                # town is known
                node = node_list[0]
                # if we known this town and the suburb and town names are identical,
                # skip further processing
                if suburb == town:
                    node.ag_sub_id = sub_id
                    node.ag_sub_cde = sub_cde
                    continue

        # print(suburb, town)

        if suburb != town:
            child_node = Node(
                suburb,
                postcode=postcode,
                ag_sub_id=sub_id,
                ag_sub_cde=sub_cde,
                local_gov=municipality,
            )
            tree.add_node(child_node, parent=node)
    # print(tree)
    return tree


def test_tree():
    tree = LocationTree()
    a_node = tree.add_node(Node(name="A"))
    tree.add_node(Node(name="B"))
    node_list = tree.find_node_by_name("B")
    assert len(node_list) == 1
    b_node = node_list[0]
    c_node = Node(name="C")
    d_node = Node(name="D")
    e_node = Node(name="E")
    tree.add_node(c_node, parent=b_node)
    tree.add_node(d_node, parent=c_node)
    tree.add_node(e_node, parent=d_node)

    assert tree.depth() == 4, "expected depth 4, got depth {}".format(tree.depth())
    assert tree.is_ancestor(a_node, b_node) == False
    assert tree.is_ancestor(b_node, c_node) == True
    assert tree.is_ancestor(c_node, b_node) == False
    assert tree.is_ancestor(b_node, e_node) == True
    # tree_list = list(tree)
    # print(tree_list)


def test_afrigis_tree(input_file):
    tree = afrigis_to_tree(input_file)
    # print(tree)
    cape_town_node = tree.find_node_by_name("Cape Town")
    assert len(cape_town_node) == 1
    cape_town_node = cape_town_node[0]

    ceres_node = tree.find_node_by_name("Ceres")
    assert len(ceres_node) == 1
    ceres_node = ceres_node[0]

    muizenberg_node = tree.find_node_by_name("Muizenberg")
    assert len(muizenberg_node) == 1
    muizenberg_node = muizenberg_node[0]

    assert tree.is_ancestor(cape_town_node, ceres_node) == False
    assert tree.is_ancestor(cape_town_node, muizenberg_node) == True

    langa_node = tree.find_node_by_name('Langa')
    assert len(langa_node) == 1
    langa_node = langa_node[0]
    assert langa_node.ag_sub_id == '10618'

if __name__ == "__main__":
    test_tree()

    parser = argparse.ArgumentParser()
    parser.add_argument("input_file", type=argparse.FileType())
    args = parser.parse_args()

    test_afrigis_tree(args.input_file)

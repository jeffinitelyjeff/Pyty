def get_namespace_contents(doc):
    """Returns the contents present in the C{doc}'s namespace, encoded as a
    dictionary mapping identifiers (strs) to L{epydoc.apidoc.VariableDoc}s. 
    That is, C{get_namespace_contents} called on a module will only return
    information about module-level variables, functions, and classes.

    @type doc: L{epydoc.apidoc.APIDoc}.
    @param doc: Representation of API documentation for a Python object (which
        can be a module, class, etc.).
    @rtype: dict {str : C{VariableDoc}}.
    @return: Contents of C{doc}'s namespace.
    """

    return api_doc.variables


def get_all_objects(doc):
    """Recursively gathers API documentation on all objects present in C{doc},
    not just those directly in C{doc}'s namespace. Returns all the contents of
    C{doc}, encoded as a dictionary mapping identifiers (strs) to
    L{epydoc.apidoc.VariableDoc}s.

    @type doc: L{epydoc.apidoc.APIDoc}.
    @param doc: Representation of API documentation for a Python object (which
        can be a module, class, etc.).
    @rtype: dict {C{str} : C{VariableDoc}}.
    @return: All contents of C{doc}.
    """

    return get_all_objects_helper({}, doc)


def get_all_objects_helper(d, doc):
    """Helper function for L{get_all_objects}. Passes along a dictionary to
    store to incrementally store variable mappings.

    @type d: dict {C{str} : C{VariableDoc}}.
    @param d: Storage dictionary. Initially stores all previous contents that
        have been found.
    @rtype: dict {C{str} : C{VariableDoc}}.
    @return: Updates C{d} to add contents found in the namespace of C{doc}, as
        well as all in the namespace of all of C{doc}'s children.
    """

    namespace_contents = get_namespace_contents(doc)
    d.update(namespace_contents)

    return get_all_objects_helper(d, doc)

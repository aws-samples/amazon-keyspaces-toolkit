# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


# legacydesc3x is using legacy describe statement that works with 3x and 2x Cassandra clusters

# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from cqlshlib.util import trim_if_present
from cqlshlib import cql3handling

from cassandra.metadata import (ColumnMetadata, KeyspaceMetadata, TableMetadata, protect_name, protect_names)

def do_describe_3x(cqlshell, cqlruleset, parsed, out, cmd):

        def get_keyspaces_3x():
            return cqlshell.conn.metadata.keyspaces.values()

        def get_cluster_name_3x():
            return cqlshell.conn.metadata.cluster_name

        def get_ring_3x():
            cqlshell.conn.metadata.token_map.rebuild_keyspace(ks, build_if_absent=True)
            return cqlshell.conn.metadata.token_map.tokens_to_hosts_by_ks[ks]

        #modified for python3
        def get_keyspace_names_3x_mod():
            return list(cqlshell.conn.metadata.keyspaces.keys())

        def get_columnfamily_names_3x(ksname=None):
            if ksname is None:
                ksname = cqlshell.current_keyspace

        def get_keyspace_meta_3x( ksname):
            if ksname not in cqlshell.conn.metadata.keyspaces:
                raise KeyspaceNotFound('Keyspace %r not found.' % ksname)
            return cqlshell.conn.metadata.keyspaces[ksname]

        def get_partitioner_3x():
            return cqlshell.conn.metadata.partitioner

        def get_fake_auth_table_meta_3x(ksname, tablename):
            # may be using external auth implementation so internal tables
            # aren't actually defined in schema. In this case, we'll fake
            # them up
            if tablename == 'roles':
                ks_meta = KeyspaceMetadata(ksname, True, None, None)
                table_meta = TableMetadata(ks_meta, 'roles')
                table_meta.columns['role'] = ColumnMetadata(table_meta, 'role', cassandra.cqltypes.UTF8Type)
                table_meta.columns['is_superuser'] = ColumnMetadata(table_meta, 'is_superuser', cassandra.cqltypes.BooleanType)
                table_meta.columns['can_login'] = ColumnMetadata(table_meta, 'can_login', cassandra.cqltypes.BooleanType)
            elif tablename == 'role_permissions':
                ks_meta = KeyspaceMetadata(ksname, True, None, None)
                table_meta = TableMetadata(ks_meta, 'role_permissions')
                table_meta.columns['role'] = ColumnMetadata(table_meta, 'role', cassandra.cqltypes.UTF8Type)
                table_meta.columns['resource'] = ColumnMetadata(table_meta, 'resource', cassandra.cqltypes.UTF8Type)
                table_meta.columns['permission'] = ColumnMetadata(table_meta, 'permission', cassandra.cqltypes.UTF8Type)
            else:
                raise ColumnFamilyNotFound("Column family %r not found" % tablename)

        def get_table_meta_3x( ksname, tablename):
            if ksname is None:
                ksname = cqlshell.current_keyspace
            ksmeta = get_keyspace_meta_3x( ksname)

            if tablename not in ksmeta.tables:
                if ksname == 'system_auth' and tablename in ['roles', 'role_permissions']:
                    get_fake_auth_table_meta_3x( ksname, tablename)
                else:
                    raise ColumnFamilyNotFound("Column family %r not found" % tablename)
            else:
                return ksmeta.tables[tablename]

        def get_index_meta_3x(ksname, idxname):
            if ksname is None:
                ksname = cqlshell.current_keyspace
            ksmeta = get_keyspace_meta_3x(ksname)

            if idxname not in ksmeta.indexes:
                raise IndexNotFound("Index %r not found" % idxname)

            return ksmeta.indexes[idxname]

        def get_view_meta_3x( ksname, viewname):
            if ksname is None:
                ksname = cqlshell.current_keyspace
            ksmeta = get_keyspace_meta_3x(ksname)

            if viewname not in ksmeta.views:
                raise MaterializedViewNotFound("Materialized view %r not found" % viewname)
            return ksmeta.views[viewname]

        def get_object_meta_3x( ks, name):
            if name is None:
                if ks and ks in cqlshell.conn.metadata.keyspaces:
                    return cqlshell.conn.metadata.keyspaces[ks]
                elif cqlshell.current_keyspace is None:
                    raise ObjectNotFound("%r not found in keyspaces" % (ks))
                else:
                    name = ks
                    ks = cqlshell.current_keyspace

            if ks is None:
                ks = cqlshell.current_keyspace

            ksmeta = get_keyspace_meta_3x( ks)

            if name in ksmeta.tables:
                return ksmeta.tables[name]
            elif name in ksmeta.indexes:
                return ksmeta.indexes[name]
            elif name in ksmeta.views:
                return ksmeta.views[name]

            raise ObjectNotFound("%r not found in keyspace %r" % (name, ks))

        def cql_unprotect_name_3x(namestr):
            if namestr is None:
                return
            return cqlruleset.dequote_name(namestr)

        def print_recreate_keyspace_3x(ksdef, out):
                out.write(ksdef.export_as_string())
                out.write("\n")

        def print_recreate_columnfamily_3x( ksname, cfname, out):
                """
                Output CQL commands which should be pasteable back into a CQL session
                    to recreate the given table.
                    Writes output to the given out stream.
                """
                out.write(get_table_meta_3x( ksname, cfname).export_as_string())
                out.write("\n")

        def print_recreate_index_3x( ksname, idxname, out):
                """
                Output CQL commands which should be pasteable back into a CQL session
                to recreate the given index.

                Writes output to the given out stream.
                """
                out.write(get_index_meta_3x(ksname, idxname).export_as_string())
                out.write("\n")

        def print_recreate_materialized_view_3x( ksname, viewname, out):
                """
                Output CQL commands which should be pasteable back into a CQL session
                to recreate the given materialized view.

                Writes output to the given out stream.
                """
                out.write(get_view_meta_3x( ksname, viewname).export_as_string())
                out.write("\n")

        def print_recreate_object_3x( ks, name, out):
                """
                Output CQL commands which should be pasteable back into a CQL session
                to recreate the given object (ks, table or index).
                Writes output to the given out stream.
                """
                out.write(get_object_meta_3x( ks, name).export_as_string())
                out.write("\n")

        def describe_keyspaces_3x():
                """
                Print the output for a DESCRIBE KEYSPACES query
                """
                print('')
                cmd.Cmd.columnize(cqlshell, get_keyspace_names_3x_mod())
                print('')    

        def describe_keyspace_3x( ksname):
                print_recreate_keyspace_3x( get_keyspace_meta_3x( ksname), out)
                print()
            
        def describe_columnfamily_3x(ksname, cfname):
                if ksname is None:
                    ksname = cqlshell.current_keyspace
                if ksname is None:
                    raise NoKeyspaceError("No keyspace specified and no current keyspace")
                print()
                print_recreate_columnfamily_3x( ksname, cfname, out)
                print()

        def describe_index_3x(ksname, idxname):
                print()
                print_recreate_index_3x( ksname, idxname, out)
                print()

        def describe_materialized_view_3x( ksname, viewname):
                if ksname is None:
                    ksname = cqlshell.current_keyspace
                if ksname is None:
                    raise NoKeyspaceError("No keyspace specified and no current keyspace")
                print()
                print_recreate_materialized_view_3x( ksname, viewname, out)
                print()

        def describe_object_3x(ks, name):
                print()
                print_recreate_object_3x( ks, name, out)
                print()

        def describe_columnfamilies_3x( ksname):
                print()
                if ksname is None:
                    for k in get_keyspaces_3x():
                        name = k.name
                        print('Keyspace %s' % name)
                        print('---------%s' % ('-' * len(name)))
                        cmd.Cmd.columnize(cqlshell, get_columnfamily_names_3x(k.name))
                        print()
                else:
                    cmd.Cmd.columnize(cqlshell, get_columnfamily_names_3x(ksname))
                    print()

        def columnize_unicode_3x( name_list, quote=False):
                """
                Used when columnizing identifiers that may contain unicode
                """
                names = [n.encode('utf-8') for n in name_list]
                if quote:
                    names = protect_names(names)
                cmd.Cmd.columnize(cqlshell, names)
                print()

        def describe_functions_3x( ksname):
                print()
                if ksname is None:
                    for ksmeta in get_keyspaces_3x():
                        name = protect_name(ksmeta.name)
                        print ('Keyspace %s' % name)
                        print ('---------%s' % '-' * len(name))
                        columnize_unicode_3x( ksmeta.functions.keys())
                else:
                    ksmeta = get_keyspace_meta_3x(ksname)
                    columnize_unicode_3x( ksmeta.functions.keys())

        #filter modified for python3
        def describe_function_3x_mod( ksname, functionname):
                if ksname is None:
                    ksname = cqlshell.current_keyspace
                if ksname is None:
                    raise NoKeyspaceError("No keyspace specified and no current keyspace")
                print()
                ksmeta = get_keyspace_meta_3x(ksname)
                functions = list(filter(lambda f: f.name == functionname, ksmeta.functions.values()))
                if len(functions) == 0:
                    raise FunctionNotFound("User defined function %r not found" % functionname)
                print ('\n\n'.join(func.export_as_string() for func in functions))
                print()

        def describe_aggregates_3x(ksname):
                print()
                if ksname is None:
                    for ksmeta in get_keyspaces_3x():
                        name = protect_name(ksmeta.name)
                        print ('Keyspace %s' % name)
                        print ('---------%s' % '-' * len(name))
                        columnize_unicode_3x( ksmeta.aggregates.keys())
                else:
                    ksmeta = get_keyspace_meta_3x( ksname)
                    columnize_unicode_3x( ksmeta.aggregates.keys())

        #filter modified for python3
        def describe_aggregate_3x_mod(ksname, aggregatename):
                if ksname is None:
                    ksname = cqlshell.current_keyspace
                if ksname is None:
                    raise NoKeyspaceError("No keyspace specified and no current keyspace")
                print()
                ksmeta = get_keyspace_meta_3x( ksname)
                aggregates = list(filter(lambda f: f.name == aggregatename, ksmeta.aggregates.values()))
                if len(aggregates) == 0:
                    raise FunctionNotFound("User defined aggregate %r not found" % aggregatename)
                print ('\n\n'.join(aggr.export_as_string() for aggr in aggregates))
                print()

        def describe_usertypes_3x(ksname):
                print()
                if ksname is None:
                    for ksmeta in get_keyspaces_3x():
                        name = protect_name(ksmeta.name)
                        print ('Keyspace %s' % name)
                        print ('---------%s' % '-' * len(name))
                        columnize_unicode_3x( ksmeta.user_types.keys(), quote=True)
                else:
                    ksmeta = get_keyspace_meta_3x( ksname)
                    columnize_unicode_3x( ksmeta.user_types.keys(), quote=True)

        def describe_usertype_3x( ksname, typename):
                if ksname is None:
                    ksname = cqlshell.current_keyspace
                if ksname is None:
                    raise NoKeyspaceError("No keyspace specified and no current keyspace")
                print()
                ksmeta = get_keyspace_meta_3x( ksname)
                try:
                    usertype = ksmeta.user_types[typename]
                except KeyError:
                    raise UserTypeNotFound("User type %r not found" % typename)
                print (usertype.export_as_string())


        def describe_cluster_3x():
                print('\nCluster: %s' % get_cluster_name_3x())
                p = trim_if_present(get_partitioner_3x(), 'org.apache.cassandra.dht.')
                print('Partitioner: %s\n' % p)
                # TODO: snitch?
                # snitch = trim_if_present(cqlshell.get_snitch(), 'org.apache.cassandra.locator.')
                # print 'Snitch: %s\n' % snitch
                if cqlshell.current_keyspace is not None and cqlshell.current_keyspace != 'system':
                    print("Range ownership:")
                    ring = get_ring_3x(cqlshell.current_keyspace)
                    for entry in ring.items():
                        print(' %39s  [%s]' % (str(entry[0].value), ', '.join([host.address for host in entry[1]])))
                    print()

        def describe_schema_3x( include_system=False):
                print()
                for k in get_keyspaces_3x():
                    if include_system or k.name not in cql3handling.SYSTEM_KEYSPACES:
                        print_recreate_keyspace_3x( k, out)
                        print()

        what = parsed.matched[1][1].lower()
        if what == 'functions':
            describe_functions_3x( cqlshell.current_keyspace)
        elif what == 'function':
            ksname = cql_unprotect_name_3x(parsed.get_binding('ksname', None))
            functionname = cql_unprotect_name_3x(parsed.get_binding('udfname'))
            describe_function_3x_mod( ksname, functionname)
        elif what == 'aggregates':
            describe_aggregates_3x( cqlshell.current_keyspace)
        elif what == 'aggregate':
            ksname = cql_unprotect_name_3x(parsed.get_binding('ksname', None))
            aggregatename = cql_unprotect_name_3x(parsed.get_binding('udaname'))
            describe_aggregate_3x_mod( ksname, aggregatename)
        elif what == 'keyspaces':
            describe_keyspaces_3x()
        elif what == 'keyspace':
            ksname = cql_unprotect_name_3x(parsed.get_binding('ksname', ''))
            if not ksname:
                ksname = cqlshell.current_keyspace
                if ksname is None:
                    cqlshell.printerr('Not in any keyspace.')
                    return
            describe_keyspace_3x( ksname)
        elif what in ('columnfamily', 'table'):
            ks = cql_unprotect_name_3x(parsed.get_binding('ksname', None))
            cf = cql_unprotect_name_3x(parsed.get_binding('cfname'))
            describe_columnfamily_3x(ks, cf)
        elif what == 'index':
            ks = cql_unprotect_name_3x(parsed.get_binding('ksname', None))
            idx = cql_unprotect_name_3x(parsed.get_binding('idxname', None))
            describe_index_3x( ks, idx)
        elif what == 'materialized' and parsed.matched[2][1].lower() == 'view':
            ks = cql_unprotect_name_3x(parsed.get_binding('ksname', None))
            mv = cql_unprotect_name_3x(parsed.get_binding('mvname'))
            describe_materialized_view_3x( ks, mv)
        elif what in ('columnfamilies', 'tables'):
            describe_columnfamilies_3x( cqlshell.current_keyspace)
        elif what == 'types':
            describe_usertypes_3x( cqlshell.current_keyspace)
        elif what == 'type':
            ks = cql_unprotect_name_3x( parsed.get_binding('ksname', None))
            ut = cql_unprotect_name_3x( parsed.get_binding('utname'))
            describe_usertype_3x(ks, ut)
        elif what == 'cluster':
            describe_cluster_3x()
        elif what == 'schema':
            describe_schema_3x(False)
        elif what == 'full' and parsed.matched[2][1].lower() == 'schema':
            describe_schema_3x( True)
        elif what:
            ks = cql_unprotect_name_3x(parsed.get_binding('ksname', None))
            name = cql_unprotect_name_3x(parsed.get_binding('cfname'))
            if not name:
                name = cql_unprotect_name_3x(parsed.get_binding('idxname', None))
            if not name:
                name = cql_unprotect_name_3x(parsed.get_binding('mvname', None))
            describe_object_3x( ks, name)

       #do_desc_3x = do_describe_3x 
          
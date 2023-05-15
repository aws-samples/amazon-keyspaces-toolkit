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
from cassandra.metadata import (ColumnMetadata, KeyspaceMetadata, TableMetadata)
from cassandra.cqltypes import cql_typename
from cqlshlib.util import trim_if_present
from cqlshlib import cql3handling

import  cmd, sys


class NoKeyspaceError(Exception):
    pass

class ObjectNotFound(Exception):
    pass

def get_object_meta(self, ks, name):
        if name is None:
            if ks and ks in self.conn.metadata.keyspaces:
                return self.conn.metadata.keyspaces[ks]
            elif self.current_keyspace is None:
                raise ObjectNotFound("'{}' not found in keyspaces".format(ks))
            else:
                name = ks
                ks = self.current_keyspace

        if ks is None:
            ks = self.current_keyspace

        ksmeta = self.get_keyspace_meta(ks)

        if name in ksmeta.tables:
            return ksmeta.tables[name]
        elif name in ksmeta.indexes:
            return ksmeta.indexes[name]
        elif name in ksmeta.views:
            return ksmeta.views[name]

        raise ObjectNotFound("'{}' not found in keyspace '{}'".format(name, ks))

def get_keyspace_names(self):
        return list(self.conn.metadata.keyspaces.keys())

def get_columnfamily_names(self, ksname=None):
        if ksname is None:
            ksname = self.current_keyspace
        return list(self.get_keyspace_meta(ksname).tables.keys())

def print_recreate_keyspace(self, ksdef, out):
    out.write(ksdef.export_as_string())
    out.write("\n")

def print_recreate_columnfamily(self, ksname, cfname, out):
    """
    Output CQL commands which should be pasteable back into a CQL session
        to recreate the given table.
        Writes output to the given out stream.
    """
    out.write(self.get_table_meta(ksname, cfname).export_as_string())
    out.write("\n")

def print_recreate_object(self, ks, name, out):
        """
        Output CQL commands which should be pasteable back into a CQL session
        to recreate the given object (ks, table or index).
        Writes output to the given out stream.
        """
        out.write(get_object_meta(self, ks, name).export_as_string())
        out.write("\n")

def describe_keyspaces_3x(self):
        """
        Print the output for a DESCRIBE KEYSPACES query
        """
        print('')
        cmd.Cmd.columnize(self, get_keyspace_names(self))
        print('')    

def describe_keyspace_3x(self, ksname):
        print('calling print_recreate')
        print_recreate_keyspace(self, self.get_keyspace_meta(ksname), sys.stdout)
        print
    
def describe_columnfamily_3x(self, ksname, cfname):
        if ksname is None:
            ksname = self.current_keyspace
        if ksname is None:
            raise NoKeyspaceError("No keyspace specified and no current keyspace")
        print
        print_recreate_columnfamily(self, ksname, cfname, sys.stdout)
        print
    
def describe_columnfamilies_3x(self, ksname):
        print
        if ksname is None:
            for k in self.get_keyspaces():
                name = k.name
                print('Keyspace %s' % name)
                print('---------%s' % ('-' * len(name)))
                cmd.Cmd.columnize(self, get_columnfamily_names(self, k.name))
                print
        else:
            cmd.Cmd.columnize(self, get_columnfamily_names(self, ksname))
            print

def describe_object_3x(self, ks, name):
        print
        print_recreate_object(self, ks, name, sys.stdout)
        print

def describe_schema_3x(self, include_system=False):
        print
        for k in self.get_keyspaces():
            if include_system or k.name not in cql3handling.SYSTEM_KEYSPACES:
                print_recreate_keyspace(self, k, sys.stdout)
                print

def describe_cluster_3x(self):
        print('\nCluster: %s' % self.get_cluster_name())
        p = trim_if_present(self.get_partitioner(), 'org.apache.cassandra.dht.')
        print('Partitioner: %s\n' % p)
        # TODO: snitch?
        # snitch = trim_if_present(self.get_snitch(), 'org.apache.cassandra.locator.')
        # print 'Snitch: %s\n' % snitch
        if self.current_keyspace is not None and self.current_keyspace != 'system':
            print("Range ownership:")
            ring = self.get_ring(self.current_keyspace)
            for entry in ring.items():
                print(' %39s  [%s]' % (str(entry[0].value), ', '.join([host.address for host in entry[1]])))
            print
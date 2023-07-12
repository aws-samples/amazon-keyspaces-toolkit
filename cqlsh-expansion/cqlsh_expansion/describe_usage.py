
import re
def count_elements(file_path):
    with open(file_path, 'r') as f:
        content = f.read()

    views = content.count('MATERIALIZED VIEW')
    types = content.count('CREATE TYPE')
    indexes = content.count('CREATE INDEX')
    aggregates = content.count('CREATE AGGREGATE')
    functions = content.count('CREATE FUNCTION')
    triggers = content.count('CREATE TRIGGER')
    frozens = content.count('frozen*<')
    keyspaces = content.count('CREATE KEYSPACE')
    tables = content.count('CREATE TABLE')

    return views, types, indexes, aggregates, functions, triggers, frozens, keyspaces, tables



def count_occurrences(word, file_contents):

    viewspattern = re.compile(word, re.IGNORECASE)
    matches = viewspattern.findall(file_contents)
    return len(matches)

if __name__ == "__main__":
    views, types, indexes, aggregates, functions, triggers, frozens, keyspaces, tables = count_elements("/Users/mjraney/dev/MCS/github/amazon-keyspaces-toolkit/cqlsh-expansion/schema.txt")

    filename = "/Users/mjraney/dev/MCS/github/amazon-keyspaces-toolkit/cqlsh-expansion/schema.txt";

    with open(filename, 'r') as f:
        file_contents = f.read()
    print(count_occurrences("CREATE +KEYSPACE", file_contents))
    print(count_occurrences("CREATE +KEYSPACE", file_contents))

    print(f"Number of views: {views}")
    print(f"Number of types: {types}")
    print(f"Number of indexes: {indexes}")
    print(f"Number of aggregates: {aggregates}")
    print(f"Number of functions: {functions}")
    print(f"Number of triggers: {triggers}")
    print(f"Number of frozens: {frozens}")
    print(f"Number of keyspaces: {keyspaces}")
    print(f"Number of tables: {tables}")
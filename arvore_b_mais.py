
import json
import shutil
from bisect import bisect_left, bisect_right
from pathlib import Path
from time import perf_counter


class BPlusTree:
    def __init__(self, directory="paginas", order=4):
        self.order = order
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)

        self.reads = 0
        self.writes = 0
        self.next_page_id = 0

        self.root = self.new_page_id()
        self.write_page(self.root, {
            "leaf": True,
            "keys": [],
            "children": [],
            "next": None
        })

    def new_page_id(self):
        page_id = self.next_page_id
        self.next_page_id += 1
        return page_id

    def page_path(self, page_id):
        return self.directory / f"pagina_{page_id}.json"

    def read_page(self, page_id):
        with open(self.page_path(page_id), "r",
                  encoding="utf-8") as file:
            node = json.load(file)

        self.reads += 1
        return node

    def write_page(self, page_id, node):
        with open(self.page_path(page_id), "w",
                  encoding="utf-8") as file:
            json.dump(node, file, ensure_ascii=False)

        self.writes += 1

    def insert(self, key):
        reads_before = self.reads
        writes_before = self.writes

        split = self._insert(self.root, key)

        if split is not None:
            separator, right_page = split

            new_root = self.new_page_id()

            self.write_page(new_root, {
                "leaf": False,
                "keys": [separator],
                "children": [self.root, right_page],
                "next": None
            })

            self.root = new_root

        return (
            self.reads - reads_before,
            self.writes - writes_before
        )

    def _insert(self, page_id, key):
        node = self.read_page(page_id)

        if node["leaf"]:
            index = bisect_left(node["keys"], key)

            if (index < len(node["keys"])
                    and node["keys"][index] == key):
                return None

            node["keys"].insert(index, key)

            if len(node["keys"]) < self.order:
                self.write_page(page_id, node)
                return None

            return self._split_leaf(page_id, node)

        index = bisect_right(node["keys"], key)
        child_page = node["children"][index]

        split = self._insert(child_page, key)

        if split is None:
            return None

        separator, right_page = split

        node["keys"].insert(index, separator)
        node["children"].insert(index + 1, right_page)

        if len(node["keys"]) < self.order:
            self.write_page(page_id, node)
            return None

        return self._split_internal(page_id, node)

    def _split_leaf(self, page_id, node):
        middle = len(node["keys"]) // 2

        right_page = self.new_page_id()

        right_node = {
            "leaf": True,
            "keys": node["keys"][middle:],
            "children": [],
            "next": node["next"]
        }

        node["keys"] = node["keys"][:middle]
        node["next"] = right_page

        self.write_page(page_id, node)
        self.write_page(right_page, right_node)

        return right_node["keys"][0], right_page

    def _split_internal(self, page_id, node):
        middle = len(node["keys"]) // 2
        separator = node["keys"][middle]

        right_page = self.new_page_id()

        right_node = {
            "leaf": False,
            "keys": node["keys"][middle + 1:],
            "children": node["children"][middle + 1:],
            "next": None
        }

        node["keys"] = node["keys"][:middle]
        node["children"] = node["children"][:middle + 1]

        self.write_page(page_id, node)
        self.write_page(right_page, right_node)

        return separator, right_page

    def snapshot(self):
        current = [self.root]
        levels = []

        while current:
            nodes = [
                self.read_page(page_id)
                for page_id in current
            ]

            levels.append([
                node["keys"] for node in nodes
            ])

            current = [
                child
                for node in nodes
                if not node["leaf"]
                for child in node["children"]
            ]

        return levels

    def get_all_keys(self):
        page_id = self.root

        while True:
            node = self.read_page(page_id)

            if node["leaf"]:
                break

            page_id = node["children"][0]

        keys = []

        while True:
            keys.extend(node["keys"])

            if node["next"] is None:
                break

            node = self.read_page(node["next"])

        return keys


# Dados da atividade
siglas = [
    "AC", "AL", "AP", "AM", "BA", "CE", "DF",
    "ES", "GO", "MA", "MT", "MS", "MG", "PA",
    "PB", "PR", "PE", "PI", "RJ", "RN", "RS",
    "RO", "RR", "SC", "SP", "SE", "TO"
]

# Limpa somente a pasta de páginas desta execução.
directory = Path("paginas_arvore_b")

if directory.exists():
    shutil.rmtree(directory)

tree = BPlusTree(directory=directory, order=4)

states = {}
results = []

start = perf_counter()

for i, sigla in enumerate(siglas, start=1):
    reads, writes = tree.insert(sigla)
    results.append((i, sigla, reads, writes))

    if i in [5, 10, 15, 20, 25]:
        states[i] = tree.snapshot()

elapsed = perf_counter() - start

# As leituras para visualizar os estados também
# são operações reais sobre os arquivos.
# Guardamos o total antes das verificações finais.
total_reads = tree.reads
total_writes = tree.writes

print("===== INSERÇÕES =====")

for i, sigla, reads, writes in results:
    print(
        f"Inserção {i:02d}: {sigla} | "
        f"Leituras: {reads} | Escritas: {writes}"
    )

print("\n===== CINCO ESTADOS INTERMEDIÁRIOS =====")

for count, levels in states.items():
    print(f"\nApós {count} inserções:")

    for level, nodes in enumerate(levels):
        print(f"Nível {level}: {nodes}")

print("\n===== ÁRVORE FINAL =====")

final_levels = tree.snapshot()

for level, nodes in enumerate(final_levels):
    print(f"Nível {level}: {nodes}")

valid = tree.get_all_keys() == sorted(siglas)

print("\n===== RESULTADOS =====")
print("Leituras durante inserções:",
      sum(item[2] for item in results))
print("Escritas durante inserções:",
      sum(item[3] for item in results))
print("Leituras incluindo estados intermediários:",
      total_reads)
print("Escritas incluindo estados intermediários:",
      total_writes)
print(f"Tempo da carga e captura: {elapsed:.8f} segundos")
print("Todas as 27 siglas foram inseridas?", valid)
print("Arquivos armazenados em:", directory.resolve())

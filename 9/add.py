import itertools
from dataclasses import dataclass
from typing import List, Dict

from PySide6.QtWidgets import (QVBoxLayout,
                               QPushButton, QDialog, QTextEdit)


@dataclass
class SolverResult:
    mapping: Dict[str, int]
    matched_edges: List[str]


class EgeSolver:

    def solve(self, graph_adj: Dict[str, List[str]], matrix_data: List[List[str]]) -> List[SolverResult]:
        matrix_adj = {}
        matrix_weights = {}
        size = len(matrix_data)
        indices = range(size)

        for r in indices:
            neighbors = set()
            for c in indices:
                val = matrix_data[r][c].strip()
                if val and val != '0':
                    neighbors.add(c)
                    matrix_weights[tuple(sorted((r, c)))] = val
            matrix_adj[r] = neighbors

        graph_nodes = sorted(list(graph_adj.keys()))

        if len(graph_nodes) != size:
            return []

        solutions = []

        for perm in itertools.permutations(indices):
            mapping = {name: idx for name, idx in zip(graph_nodes, perm)}

            if self._is_isomorphic(graph_adj, matrix_adj, mapping):
                edges_info = []
                processed_edges = set()

                for u_name in graph_nodes:
                    u_idx = mapping[u_name]
                    for v_name in graph_adj[u_name]:
                        v_idx = mapping[v_name]

                        edge_key = tuple(sorted((u_idx, v_idx)))
                        if edge_key not in processed_edges:
                            weight = matrix_weights.get(edge_key, "?")
                            edges_info.append(f"{u_name}-{v_name} (П{u_idx + 1}-П{v_idx + 1}): {weight}")
                            processed_edges.add(edge_key)

                final_mapping = {k: v + 1 for k, v in mapping.items()}
                solutions.append(SolverResult(final_mapping, sorted(edges_info)))

        return solutions

    def _is_isomorphic(self, graph_adj, matrix_adj, mapping):
        for node_name, neighbors in graph_adj.items():

            mapped_idx = mapping[node_name]
            matrix_neighbors = matrix_adj[mapped_idx]
            graph_neighbors_mapped = {mapping[n] for n in neighbors}

            if matrix_neighbors != graph_neighbors_mapped:
                return False
        return True


class SolutionDialog(QDialog):
    def __init__(self, solutions: List[SolverResult], parent=None):
        super().__init__(parent)
        self.setWindowTitle("Результат решения")
        self.resize(400, 500)

        layout = QVBoxLayout(self)

        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setStyleSheet("background-color: #333; color: white; font-size: 14px;")
        layout.addWidget(self.text_edit)

        btn_ok = QPushButton("Закрыть")
        btn_ok.clicked.connect(self.accept)
        layout.addWidget(btn_ok)

        self._format_output(solutions)

    def _format_output(self, solutions: List[SolverResult]):
        html = ""
        if not solutions:
            html = "<h2 style='color: #ff5555'>Решений не найдено!</h2>"
            html += "<p>Возможные причины:</p><ul>"
            html += "<li>Топология графа не совпадает с заполненными ячейками таблицы.</li>"
            html += "<li>Разное количество вершин.</li>"
            html += "<li>Вы забыли соединить узлы в редакторе или поставить число в таблице.</li></ul>"
        else:
            count = len(solutions)
            html += f"<h2 style='color: #55ff55'>Найдено вариантов: {count}</h2>"
            html += "<hr>"

            for i, sol in enumerate(solutions):
                html += f"<h3>Вариант {i + 1}</h3>"

                html += "<table border='1' cellspacing='0' cellpadding='5' style='border-color: #666;'>"
                html += "<tr><th>Граф</th><th>Таблица (Пункт)</th></tr>"

                sorted_map = sorted(sol.mapping.items(), key=lambda item: item[0])
                for name, idx in sorted_map:
                    html += f"<tr><td align='center'><b>{name}</b></td><td align='center'>P{idx}</td></tr>"
                html += "</table>"

                html += "<p><b>Веса ребер:</b></p><ul>"
                for edge in sol.matched_edges:
                    html += f"<li>{edge}</li>"
                html += "</ul>"
                html += "<hr>"

        self.text_edit.setHtml(html)

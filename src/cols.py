from src.num import NUM
from src.row import ROW
from src.sym import SYM


class COLS:
    def __init__(self, t: list) -> None:
        """Generate NUMs and SYMs from column names"""
        self.names = t
        self.all = []
        self.x = []
        self.y = []
        self.klass = None

        for n, col_name in enumerate(t):
            col = NUM(n, col_name) if col_name[0].isupper() else SYM(n, col_name)
            self.all.append(col)
            if not col_name[-1] == "X":
                if "!" in col_name:
                    self.klass = col
                if "+" in col_name or "-" in col_name or "!" in col_name:
                    self.y.append(col)
                else:
                    self.x.append(col)

    def add(self, row: ROW) -> None:
        """
        Updates the (not skipped) columns with details from `row`
        :param row: ROW:
        """
        for col in self.x + self.y:
            col.add(row.cells[col.at])

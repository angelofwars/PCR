import json
import os


class PCRRecipe:
    def __init__(self, name, buffer, mgcl2, dntps, primer_f, primer_r, h2o, taq,
                 primer1_name="", primer2_name="", program="", temp=""):
        self.name = name
        self.buffer = buffer
        self.mgcl2 = mgcl2
        self.dntps = dntps
        self.primer_f = primer_f
        self.primer_r = primer_r
        self.h2o = h2o
        self.taq = taq

        self.primer1_name = primer1_name
        self.primer2_name = primer2_name
        self.program = program
        self.temp = temp

    @property
    def mastermix(self):
        return round(self.buffer + self.mgcl2 + self.dntps + self.primer_f + self.primer_r + self.h2o + self.taq, 2)

    def calculate(self, rxn):
        return [
            ["10x-буфер", self.buffer, round(self.buffer * rxn, 2)],
            ["MgCl2", self.mgcl2, round(self.mgcl2 * rxn, 2)],
            ["dNTPs", self.dntps, round(self.dntps * rxn, 2)],
            [f"Праймер F", self.primer_f, round(self.primer_f * rxn, 2)],
            [f"Праймер R", self.primer_r, round(self.primer_r * rxn, 2)],
            ["H2O", self.h2o, round(self.h2o * rxn, 2)],
            ["Taq-Полимераза", self.taq, round(self.taq * rxn, 2)],
        ]

    def to_dict(self):
        return self.__dict__

    @classmethod
    def from_dict(cls, data):
        return cls(**data)


class ProtocolDatabase:
    def __init__(self, filename="protocols.json"):
        self.filename = filename
        self.recipes = {}
        self.load()

    def load(self):
        if os.path.exists(self.filename):
            with open(self.filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for k, v in data.items():
                    self.recipes[k] = PCRRecipe.from_dict(v)
        else:
            # Шаблон на 20 мкл
            self.recipes["Стандарт (20 µL)"] = PCRRecipe(
                "Стандарт (20 µL)", 2.0, 2.0, 0.6, 0.1, 0.1, 13.05, 0.15,
                "Праймер_F", "Праймер_R", "MAS30100", "60°C"
            )
            # НОВЫЙ Шаблон на 16 мкл из вашего скриншота
            self.recipes["Анализ (16 µL)"] = PCRRecipe(
                "Анализ (16 µL)", 1.6, 1.0, 0.3, 0.5, 0.5, 10.0, 0.1,
                "Ex1/C/F", "Intr1/B/R3", "MAS30100", "60°C"
            )
            self.save()

    def save(self):
        with open(self.filename, 'w', encoding='utf-8') as f:
            data = {k: v.to_dict() for k, v in self.recipes.items()}
            json.dump(data, f, ensure_ascii=False, indent=4)

    def add_or_update(self, recipe):
        self.recipes[recipe.name] = recipe
        self.save()

    def get_recipe(self, name):
        return self.recipes.get(name)

    def get_all_names(self):
        return list(self.recipes.keys())
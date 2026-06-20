class PCRRecipe:
    def __init__(self):
        # Базовые объемы на 1 реакцию
        self.buffer = 2.0
        self.mgcl2 = 2.0
        self.dntps = 0.6
        self.primer_f = 0.1
        self.primer_r = 0.1
        self.h2o = 13.05
        self.taq = 0.15
        self.mastermix = 18.0

    def calculate(self, rxn):
        """Возвращает готовый список строк для таблицы и Excel"""
        return [
            ["10x-буфер синтол", self.buffer, round(self.buffer * rxn, 1)],
            ["MgCl2 25 mM", self.mgcl2, round(self.mgcl2 * rxn, 1)],
            ["10mM dNTPs", self.dntps, round(self.dntps * rxn, 1)],
            ["Праймер_F", self.primer_f, round(self.primer_f * rxn, 1)],
            ["Праймер_R", self.primer_r, round(self.primer_r * rxn, 1)],
            ["H2O", self.h2o, round(self.h2o * rxn, 1)],
            ["HS-Taq-Полимераза", self.taq, round(self.taq * rxn, 2)],
        ]
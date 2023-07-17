import sqlite3 as sqlite



class ScanHistory:
    def __init__(self, filename="test.db"):
        self.type = "sqlite"
        self.filename = filename
        self.connect()
        query = """
                CREATE TABLE IF NOT EXISTS scans(patient_name text, scan_time_hours double, Heart double, 
                Spleen double, Liver double, 
                Kidneys double, Bladder double, Tumor double);
                """
        self.cur.execute(query)

    def load_patient_data(self, patient_name):
        query = """
                Select * from scans where patient_name = ? order by scan_time_hours
                """.format(patient_name)
        self.cur.execute(query, (patient_name,))
        res = self.cur.fetchall()
        print(res)
        return res

    def connect(self):
        self.con = sqlite.connect(self.filename)
        self.cur = self.con.cursor()

    def execute(self, query, val=()):
        self.cur.execute(query, val)

    def history_data(self, patient_name):
        pass

    def select_vals(self):
        query = """
                Select * from scans
                """
        self.cur.execute(query)
        res = self.cur.fetchall()
        return res

    def save_values(self, vals):
        query = """
                Insert into scans values (?, ?, ?, ?, ?, ?, ?, ?);
                """
        self.cur.execute(query, vals)
        self.con.commit()

    def load_patients(self):
        query = """
                SELECT patient_name FROM scans;
                """
        self.cur.execute(query)
        res = self.cur.fetchall()
        patient_names = []
        for i in res:
            if i not in patient_names:
                patient_names.append(i)
        return patient_names

    def close(self):
        self.con.close()


if __name__ == "__main__":
    a = ScanHistory()
    res = a.select_vals()
    print(res)

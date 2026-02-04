from src.models.base_model import BaseModel

class PaymentModel(BaseModel):
    table_name = "ref_metode_pembayaran"
    
    def getGroupedPayments(self):
        with self.conn.cursor() as cursor:
            sql = f"SELECT * FROM {self.table_name} WHERE is_active = 'Y' AND is_delete = 'N' ORDER BY order_list"
            cursor.execute(sql)
            results = cursor.fetchall()
            
            grouped = {}
            for row in results:
                group = row.get('kelompok', 'Other')
                if group not in grouped:
                    grouped[group] = []
                grouped[group].append(row)
            return grouped

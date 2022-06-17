from pyqiwip2p import QiwiP2P

import config as cfg

p2p = QiwiP2P(auth_key=cfg.QIWI_TOKEN)

bill = p2p.bill(amount=15, lifetime=5, comment="3213213")

print(bill.bill_id)
print(bill.pay_url)

print(p2p.check(bill_id=bill.bill_id).status)
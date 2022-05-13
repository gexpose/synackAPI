#!/usr/bin/env python3

from synack import synack

s1 = synack()
s1.gecko = False
s1.getSessionToken()

payouts = s1.getTransactions()
for i in range(len(payouts)):
    print(payouts[i])

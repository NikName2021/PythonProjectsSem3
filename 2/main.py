from logelement import master

elNot = master.TNot()
elAnd = master.TAnd()
elAnd.link(elNot, 1)
# az = master.TLogElement()

print(" A | B | not(A&B) ")
print("-------------------")
for A in range(2):
    elAnd.In1 = bool(A)
    for B in range(2):
        elAnd.In2 = bool(B)
        print(" ", A, "|", B, "|", int(elNot.Res))


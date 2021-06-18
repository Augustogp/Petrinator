import re

string = "(.*)T0(.*?)(?:Tl(.*?)(?:T6(.*?)(?:T7(.*?)T5|T5(.*?)T7)|T5(.*?)T6(.*?)T7|T3(.*?)T4(.*?)T6(.*?)T7(.*?)T2)|T8(.*?)(?:T9(.*?)(?:T10(.*?)T12|T12(.*?)T10)|T12(.*?)T9(.*?)T10|T13(.*?)T14(.*?)T9(.*?)T10(.*?)T11))(.*)"
#string = "(.*)T0(.*?)(?:T1(.*?)(?:T6(.*?)(?:T7(.*?)T5|T5(.*?)T7)|T5(.*?)T6(.*?)T7|T3(.*?)T4(.*?)T6(.*?)T7)|T8(.*?)(?:T9(.*?)(?:T10(.*?)T12|T12(.*?)T10)|T12(.*?)T9(.*?)T10|T13(.*?)T14(.*?)T9(.*?)T10))(.*)"
patron = re.compile(string)
archivo = open("out/transiciones.txt", "r").read()
res = archivo

while True:
    nuevo_resultado = ""
    match = patron.match(res)
    if not match:
        break
    for group in match.groups():
        if group is not None: nuevo_resultado += group
    res = nuevo_resultado

print ("Al eliminar las invariantes, se obtiene\n " + res + "\n")

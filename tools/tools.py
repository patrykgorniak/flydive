import json



def main():
    """TODO: Docstring for main.
    :returns: TODO

    """


    with open("../tests/wizzair/testdata/Markets.json") as f:
        conn = f.read()
        f.close()
    
    conn2 = conn.split(";")[2].replace("wizzAutocomplete.MARKETINFO = ","").replace("'","")

    js2 = json.loads(conn2)
    list = []
    for line in js2:
        for ASL in line["ASL"]:
            list.append( {"SC": ASL["SC"], "DS": line["DS"]})
    print(len(list))

if __name__=='__main__':
    main()

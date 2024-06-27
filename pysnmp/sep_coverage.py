ari_coverage = {
    664: False,
    668: False,
    671: False,
    675: False,
    685: False,
    688: False,
    691: False,
    694: False,
}


def ari_hit(line=None):
    if line:
        ari_coverage[line] = True

    with open("coverage_ari.txt", "w") as f:
        f.write(str(ari_coverage))
        f.write(f"\n{100 * sum(ari_coverage.values()) / len(ari_coverage)}%\n")


ari_hit()

rares_coverage = {76: False, 78: False, 81: False, 86: False, 151: False, 153: False}


def rares_hit(line=None):
    if line:
        rares_coverage[line] = True

    with open("coverage_rares.txt", "w") as f:
        f.write(str(rares_coverage))
        f.write(f"\n{100 * sum(rares_coverage.values()) / len(rares_coverage)}%\n")


rares_hit()

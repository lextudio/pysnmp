ari_coverage = {
    664: False,
    668: False,
    671: False,
    675: False,
    685: False,
    688: False,
    691: False,
    694: False
}


def ari_hit(line=None):
    if line:
        ari_coverage[line] = True

    with open("coverage_ari.txt", "w") as f:
        f.write(str(ari_coverage))
        f.write(f"\n{100 * sum(ari_coverage.values()) / len(ari_coverage)}%\n")

ari_hit()

class Issuers:
    def __init__(self, issuers=None):
        if issuers is None:
            issuers = []
        self.issuers = issuers

    def __str__(self):
        return " ".join(self.issuers)


class MexicanIssuers(Issuers):
    def __init__(self):
        super().__init__(
            ['HERDEZ.MX', 'CUERVO.MX', 'AMXB.MX', 'ELEKTRA.MX', 'HOMEX.MX', 'HCITY.MX', 'GRUMAB.MX', 'GPROFUT.MX',
             'GNP.MX', 'BIMBOA.MX', 'CEMEXCPO.MX', 'ALFAA.MX', 'KOFUBL.MX', 'AMZN.MX', 'MEGACPO.MX', 'GCARSOA1.MX',
             'GFNORTEO.MX', 'VESTA.MX', 'WALMEX.MX', 'OMAB.MX', 'KIMBERA.MX', 'GMEXICOB.MX', 'LABB.MX', 'VOLARA.MX',
             'BBAJIOO.MX', 'FEMSAUBD.MX', 'GMBXF', 'GAPB.MX', 'TLEVISACPO.MX', 'PE&OLES.MX', 'ALSEA.MX', 'AC.MX',
             'ASURB.MX', 'LIVEPOLC-1.MX', 'GCC.MX', 'ORBIA.MX', 'PINFRA.MX', 'Q.MX', 'BOLSAA.MX', 'ALPEKA.MX',
             'GENTERA.MX', 'ORBIA.MX', 'KOFUBL.MX', 'AGUA.MX', 'SIMECB.MX', 'VESTA.MX', 'FRES.MX', 'VOLARA.MX',
             'MSFT.MX', 'GOOGL.MX', '^MXX'])


class NYSE(Issuers):
    def __init__(self):
        super().__init__(
            ['HERDEZ.MX', 'CUERVO.MX', 'AMXB.MX', 'ELEKTRA.MX', 'HOMEX.MX', 'HCITY.MX', 'GRUMAB.MX', 'GPROFUT.MX',
             'GNP.MX', 'BIMBOA.MX', 'CEMEXCPO.MX', 'ALFAA.MX', 'KOFUBL.MX', 'AMZN.MX', 'MEGACPO.MX', 'GCARSOA1.MX',
             'GFNORTEO.MX', 'VESTA.MX', 'WALMEX.MX', 'OMAB.MX', 'KIMBERA.MX', 'GMEXICOB.MX', 'LABB.MX', 'VOLARA.MX',
             'BBAJIOO.MX', 'FEMSAUBD.MX', 'GMBXF', 'GAPB.MX', 'TLEVISACPO.MX', 'PE&OLES.MX', 'ALSEA.MX', 'AC.MX',
             'ASURB.MX', 'LIVEPOLC-1.MX', 'GCC.MX', 'ORBIA.MX', 'PINFRA.MX', 'Q.MX', 'BOLSAA.MX', 'ALPEKA.MX',
             'GENTERA.MX', 'ORBIA.MX', 'KOFUBL.MX', 'AGUA.MX', 'SIMECB.MX', 'VESTA.MX', 'FRES.MX', 'VOLARA.MX',
             'MSFT.MX', 'GOOGL.MX', '^MXX'])
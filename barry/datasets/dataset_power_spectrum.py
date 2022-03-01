import logging

import sys

sys.path.append("..")
from barry.datasets.dataset import MultiDataset
from barry.datasets.dataset_power_spectrum_abc import PowerSpectrum


class PowerSpectrum_SDSS_DR12(PowerSpectrum):

    """Power spectrum for SDSS BOSS DR12 sample for NGC and SGC with mean redshifts z = 0.38, 0.51 and 0.61.
    Uses data from https://fbeutler.github.io/hub/boss_papers.html. Only even multipoles.
    Mock power spectra include hexadecapole, but data power spectra doesn't.
    """

    def __init__(
        self,
        redshift_bin=3,
        galactic_cap="ngc",
        name=None,
        min_k=0.02,
        max_k=0.30,
        step_size=2,
        recon=None,
        reduce_cov_factor=1,
        num_mocks=None,
        postprocess=None,
        fake_diag=False,
        realisation=None,
        isotropic=True,
        fit_poles=(0,),
    ):

        self.nredshift_bins = 3
        self.nsmoothtypes = 1

        if redshift_bin not in [1, 2, 3]:
            raise NotImplementedError("Redshift bin for SDSS_DR12 must be 1, 2 or 3, corresponding to 0.38, 0.51 and 0.61 respectively")

        if galactic_cap.lower() not in ["ngc", "sgc"]:
            raise NotImplementedError("Galactic cap for SDSS_DR12 must be NGC or SGC")

        if any(pole in [1, 3] for pole in fit_poles):
            raise NotImplementedError("Only even multipoles included in SDSS_DR12")

        if realisation is not None:
            if not isinstance(realisation, int):
                if realisation.lower() != "data":
                    raise ValueError("Realisation is not None (mock mean), an integer (mock realisation), or 'data'")
                elif any(pole in [4] for pole in fit_poles):
                    raise NotImplementedError("Hexadecapole not included in SDSS_DR12 data realisation, only in mocks")

        reds = ["z1", "z2", "z3"]
        datafile = "sdss_dr12_pk_" + galactic_cap.lower() + "_" + reds[redshift_bin - 1] + ".pkl"

        super().__init__(
            datafile,
            name=name,
            min_k=min_k,
            max_k=max_k,
            step_size=step_size,
            recon=recon,
            reduce_cov_factor=reduce_cov_factor,
            num_mocks=num_mocks,
            postprocess=postprocess,
            fake_diag=fake_diag,
            realisation=realisation,
            isotropic=isotropic,
            fit_poles=fit_poles,
        )


class PowerSpectrum_eBOSS_LRGpCMASS(PowerSpectrum):

    """Power spectrum for SDSS DR12 eBOSS LRGpCMASS sample for NGC and SGC at redshift 0.698.
    Only even multipoles.
    """

    def __init__(
        self,
        galactic_cap="ngc",
        name=None,
        min_k=0.02,
        max_k=0.30,
        step_size=1,
        recon=None,
        reduce_cov_factor=1,
        num_mocks=None,
        postprocess=None,
        fake_diag=False,
        realisation=None,
        isotropic=True,
        fit_poles=(0,),
    ):

        self.nredshift_bins = 1
        self.nsmoothtypes = 1

        if galactic_cap.lower() not in ["ngc", "sgc"]:
            raise NotImplementedError("Galactic cap for SDSS_DR12 must be NGC or SGC")

        if any(pole in [1, 3] for pole in fit_poles):
            raise NotImplementedError("Only even multipoles included in SDSS_DR12")

        if realisation is not None:
            if not isinstance(realisation, int):
                if realisation.lower() != "data":
                    raise ValueError("Realisation is not None (mock mean), an integer (mock realisation), or 'data'")

        datafile = "sdss_dr16_lrgpcmass_pk_" + galactic_cap.lower() + ".pkl"

        super().__init__(
            datafile,
            name=name,
            min_k=min_k,
            max_k=max_k,
            step_size=step_size,
            recon=recon,
            reduce_cov_factor=reduce_cov_factor,
            num_mocks=num_mocks,
            postprocess=postprocess,
            fake_diag=fake_diag,
            realisation=realisation,
            isotropic=isotropic,
            fit_poles=fit_poles,
        )


class PowerSpectrum_Beutler2019(PowerSpectrum):

    """Updated power spectrum for SDSS BOSS DR12 sample for NGC and SGC with mean redshift z = 0.38 and 0.61.
    Uses data from https://fbeutler.github.io/hub/deconv_paper.html. Include Odd multipoles, but only pre-recon.
    """

    def __init__(
        self,
        redshift_bin=2,
        galactic_cap="ngc",
        name=None,
        min_k=0.02,
        max_k=0.30,
        step_size=None,
        recon=None,
        reduce_cov_factor=1,
        num_mocks=None,
        postprocess=None,
        fake_diag=False,
        realisation=None,
        isotropic=True,
        fit_poles=(0,),
    ):

        self.nredshift_bins = 2
        self.nsmoothtypes = 1

        if recon is not None:
            raise NotImplementedError("Post-recon data not available for Beutler2019 data")

        if redshift_bin not in [1, 2]:
            raise NotImplementedError("Redshift bin for Beutler2019 must be 1 or 2, corresponding to 0.38 and 0.61 respectively")

        if galactic_cap.lower() not in ["ngc", "sgc"]:
            raise NotImplementedError("Galactic cap for Beutler2019 must be NGC or SGC")

        if realisation is not None:
            if not isinstance(realisation, int):
                if realisation.lower() != "data":
                    raise ValueError("Realisation is not None (mock mean), an integer (mock realisation), or 'data'")

        reds = ["z038", "z061"]
        datafile = "beutler_2019_dr12_" + reds[redshift_bin - 1] + "_pk_" + galactic_cap.lower() + ".pkl"

        super().__init__(
            datafile,
            name=name,
            min_k=min_k,
            max_k=max_k,
            step_size=step_size,
            recon=recon,
            reduce_cov_factor=reduce_cov_factor,
            num_mocks=num_mocks,
            postprocess=postprocess,
            fake_diag=fake_diag,
            realisation=realisation,
            isotropic=isotropic,
            fit_poles=fit_poles,
        )


class PowerSpectrum_DESIMockChallenge_Post(PowerSpectrum):
    """ Post reconstruction power spectra from the DESI Mock Challenge in cubic boxes  """

    def __init__(
        self,
        name=None,
        min_k=0.02,
        max_k=0.30,
        step_size=None,
        recon=None,
        reduce_cov_factor=1,
        num_mocks=None,
        postprocess=None,
        fake_diag=False,
        realisation=None,
        isotropic=True,
        fit_poles=(0,),
        covtype="cov-std",
        smoothtype=3,
    ):

        self.nredshift_bins = 1
        self.nsmoothtypes = 4

        covtypes = ["cov-std", "cov-fix"]
        if covtype.lower() not in covtypes:
            raise NotImplementedError("covtype not recognised, must be cov-std, cov-fix")

        smoothnames = ["5", "10", "15", "20"]
        if smoothtype not in [1, 2, 3, 4]:
            raise NotImplementedError(
                "smoothtype not recognised, must be in 1, 2, 3 or 4 corresponding to smoothing scales of 5, 10, 15, 20 Mpc/h respectively"
            )

        if any(pole in [1, 3] for pole in fit_poles):
            raise NotImplementedError("Only even multipoles included in DESIMockChallenge")

        reconname = "pre" if recon is None else recon.lower()
        covname = "" if covtype.lower() == "cov-fix" else "_nonfix"
        smoothname = "" if recon is None else "_" + smoothnames[smoothtype]
        datafile = "desi_mock_challenge_post_stage_2_pk_" + reconname + smoothname + covname + ".pkl"

        super().__init__(
            datafile,
            name=name,
            min_k=min_k,
            max_k=max_k,
            step_size=step_size,
            recon=recon,
            reduce_cov_factor=reduce_cov_factor,
            num_mocks=num_mocks,
            postprocess=postprocess,
            fake_diag=fake_diag,
            realisation=realisation,
            isotropic=isotropic,
            fit_poles=fit_poles,
        )


class PowerSpectrum_DESILightcone_Mocks_Recon(PowerSpectrum):
    """ Power spectrum from the DESI Mock Challenge on lightcones """

    def __init__(
        self,
        name=None,
        min_k=0.02,
        max_k=0.30,
        step_size=None,
        recon=None,
        reduce_cov_factor=1,
        num_mocks=None,
        postprocess=None,
        fake_diag=False,
        realisation=None,
        isotropic=True,
        fit_poles=(0,),
        type="julian_reciso",
    ):

        self.nredshift_bins = 1
        self.nsmoothtypes = 1

        types = [
            "julian_reciso",
            "julian_recsym",
            "martin_reciso",
            "martin_recsym",
        ]
        if type.lower() not in types:
            raise NotImplementedError("Type not recognised, must be julian_reciso, julian_recsym, martin_reciso, martin_recsym")

        if any(pole in [1, 3] for pole in fit_poles):
            raise NotImplementedError("Only even multipoles included in DESIMockChallenge")

        datafiles = [
            "desi_lightcone_mocks_recon_julian_reciso.pkl",
            "desi_lightcone_mocks_recon_julian_recsym.pkl",
            "desi_lightcone_mocks_recon_martin_reciso.pkl",
            "desi_lightcone_mocks_recon_martin_recsym.pkl",
        ]
        datafile = datafiles[types.index(type.lower())]

        super().__init__(
            datafile,
            name=name,
            min_k=min_k,
            max_k=max_k,
            step_size=step_size,
            recon=recon,
            reduce_cov_factor=reduce_cov_factor,
            num_mocks=num_mocks,
            postprocess=postprocess,
            fake_diag=fake_diag,
            realisation=realisation,
            isotropic=isotropic,
            fit_poles=fit_poles,
        )


if __name__ == "__main__":

    import matplotlib.pyplot as plt
    import numpy as np

    logging.basicConfig(level=logging.DEBUG, format="[%(levelname)7s |%(funcName)20s]   %(message)s")
    logging.getLogger("matplotlib").setLevel(logging.ERROR)

    if False:

        # Plot the data and mock average for the SDSS_DR12 spectra
        for j, recon in enumerate(["iso", None]):
            for galactic_cap in ["ngc", "sgc"]:
                for redshift_bin in [1, 2, 3]:
                    dataset = PowerSpectrum_SDSS_DR12(
                        redshift_bin=redshift_bin,
                        galactic_cap=galactic_cap,
                        isotropic=False,
                        recon=recon,
                        fit_poles=[0, 2, 4],
                        min_k=0.02,
                        max_k=0.30,
                    )
                    for i, realisation in enumerate([None, "data", 500]):
                        dataset.set_realisation(realisation)
                        data = dataset.get_data()
                        label = [r"$P_{0}(k)$", r"$P_{2}(k)$", r"$P_{4}(k)$"] if i == 0 else [None, None, None]
                        color = ["r", "b", "g"]
                        fmt = "o" if i == 0 else "None"
                        ls = "None" if i == 0 else "-"
                        yerr = (
                            [
                                data[0]["ks"] * np.sqrt(np.diag(data[0]["cov"]))[0 : len(data[0]["ks"])],
                                data[0]["ks"] * np.sqrt(np.diag(data[0]["cov"]))[2 * len(data[0]["ks"]) : 3 * len(data[0]["ks"])],
                                data[0]["ks"] * np.sqrt(np.diag(data[0]["cov"]))[4 * len(data[0]["ks"]) : 5 * len(data[0]["ks"])],
                            ]
                            if i == 0
                            else [None, None, None]
                        )
                        for m, pk in enumerate(["pk0", "pk2", "pk4"]):
                            plt.errorbar(
                                data[0]["ks"],
                                data[0]["ks"] * data[0][pk],
                                yerr=yerr[m],
                                marker=fmt,
                                ls=ls,
                                c=color[m],
                                zorder=i,
                                label=label[m],
                            )
                    plt.xlabel(r"$k$")
                    plt.ylabel(r"$k\,P(k)$")
                    plt.title(dataset.name)
                    plt.legend()
                    plt.show()

    if True:

        # Plot the data and mock average for the eBOSS LRGpCMASS spectra
        for j, recon in enumerate(["iso", None]):
            for galactic_cap in ["ngc", "sgc"]:
                dataset = PowerSpectrum_eBOSS_LRGpCMASS(
                    galactic_cap=galactic_cap,
                    isotropic=False,
                    recon=recon,
                    fit_poles=[0, 2, 4],
                    min_k=0.02,
                    max_k=0.30,
                )
                for i, realisation in enumerate([None, "data", 500]):
                    dataset.set_realisation(realisation)
                    data = dataset.get_data()
                    label = [r"$P_{0}(k)$", r"$P_{2}(k)$", r"$P_{4}(k)$"] if i == 0 else [None, None, None]
                    color = ["r", "b", "g"]
                    fmt = "o" if i == 0 else "None"
                    ls = "None" if i == 0 else "-"
                    yerr = (
                        [
                            data[0]["ks"] * np.sqrt(np.diag(data[0]["cov"]))[0 : len(data[0]["ks"])],
                            data[0]["ks"] * np.sqrt(np.diag(data[0]["cov"]))[2 * len(data[0]["ks"]) : 3 * len(data[0]["ks"])],
                            data[0]["ks"] * np.sqrt(np.diag(data[0]["cov"]))[4 * len(data[0]["ks"]) : 5 * len(data[0]["ks"])],
                        ]
                        if i == 0
                        else [None, None, None]
                    )
                    for m, pk in enumerate(["pk0", "pk2", "pk4"]):
                        plt.errorbar(
                            data[0]["ks"],
                            data[0]["ks"] * data[0][pk],
                            yerr=yerr[m],
                            marker=fmt,
                            ls=ls,
                            c=color[m],
                            zorder=i,
                            label=label[m],
                        )
                plt.xlabel(r"$k$")
                plt.ylabel(r"$k\,P(k)$")
                plt.title(dataset.name)
                plt.legend()
                plt.show()

    if False:

        # Plot the data and mock average for the Beutler2019 spectra
        for j, recon in enumerate([None]):
            for galactic_cap in ["ngc", "sgc"]:
                for redshift_bin in [1, 3]:
                    dataset = PowerSpectrum_Beutler2019(
                        redshift_bin=redshift_bin,
                        galactic_cap=galactic_cap,
                        isotropic=False,
                        recon=recon,
                        fit_poles=[0, 1, 2, 3, 4],
                        min_k=0.02,
                        max_k=0.30,
                    )
                    for i, realisation in enumerate([None, "data", 500]):
                        dataset.set_realisation(realisation)
                        data = dataset.get_data()
                        label = (
                            [r"$P_{0}(k)$", r"$P_{1}(k)$", r"$P_{2}(k)$", r"$P_{3}(k)$", r"$P_{4}(k)$"]
                            if i == 0
                            else [None, None, None, None, None]
                        )
                        color = ["r", "b", "g", "orange", "purple"]
                        fmt = "o" if i == 0 else "None"
                        ls = "None" if i == 0 else "-"
                        for m, pk in enumerate(["pk0", "pk1", "pk2", "pk3", "pk4"]):
                            yerr = data[0]["ks"] * np.sqrt(np.diag(data[0]["cov"]))[m * len(data[0]["ks"]) : (m + 1) * len(data[0]["ks"])]
                            plt.errorbar(
                                data[0]["ks"],
                                data[0]["ks"] * data[0][pk],
                                yerr=yerr if i == 0 else None,
                                marker=fmt,
                                ls=ls,
                                c=color[m],
                                zorder=i,
                                label=label[m],
                            )
                    plt.xlabel(r"$k$")
                    plt.ylabel(r"$k\,P(k)$")
                    plt.title(dataset.name)
                    plt.legend()
                    plt.show()

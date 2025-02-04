import sys

sys.path.append("..")
sys.path.append("../../")
from barry.samplers import DynestySampler
from barry.config import setup
from barry.models import PowerBeutler2017
from barry.datasets.dataset_power_spectrum import PowerSpectrum_DESI_KP4
from barry.fitter import Fitter
import numpy as np
import pandas as pd
from barry.models.model import Correction
from barry.utils import weighted_avg_and_cov
import matplotlib.pyplot as plt
from chainconsumer import ChainConsumer

# Config file to fit the abacus cutsky mock means and individual realisations using Dynesty.

# Convenience function to plot histograms of the errors and cross-correlation coefficients
def plot_alphas(stats, figname):

    colors = ["#CAF270", "#84D57B", "#4AB482", "#219180", "#1A6E73", "#234B5B", "#232C3B"]

    fig, axes = plt.subplots(figsize=(4, 5), nrows=5, ncols=4, sharex=True, sharey="row", squeeze=False)
    plt.subplots_adjust(left=0.1, top=0.95, bottom=0.05, right=0.95, hspace=0.0, wspace=0.0)
    for n_poly in range(3, 7):
        index = np.where(stats[:, 1] == n_poly)[0]
        print(stats[index])

        for param in range(5):
            axes[param, n_poly - 3].plot(stats[index, 0], stats[index, param + 2], color=colors[n_poly - 3], zorder=1, alpha=0.75, lw=0.8)
            axes[param, n_poly - 3].fill_between(
                stats[index, 0],
                stats[index, param + 2] - stats[index, param + 7],
                stats[index, param + 2] + stats[index, param + 7],
                color=colors[n_poly - 3],
                zorder=1,
                alpha=0.5,
                lw=0.8,
            )
            axes[param, n_poly - 3].axhline(0.0, color="k", ls="--", zorder=0, lw=0.8)

        axes[0, n_poly - 3].set_ylim(-0.04 / 5, 0.04 / 5)
        axes[1, n_poly - 3].set_ylim(-0.02 / 5, 0.02 / 5)
        axes[2, n_poly - 3].set_ylim(-2.0, 2.0)
        axes[3, n_poly - 3].set_ylim(-2.0, 2.0)
        axes[4, n_poly - 3].set_ylim(-2.0, 2.0)
        axes[4, n_poly - 3].set_xlabel(r"$\sigma_{\Sigma}$")
        if n_poly == 3:
            axes[0, n_poly - 3].set_ylabel(r"$\alpha_{||}-1$")
            axes[1, n_poly - 3].set_ylabel(r"$\alpha_{\perp}-1$")
            axes[2, n_poly - 3].set_ylabel(r"$\Sigma_{||}-5.4$")
            axes[3, n_poly - 3].set_ylabel(r"$\Sigma_{\perp}-1.8$")
            axes[4, n_poly - 3].set_ylabel(r"$\Sigma_{s}$")
        axes[0, n_poly - 3].text(
            0.05,
            0.95,
            f"$N_{{poly}} = {{{n_poly}}}$",
            transform=axes[0, n_poly - 3].transAxes,
            ha="left",
            va="top",
            fontsize=8,
            color=colors[n_poly - 3],
        )

    fig.savefig(figname, bbox_inches="tight", transparent=True, dpi=300)


def plot_errors(stats, figname):

    colors = ["#CAF270", "#84D57B", "#4AB482", "#219180", "#1A6E73", "#234B5B", "#232C3B"]

    fig, axes = plt.subplots(figsize=(4, 5), nrows=5, ncols=4, sharex=True, sharey="row", squeeze=False)
    plt.subplots_adjust(left=0.1, top=0.95, bottom=0.05, right=0.95, hspace=0.0, wspace=0.0)
    for n_poly in range(3, 7):
        index = np.where(stats[:, 1] == n_poly)[0]
        print(stats[index, 0], stats[index, 2], stats[index, 3])

        for param in range(5):
            axes[param, n_poly - 3].plot(stats[index, 0], stats[index, param + 7], color=colors[n_poly - 3], zorder=1, alpha=0.75, lw=0.8)
            axes[param, n_poly - 3].axhline(0.0, color="k", ls="--", zorder=0, lw=0.8)
        axes[0, n_poly - 3].set_ylim(0.0, 0.01 / 5)
        axes[1, n_poly - 3].set_ylim(0.0, 0.01 / 5)
        axes[2, n_poly - 3].set_ylim(0.0, 3.0)
        axes[3, n_poly - 3].set_ylim(0.0, 3.0)
        axes[4, n_poly - 3].set_ylim(0.0, 3.0)
        axes[4, n_poly - 3].set_xlabel(r"$\sigma_{\Sigma}$")
        if n_poly == 3:
            axes[0, n_poly - 3].set_ylabel(r"$\sigma_{\alpha_{||}}$")
            axes[1, n_poly - 3].set_ylabel(r"$\sigma_{\alpha_{\perp}}$")
            axes[2, n_poly - 3].set_ylabel(r"$\sigma_{\Sigma_{nl,||}}$")
            axes[3, n_poly - 3].set_ylabel(r"$\sigma_{\Sigma_{nl,\perp}}$")
            axes[4, n_poly - 3].set_ylabel(r"$\sigma_{\Sigma_{s}}$")
        axes[0, n_poly - 3].text(
            0.05,
            0.95,
            f"$N_{{poly}} = {{{n_poly}}}$",
            transform=axes[0, n_poly - 3].transAxes,
            ha="left",
            va="top",
            fontsize=8,
            color=colors[n_poly - 3],
        )

    fig.savefig(figname, bbox_inches="tight", transparent=True, dpi=300)


if __name__ == "__main__":

    # Get the relative file paths and names
    pfn, dir_name, file = setup(__file__, "/reduced_cov/")

    # Set up the Fitting class and Dynesty sampler with 250 live points.
    fitter = Fitter(dir_name, remove_output=False)
    sampler = DynestySampler(temp_dir=dir_name, nlive=250)

    # The optimal sigma values we found when fitting the mocks with fixed alpha/epsilon
    sigma_nl_par = {None: 9.6, "sym": 5.4}
    sigma_nl_perp = {None: 5.0, "sym": 1.8}
    sigma_s = 0.0

    kmins = [0.0, 0.01, 0.02, 0.03, 0.04, 0.05]
    kmaxs = [0.20, 0.22, 0.24, 0.26, 0.28, 0.30, 0.32, 0.34, 0.36, 0.38, 0.40]

    colors = ["#CAF270", "#84D57B", "#4AB482", "#219180", "#1A6E73", "#234B5B", "#232C3B"]

    # Loop over the mocktypes
    allnames = []

    # Loop over pre- and post-recon measurements
    for r, recon in enumerate([None, "sym"]):

        model = PowerBeutler2017(
            recon=recon,
            marg="full",
            poly_poles=[0, 2],
            correction=Correction.NONE,
            n_poly=4,  # 4 polynomial terms for Xi(s)
        )

        # Set Gaussian priors for the BAO damping centred on the optimal values
        # found from fitting with fixed alpha/epsilon and with width 2 Mpc/h
        model.set_default("sigma_nl_par", sigma_nl_par[recon], min=0.0, max=20.0, sigma=2.0, prior="gaussian")
        model.set_default("sigma_nl_perp", sigma_nl_perp[recon], min=0.0, max=20.0, sigma=2.0, prior="gaussian")
        model.set_default("sigma_s", sigma_s, min=0.0, max=20.0, sigma=2.0, prior="gaussian")

        pktemplate = np.loadtxt("../../barry/data/desi_kp4/DESI_Pk_template.dat")
        model.kvals, model.pksmooth, model.pkratio = pktemplate.T

        for kmin in kmins:
            for kmax in kmaxs:

                dataset = PowerSpectrum_DESI_KP4(
                    datafile="desi_kp4_abacus_cubicbox_cv_pk_lrg.pkl",
                    recon=model.recon,
                    fit_poles=model.poly_poles,
                    min_k=kmin,
                    max_k=kmax,
                    realisation=None,
                    num_mocks=1000,
                    reduce_cov_factor=25,
                )

                name = dataset.name + f" mock mean kmin =" + str(kmin) + " kmax =" + str(kmax)
                fitter.add_model_and_dataset(model, dataset, name=name)
                allnames.append(name)

    # Submit all the jobs to NERSC. We have quite a few (72), so we'll
    # only assign 1 walker (processor) to each. Note that this will only run if the
    # directory is empty (i.e., it won't overwrite existing chains)
    fitter.set_sampler(sampler)
    fitter.set_num_walkers(1)
    fitter.fit(file)

    # Everything below here is for plotting the chains once they have been run. The should_plot()
    # function will check for the presence of chains and plot if it finds them on your laptop. On the HPC you can
    # also force this by passing in "plot" as the second argument when calling this code from the command line.
    if fitter.should_plot():
        import logging

        logging.info("Creating plots")

        # Set up a ChainConsumer instance. Plot the MAP for individual realisations and a contour for the mock average
        datanames = ["Xi", "Pk", "Pk_CV"]

        c = [
            ChainConsumer(),
            ChainConsumer(),
            ChainConsumer(),
        ]

        # Loop over all the chains
        stats = [[] for _ in range(len(datanames))]
        output = {k: [] for k in datanames}
        for posterior, weight, chain, evidence, model, data, extra in fitter.load():

            # Get the realisation number and redshift bin
            recon_bin = 0 if "Prerecon" in extra["name"] else 1
            data_bin = 0 if "Xi" in extra["name"] else 1 if "CV" not in extra["name"] else 2
            sigma_bin = int(extra["name"].split("fixed_type ")[1].split(" ")[0])
            redshift_bin = int(2.0 * len(sigma_sigma) * data_bin + 2.0 * sigma_bin + recon_bin)

            # Store the chain in a dictionary with parameter names
            df = pd.DataFrame(chain, columns=model.get_labels())

            # Compute alpha_par and alpha_perp for each point in the chain
            alpha_par, alpha_perp = model.get_alphas(df["$\\alpha$"].to_numpy(), df["$\\epsilon$"].to_numpy())
            df["$\\alpha_\\parallel$"] = alpha_par
            df["$\\alpha_\\perp$"] = alpha_perp
            mean, cov = weighted_avg_and_cov(
                df[["$\\alpha_\\parallel$", "$\\alpha_\\perp$", "$\\Sigma_{nl,||}$", "$\\Sigma_{nl,\\perp}$", "$\\Sigma_s$"]],
                weight,
                axis=0,
            )
            extra.pop("realisation", None)
            if "n_poly=5" in extra["name"]:
                extra["name"] = datanames[data_bin] + f" fixed_type {sigma_bin}"
                c[data_bin].add_chain(df, weights=weight, **extra, plot_contour=True, plot_point=False, show_as_1d_prior=False)

            stats[data_bin].append(
                [
                    sigma_sigma[sigma_bin],
                    model.n_poly,
                    mean[0] - 1.0,
                    mean[1] - 1.0,
                    mean[2] - 5.4,
                    mean[3] - 1.8,
                    mean[4],
                    np.sqrt(cov[0, 0]),
                    np.sqrt(cov[1, 1]),
                    np.sqrt(cov[2, 2]),
                    np.sqrt(cov[3, 3]),
                    np.sqrt(cov[4, 4]),
                ]
            )
            output[datanames[data_bin]].append(
                f"{sigma_sigma[sigma_bin]:6.4f}, {model.n_poly:3d}, {mean[0]:6.4f}, {mean[1]:6.4f}, {mean[2]:6.4f}, {mean[3]:6.4f}, {mean[4]:6.4f}, {np.sqrt(cov[0, 0]):6.4f}, {np.sqrt(cov[1, 1]):6.4f}, {np.sqrt(cov[2, 2]):6.4f}, {np.sqrt(cov[3, 3]):6.4f}, {np.sqrt(cov[4, 4]):6.4f}"
            )

        print(stats)

        for data_bin in range(3):
            if "Pre" in datanames[data_bin]:
                truth = {
                    "$\\alpha_\\perp$": 1.0,
                    "$\\alpha_\\parallel$": 1.0,
                    "$\\Sigma_{nl,||}$": 9.71,
                    "$\\Sigma_{nl,\\perp}$": 4.66,
                    "$\\Sigma_s$": None,
                }
            else:
                truth = {
                    "$\\alpha_\\perp$": 1.0,
                    "$\\alpha_\\parallel$": 1.0,
                    "$\\Sigma_{nl,||}$": 5.29,
                    "$\\Sigma_{nl,\\perp}$": 1.57,
                    "$\\Sigma_s$": None,
                }

            c[data_bin].configure(bins=20, sigmas=[0, 1])
            c[data_bin].plotter.plot(
                filename=["/".join(pfn.split("/")[:-1]) + "/" + datanames[data_bin] + "_contour.png"],
                truth=truth,
                parameters=["$\\alpha_\\parallel$", "$\\alpha_\\perp$", "$\\Sigma_{nl,||}$", "$\\Sigma_{nl,\\perp}$", "$\\Sigma_s$"],
                legend=True,
                extents=[(0.98, 1.02), (0.98, 1.02)],
            )

            # Plot histograms of the errors and r_off
            plot_alphas(np.array(stats[data_bin]), "/".join(pfn.split("/")[:-1]) + "/" + datanames[data_bin] + "_alphas.png")
            plot_errors(np.array(stats[data_bin]), "/".join(pfn.split("/")[:-1]) + "/errs_" + datanames[data_bin] + "_alphas.png")

            # Save all the numbers to a file
            with open(dir_name + "/Barry_fit_" + datanames[data_bin] + ".txt", "w") as f:
                f.write(
                    "# N_poly, alpha_par, alpha_perp, sigma_alpha_par, sigma_alpha_perp, corr_alpha_par_perp, rd_of_template, bf_chi2, dof\n"
                )
                for l in output[datanames[data_bin]]:
                    f.write(l + "\n")

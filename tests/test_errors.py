import pytest
import numpy as np
import pandas as pd
from pyfixest import Fixest
from pyfixest.utils import get_data
from pyfixest.exceptions import (
    DuplicateKeyError,
    EndogVarsAsCovarsError,
    InstrumentsAsCovarsError,
    UnderDeterminedIVError,
    VcovTypeNotSupportedError,
    MultiEstNotSupportedError,
    NanInClusterVarError,
)

from pyfixest.FormulaParser import FixestFormulaParser

def test_formula_parser2():
    with pytest.raises(DuplicateKeyError):
        FixestFormulaParser("y ~ sw(a, b) +  sw(c, d)| sw(X3, X4))")


def test_formula_parser3():
    with pytest.raises(DuplicateKeyError):
        FixestFormulaParser("y ~ sw(a, b) +  csw(c, d)| sw(X3, X4))")


# def test_formula_parser2():
#    with pytest.raises(FixedEffectInteractionError):
#        FixestFormulaParser('y ~ X1 + X2 | X3:X4')

# def test_formula_parser3():
#    with pytest.raises(CovariateInteractionError):
#        FixestFormulaParser('y ~ X1 + X2^X3')


def test_i_ref():
    data = get_data()
    fixest = Fixest(data)

    with pytest.raises(ValueError):
        fixest.feols("y ~ i(X1, X2, ref = -1)", vcov="iid")


def test_cluster_na():
    """
    test if a nan value in a cluster variable raises
    an error
    """

    data = get_data()
    data = data.dropna()
    data["f3"] = data["f3"].astype("int64")
    data["f3"][5] = np.nan

    fixest = Fixest(data)
    with pytest.raises(NanInClusterVarError):
        fixest.feols("Y ~ X1", vcov={"CRV1": "f3"})


def test_error_hc23_fe():
    """
    test if HC2&HC3 inference with fixed effects regressions raises an error (currently not supported)
    """
    data = get_data().dropna()

    fixest = Fixest(data)
    with pytest.raises(VcovTypeNotSupportedError):
        fixest.feols("Y ~ X1 | f2", vcov="HC2")

    with pytest.raises(VcovTypeNotSupportedError):
        fixest.feols("Y ~ X1 | f2", vcov="HC3")


def test_depvar_numeric():
    """
    test if feols() throws an error when the dependent variable is not numeric
    """

    data = get_data()
    data["Y"] = data["Y"].astype("str")
    data["Y"] = pd.Categorical(data["Y"])

    fixest = Fixest(data)
    with pytest.raises(TypeError):
        fixest.feols("Y ~ X1")


def test_iv_errors():
    data = get_data()

    fixest = Fixest(data)
    # under determined
    with pytest.raises(UnderDeterminedIVError):
        fixest.feols("Y ~ X1 | Z1 + Z2 ~ 24 ")
    # instrument specified as covariate
    with pytest.raises(InstrumentsAsCovarsError):
        fixest.feols("Y ~ X1 | Z1  ~ X1 + X2")
    # endogeneous variable specified as covariate
    with pytest.raises(EndogVarsAsCovarsError):
        fixest.feols("Y ~ Z1 | Z1  ~ X1")
    # instrument specified as covariate
    # with pytest.raises(InstrumentsAsCovarsError):
    #    fixest.feols('Y ~ X1 | Z1 + Z2 ~ X3 + X4')
    # underdetermined IV
    # with pytest.raises(UnderDeterminedIVError):
    #    fixest.feols('Y ~ X1 + X2 | X1 + X2 ~ X4 ')
    # with pytest.raises(UnderDeterminedIVError):
    #    fixest.feols('Y ~ X1 | Z1 + Z2 ~ X2 + X3 ')
    # CRV3 inference
    with pytest.raises(VcovTypeNotSupportedError):
        fixest.feols("Y ~ 1 | Z1 ~ X1 ", vcov={"CRV3": "group_id"})
    # wild bootstrap
    with pytest.raises(VcovTypeNotSupportedError):
        fixest.feols("Y ~ 1 | Z1 ~ X1 ").wildboottest(param="Z1", B=999)
    # multi estimation error
    with pytest.raises(MultiEstNotSupportedError):
        fixest.feols("Y + Y2 ~ 1 | Z1 ~ X1 ")
    with pytest.raises(MultiEstNotSupportedError):
        fixest.feols("Y  ~ 1 | sw(f2, f3) | Z1 ~ X1 ")
    with pytest.raises(MultiEstNotSupportedError):
        fixest.feols("Y  ~ 1 | csw(f2, f3) | Z1 ~ X1 ")
    # unsupported HC vcov
    with pytest.raises(VcovTypeNotSupportedError):
        fixest.feols("Y  ~ 1 | Z1 ~ X1", vcov="HC2")
    with pytest.raises(VcovTypeNotSupportedError):
        fixest.feols("Y  ~ 1 | Z1 ~ X1", vcov="HC3")


@pytest.mark.skip("Not yet implemented.")
def test_poisson_devpar_count():
    """
    check that the dependent variable is a count variable
    """

    data = get_data()
    fixest = Fixest(data)
    # under determined
    with pytest.raises(AssertionError):
        fixest.fepois("Y ~ X1 | X4 ")

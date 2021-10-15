# Copyright (C) 2021 The PyCBC development team

#
# =============================================================================
#
#                                   Preamble
#
# =============================================================================
#
""" This module provides default site catalogs, which should be suitable for
most use cases. You can override individual details here. It should also be
possible to implement a new site, but not sure how that would work in practice.
"""

import os
import distutils
import urllib.parse
from urllib.parse import urljoin
from urllib.request import pathname2url
from Pegasus.api import Directory, FileServer, Site, Operation, Namespace
from Pegasus.api import Arch, OS

# NOTE urllib is weird. For some reason it only allows known schemes and will
# give *wrong* results, rather then failing, if you use something like gsiftp
# We can add schemes explicitly, as below, but be careful with this!
urllib.parse.uses_relative.append('gsiftp')
urllib.parse.uses_netloc.append('gsiftp')


def add_site_pegasus_profile(site, cp):
    """Add options from [pegasus_profile] in configparser to site"""
    # Add global profile information
    if cp.has_section('pegasus_profile'):
        add_ini_site_profile(site, cp, 'pegasus_profile')
    # Add site-specific profile information
    if cp.has_section('pegasus_profile-{}'.format(site.name)):
        add_ini_site_profile(site, cp, 'pegasus_profile-{}'.format(site.name))


def add_ini_site_profile(site, cp, sec):
    """Add options from sec in configparser to site"""
    for opt in cp.options(sec):
        namespace = opt.split('|')[0]
        if namespace in ('pycbc', 'container'):
            continue

        value = cp.get(sec, opt).strip()
        key = opt.split('|')[1]
        site.add_profiles(Namespace(namespace), key=key, value=value)


def add_local_site(sitecat, cp, local_path, local_url):
    """Add the local site to sitecatalog"""
    # local_url must end with a '/'
    if not local_url.endswith('/'):
        local_url = local_url + '/'

    local = Site("local", arch=Arch.X86_64, os_type=OS.LINUX)
    add_site_pegasus_profile(local, cp)

    local_dir = Directory(Directory.SHARED_SCRATCH,
                          path=os.path.join(local_path, 'local-site-scratch'))
    local_file_serv = FileServer(urljoin(local_url, 'local-site-scratch'),
                                 Operation.ALL)
    local_dir.add_file_servers(local_file_serv)
    local.add_directories(local_dir)

    local.add_profiles(Namespace.PEGASUS, key="style", value="condor")
    local.add_profiles(Namespace.CONDOR, key="getenv", value="True")
    sitecat.add_sites(local)


def add_condorpool_symlink_site(sitecat, cp):
    """Add condorpool_symlink site to site catalog"""
    site = Site("condorpool_symlink", arch=Arch.X86_64, os_type=OS.LINUX)
    add_site_pegasus_profile(site, cp)

    site.add_profiles(Namespace.PEGASUS, key="style", value="condor")
    site.add_profiles(Namespace.PEGASUS, key="transfer.links",
                      value="true")
    site.add_profiles(Namespace.PEGASUS, key="data.configuration",
                      value="nonsharedfs")
    site.add_profiles(Namespace.PEGASUS, key='transfer.bypass.input.staging',
                      value="true")
    site.add_profiles(Namespace.PEGASUS, key='auxillary.local',
                      value="true")
    site.add_profiles(Namespace.CONDOR, key="+OpenScienceGrid",
                      value="False")
    site.add_profiles(Namespace.CONDOR, key="should_transfer_files",
                      value="Yes")
    site.add_profiles(Namespace.CONDOR, key="when_to_transfer_output",
                      value="ON_EXIT_OR_EVICT")
    site.add_profiles(Namespace.CONDOR, key="getenv", value="True")
    site.add_profiles(Namespace.CONDOR, key="+DESIRED_Sites",
                      value='"nogrid"')
    site.add_profiles(Namespace.CONDOR, key="+IS_GLIDEIN",
                      value='"False"')
    site.add_profiles(Namespace.CONDOR, key="+flock_local",
                      value="True")
    site.add_profiles(Namespace.DAGMAN, key="retry", value="2")
    sitecat.add_sites(site)


def add_condorpool_copy_site(sitecat, cp):
    """Add condorpool_copy site to site catalog"""
    site = Site("condorpool_copy", arch=Arch.X86_64, os_type=OS.LINUX)
    add_site_pegasus_profile(site, cp)

    site.add_profiles(Namespace.PEGASUS, key="style", value="condor")
    site.add_profiles(Namespace.PEGASUS, key="data.configuration",
                      value="nonsharedfs")
    site.add_profiles(Namespace.PEGASUS, key='transfer.bypass.input.staging',
                      value="true")
    site.add_profiles(Namespace.PEGASUS, key='auxillary.local',
                      value="true")
    site.add_profiles(Namespace.CONDOR, key="+OpenScienceGrid",
                      value="False")
    site.add_profiles(Namespace.CONDOR, key="should_transfer_files",
                      value="Yes")
    site.add_profiles(Namespace.CONDOR, key="when_to_transfer_output",
                      value="ON_EXIT_OR_EVICT")
    site.add_profiles(Namespace.CONDOR, key="getenv", value="True")
    site.add_profiles(Namespace.CONDOR, key="+DESIRED_Sites",
                      value='"nogrid"')
    site.add_profiles(Namespace.CONDOR, key="+IS_GLIDEIN",
                      value='"False"')
    site.add_profiles(Namespace.CONDOR, key="+flock_local",
                      value="True")
    site.add_profiles(Namespace.DAGMAN, key="retry", value="2")
    sitecat.add_sites(site)


def add_condorpool_shared_site(sitecat, cp, local_path, local_url):
    """Add condorpool_shared site to site catalog"""
    # local_url must end with a '/'
    if not local_url.endswith('/'):
        local_url = local_url + '/'

    site = Site("condorpool_shared", arch=Arch.X86_64, os_type=OS.LINUX)
    add_site_pegasus_profile(site, cp)

    # It's annoying that this is needed!
    local_dir = Directory(Directory.SHARED_SCRATCH,
                          path=os.path.join(local_path, 'cpool-site-scratch'))
    local_file_serv = FileServer(urljoin(local_url, 'cpool-site-scratch'),
                                 Operation.ALL)
    local_dir.add_file_servers(local_file_serv)
    site.add_directories(local_dir)

    site.add_profiles(Namespace.PEGASUS, key="style", value="condor")
    site.add_profiles(Namespace.PEGASUS, key="data.configuration",
                      value="sharedfs")
    site.add_profiles(Namespace.PEGASUS, key='transfer.bypass.input.staging',
                      value="true")
    site.add_profiles(Namespace.PEGASUS, key='auxillary.local',
                      value="true")
    site.add_profiles(Namespace.CONDOR, key="+OpenScienceGrid",
                      value="False")
    site.add_profiles(Namespace.CONDOR, key="should_transfer_files",
                      value="Yes")
    site.add_profiles(Namespace.CONDOR, key="when_to_transfer_output",
                      value="ON_EXIT_OR_EVICT")
    site.add_profiles(Namespace.CONDOR, key="getenv", value="True")
    site.add_profiles(Namespace.CONDOR, key="+DESIRED_Sites",
                      value='"nogrid"')
    site.add_profiles(Namespace.CONDOR, key="+IS_GLIDEIN",
                      value='"False"')
    site.add_profiles(Namespace.CONDOR, key="+flock_local",
                      value="True")
    site.add_profiles(Namespace.DAGMAN, key="retry", value="2")
    # Need to set PEGASUS_HOME
    peg_home = distutils.spawn.find_executable('pegasus-plan')
    assert peg_home.endswith('bin/pegasus-plan')
    peg_home = peg_home.replace('bin/pegasus-plan', '')
    site.add_profiles(Namespace.ENV, key="PEGASUS_HOME", value=peg_home)
    sitecat.add_sites(site)

# Would like to add this, but need to figure out some issues with copy
# protocol. Probably condorio would be the ideal thing to use here, but that
# doesn't work with our INSPIRAL 111111/FILENAME.xml LFN schem

# def add_condorpool_nonfs_site(sitecat, cp):


def add_osg_site(sitecat, cp):
    """Add osg site to site catalog"""
    site = Site("osg", arch=Arch.X86_64, os_type=OS.LINUX)
    add_site_pegasus_profile(site, cp)
    site.add_profiles(Namespace.PEGASUS, key="style", value="condor")
    site.add_profiles(Namespace.PEGASUS, key="data.configuration",
                      value="nonsharedfs")
    site.add_profiles(Namespace.PEGASUS, key='transfer.bypass.input.staging',
                      value="true")
    site.add_profiles(Namespace.CONDOR, key="should_transfer_files",
                      value="Yes")
    site.add_profiles(Namespace.CONDOR, key="when_to_transfer_output",
                      value="ON_EXIT_OR_EVICT")
    site.add_profiles(Namespace.CONDOR, key="+OpenScienceGrid",
                      value="True")
    site.add_profiles(Namespace.CONDOR, key="getenv",
                      value="False")
    site.add_profiles(Namespace.CONDOR, key="+InitializeModulesEnv",
                      value="False")
    site.add_profiles(Namespace.CONDOR, key="+SingularityCleanEnv",
                      value="True")
    site.add_profiles(Namespace.CONDOR, key="Requirements",
                      value="(HAS_SINGULARITY =?= TRUE) && "
                            "(HAS_LIGO_FRAMES =?= True) && "
                            "(IS_GLIDEIN =?= True)")
    # FIXME: This one should be moved to be latest release and/or chosen in the
    #        config file.
    site.add_profiles(Namespace.CONDOR, key="+SingularityImage",
                      value='"/cvmfs/singularity.opensciencegrid.org/pycbc/pycbc-el7:v1.18.0"')
    # On OSG failure rate is high
    site.add_profiles(Namespace.DAGMAN, key="retry", value="4")
    site.add_profiles(Namespace.ENV, key="LAL_DATA_PATH",
                      value="/cvmfs/oasis.opensciencegrid.org/ligo/sw/pycbc/lalsuite-extra/current/share/lalsimulation")
    sitecat.add_sites(site)


def add_site(sitecat, sitename, cp, out_dir=None):
    """Add site sitename to sitecatalog"""
    if out_dir is None:
        out_dir = os.getcwd()
    local_url = urljoin('file://', pathname2url(out_dir))
    if sitename == 'local':
        add_local_site(sitecat, cp, out_dir, local_url)
    elif sitename == 'condorpool_symlink':
        add_condorpool_symlink_site(sitecat, cp)
    elif sitename == 'condorpool_copy':
        add_condorpool_copy_site(sitecat, cp)
    elif sitename == 'condorpool_shared':
        add_condorpool_shared_site(sitecat, cp, out_dir, local_url)
    elif sitename == 'osg':
        add_osg_site(sitecat, cp)
    else:
        raise ValueError("Do not recognize site {}".format(sitename))